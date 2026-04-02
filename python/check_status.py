
from config import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("check-db")

def check():
    # Count daily_prices
    res = db.select("daily_prices", "count", limit=1)
    # Note: Supabase REST API count is a bit different, but let's try a simple select
    
    # Get distinct dates
    prices = db.select("daily_prices", "date", order="date.desc")
    unique_dates = sorted(list(set(p['date'] for p in prices)))
    
    logger.info(f"Total unique dates in daily_prices: {len(unique_dates)}")
    if unique_dates:
        logger.info(f"Date range: {unique_dates[0]} to {unique_dates[-1]}")
    
    # Check predictions
    preds = db.select("predictions", "count", limit=1)
    logger.info(f"Predictions table has data: {bool(preds)}")

if __name__ == "__main__":
    check()
