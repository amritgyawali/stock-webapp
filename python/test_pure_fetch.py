import requests
import json
import urllib3

urllib3.disable_warnings()

url = "https://www.nepalstock.com/api/nots/nepse-data/todays-price/?businessDate=2026-03-26"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Content-Type": "application/json",
    "Origin": "https://www.nepalstock.com",
    "Referer": "https://www.nepalstock.com/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Connection": "keep-alive"
}
payload = {
    "id": 147,
    "businessDate": "2026-03-26"
}

print("Executing purely vanilla POST request...")
try:
    response = requests.post(url, headers=headers, json=payload, verify=False, timeout=15)
    print(f"Status Code: {response.status_code}")
    print(response.text[:500])
except Exception as e:
    print(f"Failed: {e}")
