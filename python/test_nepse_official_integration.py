import sys
import os
import logging

# Add temp_nepse to path so 'import nepse' works
sys.path.append(os.path.join(os.path.dirname(__file__), "temp_nepse"))

from nepse_official_client import NepseOfficialClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("test-integration")

def test_integration():
    logger.info("🧪 Starting Integration Test for NepseUnofficialApi via Node.js Bridge...")
    
    client = NepseOfficialClient()
    
    if not client.is_available():
        logger.error("❌ NepseOfficialClient is not available. Check dependencies and bridge.")
        return

    logger.info("📡 Fetching Market Summary...")
    try:
        summary = client.get_market_summary()
        if summary:
            logger.info(f"✅ Market Summary: {summary}")
        else:
            logger.warning("⚠️ Received empty market summary.")
            
        logger.info("📡 Fetching Today's Prices...")
        prices = client.get_today_prices()
        if prices is not None and not prices.empty:
            logger.info(f"✅ Successfully fetched {len(prices)} price rows.")
            logger.info(f"Snapshot:\n{prices.head()}")
        else:
            logger.warning("⚠️ No price data received. Market might be closed or API failing.")
            
    except Exception as e:
        logger.error(f"❌ Integration test failed with ERROR: {e}")

if __name__ == "__main__":
    test_integration()
