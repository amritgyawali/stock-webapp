import logging
import sys
import os
from predictor import StockPredictor

# Ensure logging is pointing to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout
)

logger = logging.getLogger("predictor-runner")

def main():
    logger.info("🚀 Manually launching StockPredictor...")
    try:
        predictor = StockPredictor()
        num_stored = predictor.run_predictions()
        logger.info(f"✅ Predictor finished. Stored {num_stored} predictions.")
    except Exception as e:
        logger.error(f"❌ Predictor failed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
