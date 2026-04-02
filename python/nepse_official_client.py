"""
NEPSE Official Client — Adapter for NepseUnofficialApi
Wraps the 'nepse' library (basic-bgnr/NepseUnofficialApi) and
returns data in the same shape that NepseScraper already expects.

Install: pip install git+https://github.com/basic-bgnr/NepseUnofficialApi
"""

from __future__ import annotations

import logging
from typing import Optional

import pandas as pd

logger = logging.getLogger("nepse-official-client")

# ─────────────────────────────────────────────────────────────
# Try to import the library; gracefully degrade if missing.
# ─────────────────────────────────────────────────────────────
try:
    from nepse import Nepse

    _NEPSE_AVAILABLE = True
except ImportError as e:
    import traceback
    traceback.print_exc()
    _NEPSE_AVAILABLE = False
    logger.warning(
        f"⚠️  NepseUnofficialApi not installed or error: {e}. "
        "Run: pip install git+https://github.com/basic-bgnr/NepseUnofficialApi"
    )


class NepseOfficialClient:
    """
    Thin adapter around NepseUnofficialApi that returns data in the
    same dict/DataFrame format expected by NepseScraper.

    Usage
    -----
    client = NepseOfficialClient()
    if client.is_available():
        companies = client.get_company_list()   # list[dict]
        prices_df = client.get_today_prices()   # pd.DataFrame | None
        summary   = client.get_market_summary() # dict
    """

    def __init__(self):
        self._nepse: Optional[object] = None
        self._initialized = False

    # ─────────────────────────────────────────────────────────
    # PUBLIC INTERFACE
    # ─────────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """Returns True if the library is installed and the client connected."""
        if not _NEPSE_AVAILABLE:
            return False
        return self._ensure_connected()

    def get_company_list(self) -> list[dict]:
        """
        Returns list of dicts with keys: symbol, name, sector.
        """
        if not self._ensure_connected():
            return []

        try:
            raw = self._nepse.getCompanyList()
            return self._parse_company_list(raw)
        except Exception as exc:
            logger.error(f"NepseOfficialClient.get_company_list error: {exc}")
            return []

    def get_today_prices(self) -> Optional[pd.DataFrame]:
        """
        Returns DataFrame with columns:
            symbol, open, high, low, close, prev_close,
            volume, turnover, change_pct
        Returns None on failure.
        """
        if not self._ensure_connected():
            return None

        try:
            raw = self._nepse.getPriceVolume()
            df = self._parse_price_data(raw)
            if df is not None and not df.empty:
                logger.info(f"✅ NepseOfficialClient fetched {len(df)} price rows via official API")
            return df
        except Exception as exc:
            logger.error(f"NepseOfficialClient.get_today_prices error: {exc}")
            # Try live market as secondary
            try:
                raw = self._nepse.getLiveMarket()
                return self._parse_price_data(raw)
            except Exception as exc2:
                logger.error(f"NepseOfficialClient.get_live_market fallback error: {exc2}")
                return None

    def get_market_summary(self) -> dict:
        """
        Returns dict with keys matching the market_summary table:
            nepse_index, nepse_change, nepse_change_pct,
            total_turnover, total_traded_shares, total_transactions,
            total_scrips_traded
        """
        if not self._ensure_connected():
            return {}

        summary: dict = {}

        # NEPSE index
        try:
            idx = self._nepse.getNepseIndex()
            if isinstance(idx, dict):
                summary["nepse_index"] = self._safe_float(
                    idx.get("currentValue", idx.get("index"))
                )
                summary["nepse_change"] = self._safe_float(
                    idx.get("change", idx.get("pointChange"))
                )
                summary["nepse_change_pct"] = self._safe_float(
                    idx.get("percentChange", idx.get("perChange"))
                )
            elif isinstance(idx, list) and idx:
                first = idx[0]
                summary["nepse_index"] = self._safe_float(
                    first.get("currentValue", first.get("index"))
                )
                summary["nepse_change"] = self._safe_float(
                    first.get("change", first.get("pointChange"))
                )
                summary["nepse_change_pct"] = self._safe_float(
                    first.get("percentChange", first.get("perChange"))
                )
        except Exception as exc:
            logger.warning(f"Could not fetch NEPSE index: {exc}")

        # Market summary
        try:
            data = self._nepse.getSummary()
            if isinstance(data, dict):
                summary["total_turnover"] = self._safe_float(
                    data.get("Total Turnover Rs:", data.get("totalTurnover"))
                )
                summary["total_traded_shares"] = self._safe_int(
                    data.get("Total Traded Shares", data.get("totalTradedShares"))
                )
                summary["total_transactions"] = self._safe_int(
                    data.get("Total Transactions", data.get("totalTransactions"))
                )
                summary["total_scrips_traded"] = self._safe_int(
                    data.get("Total Scrips Traded", data.get("totalScripsTraded"))
                )
        except Exception as exc:
            logger.warning(f"Could not fetch market summary: {exc}")

        # Strip None values
        return {k: v for k, v in summary.items() if v is not None}

    def get_top_gainers(self) -> list[dict]:
        """Returns top gainers as list[dict] with symbol, change_pct, close keys."""
        if not self._ensure_connected():
            return []
        try:
            raw = self._nepse.getTopGainers()
            return self._parse_movers(raw)
        except Exception as exc:
            logger.error(f"get_top_gainers error: {exc}")
            return []

    def get_top_losers(self) -> list[dict]:
        """Returns top losers as list[dict] with symbol, change_pct, close keys."""
        if not self._ensure_connected():
            return []
        try:
            raw = self._nepse.getTopLosers()
            return self._parse_movers(raw)
        except Exception as exc:
            logger.error(f"get_top_losers error: {exc}")
            return []

    def get_market_depth(self, symbol: str) -> dict:
        """Returns market depth (supply/demand) for a specific symbol."""
        if not self._ensure_connected():
            return {}
        try:
            raw = self._nepse.getStockTradingAverageSubindices(symbol)
            return raw if isinstance(raw, dict) else {}
        except Exception as exc:
            logger.error(f"get_market_depth({symbol}) error: {exc}")
            return {}

    # ─────────────────────────────────────────────────────────
    # PRIVATE HELPERS
    # ─────────────────────────────────────────────────────────

    def _ensure_connected(self) -> bool:
        """Lazy-initialize and connect to NEPSE once."""
        if self._initialized:
            return self._nepse is not None

        self._initialized = True
        if not _NEPSE_AVAILABLE:
            return False

        try:
            logger.info("🔌 Connecting to NEPSE via NepseUnofficialApi…")
            nepse = Nepse()
            nepse.setTLSVerification(False)  # Temporary — NEPSE SSL cert chain incomplete
            # Trigger a lightweight call to validate the connection
            _ = nepse.getNepseIndex()
            self._nepse = nepse
            logger.info("✅ NEPSE official connection established")
            return True
        except Exception as exc:
            logger.error(f"❌ Failed to connect via NepseUnofficialApi: {exc}")
            self._nepse = None
            return False

    def _parse_company_list(self, raw) -> list[dict]:
        """Normalise raw company list into [{symbol, name, sector}]."""
        companies = []
        items = raw if isinstance(raw, list) else (raw.get("content", []) if isinstance(raw, dict) else [])
        for item in items:
            if not isinstance(item, dict):
                continue
            symbol = (
                item.get("symbol", item.get("Symbol", item.get("stockSymbol", "")))
            )
            if not symbol:
                continue
            companies.append({
                "symbol": str(symbol).strip().upper(),
                "name": item.get("companyName", item.get("name", item.get("stockName", symbol))),
                "sector": item.get("sectorName", item.get("sector", "Unknown")),
            })
        return companies

    def _parse_price_data(self, raw) -> Optional[pd.DataFrame]:
        """Normalise raw price data into a DataFrame."""
        items = raw if isinstance(raw, list) else (raw.get("content", []) if isinstance(raw, dict) else [])
        if not items:
            return None

        records = []
        for item in items:
            if not isinstance(item, dict):
                continue
            symbol = item.get("symbol", item.get("Symbol", item.get("stockSymbol", "")))
            if not symbol:
                continue

            records.append({
                "symbol": str(symbol).strip().upper(),
                "open": self._safe_float(item.get("openPrice", item.get("open"))),
                "high": self._safe_float(item.get("highPrice", item.get("high"))),
                "low": self._safe_float(item.get("lowPrice", item.get("low"))),
                "close": self._safe_float(
                    item.get("lastTradedPrice", item.get("ltp", item.get("close", item.get("closingPrice"))))
                ),
                "prev_close": self._safe_float(
                    item.get("previousClose", item.get("previousClosingPrice", item.get("prevClose")))
                ),
                "volume": self._safe_int(
                    item.get("totalTradeQuantity", item.get("volume", item.get("shareTraded")))
                ),
                "turnover": self._safe_float(item.get("turnover", item.get("amount"))),
                "change_pct": self._safe_float(
                    item.get("percentageChange", item.get("perChange", item.get("percentChange")))
                ),
            })

        return pd.DataFrame(records) if records else None

    def _parse_movers(self, raw) -> list[dict]:
        """Parse top gainers/losers list."""
        items = raw if isinstance(raw, list) else (raw.get("content", []) if isinstance(raw, dict) else [])
        movers = []
        for item in items:
            if not isinstance(item, dict):
                continue
            symbol = item.get("symbol", item.get("Symbol", ""))
            if not symbol:
                continue
            movers.append({
                "symbol": str(symbol).strip().upper(),
                "close": self._safe_float(
                    item.get("lastTradedPrice", item.get("ltp", item.get("close")))
                ),
                "change_pct": self._safe_float(
                    item.get("percentageChange", item.get("perChange"))
                ),
            })
        return movers

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


# ─────────────────────────────────────────────────────────────
# Singleton — reuse across the process lifetime
# ─────────────────────────────────────────────────────────────
nepse_client = NepseOfficialClient()
