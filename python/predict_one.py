
import logging
import pandas as pd
from predictor import StockPredictor
from config import db

logging.basicConfig(level=logging.DEBUG) # Force DEBUG
logger = logging.getLogger("predict-one")

def run():
    p = StockPredictor()
    # Pick a stock we KNOW has data (e.g., NABIL)
    stock = db.select("stocks", "id,symbol", {"symbol": "eq.NABIL"}, limit=1)
    if not stock:
        logger.error("NABIL not found in stocks table!")
        return
        
    stock_id = stock[0]['id']
    symbol = stock[0]['symbol']
    logger.info(f"Predicting for {symbol} (ID: {stock_id})...")
    
    rows = db.select("daily_prices", "*", {"stock_id": f"eq.{stock_id}"}, order="date.desc", limit=300)
    logger.info(f"Retrieved {len(rows)} daily_prices rows.")
    
    # Run the private predict method
    try:
        pred = p._predict_stock(stock_id, symbol)
        if pred:
            logger.info(f"✅ Prediction SUCCESS: {pred}")
        else:
            logger.warning("❌ Prediction returned None.")
            # Check internal thresholds
            if len(rows) < p.indicator_calc.SMA_LONG_PERIOD + 30: # 230
               logger.warning(f"  Insufficient history: {len(rows)} < 230")
               
    except Exception as e:
        logger.error(f"💀 CRASH: {e}", exc_info=True)

if __name__ == "__main__":
    run()
