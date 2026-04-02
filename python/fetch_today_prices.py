#!/usr/bin/env python3
"""Quick script to fetch today's NEPSE prices and store in database."""

import sys
from datetime import datetime
import pandas as pd
from config import db
from nepse_official_client import nepse_client

print("=" * 60)
print("🚀 Direct NEPSE Price Fetcher for Today (2026-04-02)")
print("=" * 60)

try:
    # Initialize NEPSE client
    print("\n📡 Connecting to official NEPSE API...")
    if not nepse_client.is_available():
        print("❌ Cannot connect to NEPSE")
        sys.exit(1)
    
    print("✅ Connected to NEPSE")
    
    # Fetch today's prices
    print("\n📊 Fetching today's stock prices...")
    df = nepse_client.get_today_prices()
    
    if df is None or df.empty:
        print("❌ No prices returned from NEPSE")
        sys.exit(1)
    
    print(f"✅ Fetched {len(df)} stock prices")
    print(f"\nColumns in data: {list(df.columns)}")
    print(f"\nFirst 3 rows:\n{df.head(3)}")
    
    # Check for SHEL
    shel = df[df['symbol'] == 'SHEL']
    if not shel.empty:
        print(f"\n🎯 SHEL found: close={shel.iloc[0].get('close')}, open={shel.iloc[0].get('open')}")
    else:
        print("\n⚠️  SHEL not found in today's data")
    
    # Need to map symbols to stock_ids - fetch stock mapping
    print("\n📚 Fetching stock symbol to ID mapping...")
    stocks = db.select('stocks', 'id,symbol', limit=1000)
    symbol_to_id = {s['symbol']: s['id'] for s in stocks}
    print(f"✅ Loaded {len(symbol_to_id)} stock mappings")
    
    # Store in database with upsert (handle conflicts on stock_id, date)
    print("\n💾 Storing prices in database...")
    today = datetime.now().date().isoformat()  # 2026-04-02
    
    # Prepare data for upsert
    records_to_insert = []
    skipped = 0
    for _, row in df.iterrows():
        symbol = row.get('symbol')
        stock_id = symbol_to_id.get(symbol)
        
        if not stock_id:
            skipped += 1
            continue
        
        rec = {
            'stock_id': stock_id,
            'date': today,
            'open': float(row.get('open')) if pd.notna(row.get('open')) else None,
            'high': float(row.get('high')) if pd.notna(row.get('high')) else None,
            'low': float(row.get('low')) if pd.notna(row.get('low')) else None,
            'close': float(row.get('close')) if pd.notna(row.get('close')) else None,
            'volume': int(row.get('volume')) if pd.notna(row.get('volume')) else 0,
            'turnover': float(row.get('turnover')) if pd.notna(row.get('turnover')) else None,
        }
        records_to_insert.append(rec)
    
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} symbols not found in stock mapping")
    
    # Upsert records
    result = db.upsert('daily_prices', records_to_insert, on_conflict='stock_id,date')
    print(f"✅ Successfully upserted {len(records_to_insert)} prices into database")
    
    # Verify SHEL was stored
    print("\n🔍 Verifying SHEL storage...")
    shel_db = db.select('daily_prices', '*', {'stock_id': 'eq.2934', 'date': f'eq.{today}'}, limit=1)
    if shel_db:
        print(f"✅ SHEL confirmed in DB: close={shel_db[0].get('close')}")
    else:
        print("❌ SHEL not found in database after insert")
    
    print("\n" + "=" * 60)
    print(f"✅ Pipeline complete. {len(records_to_insert)} prices stored for {today}")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
