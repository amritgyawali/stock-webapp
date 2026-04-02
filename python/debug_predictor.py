
from predictor import StockPredictor
import logging
from config import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug-predictor")

def debug():
    p = StockPredictor()
    stocks = db.select("stocks", "id,symbol", {"is_active": "eq.true"}, limit=5)
    for stock in stocks:
        logger.info(f"Checking {stock['symbol']} (ID: {stock['id']})...")
        rows = db.select("daily_prices", "*", {"stock_id": f"eq.{stock['id']}"}, order="date.desc", limit=100)
        logger.info(f"  Found {len(rows)} price rows.")
        
        # Test the prediction logic
        pred = p._predict_stock(stock['id'], stock['symbol'])
        if pred:
            logger.info(f"  ✅ Prediction: {pred['predicted_close']}")
        else:
            # Let's see why it returned None
            if not rows or len(rows) < 30: # MIN_HISTORY_DAYS
                logger.info("  ❌ Too few rows.")
            else:
                logger.info("  ❌ Still None - likely feature engineering or target missing.")

if __name__ == "__main__":
    debug()
