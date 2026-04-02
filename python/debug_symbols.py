"""Debug script to check symbol fields in different tables"""
import json
from config import db

# Get a sample symbol from prices
prices = db.select('daily_prices', columns='*', limit=3)
print('Sample from daily_prices:')
for p in prices:
    print(f"  {json.dumps({k: str(v) if not isinstance(v, (int, float, bool, type(None))) else v for k, v in p.items()})}")

print()

# Get a sample from predictions
preds = db.select('predictions', columns='*', limit=3)
print('Sample from predictions:')
for p in preds:
    print(f"  {json.dumps({k: str(v) if not isinstance(v, (int, float, bool, type(None))) else v for k, v in p.items()})}")

print()

# Get a sample from stocks
stocks = db.select('stocks', columns='*', limit=3)
print('Sample from stocks:')
for s in stocks:
    print(f"  {json.dumps({k: str(v) if not isinstance(v, (int, float, bool, type(None))) else v for k, v in s.items()})}")
