from nepse_scraper import NepseScraper
import pandas as pd
import json

scraper = NepseScraper(verify_ssl=False)

def test():
    try:
        # According to the scraper name, today_price
        date_str = "2026-03-26"
        data = scraper.get_today_price(business_date=date_str)
        print(f"✅ get_today_price successful for {date_str}!")
        print(f"Count: {len(data)}")
        if data:
            print("First item sample:")
            print(json.dumps(data[0], indent=2))
        else:
            print("No data found for this date.")
    except Exception as e:
        print(f"❌ get_today_price failed: {e}")

    try:
        # Check if it has a way to get historical or with parameters
        print("\nChecking NepseScraper methods...")
        methods = [m for m in dir(scraper) if not m.startswith('_')]
        print(methods)
    except Exception as e:
        pass

test()
