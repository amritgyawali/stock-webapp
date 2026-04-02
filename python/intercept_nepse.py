import time
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nepse-interceptor")

def intercept_nepse_data(date_str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Use a real user agent
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        captured_data = {"token": None, "data_result": None}
        
        def handle_response(response):
            if "refresh-token" in response.url:
                try:
                    logger.info("Captured Refresh Token response.")
                    # We might need headers from the *request* too
                except: pass
            if "todays-price" in response.url:
                try:
                    logger.info("Captured Todays Price response.")
                    captured_data["data_result"] = response.text()[:2000]
                except: pass

        page.on("response", handle_response)
        
        logger.info("Navigating to today-price page...")
        page.goto("https://www.nepalstock.com/today-price", wait_until="networkidle")
        time.sleep(3)
        
        logger.info("Attempting to find and click the Filter/Download buttons to trigger API calls...")
        
        # Sometimes you need to click 'Filter' or Change the date to trigger the fetch
        try:
            # First, try to just fetch via the page's own context but with correct headers
            # We can find the token by looking at existing requests the page already made
            pass
        except: pass
        
        # Let's try to trigger the 'Download' or 'Filter' logic
        # Date input is usually type='date'
        try:
            # Set the date first to trigger internal state change
            page.fill("input[type='date']", date_str)
            page.click("button:has-text('Filter')") 
            time.sleep(5)
        except Exception as e:
            logger.warning(f"Filter click failed: {e}")

        if captured_data["data_result"]:
            print(f"CAPTURED_DATA_START\n{captured_data['data_result']}\nCAPTURED_DATA_END")
        else:
            logger.error("Failed to capture data. Checking alternative: Download as CSV...")
            # Try clicking the "Download as CSV" if it exists
            try:
                # The download usually triggers a POST to the PDF/CSV generator or just the API
                # Some sites use <a> with download attribute or a button that calls window.open
                pass
            except: pass

        browser.close()

if __name__ == "__main__":
    # NEPSE trades Sun-Thu. March 29, 2026 is Sunday (Trading Day)
    intercept_nepse_data("2026-03-29")
