"""
NEPSE Live Data Fetcher
Uses NepseUnofficialApi (https://github.com/basic-bgnr/NepseUnofficialApi)
to fetch real-time market data and persist it to Supabase.

Run this once per trading day (or on a schedule) to keep the DB up to date.
"""

import time
import traceback
from datetime import datetime, timezone, timedelta

from config import db, logger, get_nepal_date_str

# Nepal Time
NPT = timezone(timedelta(hours=5, minutes=45))


def get_nepse_client():
    """Initialize and return the Nepse client."""
    try:
        from nepse import Nepse
        nepse = Nepse()
        nepse.setTLSVerification(False)  # Required due to Nepse's incomplete SSL chain
        return nepse
    except ImportError:
        logger.error(
            "❌ 'nepse' package not found. Install it with:\n"
            "   pip install git+https://github.com/basic-bgnr/NepseUnofficialApi"
        )
        raise


def upsert_stock(symbol: str, name: str, sector: str) -> int | None:
    """Ensure stock exists in DB and return its ID."""
    existing = db.select("stocks", "id", {"symbol": f"eq.{symbol}"})
    if existing:
        return existing[0]["id"]
    result = db.upsert(
        "stocks",
        {"symbol": symbol, "name": name, "sector": sector or "General", "is_active": True},
        on_conflict="symbol",
    )
    if result:
        return result[0]["id"]
    return None


def fetch_and_store_live_prices(nepse, today: str) -> int:
    """
    Fetch today's live price data and upsert into daily_prices table.
    Returns number of records stored.
    """
    logger.info("📡 Fetching live price data from Nepse...")

    try:
        price_data = nepse.getPriceVolume()
    except Exception as e:
        logger.error(f"Failed to fetch price/volume data: {e}")
        return 0

    if not price_data:
        logger.warning("No price data returned from Nepse API.")
        return 0

    # Build symbol→id cache to avoid repeated DB lookups
    all_stocks = db.select("stocks", "id,symbol")
    stock_map = {s["symbol"]: s["id"] for s in (all_stocks or [])}

    records = []
    new_stocks = []

    for item in price_data:
        symbol = item.get("symbol") or item.get("s") or item.get("securityName", "")
        if not symbol:
            continue

        # Normalise field names (the library uses different casing across endpoints)
        name = item.get("securityName") or item.get("name") or symbol
        sector = item.get("sectorName") or item.get("sector") or "General"
        close = _to_float(item.get("closingPrice") or item.get("ltp") or item.get("close"))
        open_ = _to_float(item.get("openPrice") or item.get("open"))
        high = _to_float(item.get("highPrice") or item.get("high"))
        low = _to_float(item.get("lowPrice") or item.get("low"))
        prev_close = _to_float(item.get("previousClose") or item.get("prevClose"))
        volume = _to_float(item.get("totalTradeQuantity") or item.get("volume"))
        turnover = _to_float(item.get("totalTradeValue") or item.get("turnover"))

        if close is None:
            continue

        # Change %
        if prev_close and prev_close > 0 and close is not None:
            change_pct = round((close - prev_close) / prev_close * 100, 2)
        else:
            change_pct = 0.0

        # Resolve stock_id
        if symbol not in stock_map:
            new_stocks.append({"symbol": symbol, "name": name, "sector": sector, "is_active": True})

        records.append({
            "symbol": symbol,
            "name": name,
            "sector": sector,
            "date": today,
            "open": open_ or close,
            "high": high or close,
            "low": low or close,
            "close": close,
            "prev_close": prev_close,
            "volume": int(volume) if volume else 0,
            "turnover": turnover or 0.0,
            "change_pct": change_pct,
        })

    # Upsert any brand-new stocks first
    if new_stocks:
        logger.info(f"  🆕 Inserting {len(new_stocks)} new stock entries...")
        for s in new_stocks:
            try:
                result = db.upsert("stocks", s, on_conflict="symbol")
                if result:
                    stock_map[s["symbol"]] = result[0]["id"]
            except Exception:
                pass
        # Refresh map
        all_stocks = db.select("stocks", "id,symbol")
        stock_map = {s["symbol"]: s["id"] for s in (all_stocks or [])}

    # Build daily_prices records with resolved stock_ids
    price_records = []
    for r in records:
        sid = stock_map.get(r["symbol"])
        if not sid:
            continue
        # Sanity-check: skip insane daily moves (> 15% up/down hard cap)
        if abs(r["change_pct"]) > 15:
            logger.warning(f"  ⚠️  Skipping {r['symbol']} – suspicious change {r['change_pct']}%")
            continue
        price_records.append({
            "stock_id": sid,
            "date": r["date"],
            "open": r["open"],
            "high": r["high"],
            "low": r["low"],
            "close": r["close"],
            "prev_close": r["prev_close"],
            "volume": r["volume"],
            "turnover": r["turnover"],
            "change_pct": r["change_pct"],
        })

    # Batch upsert in chunks of 100
    stored = 0
    CHUNK = 100
    for i in range(0, len(price_records), CHUNK):
        chunk = price_records[i:i + CHUNK]
        try:
            db.upsert("daily_prices", chunk, on_conflict="stock_id,date")
            stored += len(chunk)
        except Exception as e:
            logger.error(f"  Batch upsert error (chunk {i}): {e}")

    logger.info(f"  ✅ Stored {stored} price records for {today}.")
    return stored


