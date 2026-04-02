import time
import json
import logging
import requests
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nepse-real-api")

def get_real_nepse_token():
    """Fetches a Bearer token by refreshing it in a headless browser session."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a real user agent
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        token_data = {"token": None}
        
        def handle_request(request):
            # Intercept any outgoing Bearer token from the page
            auth = request.headers.get("authorization")
            if auth and "Bearer" in auth:
                token_data["token"] = auth
                logger.info("Captured Bearer token from outgoing request.")

        page.on("request", handle_request)
        
        logger.info("Accessing NEPSE to initialize session...")
        page.goto("https://www.nepalstock.com/today-price", wait_until="networkidle")
        time.sleep(3)
        
        # Trigger any request that might have a token
        page.click("button:has-text('Filter')") 
        time.sleep(3)
        
        browser.close()
        return token_data["token"]

def fetch_data_with_token(token, date_str):
    """Hits the official NEPSE API using a captured Bearer token."""
    url = f"https://www.nepalstock.com/api/nots/nepse-data/todays-price/?businessDate={date_str}"
    headers = {
        "Authorization": token,
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    payload = {"businessDate": date_str}
    
    logger.info(f"POSTing to {url}...")
    # NEPSE API sometimes requires verify=False or specific SSL handling
    response = requests.post(url, headers=headers, json=payload, verify=False)
    
    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed with status {response.status_code}: {response.text[:200]}")
        return None

if __name__ == "__main__":
    token = get_real_nepse_token()
    if token:
        logger.info(f"Token acquired. Fetching for 2026-03-29...")
        data = fetch_data_with_token(token, "2026-03-29")
        if data:
            # Check data format
            print(f"DATA_HEAD\n{json.dumps(data[:2] if isinstance(data, list) else data, indent=2)}\nDATA_TAIL")
        else:
            logger.error("No data returned.")
    else:
        logger.error("Token acquisition failed.")
