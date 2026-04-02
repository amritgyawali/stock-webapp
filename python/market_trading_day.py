#!/usr/bin/env python3
"""
Market Trading Day Calculator
Handles Nepal stock market opening hours (11:00 AM - 3:00 PM)
Correctly determines the "trading day" based on current time

Important:
- Market opens: 11:00 AM Nepal Time
- Market closes: 3:00 PM Nepal Time
- Trading days: Sunday - Thursday

Logic:
- If current time < 11:00 AM → Latest market data is from YESTERDAY
- If current time >= 11:00 AM → Latest market data is from TODAY
"""

from datetime import datetime, timezone, timedelta
import logging

logger = logging.getLogger("market-trading-day")

# Market hours (Nepal timezone)
MARKET_OPEN_HOUR = 11  # 11:00 AM
MARKET_CLOSE_HOUR = 15  # 3:00 PM (15:00)
MARKET_OPEN_DAYS = [6, 0, 1, 2, 3]  # Sunday=6, Monday=0, ..., Thursday=3


def get_nepal_time() -> datetime:
    """Get current time in Nepal Standard Time (UTC+5:45)"""
    nepal_offset = timedelta(hours=5, minutes=45)
    utc_now = datetime.now(timezone.utc)
    nepal_tz = timezone(nepal_offset)
    return utc_now.astimezone(nepal_tz)


def is_market_trading_day(check_date: datetime = None) -> bool:
    """
    Check if given date is a market trading day (Sun-Thu)
    
    Args:
        check_date: datetime object (defaults to Nepal time now)
    
    Returns:
        bool: True if market trades on this day
    """
    if check_date is None:
        check_date = get_nepal_time()
    
    # Python weekday: Monday=0, Sunday=6
    weekday = check_date.weekday()
    
    # Market trades: Sunday(6), Mon(0), Tue(1), Wed(2), Thu(3)
    return weekday in MARKET_OPEN_DAYS


def is_market_open_now(check_time: datetime = None) -> bool:
    """
    Check if market is currently open (within 11 AM - 3 PM)
    
    Args:
        check_time: datetime object (defaults to Nepal time now)
    
    Returns:
        bool: True if between 11 AM and 3 PM
    """
    if check_time is None:
        check_time = get_nepal_time()
    
    if not is_market_trading_day(check_time):
        return False
    
    hour = check_time.hour
    return MARKET_OPEN_HOUR <= hour < MARKET_CLOSE_HOUR


def get_latest_trading_date(reference_time: datetime = None) -> str:
    """
    Get the date of the latest available market data
    
    CRITICAL LOGIC:
    - If current time < 11:00 AM → Today's market hasn't opened
                                  → Latest data is from YESTERDAY (if it was trading day)
    - If current time >= 11:00 AM → Today's market is open or closed
                                   → Latest data is from TODAY
    
    Args:
        reference_time: datetime to base calculation on (defaults to Nepal time now)
    
    Returns:
        str: Date in format "YYYY-MM-DD" of the latest trading day
    
    Examples:
        10:30 AM Thursday → "2026-04-01" (Yesterday's data)
        11:30 AM Thursday → "2026-04-02" (Today's data)
        4:30 PM Thursday → "2026-04-02" (Today's market closed, still today's data)
        11:30 AM Friday → "2026-04-02" (Friday no market, data from last Thursday)
    """
    
    if reference_time is None:
        reference_time = get_nepal_time()
    
    current_hour = reference_time.hour
    
    # MAIN LOGIC: Before 11 AM = use yesterday's data
    if current_hour < MARKET_OPEN_HOUR:
        # Haven't reached market opening yet today
        # Latest data is from yesterday
        check_date = reference_time - timedelta(days=1)
        logger.info(f"Before market open (11 AM). Using yesterday's data: {check_date.strftime('%Y-%m-%d')}")
    else:
        # Market is open or has closed already today
        # Latest data is from today
        check_date = reference_time
        logger.info(f"After market open (11 AM). Using today's data: {check_date.strftime('%Y-%m-%d')}")
    
    # Find the most recent trading day (skip weekends/Friday)
    while not is_market_trading_day(check_date):
        logger.debug(f"  {check_date.strftime('%A, %Y-%m-%d')} - Not a trading day, going back")
        check_date = check_date - timedelta(days=1)
    
    trading_date = check_date.strftime('%Y-%m-%d')
    weekday_name = check_date.strftime('%A')
    logger.info(f"Latest trading date: {trading_date} ({weekday_name})")
    
    return trading_date


