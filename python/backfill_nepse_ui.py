import time
import logging
from playwright.sync_api import sync_playwright
import datetime

logger = logging.getLogger("nepse-historic")
logging.basicConfig(level=logging.INFO)

def fetch_history_nepse_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0")
        page = context.new_page()
        
        logger.info("Navigate to Nepse UI...")
        page.goto("https://www.nepalstock.com/today-price", timeout=60000)
        page.wait_for_selector("input[type='date']", timeout=30000)
        
        # Test 1 iteration
        test_date = "2026-03-15"
        logger.info(f"Targeting date {test_date}")
        
        page.fill("input[type='date']", test_date)
        
        # Click Filter
        page.click("button:has-text('Filter')")
        
        # Wait for API fetch
        page.wait_for_timeout(5000)
        
        # Look for table
        table_html = page.locator("table").inner_html()
        logger.info(f"Html snip: {table_html[:100]}")
        
        browser.close()

if __name__ == "__main__":
    fetch_history_nepse_ui()
