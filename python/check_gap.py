
from config import db
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("check-db")

def check():
    dates_to_check = []
    current = datetime(2026, 3, 27)
    for _ in range(50):
        dates_to_check.append(current.strftime("%Y-%m-%d"))
        current -= timedelta(days=1)
    
    missing = []
    present = []
    
    for d in dates_to_check:
        res = db.select("daily_prices", "id", filters={"date": f"eq.{d}"}, limit=1)
        if res:
            present.append(d)
        else:
            missing.append(d)
            
    logger.info(f"Summary of last 50 days:")
    logger.info(f"Present ({len(present)}): {present}")
    logger.info(f"Missing ({len(missing)}): {missing}")

if __name__ == "__main__":
    check()
