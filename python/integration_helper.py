#!/usr/bin/env python3
"""
Integration Helper
Shows how to use manual data merger in the main pipeline
"""

from manual_data_merger import (
    merge_manual_and_scraped_data,
    load_manual_data_for_date,
    has_manual_data_for_date,
    get_nepal_date
)
import logging

logger = logging.getLogger("integration")

def process_daily_prices_with_manual_override(
    scraped_prices: list,
    target_date: str = None
) -> tuple:
    """
    Process daily stock prices, merging scraped data with manual uploads
    
    Usage in main pipeline:
    ```python
    # After scraping prices
    merged_prices, stats = process_daily_prices_with_manual_override(scraped_prices)
    
    # Then upload to database
    db.upsert("daily_prices", merged_prices)
    ```
    
    Args:
        scraped_prices: List of price dicts from scraper
        target_date: Date to process (defaults to today)
    
    Returns:
        Tuple of (merged_prices, merge_stats)
    """
    
    return merge_manual_and_scraped_data(scraped_prices, target_date)

def check_manual_data_status(target_date: str = None) -> dict:
    """
    Get status of manual data for a given date
    
    Returns dict with:
    - has_manual: bool - whether manual data exists
    - record_count: int - number of records
    - status: str - human readable status
    """
    
    if target_date is None:
        target_date = get_nepal_date()
    
    manual_data = load_manual_data_for_date(target_date)
    
    return {
        "date": target_date,
        "has_manual": not manual_data.empty,
        "record_count": len(manual_data) if not manual_data.empty else 0,
        "status": f"{len(manual_data)} manual records loaded" if not manual_data.empty else "No manual data - will use scraped only"
    }

# ============================================================
# Example Usage in main.py pipeline
# ============================================================

def example_pipeline_integration():
    """
    Example showing how to integrate manual data in main.py
    
    In main.py, after getting scraped prices:
    
    ```python
    # Step 1: Scrape prices
    prices = scraper.get_live_prices()
    
    # Step 2: Check for manual overrides
    from integration_helper import process_daily_prices_with_manual_override
    prices, merge_stats = process_daily_prices_with_manual_override(prices)
    
    # Step 3: Report any conflicts
    if merge_stats['conflicts']:
        print(f"⚠️  Price conflicts found and resolved using manual data:")
        for conflict in merge_stats['conflicts']:
            print(f"  {conflict['symbol']}: scrape={conflict['scraped_close']} vs manual={conflict['manual_close']}")
    
    # Step 4: Upload to database
    result = db.upsert("daily_prices", prices, on_conflict="stock_id, date")
    print(f"✓ Uploaded {len(prices)} prices (manual: {merge_stats['used_manual']}, scraped: {merge_stats['used_scraped']})")
    ```
    """
    pass

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Integration Helper Examples")
    print("=" * 60)
    
    # Example 1: Check manual data status
    status = check_manual_data_status()
    print(f"\nManual Data Status:")
    print(f"  Date: {status['date']}")
    print(f"  Has Manual: {status['has_manual']}")
    print(f"  Status: {status['status']}")
    
    # Example 2: Show how to use in pipeline
    print(f"\n\nTo integrate in main.py:")
    print("""
    from integration_helper import process_daily_prices_with_manual_override
    
    # In your pipeline:
    merged_prices, stats = process_daily_prices_with_manual_override(scraped_prices)
    db.upsert("daily_prices", merged_prices)
    
    print(f"Merged data: {stats['used_manual']} manual + {stats['used_scraped']} scraped")
    """)
