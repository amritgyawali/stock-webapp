
from config import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("check-db")

def check():
    dates = db.select("daily_prices", "date", order="date.desc", limit=5)
    for d in sorted(list(set(r['date'] for r in dates))):
        res = db.select("daily_prices", "count", filters={"date": f"eq.{d}"})
        # Supabase select(count=exact) is needed, but we can just select id and len
        ids = db.select("daily_prices", "id", filters={"date": f"eq.{d}"})
        logger.info(f"Date {d}: {len(ids)} stocks")

if __name__ == "__main__":
    check()
