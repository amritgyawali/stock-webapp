"""
Import official NEPSE CSV data into Supabase
Fixes pricing discrepancies with official NEPSE daily prices
"""

import csv
import sys
from datetime import datetime
from config import db, logger

def import_csv_prices(csv_path):
    """Import prices from official NEPSE CSV export."""
    logger.info(f"📥 Importing prices from: {csv_path}")
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            rows = list(csv_reader)
            
        logger.info(f"📊 Found {len(rows)} stocks in CSV")
        
        # First, ensure all stocks exist
        existing_stocks = db.select("stocks", "id,symbol")
        existing_symbols = {s['symbol']: s['id'] for s in existing_stocks}
        
        # Collect all price data first
        price_data_list = []
        errors = []
        
        for row in rows:
            try:
                symbol = row['Symbol'].strip()
                business_date = row['Business Date'].strip()
                
                # Skip rows with malformed prices
                try:
                    close_price = float(row['Close Price'])
                    open_price = float(row['Open Price'])
                    high_price = float(row['High Price'])
                    low_price = float(row['Low Price'])
                    prev_close = float(row['Previous Day Close Price'])
                except ValueError as ve:
                    logger.warning(f"  ⊘ Skipping {symbol}: Invalid price data - {ve}")
                    errors.append(f"{symbol}: Invalid price format")
                    continue
                
                total_traded_qty = int(float(row['Total Traded Quantity']))
                total_traded_value = float(row['Total Traded Value'])
                
                # Get or create stock
                if symbol not in existing_symbols:
                    security_name = row['Security Name'].strip()
                    # Insert new stock
                    new_stock = db.insert("stocks", {
                        "symbol": symbol,
                        "name": security_name,
                        "sector": "TBD",
                        "is_active": True
                    })
                    stock_id = new_stock[0]['id']
                    existing_symbols[symbol] = stock_id
                    logger.info(f"  ➕ Created new stock: {symbol}")
                else:
                    stock_id = existing_symbols[symbol]
                
                price_data = {
                    "stock_id": stock_id,
                    "date": business_date,
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "prev_close": prev_close,
                    "volume": total_traded_qty,
                    "turnover": total_traded_value
                }
                
                price_data_list.append((symbol, price_data))
                if symbol == "KKHC":
                    logger.info(f"  📊 Prepared {symbol}: Close={close_price}")
                
            except Exception as e:
                errors.append(f"{row.get('Symbol', 'UNKNOWN')}: {str(e)}")
                logger.error(f"    ❌ Error processing {row.get('Symbol', 'UNKNOWN')}: {e}")
        
        # Batch upsert all prices
        logger.info(f"\n📤 Upserting {len(price_data_list)} prices...")
        if price_data_list:
            price_list = [p[1] for p in price_data_list]
            try:
                db.upsert("daily_prices", price_list, on_conflict="stock_id,date")
                inserted = len(price_data_list)
                updated = 0
                
                # Check which one is KKHC
                for symbol, pdata in price_data_list:
                    if symbol == "KKHC":
                        logger.info(f"  ✅ Upserted {symbol}: Close={pdata['close']}")
                        break
                        
            except Exception as e:
                logger.error(f"Batch upsert failed: {e}")
                inserted = 0
                updated = 0
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info(f"✅ Import Summary:")
        logger.info(f"   Inserted: {inserted} prices")
        logger.info(f"   Updated:  {updated} prices")
        logger.info(f"   Errors:   {len(errors)}")
        if errors:
            logger.info(f"\n   Error details:")
            for err in errors[:10]:  # Show first 10 errors
                logger.info(f"     - {err}")
        logger.info("=" * 60 + "\n")
        
        return inserted, updated, len(errors)
        
    except FileNotFoundError:
        logger.error(f"❌ CSV file not found: {csv_path}")
        return 0, 0, 1
    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return 0, 0, 1


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_nepse_csv.py <csv_file_path>")
        print("Example: python import_nepse_csv.py ../Downloads/Compressed/Today's Price - 2026-04-01.csv")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    import_csv_prices(csv_path)
