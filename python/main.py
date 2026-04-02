"""
NEPSE Stock Analysis — Main Orchestrator
Entry point for the daily automation pipeline.
"""

import sys
import time
import argparse
from datetime import datetime

from config import logger, db, is_trading_day, get_nepal_time, get_nepal_date_str
from scraper import NepseScraper
from indicators import TechnicalIndicators
from predictor import StockPredictor


def run_pipeline(force: bool = False, dry_run: bool = False):
    """Execute the complete daily pipeline."""
    start_time = time.time()
    nepal_now = get_nepal_time()

    logger.info("=" * 60)
    logger.info(f"🚀 NEPSE Stock Analyzer — Daily Pipeline")
    logger.info(f"📅 Nepal Time: {nepal_now.strftime('%Y-%m-%d %H:%M:%S NPT')}")
    logger.info(f"📅 Today: {get_nepal_date_str()}")
    logger.info(f"🔧 Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    logger.info("=" * 60)

    # Check trading day
    if not force and not is_trading_day():
        logger.info("📅 Today is not a NEPSE trading day (Friday/Saturday). Exiting.")
        return

    # Dry run mode
    if dry_run:
        logger.info("🧪 DRY RUN — testing connectivity only")
        _test_supabase()
        _test_nepse_api()
        return

    # Initialize
    scraper = NepseScraper()
    indicators = TechnicalIndicators()
    predictor = StockPredictor()
    results = {}

    # Step 1: Sync company list
    logger.info("\n📋 STEP 1/5: Syncing company list...")
    try:
        results["companies"] = scraper.sync_company_list()
    except Exception as e:
        logger.error(f"Company sync failed: {e}")
        results["companies"] = 0

    # Step 2 & 3: Multi-Source Fetch & Consensus Storage
    logger.info("\n📊 STEP 2/5: Cross-Validating Multi-Source Prices...")
    try:
        from verify_data import verify_and_sync
        verify_and_sync()
        results["fetched"] = 1
        results["stored"] = 1
    except Exception as e:
        logger.error(f"Multi-source fetch failed: {e}")
        results["fetched"] = 0
        results["stored"] = 0

    try:
        logger.info("\n📊 STEP 3/5: Fetching Market Summary...")
        results["summary"] = scraper.fetch_and_store_market_summary()
    except Exception as e:
        logger.error(f"Market summary failed: {e}")

    # Step 4: Calculate indicators
    logger.info("\n🧮 STEP 4/5: Calculating technical indicators...")
    try:
        results["indicators"] = indicators.calculate_all_indicators()
    except Exception as e:
        logger.error(f"Indicator calculation failed: {e}")
        results["indicators"] = 0

    # Step 5: ML predictions
    logger.info("\n🤖 STEP 5/5: Running ML predictions...")
    try:
        results["predictions"] = predictor.run_predictions()
    except Exception as e:
        logger.error(f"ML predictions failed: {e}")
        results["predictions"] = 0

    # Bonus: Update accuracy
    logger.info("\n📏 BONUS: Updating accuracy...")
    try:
        predictor.update_accuracy()
    except Exception as e:
        logger.error(f"Accuracy update failed: {e}")

    # Summary
    elapsed = round(time.time() - start_time, 2)
    logger.info("\n" + "=" * 60)
    logger.info("📊 PIPELINE COMPLETE:")
    logger.info(f"  Companies synced:   {results.get('companies', 0)}")
    logger.info(f"  Prices fetched:     {results.get('fetched', 0)}")
    logger.info(f"  Prices stored:      {results.get('stored', 0)}")
    logger.info(f"  Indicators updated: {results.get('indicators', 0)}")
    logger.info(f"  Predictions made:   {results.get('predictions', 0)}")
    logger.info(f"  Time elapsed:       {elapsed}s")
    logger.info("=" * 60)


def _test_supabase():
    """Test Supabase connectivity."""
    logger.info("\n🔌 Testing Supabase connection...")
    try:
        connected = db.health_check()
        if connected:
            logger.info("  ✅ Supabase is reachable!")
        else:
            logger.error("  ❌ Supabase not reachable. Check your URL and key.")
    except Exception as e:
        logger.error(f"  ❌ Supabase error: {e}")


def _test_nepse_api():
    """Test NEPSE API connectivity."""
    import requests
    from config import NEPSE_ENDPOINTS, REQUEST_TIMEOUT, REQUEST_HEADERS

    logger.info("\n🔌 Testing NEPSE API...")
    session = requests.Session()
    session.headers.update(REQUEST_HEADERS)

    for name in ["summary", "price_volume", "company_list", "nepse_index"]:
        url = NEPSE_ENDPOINTS.get(name)
        if not url:
            continue
        try:
            resp = session.get(url, timeout=REQUEST_TIMEOUT)
            data = resp.json()
            if isinstance(data, list):
                count = len(data)
                sample = data[0] if data else {}
            elif isinstance(data, dict):
                count = len(data.keys())
                sample = dict(list(data.items())[:3])
            else:
                count = 0
                sample = str(data)[:100]
            logger.info(f"  ✅ {name}: HTTP {resp.status_code}, {count} items")
            logger.info(f"     Sample: {sample}")
        except Exception as e:
            logger.error(f"  ❌ {name}: {e}")

    logger.info("\n🧪 Dry run complete. No data written.")


def main():
    parser = argparse.ArgumentParser(description="NEPSE Stock Analyzer")
    parser.add_argument("--force", action="store_true", help="Run on non-trading days")
    parser.add_argument("--dry-run", action="store_true", help="Test APIs only")
    args = parser.parse_args()

    try:
        run_pipeline(force=args.force, dry_run=args.dry_run)
    except Exception as e:
        logger.critical(f"💀 Pipeline crashed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
