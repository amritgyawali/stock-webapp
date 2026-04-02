#!/usr/bin/env python3
from config import db

# Get SHEL stock ID first
stocks = db.select('stocks', 'id,symbol', {'symbol': 'eq.SHEL'}, limit=1)
if stocks:
    shel_id = stocks[0]['id']
    print(f"✅ SHEL ID: {shel_id}")
    
    # Check today's SHEL price
    shel_price = db.select('daily_prices', '*', {'stock_id': f'eq.{shel_id}', 'date': 'eq.2026-04-02'}, limit=1)
    if shel_price:
        p = shel_price[0]
        print(f"\n🎯 SHEL TODAY (2026-04-02):")
        print(f"   Close: {p.get('close')}")
        print(f"   Open:  {p.get('open')}")
        print(f"   High:  {p.get('high')}")
        print(f"   Low:   {p.get('low')}")
        print(f"   Volume: {p.get('volume')}")
        print(f"   Turnover: {p.get('turnover')}")
    else:
        print(f"❌ No price data for SHEL on 2026-04-02")
        
        # Check what date SHEL has most recent
        all_shel = db.select('daily_prices', '*', {'stock_id': f'eq.{shel_id}'}, order='date.desc', limit=3)
        if all_shel:
            print(f"\n📅 Most recent SHEL prices:")
            for p in all_shel:
                print(f"   {p.get('date')}: close={p.get('close')}")
else:
    print("❌ SHEL not found in stocks table")

# Show date range in database
print("\n📊 Date range in database:")
dates = db.select('daily_prices', 'date', order='date.desc', limit=1)
if dates:
    print(f"   Latest: {dates[0]['date']}")
dates_old = db.select('daily_prices', 'date', order='date.asc', limit=1)
if dates_old:
    print(f"   Oldest: {dates_old[0]['date']}")
