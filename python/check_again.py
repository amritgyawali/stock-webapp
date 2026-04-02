
from config import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("check-db")

def check():
    # Total row count
    res = db.select("daily_prices", "id", limit=1, filters={"date": "eq.2026-03-03"})
    logger.info(f"Existing rows for 2026-03-03: {len(res)}")
    
    # All unique dates
    all_prices = db.select("daily_prices", "date")
    unique_dates = sorted(list(set(p['date'] for p in all_prices)))
    logger.info(f"Unique dates ({len(unique_dates)}): {unique_dates}")

if __name__ == "__main__":
    check()
