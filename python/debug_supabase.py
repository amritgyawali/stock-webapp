import os
import requests
from dotenv import load_dotenv

load_dotenv()

url = f"{os.getenv('SUPABASE_URL')}/rest/v1/daily_prices"
headers = {
    "apikey": os.getenv("SUPABASE_SERVICE_ROLE_KEY"),
    "Authorization": f"Bearer {os.getenv('SUPABASE_SERVICE_ROLE_KEY')}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

# 1. Fetch a valid stock_id first
stock_url = f"{os.getenv('SUPABASE_URL')}/rest/v1/stocks?select=id&limit=1"
stock_id = requests.get(stock_url, headers=headers).json()[0]["id"]

data = [{
    "stock_id": stock_id,
    "date": "2025-01-01",
    "close": 999.99,
    "volume": 1000
}]

print(f"Testing direct POST to {url} with stock_id {stock_id}...")
resp = requests.post(url, headers=headers, json=data)

print(f"Status Code: {resp.status_code}")
print(f"Response Body: {resp.text}")
