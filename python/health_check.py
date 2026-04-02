from config import db, logger

print("\n=== SYSTEM HEALTH CHECK ===\n")

# 1. Supabase connection
try:
    connected = db.health_check()
    print(f"✅ Supabase Connection: {'CONNECTED' if connected else 'DISCONNECTED'}")
except Exception as e:
    print(f"❌ Supabase Connection Error: {e}")

# 2. Check stocks count
try:
    stocks = db.select("stocks", "id,symbol", {"is_active": "eq.true"})
    print(f"✅ Active Stocks: {len(stocks)} companies")
except Exception as e:
    print(f"❌ Stocks Query Error: {e}")

# 3. Check recent prices
try:
    from config import get_nepal_date_str
    today = get_nepal_date_str()
    prices = db.select("daily_prices", "*", {"date": f"eq.{today}"}, limit=10)
    print(f"✅ Today's Data ({today}): {len(prices)} price records found")
    if prices:
        print(f"   Sample: {prices[0].get('symbol', 'N/A')} - Close: {prices[0].get('close', 'N/A')}")
except Exception as e:
    print(f"❌ Prices Query Error: {e}")

# 4. Check predictions
try:
    preds = db.select("predictions", "*", order="prediction_date.desc", limit=5)
    if preds:
        latest_date = preds[0].get('prediction_date')
        top5_count = len([p for p in preds if p.get('buy_rank')])
        print(f"✅ Predictions: Latest={latest_date}, Top 5 picks tracked")
    else:
        print(f"⚠️  No predictions yet (need 30+ days of data)")
except Exception as e:
    print(f"❌ Predictions Query Error: {e}")

# 5. Market summary
try:
    summary = db.select("market_summary", "*", order="date.desc", limit=1)
    if summary:
        latest = summary[0]
        nepse_index = latest.get('nepse_index', 'N/A')
        print(f"✅ Market Summary: NEPSE Index = {nepse_index}")
    else:
        print(f"⚠️  No market summary yet")
except Exception as e:
    print(f"❌ Market Summary Error: {e}")

print("\n=== HEALTH CHECK COMPLETE ===\n")
