#!/usr/bin/env python3
"""
Integration Guide: Market Trading Day Logic

Shows how to integrate market_trading_day.py into existing code
"""

# ==============================================================================
# 1. PYTHON INTEGRATION (main.py, predictor.py, scraper.py)
# ==============================================================================

PYTHON_INTEGRATION_EXAMPLE = """
# At the top of main.py / predictor.py / scraper.py
from market_trading_day import get_latest_trading_date, get_market_status

def main():
    # BEFORE (incorrect): Uses calendar date
    # from datetime import datetime, timezone, timedelta
    # nepal_offset = timedelta(hours=5, minutes=45)
    # nepal_now = datetime.now(timezone.utc).astimezone(timezone(nepal_offset))
    # today_npt = nepal_now.strftime('%Y-%m-%d')
    
    # AFTER (correct): Uses market trading date
    latest_trading_date = get_latest_trading_date()
    print(f"Fetching data for: {latest_trading_date}")
    
    # Get full market status if needed
    status = get_market_status()
    print(f"Market Status: {status['status']}")
    print(f"Data availability: {status['latest_data_from']}")
    
    # Continue with your pipeline
    prices = scrape_prices(date=latest_trading_date)
    predictions = predict_prices(date=latest_trading_date)
    upload_to_db(prices, predictions, date=latest_trading_date)
"""

# ==============================================================================
# 2. NEXT.JS INTEGRATION (page.tsx)
# ==============================================================================

NEXTJS_INTEGRATION_EXAMPLE = """
// In web/app/page.tsx getDashboardData()

// BEFORE (incorrect logic)
// const nepalOffset = 5 * 60 + 45;
// const nowUtc = new Date();
// const nepalTime = new Date(nowUtc.getTime() + nepalOffset * 60 * 1000);
// const todayNPT = nepalTime.toISOString().slice(0, 10);

// AFTER (correct logic - call Python API or use library)
// Option 1: Call existing Python API endpoint (recommended)
async function getLatestTradingDate() {
  const response = await fetch('/api/market-trading-date');
  const data = await response.json();
  return data.latest_trading_date;  // "2026-04-01" (if before 11 AM)
}

// Option 2: Use date-fns with market hours logic (if no API)
function getLatestTradingDate() {
  const nepal = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Kathmandu',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit'
  }).formatToParts(new Date());
  
  const hour = parseInt(nepal.find(p => p.type === 'hour').value);
  let date = new Date();
  
  if (hour < 11) {
    // Before market opens, use yesterday's date
    date = new Date(date.getTime() - 24 * 60 * 60 * 1000);
  }
  
  return date.toISOString().slice(0, 10);
}

// Then use it in getDashboardData()
async function getDashboardData() {
  const latestTradingDate = await getLatestTradingDate();
  
  const [{ data: topPicks }, { data: predictions }] = await Promise.all([
    supabase.from("predictions")
      .select("*, stocks(*)")
      .eq("prediction_date", latestTradingDate)  // Use trading date, not calendar date
      .order("buy_score", { ascending: false })
      .limit(5),
    supabase.from("daily_prices")
      .select("*")
      .eq("date", latestTradingDate)  // Use trading date, not calendar date
      .limit(400)
  ]);
  
  return { topPicks, predictions };
}
"""

# ==============================================================================
# 3. API ENDPOINT (recommended for Next.js)
# ==============================================================================

NEXTJS_API_ENDPOINT = """
// pages/api/market-trading-date.ts (or app/api/market-trading-date/route.ts)

import { get_latest_trading_date } from '@/python/market_trading_day';

export async function GET(request: Request) {
  const latest_trading_date = get_latest_trading_date();
  
  return Response.json({
    latest_trading_date,
    hint: "Use this date for all database queries (not calendar date)"
  });
}

// Usage in components:
// const res = await fetch('/api/market-trading-date');
// const { latest_trading_date } = await res.json();
"""

# ==============================================================================
# 4. SCRAPER UPDATES (scraper.py)
# ==============================================================================

SCRAPER_INTEGRATION = """
# In scraper.py

from market_trading_day import get_latest_trading_date, get_market_status

def get_live_prices():
    '''
    Fetch live stock prices for the latest trading day
    
    IMPORTANT: This should run AFTER market closes or during market hours
    For data from before 11 AM, will automatically use previous day's data
    '''
    
    latest_trading_date = get_latest_trading_date()
    status = get_market_status()
    
    logger.info(f"Scraping prices for: {latest_trading_date}")
    logger.info(f"Market status: {status['status']}")
    
    # Scraper continues as normal
    prices = fetch_from_nepse_api(date=latest_trading_date)
    
    # Add date info
    for price in prices:
        price['date'] = latest_trading_date
    
    return prices, status
"""

# ==============================================================================
# 5. ML PREDICTOR UPDATES (predictor.py)
# ==============================================================================

