import time
import json
import logging
from playwright.sync_api import sync_playwright

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nepse-api-tester")

def test_nepse_api(date_str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        logger.info("Navigating to NEPSE to establish session...")
        page.goto("https://www.nepalstock.com/today-price", wait_until="networkidle")
        time.sleep(2)
        
        logger.info(f"Attempting to fetch data for {date_str} via in-page fetch...")
        
        # Execute fetch in the browser context to use existing cookies/headers
        js_code = f"""
        async () => {{
            const response = await fetch('https://www.nepalstock.com/api/nots/nepse-data/todays-price/?businessDate={date_str}', {{
                method: 'POST',
                headers: {{
                    'Accept': 'application/json, text/plain, */*',
                    'Content-Type': 'application/json'
                }},
                body: JSON.stringify({{
                    businessDate: "{date_str}"
                }})
            }});
            return await response.text();
        }}
        """
        
        try:
            result = page.evaluate(js_code)
            logger.info("Fetch completed.")
            if result:
                print(f"RESULT_START\n{result[:2000]}\nRESULT_END")
            else:
                logger.error("Empty result from fetch.")
        except Exception as e:
            logger.error(f"Error during fetch: {e}")
            
        browser.close()

if __name__ == "__main__":
    # Test for "today" or a recent date
    test_nepse_api("2026-03-29")
