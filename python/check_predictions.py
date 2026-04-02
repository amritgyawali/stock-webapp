
from config import db
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("check-preds")

def check():
    preds = db.select("predictions", "*", order="prediction_date.desc", limit=10)
    if preds:
        logger.info(f"✅ Found {len(preds)} recent predictions.")
        for p in preds:
            logger.info(f"Date: {p['prediction_date']}, Stock ID: {p['stock_id']}, Change: {p['predicted_change_pct']}%")
    else:
        logger.info("❌ No predictions found.")

if __name__ == "__main__":
    check()