PREDICTOR_INTEGRATION = """
# In predictor.py

from market_trading_day import get_latest_trading_date, get_market_status

def generate_predictions():
    '''
    Generate predictions for the latest trading day
    '''
    
    latest_trading_date = get_latest_trading_date()
    
    logger.info(f"Generating predictions for: {latest_trading_date}")
    
    # Fetch historical data
    historical_data = db.select('daily_prices', '*', 
        filters={'date': f'lt.{latest_trading_date}'},  # Before prediction date
        limit=30)
    
    # Generate features
    features = extract_features(historical_data)
    
    # Predict
    predictions = model.predict(features)
    
    # Store with correct date
    for i, pred in enumerate(predictions):
        pred['prediction_date'] = latest_trading_date
    
    db.upsert('predictions', predictions, on_conflict='stock_id,prediction_date')
"""

# ==============================================================================
# 6. USAGE EXAMPLES
# ==============================================================================

USAGE_EXAMPLES = """
SCENARIO 1: Check current market status
============================================
Current time: 10:30 AM Thursday, April 2, 2026

from market_trading_day import get_market_status
status = get_market_status()

Result:
{
  'current_time': '2026-04-02 10:30:00',
  'is_market_open': False,
  'status': 'Market CLOSED - Opens at 11:00 AM',
  'latest_trading_date': '2026-04-01',
  'latest_data_from': 'Previous trading day'
}

→ Should fetch data for 2026-04-01 (yesterday)


SCENARIO 2: After market opens
============================================
Current time: 12:00 PM Thursday, April 2, 2026

from market_trading_day import get_latest_trading_date
date = get_latest_trading_date()

Result: '2026-04-02'

→ Should fetch data for 2026-04-02 (today)


SCENARIO 3: Market closed day (Friday)
============================================
Current time: 11:00 AM Friday, April 3, 2026

from market_trading_day import get_latest_trading_date
date = get_latest_trading_date()

Result: '2026-04-02'

→ Should fetch data for 2026-04-02 (last trading day = Thursday)


SCENARIO 4: Check if market is trading today
============================================
from market_trading_day import is_market_trading_day
from datetime import datetime, timezone, timedelta

friday = datetime(2026, 4, 3, 12, 0, tzinfo=timezone(timedelta(hours=5, minutes=45)))
result = is_market_trading_day(friday)

Result: False

→ Friday: No trading (only Sun-Thu)
"""

# ==============================================================================
# 7. TESTING
# ==============================================================================

TEST_EXAMPLE = """
# Test the market trading day calculator

import pytest
from market_trading_day import get_latest_trading_date, is_market_trading_day
from datetime import datetime, timezone, timedelta

def test_before_11_am():
    '''Before 11 AM Thursday → should use yesterday's date'''
    reference = datetime(2026, 4, 2, 10, 30, tzinfo=timezone(timedelta(hours=5, minutes=45)))
    assert get_latest_trading_date(reference) == '2026-04-01'

def test_after_11_am():
    '''After 11 AM Thursday → should use today's date'''
    reference = datetime(2026, 4, 2, 11, 30, tzinfo=timezone(timedelta(hours=5, minutes=45)))
    assert get_latest_trading_date(reference) == '2026-04-02'

def test_friday_no_market():
    '''Friday (no market) at 11 AM → should use last Thursday'''
    reference = datetime(2026, 4, 3, 11, 30, tzinfo=timezone(timedelta(hours=5, minutes=45)))
    assert get_latest_trading_date(reference) == '2026-04-02'

def test_trading_days():
    '''Check correct trading days'''
    assert is_market_trading_day(datetime(2026, 4, 2, 12, 0, tzinfo=timezone(timedelta(hours=5, minutes=45))))  # Thu ✓
    assert not is_market_trading_day(datetime(2026, 4, 3, 12, 0, tzinfo=timezone(timedelta(hours=5, minutes=45))))  # Fri ✗
    assert not is_market_trading_day(datetime(2026, 4, 4, 12, 0, tzinfo=timezone(timedelta(hours=5, minutes=45))))  # Sat ✗
"""

if __name__ == "__main__":
    print("INTEGRATION GUIDE: Market Trading Day Logic")
    print("=" * 70)
    print()
    print("1. PYTHON INTEGRATION")
    print("-" * 70)
    print(PYTHON_INTEGRATION_EXAMPLE)
    print()
    print("2. NEXT.JS INTEGRATION (page.tsx)")
    print("-" * 70)
    print(NEXTJS_INTEGRATION_EXAMPLE)
    print()
    print("3. USAGE EXAMPLES")
    print("-" * 70)
    print(USAGE_EXAMPLES)
    print()
    print("4. TESTING")
    print("-" * 70)
    print(TEST_EXAMPLE)
