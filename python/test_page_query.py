#!/usr/bin/env python3
"""Test that page.tsx queries return correct data for today"""

import os
import sys
from datetime import datetime, timezone, timedelta
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import db

# Get today's date in Nepal Standard Time (UTC+5:45)
nepal_offset = timedelta(hours=5, minutes=45)
nepal_now = datetime.now(timezone.utc).astimezone(timezone(nepal_offset))
today_npt = nepal_now.strftime('%Y-%m-%d')

print(f"Today's date (NPT): {today_npt}")
print(f"=" * 60)

# Test 1: Predictions for today (with date filter)
print("\n[TEST 1] Predictions for today (filtered by prediction_date)")
pred_response = db.table("predictions") \
    .select("stock_id, symbol, predicted_close, predicted_change_pct, confidence_score, buy_score") \
    .eq("prediction_date", today_npt) \
    .order("buy_score", desc=True) \
    .limit(5) \
    .execute()

if pred_response.data:
    print(f"✓ Found {len(pred_response.data)} predictions for {today_npt}")
    for p in pred_response.data:
        print(f"  - {p.get('symbol', 'N/A')}: predicted_close={p.get('predicted_close')}, upside={p.get('predicted_change_pct')}%")
else:
    print(f"✗ No predictions found for {today_npt}")
    print(f"  Error: {pred_response}")

# Test 2: Daily prices for today (WITH date filter - NEW FIX)
print("\n[TEST 2] Daily prices for today (filtered by date) - NEW FIX")
prices_response = db.table("daily_prices") \
    .select("date, close, change_pct, volume, stocks(symbol, name)") \
    .eq("date", today_npt) \
    .order("close", desc=True) \
    .limit(10) \
    .execute()

if prices_response.data:
    print(f"✓ Found {len(prices_response.data)} prices for {today_npt}")
    for p in prices_response.data:
        symbol = p.get('stocks', {}).get('symbol', 'N/A')
        close = p.get('close')
        if symbol in ['SHEL', 'KKHC', 'HBL', 'SBI']:
            print(f"  - {symbol}: close={close}")
else:
    print(f"✗ No prices found for {today_npt}")
    print(f"  Response: {prices_response}")

# Test 3: Verify SHEL specifically
print("\n[TEST 3] SHEL Price Verification")
shel_response = db.table("daily_prices") \
    .select("date, close, open, high, low, volume, change_pct") \
    .eq("date", today_npt) \
    .icontains("stocks.symbol", "SHEL") \
    .execute()

if shel_response.data and len(shel_response.data) > 0:
    shel = shel_response.data[0]
    print(f"✓ SHEL data for {today_npt}:")
    print(f"    Close: {shel.get('close')} (Expected: 315.0)")
    print(f"    Open: {shel.get('open')}")
    print(f"    High: {shel.get('high')}")
    print(f"    Low: {shel.get('low')}")
    if shel.get('close') == 315.0:
        print("    ✅ CORRECT!")
    else:
        print(f"    ❌ WRONG! Got {shel.get('close')} instead of 315.0")
else:
    print(f"✗ SHEL not found for {today_npt}")

# Test 4: Check what old prices exist (debugging)
print("\n[TEST 4] Sample of old prices (debugging)")
old_response = db.table("daily_prices") \
    .select("date, close, stocks(symbol)") \
    .neq("date", today_npt) \
    .order("date", desc=True) \
    .limit(5) \
    .execute()

if old_response.data:
    print(f"Sample of non-today prices:")
    for p in old_response.data:
        symbol = p.get('stocks', {}).get('symbol', 'N/A')
        if symbol == 'SHEL':
            print(f"  - {p.get('date')}: {symbol}={p.get('close')}")
else:
    print("  (no old data or error)")

print("\n" + "=" * 60)
print("Test complete!")
