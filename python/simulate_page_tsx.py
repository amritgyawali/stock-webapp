#!/usr/bin/env python3
"""
Simulate exactly what page.tsx getDashboardData() does to verify the fix
"""

import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import db

# Compute today's date in Nepal Standard Time (UTC+5:45) exactly as page.tsx does
nepal_offset = timedelta(hours=5, minutes=45)
nepal_now = datetime.now(timezone.utc).astimezone(timezone(nepal_offset))
todayNPT = nepal_now.strftime('%Y-%m-%d')

print("SIMULATING page.tsx getDashboardData() FLOW")
print(f"Today's date (NPT): {todayNPT}")
print("=" * 70)

# =====================================================================
# STEP 1: TOP PICKS (predictions for today)
# =====================================================================
print("\n[STEP 1] Top 5 Predictions for today")
print("-" * 70)

top_picks_filters = {"prediction_date": f"eq.{todayNPT}"}
top_picks = db.select(
    "predictions",
    "*",
    filters=top_picks_filters,
    order="buy_score.desc",
    limit=5
)

if top_picks:
    print(f"✓ Found {len(top_picks)} top predictions")
    for i, p in enumerate(top_picks[:2], 1):
        symbol = p.get('symbol', 'N/A')
        score = p.get('buy_score', 0)
        pred_close = p.get('predicted_close', 0)
        upside = p.get('predicted_change_pct', 0)
        print(f"  #{i} {symbol}: buy_score={score:.2f}, predicted_close={pred_close}, upside={upside}%")
else:
    print("✗ No predictions found for today")

# =====================================================================
# STEP 2: RAW PRICES FOR TODAY (the key fix)
# =====================================================================
print("\n[STEP 2] Daily Prices for today (THE FIX)")
print("-" * 70)

# This is the FIXED query - NOW WITH DATE FILTER
prices_filters = {"date": f"eq.{todayNPT}"}
raw_prices = db.select(
    "daily_prices",
    "*",
    filters=prices_filters,
    order="close.desc",
    limit=400
)

if raw_prices:
    print(f"✓ Found {len(raw_prices)} prices for {todayNPT}")
    print("\n  Creating price lookup map...")
    
    # This is what page.tsx does - create a priceMap
    price_map = {}
    for p in raw_prices:
        symbol = p.get('stocks', {}).get('symbol', 'N/A') if isinstance(p.get('stocks'), dict) else 'N/A'
        if symbol:
            price_map[symbol] = p
    
    print(f"  ✓ Price map created with {len(price_map)} symbols")
    
    # Look up specific stocks
    print("\n  Checking key stocks:")
    for symbol in ['SHEL', 'KKHC', 'HBL', 'SBI']:
        if symbol in price_map:
            price_data = price_map[symbol]
            close = price_data.get('close')
            print(f"    {symbol}: close={close}")
            
            # Compare with expected
            if symbol == 'SHEL':
                if close == 315.0:
                    print(f"           ✅ CORRECT (expected 315.0)")
                else:
                    print(f"           ❌ WRONG (expected 315.0, got {close})")
        else:
            print(f"    {symbol}: NOT FOUND in price_map")

else:
    print(f"✗ ERROR: No prices found for {todayNPT}")
    print("  This is a critical issue - no daily data for today!")

# =====================================================================
# STEP 3: MARKET SUMMARY
# =====================================================================
print("\n[STEP 3] Market Summary (latest)")
print("-" * 70)

market_summary = db.select(
    "market_summary",
    "*",
    order="date.desc",
    limit=1
)

if market_summary:
    m = market_summary[0]
    print(f"✓ Market summary for {m.get('date')}")
    print(f"  NEPSE Index: {m.get('nepse_index')}")
    print(f"  Change: {m.get('nepse_change')} ({m.get('nepse_change_pct')}%)")
    print(f"  Total Turnover: {m.get('total_turnover')}")
else:
    print("✗ No market summary found")

# =====================================================================
# FINAL VALIDATION
# =====================================================================
print("\n" + "=" * 70)
print("VALIDATION SUMMARY")
print("=" * 70)

all_good = True

if not top_picks:
    print("❌ No predictions found")
    all_good = False
else:
    print("✅ Predictions loaded")

if not raw_prices:
    print("❌ No prices found for today")
    all_good = False
else:
    print(f"✅ Daily prices loaded ({len(raw_prices)} records for {todayNPT})")
    
    if 'SHEL' in price_map and price_map['SHEL'].get('close') == 315.0:
        print("✅ SHEL verified as 315.0")
    else:
        print("❌ SHEL not 315.0 or not found")
        all_good = False

if not market_summary:
    print("❌ Market summary not found")
    all_good = False
else:
    print("✅ Market summary loaded")

print("\n" + "=" * 70)
if all_good:
    print("✅ ALL CHECKS PASSED - page.tsx should display correct data!")
else:
    print("❌ Some checks failed - verify database state")
