"""
NEPSE Stock Analysis — Data Scraper
Fetches stock data from free NEPSE APIs with ShareSansar fallback.
"""

import requests
import pandas as pd
from typing import Optional
from bs4 import BeautifulSoup

from config import (
    logger,
    db,
    NEPSE_ENDPOINTS,
    SHARESANSAR_TODAY_PRICE,
    REQUEST_TIMEOUT,
    REQUEST_HEADERS,
    get_nepal_date_str,
)
from nepse_official_client import nepse_client
from live_nepse_fetcher import live_fetcher


class NepseScraper:
    """Fetches and stores NEPSE stock data from multiple sources."""

    def __init__(self):
        self.today = get_nepal_date_str()
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)

    # ─────────────────────────────────────────────
    # PUBLIC METHODS
    # ─────────────────────────────────────────────

    def sync_company_list(self) -> int:
        """Fetch all NEPSE-listed companies and upsert into stocks table."""
        logger.info("📋 Syncing company list...")
        companies = self._fetch_company_list_api()

        if not companies:
            logger.warning("API company list failed, trying ShareSansar fallback...")
            companies = self._fetch_company_list_sharesansar()

        if not companies:
            logger.error("❌ Could not fetch company list from any source!")
            return 0

        # Upsert into stocks table
        synced = 0
        for company in companies:
            try:
                db.upsert("stocks", {
                    "symbol": company["symbol"],
                    "name": company.get("name", company["symbol"]),
                    "sector": company.get("sector", "Unknown"),
                    "is_active": True,
                }, on_conflict="symbol")
                synced += 1
            except Exception as e:
                logger.error(f"Error upserting {company['symbol']}: {e}")

        logger.info(f"✅ Synced {synced} companies")
        return synced

    def fetch_todays_prices(self) -> pd.DataFrame:
        """Fetch today's price data for all stocks."""
        logger.info(f"📊 Fetching today's prices for {self.today}...")

        df = self._fetch_prices_api()

        if df is None or df.empty:
            logger.warning("API prices failed, trying ShareSansar fallback...")
            df = self._fetch_prices_sharesansar()

        if df is None or df.empty:
            logger.error("❌ Could not fetch prices from any source!")
            return pd.DataFrame()

        logger.info(f"✅ Fetched prices for {len(df)} stocks")
        return df

    def store_daily_prices(self, df: pd.DataFrame) -> int:
        """Store today's price data into the daily_prices table."""
        if df.empty:
            return 0

        logger.info(f"💾 Storing {len(df)} price records...")
        stock_map = self._get_stock_id_map()
        inserted = 0

        for _, row in df.iterrows():
            symbol = row.get("symbol", "")
            if symbol not in stock_map:
                continue

            stock_id = stock_map[symbol]
            record = {
                "stock_id": stock_id,
                "date": self.today,
                "open": self._safe_float(row.get("open")),
                "high": self._safe_float(row.get("high")),
                "low": self._safe_float(row.get("low")),
                "close": self._safe_float(row.get("close")),
                "prev_close": self._safe_float(row.get("prev_close")),
                "volume": self._safe_int(row.get("volume")),
                "turnover": self._safe_float(row.get("turnover")),
                "change_pct": self._safe_float(row.get("change_pct")),
            }
            # Remove None values
            record = {k: v for k, v in record.items() if v is not None}

            try:
                db.upsert("daily_prices", record, on_conflict="uq_daily_prices_stock_date")
                inserted += 1
            except Exception as e:
                logger.error(f"Error storing price for {symbol}: {e}")

        logger.info(f"✅ Stored {inserted} price records")
        return inserted

    def fetch_and_store_market_summary(self) -> dict:
        """Fetch and store today's NEPSE market summary."""
        logger.info("📈 Fetching market summary...")

        summary = {}
        # Try official client first
        if nepse_client.is_available():
            summary = nepse_client.get_market_summary()

        if not summary:
            # Fallback to unofficial mirror API
            try:
                resp = self.session.get(NEPSE_ENDPOINTS["summary"], timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                data = resp.json()

                # Also fetch NEPSE index
                idx_data = {}
                try:
                    idx_resp = self.session.get(NEPSE_ENDPOINTS["nepse_index"], timeout=REQUEST_TIMEOUT)
                    if idx_resp.ok:
                        idx_data = idx_resp.json()
                except Exception:
                    pass

                summary = {
                    "total_turnover": self._safe_float(data.get("Total Turnover Rs:")),
                    "total_traded_shares": self._safe_int(data.get("Total Traded Shares")),
                    "total_transactions": self._safe_int(data.get("Total Transactions")),
                    "total_scrips_traded": self._safe_int(data.get("Total Scrips Traded")),
                    "nepse_index": self._safe_float(idx_data.get("currentValue", idx_data.get("index"))),
                    "nepse_change": self._safe_float(idx_data.get("change", idx_data.get("pointChange"))),
                    "nepse_change_pct": self._safe_float(idx_data.get("percentChange", idx_data.get("perChange"))),
                }
            except Exception as e:
                logger.error(f"❌ Error fetching mirror market summary: {e}")

        if summary:
            summary["date"] = self.today
            summary = {k: v for k, v in summary.items() if v is not None}
            db.upsert("market_summary", summary, on_conflict="date")
            logger.info(f"✅ Market summary stored: NEPSE Index = {summary.get('nepse_index')}")
            return summary

        return {}

    # ─────────────────────────────────────────────
    # PRIVATE: API DATA FETCHERS
    # ─────────────────────────────────────────────

    def _fetch_company_list_api(self) -> list[dict]:
        """Fetch company list using the best available API."""
        # 1. Try official client first
        if nepse_client.is_available():
            companies = nepse_client.get_company_list()
            if companies:
                logger.info(f"✅ Fetched {len(companies)} companies via official library")
                return companies

        # 2. Fallback to unofficial mirror API
        try:
            resp = self.session.get(NEPSE_ENDPOINTS["company_list"], timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            companies = []
            if isinstance(data, list):
                for item in data:
                    symbol = item.get("symbol", item.get("Symbol", ""))
                    if symbol:
                        companies.append({
                            "symbol": symbol.strip().upper(),
                            "name": item.get("companyName", item.get("name", symbol)),
                            "sector": item.get("sectorName", item.get("sector", "Unknown")),
                        })
            return companies
        except Exception as e:
            logger.error(f"Mirror API company list error: {e}")
            return []

    def _fetch_prices_api(self) -> Optional[pd.DataFrame]:
        """Fetch today's prices using the best available API."""
        # 1. Try official NEPSE client first (uses NepseUnofficialApi library)
        logger.info("📡 Trying official NEPSE library (nepse) for live prices...")
        try:
            if nepse_client.is_available():
                df = nepse_client.get_today_prices()
                if df is not None and not df.empty:
                    logger.info(f"✅ Successfully fetched {len(df)} live prices from official NEPSE")
                    return df
        except Exception as e:
            logger.warning(f"Official NEPSE client error: {e}")
        
        # 2. Fallback to live fetcher
        logger.info("📡 Trying direct NEPSE API endpoint...")
        try:
            if live_fetcher.authenticate():
                df = live_fetcher.fetch_live_prices()
                if df is not None and not df.empty:
                    logger.info(f"✅ Successfully fetched {len(df)} live prices from direct endpoint")
                    return df
        except Exception as e:
            logger.warning(f"Direct NEPSE API error: {e}")

        # 3. Fallback to unofficial mirror API
        logger.info("📡 Trying mirror API as fallback...")
        try:
            resp = self.session.get(NEPSE_ENDPOINTS["price_volume"], timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if not isinstance(data, list) or len(data) == 0:
                resp = self.session.get(NEPSE_ENDPOINTS["live_market"], timeout=REQUEST_TIMEOUT)
                resp.raise_for_status()
                data = resp.json()

            if not isinstance(data, list) or len(data) == 0:
                return None

            records = []
            for item in data:
                symbol = item.get("symbol", item.get("Symbol", ""))
                if not symbol:
                    continue

                records.append({
                    "symbol": symbol.strip().upper(),
                    "open": self._safe_float(item.get("openPrice", item.get("open"))),
                    "high": self._safe_float(item.get("highPrice", item.get("high"))),
                    "low": self._safe_float(item.get("lowPrice", item.get("low"))),
                    "close": self._safe_float(
                        item.get("lastTradedPrice",
                        item.get("ltp",
                        item.get("close",
                        item.get("closingPrice"))))
                    ),
                    "prev_close": self._safe_float(
                        item.get("previousClose",
                        item.get("previousClosingPrice",
                        item.get("prevClose")))
                    ),
                    "volume": self._safe_int(
                        item.get("totalTradeQuantity",
                        item.get("volume",
                        item.get("shareTraded")))
                    ),
                    "turnover": self._safe_float(item.get("turnover", item.get("amount"))),
                    "change_pct": self._safe_float(
                        item.get("percentageChange",
                        item.get("perChange",
                        item.get("percentChange")))
                    ),
                })

            if records:
                logger.info(f"✅ Successfully fetched {len(records)} prices from mirror API")
                return pd.DataFrame(records)

        except Exception as e:
            logger.error(f"Mirror API price fetch error: {e}")
        
        return None

    # ─────────────────────────────────────────────
    # PRIVATE: SHARESANSAR FALLBACK
    # ─────────────────────────────────────────────

    def _fetch_company_list_sharesansar(self) -> list[dict]:
        """Fallback: Scrape company list from ShareSansar."""
        try:
            resp = self.session.get(SHARESANSAR_TODAY_PRICE, timeout=REQUEST_TIMEOUT, headers={
                **REQUEST_HEADERS,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            })
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            companies = []
            table = soup.find("table", class_="table")
            if table:
                for row in table.find_all("tr")[1:]:
                    cols = row.find_all("td")
                    if len(cols) >= 2:
                        symbol = cols[1].get_text(strip=True).upper()
                        if symbol:
                            companies.append({"symbol": symbol, "name": symbol, "sector": "Unknown"})
            return companies
        except Exception as e:
            logger.error(f"ShareSansar company list error: {e}")
            return []

    def _fetch_prices_sharesansar(self) -> Optional[pd.DataFrame]:
        """Fallback: Scrape today's prices from ShareSansar."""
        try:
            resp = self.session.get(SHARESANSAR_TODAY_PRICE, timeout=REQUEST_TIMEOUT, headers={
                **REQUEST_HEADERS,
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            })
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            records = []
            table = soup.find("table", class_="table")
            if not table:
                return None
            for row in table.find_all("tr")[1:]:
                cols = row.find_all("td")
                if len(cols) >= 10:
                    try:
                        records.append({
                            "symbol": cols[1].get_text(strip=True).upper(),
                            "open": self._safe_float(cols[2].get_text(strip=True).replace(",", "")),
                            "high": self._safe_float(cols[3].get_text(strip=True).replace(",", "")),
                            "low": self._safe_float(cols[4].get_text(strip=True).replace(",", "")),
                            "close": self._safe_float(cols[5].get_text(strip=True).replace(",", "")),
                            "prev_close": self._safe_float(cols[7].get_text(strip=True).replace(",", "")),
                            "volume": self._safe_int(cols[8].get_text(strip=True).replace(",", "")),
                            "turnover": self._safe_float(cols[9].get_text(strip=True).replace(",", "")),
                            "change_pct": self._safe_float(cols[6].get_text(strip=True).replace(",", "").replace("%", "")),
                        })
                    except (ValueError, IndexError):
                        continue
            return pd.DataFrame(records) if records else None
        except Exception as e:
            logger.error(f"ShareSansar price scrape error: {e}")
            return None

    # ─────────────────────────────────────────────
    # HELPERS
    # ─────────────────────────────────────────────

    def _get_stock_id_map(self) -> dict[str, int]:
        """Get mapping of symbol -> stock_id."""
        try:
            rows = db.select("stocks", "id,symbol", {"is_active": "eq.true"})
            return {row["symbol"]: row["id"] for row in rows}
        except Exception as e:
            logger.error(f"Error fetching stock map: {e}")
            return {}

    @staticmethod
    def _safe_float(value) -> Optional[float]:
        if value is None or value == "" or value == "-":
            return None
        try:
            return round(float(str(value).replace(",", "")), 2)
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _safe_int(value) -> Optional[int]:
        if value is None or value == "" or value == "-":
            return None
        try:
            return int(float(str(value).replace(",", "")))
        except (ValueError, TypeError):
            return None
