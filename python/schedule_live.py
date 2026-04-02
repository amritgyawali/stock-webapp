"""
NEPSE Live Data Scheduler
Runs the live fetcher automatically every N minutes during NEPSE market hours.

NEPSE trading sessions:
  - Sunday to Thursday
  - Pre-open: 10:30 AM NPT
  - Open:     11:00 AM NPT
  - Close:    03:00 PM NPT

Usage:
    python schedule_live.py              # Runs every 5 minutes during market hours
    python schedule_live.py --once       # Run once immediately and exit
    python schedule_live.py --interval 10  # Run every 10 minutes
"""

import argparse
import time
from datetime import datetime, timezone, timedelta

from config import logger

NPT = timezone(timedelta(hours=5, minutes=45))

# Market hours in NPT
MARKET_OPEN_HOUR = 10       # 10:30 AM
MARKET_OPEN_MIN = 30
MARKET_CLOSE_HOUR = 15      # 3:00 PM
MARKET_CLOSE_MIN = 0
TRADING_DAYS = {6, 0, 1, 2, 3}  # Sun=6, Mon=0, Tue=1, Wed=2, Thu=3


def is_market_open(now: datetime) -> bool:
    """Check if NEPSE market is currently open."""
    if now.weekday() not in TRADING_DAYS:
        return False
    market_open = now.replace(hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MIN, second=0, microsecond=0)
    market_close = now.replace(hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MIN, second=0, microsecond=0)
    return market_open <= now <= market_close


def run_once():
    """Run a single fetch cycle."""
    import nepse_live
    return nepse_live.run()


def run_scheduler(interval_minutes: int = 5):
    """
    Run the fetcher on a loop during market hours.
    Sleeps and waits outside trading hours.
    """
    logger.info(f"📅 NEPSE Scheduler started — interval: {interval_minutes} min")
    logger.info("   Will auto-fetch during Sun–Thu, 10:30 AM – 3:00 PM NPT")

    while True:
        now = datetime.now(NPT)

        if is_market_open(now):
            logger.info(f"⏰ Market is OPEN — running live fetch... [{now.strftime('%H:%M:%S NPT')}]")
            try:
                run_once()
            except Exception as e:
                logger.error(f"Fetch cycle error: {e}")
            logger.info(f"💤 Sleeping {interval_minutes} minutes until next fetch...")
            time.sleep(interval_minutes * 60)
        else:
            # Calculate next market open
            if now.weekday() not in TRADING_DAYS:
                logger.info(f"📴 Market CLOSED (weekend/holiday). Checking again in 1 hour...")
                time.sleep(3600)
            else:
                market_open = now.replace(
                    hour=MARKET_OPEN_HOUR, minute=MARKET_OPEN_MIN, second=0, microsecond=0
                )
                market_close = now.replace(
                    hour=MARKET_CLOSE_HOUR, minute=MARKET_CLOSE_MIN, second=0, microsecond=0
                )
                if now < market_open:
                    wait_sec = (market_open - now).seconds
                    logger.info(f"⏳ Market opens in {wait_sec // 60} min. Waiting...")
                    time.sleep(min(wait_sec, 600))  # Check every 10 min max
                else:
                    # After close — do one final fetch then wait for tomorrow
                    logger.info("🔔 Market just closed — running final fetch of the day...")
                    try:
                        run_once()
                    except Exception as e:
                        logger.error(f"End-of-day fetch error: {e}")
                    logger.info("📴 Market CLOSED for today. Sleeping until tomorrow...")
                    time.sleep(3600)  # Check every hour until next open


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NEPSE Live Data Scheduler")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--interval", type=int, default=5, help="Fetch interval in minutes")
    args = parser.parse_args()

    if args.once:
        print("Running single fetch...")
        run_once()
    else:
        run_scheduler(interval_minutes=args.interval)
