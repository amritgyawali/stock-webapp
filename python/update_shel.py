#!/usr/bin/env python3
from config import db
from datetime import datetime

today = '2026-04-02'

# Get SHEL stock ID
stocks = db.select('stocks', 'id', {'symbol': 'eq.SHEL'}, limit=1)
if not stocks:
    print("❌ SHEL not found")
    exit(1)

shel_id = stocks[0]['id']
print(f"🔄 Updating SHEL (ID: {shel_id}) price to 340.1 for {today}")

# Update SHEL price
result = db.update('daily_prices', 
                   {'close': 340.1},
                   {'stock_id': f'eq.{shel_id}', 'date': f'eq.{today}'})

print(f"✅ SHEL updated to 340.1")

# Verify
verify = db.select('daily_prices', '*', {'stock_id': f'eq.{shel_id}', 'date': f'eq.{today}'}, limit=1)
if verify:
    print(f"\n✅ Verified: SHEL close price = {verify[0]['close']}")
else:
    print("❌ Verification failed")
