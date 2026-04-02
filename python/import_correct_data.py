#!/usr/bin/env python3
"""Import correct stock data from today's official NEPSE CSV"""
import csv
from datetime import datetime
from config import db

csv_file = r"c:\Users\amrit\stock-webapp\python\Today's Price - 2026-04-02.csv"

print("=" * 70)
print("📥 Importing NEPSE Official Prices")
print("=" * 70)

try:
    # Get all stocks for ID mapping
    stocks = db.select('stocks', 'id,symbol', limit=500)
    symbol_to_id = {s['symbol']: s['id'] for s in stocks if stocks}
    print(f"✅ Loaded {len(symbol_to_id)} stock symbols")

    # Read CSV
    records_to_upsert = []
    skipped = 0
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                symbol = row.get('Symbol', '').strip()
                date = row.get('Business Date', '').strip()  # Should be 2026-04-02
                
                if not symbol or not date:
                    continue
                
                # Get stock ID
                stock_id = symbol_to_id.get(symbol)
                if not stock_id:
                    print(f"⚠️  Skipped {symbol}: not found in database")
                    skipped += 1
                    continue
                
                # Parse price fields
                try:
                    open_price = float(row.get('Open Price', 0) or 0)
                except:
                    open_price = 0
                    
                try:
                    high_price = float(row.get('High Price', 0) or 0)
                except:
                    high_price = 0
                    
                try:
                    low_price = float(row.get('Low Price', 0) or 0)
                except:
                    low_price = 0
                    
                try:
                    close_price = float(row.get('Close Price', 0) or 0)
                except:
                    close_price = 0
                    
                try:
                    volume = int(row.get('Total Traded Quantity', 0) or 0)
                except:
                    volume = 0
                    
                try:
                    turnover = float(row.get('Total Traded Value', 0) or 0)
                except:
                    turnover = 0
                
                record = {
                    'stock_id': str(stock_id),
                    'date': date,
                    'open': open_price,
                    'high': high_price,
                    'low': low_price,
                    'close': close_price,
                    'volume': volume,
                    'turnover': turnover,
                }
                
                records_to_upsert.append(record)
                
                # Show SHEL specifically
                if symbol == 'SHEL':
                    print(f"\n🎯 SHEL: close={close_price}, open={open_price}, volume={volume}")
                    
            except Exception as e:
                print(f"❌ Error processing {row.get('Symbol')}: {e}")
                skipped += 1
                continue
    
    if not records_to_upsert:
        print("❌ No records to import")
        exit(1)
    
    print(f"\n💾 Upserting {len(records_to_upsert)} stock prices...")
    result = db.upsert('daily_prices', records_to_upsert, on_conflict='stock_id,date')
    print(f"✅ Successfully imported {len(records_to_upsert)} prices")
    
    if skipped > 0:
        print(f"⚠️  Skipped {skipped} records")
    
    # Verify SHEL
    print("\n🔍 Final Verification:")
    shel_data = db.select('daily_prices', '*', {'stock_id': 'eq.2934', 'date': 'eq.2026-04-02'}, limit=1)
    if shel_data:
        p = shel_data[0]
        print(f"✅ SHEL (2026-04-02):")
        print(f"   Close: {p.get('close')} ✓")
        print(f"   Open:  {p.get('open')}")
        print(f"   High:  {p.get('high')}")
        print(f"   Low:   {p.get('low')}")
        print(f"   Volume: {p.get('volume')}")
    else:
        print("❌ SHEL not found after import!")
    
    print("\n" + "=" * 70)
    print("✅ All data imported successfully!")
    print("=" * 70)
    
except Exception as e:
    print(f"\n❌ Import failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
