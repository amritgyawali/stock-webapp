import time
import logging
from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nepse-download")

def download_csv(date_str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--ignore-certificate-errors", "--disable-blink-features=AutomationControlled"])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            accept_downloads=True
        )
        page = context.new_page()
        stealth_sync(page)
        
        logger.info(f"Navigating to NEPSE for {date_str}...")
        page.goto("https://www.nepalstock.com/today-price", wait_until="domcontentloaded", timeout=60000)
        
        try:
            # Wait for date input explicitly
            page.wait_for_selector("input[type='date']", timeout=30000)
            
            # Select date
            page.fill("input[type='date']", date_str)
            page.click("button:has-text('Filter')")
            
            page.wait_for_timeout(3000)
            
            # Click download
            logger.info("Clicking Download as CSV...")
            try:
                with page.expect_download(timeout=10000) as download_info:
                    page.click("a[title='Download as CSV']")
                
                download = download_info.value
                path = f"nepse_{date_str}.csv"
                download.save_as(path)
                logger.info(f"✅ Successfully downloaded to {path}")
                
                # Read first few lines
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read(500)
                    logger.info(f"File content snippet:\n{content}")
                    
            except Exception as e:
                logger.error(f"❌ Download failed: {e}")
        except Exception as filter_e:
            logger.error(f"❌ Failed to reach filter: {filter_e}")
            logger.info("Dumping page content to 'nepse_page.html'")
            with open("nepse_page.html", "w", encoding="utf-8") as f:
                f.write(page.content())
            
        browser.close()

if __name__ == "__main__":
    download_csv("2026-03-26")
