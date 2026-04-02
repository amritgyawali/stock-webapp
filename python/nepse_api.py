import time
import json
import logging
import requests
from playwright.sync_api import sync_playwright
from config import REQUEST_HEADERS

logger = logging.getLogger("nepse-api")

class NepseAPI:
    """
    Official NEPSE API Connector.
    Uses Playwright to capture the necessary Bearer token and hits the JSON endpoints.
    """
    
    def __init__(self):
        self.base_url = "https://www.nepalstock.com/api/nots/nepse-data/todays-price/"
        self.token = None
        self._last_token_time = 0

    def _refresh_bearer_token(self):
        """Launches a headless browser to capture the latest authorization header from the live site."""
        logger.info("🎬 Launching security handshake with NEPSE...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(user_agent=REQUEST_HEADERS["User-Agent"])
                page = context.new_page()
                
                captured = {"token": None}
                
                # Listen for any outgoing API request to capture the header
                def on_request(request):
                    auth = request.headers.get("authorization")
                    # NEPSE uses "Salter <token>" instead of Bearer
                    if auth and "Salter" in auth:
                        captured["token"] = auth

                page.on("request", on_request)
                
                # Navigate to trigger the site's own internal fetch/refresh logic
                page.goto("https://www.nepalstock.com/today-price", wait_until="networkidle")
                
                # Trigger the 'Download as CSV' button which the subagent verified triggers the API
                try:
                    # Specifically trigger a data-loading action
                    page.click("button.box__filter--search", timeout=5000)
                    page.wait_for_timeout(2000)
                    # Also try the CSV download link as it's a guaranteed API trigger
                    page.hover("a.table__file[title='Download as CSV']")
                except:
                    pass
                
                time.sleep(2)
                browser.close()
                
                if captured["token"]:
                    logger.info("✅ Security handshake successful. Salter token captured.")
                    self.token = captured["token"]
                    self._last_token_time = time.time()
                    return True
                else:
                    logger.error("❌ Handshake failed: Could not capture Salter token.")
                    return False
        except Exception as e:
            logger.error(f"❌ Handshake Error: {e}")
            return False

    def fetch_price_data(self, date_str):
        """
        Fetches full stock data for a specific date (YYYY-MM-DD).
        """
        # Tokens expire quickly, refresh if more than 5 minutes old
        if not self.token or (time.time() - self._last_token_time > 300):
            if not self._refresh_bearer_token():
                return None

        url = f"{self.base_url}?businessDate={date_str}"
        headers = {
            "Authorization": self.token,
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "User-Agent": REQUEST_HEADERS["User-Agent"]
        }
        payload = {"businessDate": date_str}
        
        try:
            logger.info(f"📡 Fetching official data for {date_str}...")
            # NEPSE requires POST for the todays-price endpoint
            resp = requests.post(url, headers=headers, json=payload, verify=False, timeout=20)
            
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"📊 Received {len(data) if isinstance(data, list) else 1} records.")
                return data
            elif resp.status_code == 401:
                logger.warning("⚠️ Token expired mid-request. Refreshing...")
                self.token = None
                return self.fetch_price_data(date_str)
            else:
                logger.error(f"❌ API Error {resp.status_code}: {resp.text[:200]}")
                return None
        except Exception as e:
            logger.error(f"❌ Network Error: {e}")
            return None

if __name__ == "__main__":
    # Test run
    logging.basicConfig(level=logging.INFO)
    api = NepseAPI()
    test_date = "2026-03-26"
    result = api.fetch_price_data(test_date)
    if result:
        print(f"Success! Captured {len(result)} rows.")
    else:
        print("Failed to fetch data.")