def fetch_and_store_market_summary(nepse, today: str) -> bool:
    """
    Fetch NEPSE index summary and upsert into market_summary table.
    Returns True on success.
    """
    logger.info("📊 Fetching market summary / NEPSE index...")

    nepse_index = None
    nepse_change = None
    nepse_change_pct = None
    total_turnover = None
    total_transactions = None

    # Try Summary endpoint
    try:
        summary = nepse.getSummary()
        if summary:
            nepse_index = _to_float(summary.get("nepseIndex") or summary.get("currentValue"))
            nepse_change = _to_float(summary.get("change") or summary.get("absoluteChange"))
            nepse_change_pct = _to_float(summary.get("perChange") or summary.get("percentChange"))
            total_turnover = _to_float(summary.get("totalTurnover") or summary.get("turnover"))
            total_transactions = _to_float(summary.get("totalTransactions") or summary.get("transactions"))
    except Exception as e:
        logger.warning(f"  Summary endpoint failed: {e}")

    # Fallback: try NepseIndex endpoint
    if nepse_index is None:
        try:
            idx = nepse.getNepseIndex()
            if isinstance(idx, list) and idx:
                idx = idx[0]
            if isinstance(idx, dict):
                nepse_index = _to_float(idx.get("currentValue") or idx.get("nepseIndex"))
                nepse_change = _to_float(idx.get("absoluteChange") or idx.get("change"))
                nepse_change_pct = _to_float(idx.get("percentChange") or idx.get("perChange"))
        except Exception as e:
            logger.warning(f"  NepseIndex endpoint also failed: {e}")

    record = {
        "date": today,
        "nepse_index": nepse_index,
        "nepse_change": nepse_change or 0.0,
        "nepse_change_pct": nepse_change_pct or 0.0,
        "total_turnover": total_turnover or 0.0,
        "total_transactions": int(total_transactions) if total_transactions else 0,
    }

    try:
        db.upsert("market_summary", record, on_conflict="date")
        logger.info(f"  ✅ Market summary stored — NEPSE: {nepse_index or 'N/A'} ({nepse_change_pct or 0:.2f}%)")
        return True
    except Exception as e:
        logger.error(f"  Failed to store market summary: {e}")
        return False


def fetch_top_movers(nepse) -> dict:
    """Fetch top gainers and losers for contextual logging."""
    result = {"gainers": [], "losers": []}
    try:
        gainers = nepse.getTopGainers()
        result["gainers"] = gainers[:5] if gainers else []
    except Exception:
        pass
    try:
        losers = nepse.getTopLosers()
        result["losers"] = losers[:5] if losers else []
    except Exception:
        pass
    return result


def log_top_movers(movers: dict):
    if movers["gainers"]:
        symbols = [g.get("symbol") or g.get("s", "?") for g in movers["gainers"]]
        logger.info(f"  🚀 Top Gainers today: {', '.join(symbols)}")
    if movers["losers"]:
        symbols = [l.get("symbol") or l.get("s", "?") for l in movers["losers"]]
        logger.info(f"  📉 Top Losers today: {', '.join(symbols)}")


def _to_float(val) -> float | None:
    """Safely convert any value to float."""
    if val is None:
        return None
    try:
        return float(val)
    except (ValueError, TypeError):
        return None


def run(retry: int = 3, delay: int = 10):
    """
    Main entry-point. Fetches live NEPSE data and stores it to Supabase.
    Retries on transient errors.
    """
    today = get_nepal_date_str()
    logger.info(f"🇳🇵 NEPSE Live Fetcher starting — Date: {today}")

    for attempt in range(1, retry + 1):
        try:
            nepse = get_nepse_client()

            # 1. Market Summary (NEPSE Index)
            fetch_and_store_market_summary(nepse, today)

            # 2. All live stock prices
            stored = fetch_and_store_live_prices(nepse, today)

            # 3. Top movers (log only)
            movers = fetch_top_movers(nepse)
            log_top_movers(movers)

            logger.info(f"🎉 Live data fetch complete — {stored} stocks updated in Supabase.")
            return stored

        except Exception as e:
            logger.error(f"Attempt {attempt}/{retry} failed: {e}")
            traceback.print_exc()
            if attempt < retry:
                logger.info(f"  Retrying in {delay}s...")
                time.sleep(delay)

    logger.error("❌ All retry attempts exhausted. Live fetch failed.")
    return 0


if __name__ == "__main__":
    run()
