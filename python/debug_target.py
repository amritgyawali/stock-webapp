from config import db
import pandas as pd
import numpy as np

def debug_stock(symbol="NABIL"):
    stock = db.select("stocks", "id", {"symbol": f"eq.{symbol}"}, limit=1)
    if not stock:
        print("Stock not found")
        return
    stock_id = stock[0]["id"]
    
    rows = db.select("daily_prices", "*", {"stock_id": f"eq.{stock_id}"}, order="date.desc", limit=100)
    df = pd.DataFrame(rows)
    df = df.sort_values("date").reset_index(drop=True)
    
    print(f"Columns: {df.columns.tolist()}")
    print(f"First 5 rows close prices: {df['close'].head().tolist()}")
    
    # Check target calculation
    df['high'] = pd.to_numeric(df['high'], errors='coerce')
    df['close'] = pd.to_numeric(df['close'], errors='coerce')
    
    forward_days = 5
    df['future_high'] = df['high'].shift(-forward_days).rolling(window=forward_days).max()
    df['target_upside'] = (df['future_high'] - df['close']) / df['close'] * 100
    
    print(f"Target upside head: {df['target_upside'].head().tolist()}")
    print(f"Target upside tail: {df['target_upside'].tail(10).tolist()}")
    print(f"Non-NaN targets: {df['target_upside'].count()}")

if __name__ == "__main__":
    debug_stock()
