#!/usr/bin/env python3
from config import db

# Check if any prices for today exist
prices = db.select('daily_prices', '*', {'date': 'eq.2026-04-02'}, limit=20)
if prices:
    print(f'✅ Found {len(prices)} prices for 2026-04-02')
    # Show SHEL if it exists
    for p in prices:
        if p.get('stock_id') == '2934':  # SHEL
            print(f'   SHEL: close={p.get("close")}, open={p.get("open")}, volume={p.get("volume")}')
            break
    # Show first few
    for i, p in enumerate(prices[:3]):
        print(f'   Stock {i+1}: ID={p.get("stock_id")}, close={p.get("close")}')
else:
    print('❌ No prices for 2026-04-02 yet')

# Show today's date status
print('\nDatabase Status:')
latest = db.select('daily_prices', 'date', order='date.desc', limit=10)
if latest:
    print(f'  Latest 5 dates in DB:')
    seen = set()
    for row in latest:
        d = row.get('date')
        if d not in seen:
            print(f'    - {d}')
            seen.add(d)
        if len(seen) >= 5:
            break
