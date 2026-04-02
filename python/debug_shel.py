#!/usr/bin/env python3
"""Debug SHEL in database"""
from config import db

print("Checking SHEL in database...")

# Get SHEL stock ID
stocks = db.select('stocks', 'id,symbol', {'symbol': 'eq.SHEL'}, limit=1)
if stocks:
    shel_id = stocks[0]['id']
    print(f"✅ SHEL found with ID: {shel_id}")
    
    # Check all SHEL prices
    all_shel = db.select('daily_prices', 'date,close', {'stock_id': f'eq.{shel_id}'}, order='date.desc', limit=5)
    print(f"\n📋 All SHEL prices in DB:")
    for p in all_shel:
        print(f"  {p.get('date')}: close={p.get('close')}")
        
    # Try insert if 2026-04-02 doesn't exist
    latest = db.select('daily_prices', '*', {'stock_id': f'eq.{shel_id}', 'date': 'eq.2026-04-02'})
    if not latest:
        print(f"\n⚠️  SHEL doesn't have data for 2026-04-02, inserting...")
        db.insert('daily_prices', {
            'stock_id': str(shel_id),
            'date': '2026-04-02',
            'open': 329.0,
            'high': 333.0,
            'low': 311.0,
            'close': 315.0,
            'volume': 475191,
            'turnover': 151061691.4
        })
        print("✅ Inserted SHEL for 2026-04-02")
        
        # Verify
        verify = db.select('daily_prices', '*', {'stock_id': f'eq.{shel_id}', 'date': 'eq.2026-04-02'})
        if verify:
            p = verify[0]
            print(f"\n✅ VERIFIED - SHEL for 2026-04-02:")
            print(f"   Close: {p.get('close')}")
else:
    print("❌ SHEL not found in stocks table")