def get_market_status() -> dict:
    """
    Get comprehensive market status information
    
    Returns:
        dict with status details
    """
    nepal_now = get_nepal_time()
    hour = nepal_now.hour
    minute = nepal_now.minute
    weekday = nepal_now.strftime('%A')
    
    latest_trading_date = get_latest_trading_date(nepal_now)
    is_open = is_market_open_now(nepal_now)
    
    # Determine status message
    if not is_market_trading_day(nepal_now):
        status = f"Market CLOSED - {weekday} is not a trading day"
        latest_data_from = "Previous trading day"
    elif hour < MARKET_OPEN_HOUR:
        status = f"Market CLOSED - Opens at 11:00 AM (in {MARKET_OPEN_HOUR - hour}h {60 - minute}m)"
        latest_data_from = "Previous trading day"
    elif hour >= MARKET_CLOSE_HOUR:
        status = f"Market CLOSED - Closed at 3:00 PM"
        latest_data_from = "Today's data"
    else:
        status = f"Market OPEN - Closes at 3:00 PM (in {MARKET_CLOSE_HOUR - hour}h {60 - minute}m)"
        latest_data_from = "Live for today"
    
    return {
        "current_time": nepal_now.strftime('%Y-%m-%d %H:%M:%S'),
        "timezone": "Nepal (UTC+5:45)",
        "is_trading_day": is_market_trading_day(nepal_now),
        "is_market_open": is_open,
        "status": status,
        "latest_trading_date": latest_trading_date,
        "latest_data_from": latest_data_from,
        "weekday": weekday,
        "market_open_hour": MARKET_OPEN_HOUR,
        "market_close_hour": MARKET_CLOSE_HOUR,
    }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 70)
    print("MARKET TRADING DAY CALCULATOR")
    print("=" * 70)
    
    status = get_market_status()
    
    print(f"\nCurrent Time: {status['current_time']} ({status['timezone']})")
    print(f"Day: {status['weekday']}")
    print(f"\nMarket Status: {status['status']}")
    print(f"Trading Day: {'Yes' if status['is_trading_day'] else 'No'}")
    print(f"Market Open: {'Yes' if status['is_market_open'] else 'No'}")
    print(f"\nLatest Trading Date: {status['latest_trading_date']}")
    print(f"Data Available From: {status['latest_data_from']}")
    
    print("\n" + "=" * 70)
    print("EXAMPLES (for reference)")
    print("=" * 70)
    
    examples = [
        ("10:30 AM Thursday", datetime(2026, 4, 2, 10, 30, tzinfo=timezone(timedelta(hours=5, minutes=45)))),
        ("11:30 AM Thursday", datetime(2026, 4, 2, 11, 30, tzinfo=timezone(timedelta(hours=5, minutes=45)))),
        ("2:00 PM Thursday", datetime(2026, 4, 2, 14, 0, tzinfo=timezone(timedelta(hours=5, minutes=45)))),
        ("11:00 AM Friday (no market)", datetime(2026, 4, 3, 11, 0, tzinfo=timezone(timedelta(hours=5, minutes=45)))),
    ]
    
    for description, example_time in examples:
        date = get_latest_trading_date(example_time)
        print(f"{description:30} → Trading date: {date}")
