"""
Test live NEPSE fetcher
"""
from live_nepse_fetcher import live_fetcher
import pandas as pd

print("[TEST] Testing live NEPSE fetcher...")
df = live_fetcher.fetch_live_prices()

if not df.empty:
    print(f"[OK] Fetched {len(df)} stocks")
    
    # Show SHEL price
    shel = df[df['symbol'] == 'SHEL']
    if not shel.empty:
        print(f"[OK] SHEL found!")
        print(f"     Close: {shel.iloc[0]['close']}")
        print(f"     Open: {shel.iloc[0]['open']}")
        print(f"     High: {shel.iloc[0]['high']}")
        print(f"     Low: {shel.iloc[0]['low']}")
    else:
        print("[WARN] SHEL not found in current data")
    
    print("\nFirst 5 stocks:")
    print(df.head())
else:
    print("[ERROR] No data fetched")
