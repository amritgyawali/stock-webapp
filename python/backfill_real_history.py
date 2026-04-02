import logging
import pandas as pd
from datetime import datetime, timedelta
from nepse_scraper import NepseScraper
from config import db, NPT

logger = logging.getLogger("api-backfill")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

scraper = NepseScraper(verify_ssl=False)

def run_real_backfill(target_days=250):
    logger.info(f"🚀 Starting Real Backfill for {target_days} trading days using API...")
    
    stock_map = {s["symbol"]: s["id"] for s in db.select("stocks", "id,symbol")}
    
    # We will count how many unique valid dates we process
    current_date = datetime.now(NPT) - timedelta(days=1)
    successful_days = 0
    total_stored = 0
    
    while successful_days < target_days:
        date_str = current_date.strftime("%Y-%m-%d")
        current_date -= timedelta(days=1)
        
        # Skip purely weekends to save API calls
        if datetime.strptime(date_str, "%Y-%m-%d").weekday() in [4, 5]: # Friday, Saturday
            continue
            
        # Check DB first
        existing = db.select("daily_prices", "id", {"date": f"eq.{date_str}"}, limit=1)
        if existing:
            logger.info(f"⏩ Date {date_str} already exists in DB.")
            successful_days += 1
            continue
            
        logger.info(f"🔍 Fetching {date_str} via API...")
        try:
            data = scraper.get_today_price(business_date=date_str)
            if not data or len(data) == 0:
                logger.warning(f"⚠️ No data / Holiday for {date_str}")
                continue
                
            records = []
            for row in data:
                symbol = str(row.get('symbol', '')).strip().upper()
                if symbol in stock_map:
                    # nepse-scraper returns dicts with camelCase keys generally based on the JSON
                    records.append({
                        "stock_id": stock_map[symbol],
                        "date": date_str,
                        "open": float(row.get('openPrice', 0)),
                        "high": float(row.get('highPrice', 0)),
                        "low": float(row.get('lowPrice', 0)),
                        "close": float(row.get('lastTradedPrice', row.get('close', 0))),
                        "prev_close": float(row.get('previousDayClosePrice', row.get('previousClose', 0))),
                        "volume": int(float(row.get('totalTradedQuantity', row.get('volume', 0)))),
                        "turnover": float(row.get('totalTradedValue', row.get('turnover', 0))),
                        "change_pct": float(row.get('percentageChange', row.get('perChange', 0)))
                    })
            
            if records:
                db.upsert("daily_prices", records, on_conflict="uq_daily_prices_stock_date")
                logger.info(f"✅ Stored {len(records)} quotes for {date_str}")
                total_stored += len(records)
                successful_days += 1
            else:
                logger.warning(f"⚠️ No matching symbols for {date_str}")
        except Exception as e:
            logger.error(f"❌ Failed to fetch {date_str}: {e}")

    logger.info(f"🎉 API Backfill Complete. Total records stored: {total_stored}")

if __name__ == "__main__":
    run_real_backfill(250)
