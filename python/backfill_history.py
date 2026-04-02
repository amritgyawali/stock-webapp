import logging
import random
from datetime import datetime, timedelta
from config import db

logger = logging.getLogger("synth-backfiller")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

def get_last_250_trading_days():
    dates = []
    current_date = datetime.now() - timedelta(days=1)
    
    while len(dates) < 250:
        if current_date.weekday() not in [4, 5]:  # Exclude Fri/Sat
            dates.append(current_date.strftime("%Y-%m-%d"))
        current_date -= timedelta(days=1)
        
    return dates

def run_synthetic_backfill():
    logger.info("===========================================")
    logger.info("🚀 Initiating Insta-ML Synthetic Backfill System")
    logger.info("===========================================")
    
    # 1. Fetch the MOST RECENT prices available in the DB to use as an anchor
    all_dates = db.select("daily_prices", "date", limit=1, order="date.desc")
    if not all_dates:
        logger.error("❌ CRITICAL: No reference data exists in Supabase. Run main.py first.")
        return
        
    anchor_date = all_dates[0]["date"]
    latest_prices = db.select("daily_prices", "*", {"date": f"eq.{anchor_date}"})
    
    logger.info(f"✅ Found {len(latest_prices)} reference anchor stocks from {anchor_date}. Synthesizing timeline...")
    
    dates_to_generate = get_last_250_trading_days()
    # Filter and sort
    dates_to_generate = [d for d in dates_to_generate if d != anchor_date]
    dates_to_generate.sort()
    
    total_stored = 0
    total_dates = 0
    
    for process_date in dates_to_generate:
        # Check if date already exists to avoid unique constraint violations
        existing = db.select("daily_prices", "id", {"date": f"eq.{process_date}"}, limit=1)
        if existing:
            logger.info(f"⏩ Date {process_date} already exists. Skipping synthetic generation.")
            continue

        synth_batch = []
        for baseline in latest_prices:
            # Jitter the price slightly (-2% to +2%) to simulate market variance
            variance_pct = random.uniform(-0.02, 0.02)
            base_price = float(baseline.get('close', 0))
            if base_price == 0: continue
            
            synth_price = round(base_price + (base_price * variance_pct), 2)
            
            synth_batch.append({
                "stock_id": baseline["stock_id"],
                "date": process_date,
                "close": synth_price,
                "volume": int(baseline.get("volume", 5000) * random.uniform(0.5, 1.5)),
                "change_pct": round(variance_pct * 100, 2)
            })
            
        # Push to supabase
        logger.info(f"⏳ Batch Inserting {len(synth_batch)} vectors for {process_date}...")
        try:
            # Using insert instead of upsert for historical data to avoid on_conflict header quirks
            res = db.insert("daily_prices", synth_batch)
            logger.info(f"✅ Supabase inserted {len(res) if res else 0} historical records for {process_date}")
            total_stored += len(res) if res else 0
            total_dates += 1
        except Exception as e:
            logger.error(f"Failed to batch insert for {process_date}: {e}")
            
    logger.info("===========================================")
    logger.info(f"🎉 INSTA-ML BACKFILL COMPLETE!")
    logger.info(f"📈 Total Historical Dates Active: {total_dates}/250")
    logger.info(f"💾 Total Vector Rows Safely Stored: {total_stored}")
    logger.info("===========================================")

if __name__ == "__main__":
    run_synthetic_backfill()
