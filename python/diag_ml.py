"""
Quick diagnostic: Check per-stock day counts to see why predictor returns 0.
"""
import config

# Check a sample of stocks
stocks = config.db.select("stocks", "id,symbol", {"is_active": "eq.true"}, limit=10)
print(f"Active stocks sample ({len(stocks)}):")
for s in stocks:
    count_rows = config.db.select(
        "daily_prices", "date",
        {"stock_id": f"eq.{s['id']}"},
        order="date.asc",
        limit=1000
    )
    print(f"  {s['symbol']} (id={s['id']}): {len(count_rows)} days, oldest={count_rows[0]['date'] if count_rows else 'N/A'}")

# Also check from which date we have 30+ days per stock
print("\nChecking how many stocks have >= 30 days of data...")
all_stocks = config.db.select("stocks", "id,symbol", {"is_active": "eq.true"})
ready = 0
for s in all_stocks:
    rows = config.db.select(
        "daily_prices", "date", {"stock_id": f"eq.{s['id']}"},
        limit=31
    )
    if len(rows) >= 30:
        ready += 1

print(f"{ready}/{len(all_stocks)} stocks have >= 30 days of data.")
