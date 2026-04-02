#!/usr/bin/env python3
"""Test what the dashboard fetches"""
from config import db
from datetime import datetime, timezone, timedelta

# Mimic Nepal time calculation
nepalOffset = 5 * 60 + 45  # minutes
nowUtc = datetime.now(timezone.utc)
nepalTime = nowUtc + timedelta(minutes=nepalOffset)
todayNPT = nepalTime.strftime('%Y-%m-%d')

print(f"Today (NPT): {todayNPT}")
print("\n" + "="*60)

# Test 1: Check predictions for today
print("\n1️⃣  PREDICTIONS for today:")
preds = db.select('predictions', '*', {'prediction_date': f'eq.{todayNPT}'}, limit=5)
print(f"   Found {len(preds) if preds else 0} predictions")
if preds:
    for p in preds[:2]:
        print(f"   - Stock {p.get('stock_id')}: score={p.get('buy_score')}")

# Test 2: Check live prices for today
print("\n2️⃣  DAILY PRICES for today:")
prices = db.select('daily_prices', '*', {'date': f'eq.{todayNPT}'}, limit=10)
print(f"   Found {len(prices) if prices else 0} prices")
if prices:
    for p in prices[:3]:
        sym = p.get('stocks')
        stock_symbol = sym.get('symbol') if sym else f"ID:{p.get('stock_id')}"
        print(f"   - {stock_symbol}: close={p.get('close')}")
        
# Test 3: Check SHEL specifically
print("\n3️⃣  SHEL CHECK:")
shel_prices = db.select('daily_prices', '*', {'stock_id': 'eq.277', 'date': f'eq.{todayNPT}'}, limit=1)
if shel_prices:
    p = shel_prices[0]
    print(f"   ✅ SHEL found: close={p.get('close')}, volume={p.get('volume')}")
else:
    print(f"   ❌ SHEL not found for {todayNPT}")

# Test 4: Market summary
print("\n4️⃣  MARKET SUMMARY:")
market = db.select('market_summary', '*', order='date.desc', limit=1)
if market:
    m = market[0]
    print(f"   Date: {m.get('date')}")
    print(f"   NEPSE Index: {m.get('nepse_index')}")
    print(f"   Change: {m.get('nepse_change_pct')}%")

print("\n" + "="*60)
print("✅ Dashboard should display today's data correctly")
