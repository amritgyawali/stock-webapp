#!/usr/bin/env python3
"""Verify that daily_prices query now filters by today's date"""

import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import db

# Get today's date in Nepal Standard Time (UTC+5:45)
nepal_offset = timedelta(hours=5, minutes=45)
nepal_now = datetime.now(timezone.utc).astimezone(timezone(nepal_offset))
today_npt = nepal_now.strftime('%Y-%m-%d')

print(f"Testing page.tsx query fixes")
print(f"Today's date (NPT): {today_npt}")
print("=" * 60)

# Test 1: Get daily prices for TODAY ONLY (with date filter - THIS IS THE FIX)
print("\n[TEST 1] Daily prices for TODAY (WITH date filter - THE FIX)")
filters = {"date": f"eq.{today_npt}"}
today_prices = db.select("daily_prices", 
    columns="date, close, change_pct, volume, stocks(symbol, name)", 
    filters=filters,
    limit=400)

if today_prices:
    print(f"✓ Found {len(today_prices)} prices for {today_npt}")
    # Show top prices
    print("\n  Top prices by close value:")
    sorted_prices = sorted(today_prices, key=lambda x: float(x.get('close', 0)), reverse=True)[:10]
    for p in sorted_prices:
        symbol = p.get('stocks', {}).get('symbol', 'N/A') if isinstance(p.get('stocks'), dict) else 'N/A'
        print(f"    {symbol}: {p.get('close')}")
    
    # Check SHEL specifically
    print("\n  ✓ Checking SHEL specifically...")
    shel_found = False
    for p in today_prices:
        symbol = p.get('stocks', {}).get('symbol', 'N/A') if isinstance(p.get('stocks'), dict) else 'N/A'
        if symbol == "SHEL":
            shel_found = True
            close = float(p.get('close', 0))
            print(f"    SHEL close: {close}")
            if close == 315.0:
                print(f"    ✅ CORRECT! SHEL is 315.0")
            else:
                print(f"    ❌ WRONG! SHEL is {close}, expected 315.0")
            break
    
    if not shel_found:
        print("    ❌ SHEL not found in today's data!")
else:
    print(f"✗ ERROR: No prices found for {today_npt}")

# Test 2: For comparison, check OLD prices without the date filter
print("\n[TEST 2] Old prices WITHOUT date filter (for comparison)")
old_prices = db.select("daily_prices",
    columns="date, close, stocks(symbol)",
    limit=10,
    order="date.desc")

if old_prices:
    print(f"  Sample of prices by date (most recent first):")
    seen_dates = set()
    for p in old_prices[:10]:
        date = p.get('date')
        symbol = p.get('stocks', {}).get('symbol', 'N/A') if isinstance(p.get('stocks'), dict) else 'N/A'
        if symbol == "SHEL":
            if date not in seen_dates:
                print(f"    {date}: SHEL={p.get('close')}")
                seen_dates.add(date)

print("\n" + "=" * 60)
print("Verification complete!")
print("\nExpected behavior:")
print("- TEST 1 should show SHEL = 315.0 for 2026-04-02")
print("- If SHEL is 315.0, the page.tsx fix is working! ✅")
print("- If TEST 1 shows no data, there might be a data issue")
