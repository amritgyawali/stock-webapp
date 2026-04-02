#!/usr/bin/env python3
"""
Manual vs Scraped Data Merger
Compares manual stock data (uploaded CSVs) with scraped data
Prioritizes manual data when both are available
"""

import os
import pandas as pd
import logging
from pathlib import Path
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Tuple

logger = logging.getLogger("data-merger")

MANUAL_DATA_FOLDER = Path(__file__).parent.parent / "manual stocks data"

def get_nepal_date() -> str:
    """Get today's date in Nepal Standard Time (UTC+5:45)"""
    nepal_offset = timedelta(hours=5, minutes=45)
    nepal_now = datetime.now(timezone.utc).astimezone(timezone(nepal_offset))
    return nepal_now.strftime('%Y-%m-%d')

def load_manual_data_for_date(target_date: str = None) -> pd.DataFrame:
    """
    Load manual stock data from CSV files in 'manual stocks data' folder
    
    Args:
        target_date: Date to filter for (format: YYYY-MM-DD). If None, uses today's date
    
    Returns:
        DataFrame with manual stock data, or empty DataFrame if no files found
    """
    
    if target_date is None:
        target_date = get_nepal_date()
    
    if not MANUAL_DATA_FOLDER.exists():
        logger.warning(f"Manual stocks data folder not found: {MANUAL_DATA_FOLDER}")
        return pd.DataFrame()
    
    csv_files = list(MANUAL_DATA_FOLDER.glob("*.csv"))
    if not csv_files:
        logger.info(f"No CSV files found in {MANUAL_DATA_FOLDER}")
        return pd.DataFrame()
    
    logger.info(f"Found {len(csv_files)} CSV file(s) in manual stocks data folder")
    
    # Try to load all CSV files and combine them
    all_data = []
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            
            # Standardize column names (case-insensitive)
            df.columns = df.columns.str.strip().str.lower()
            
            # Check for date column (could be 'business date', 'date', etc.)
            date_col = None
            for col in ['business date', 'date', 'business_date']:
                if col in df.columns:
                    date_col = col
                    break
            
            # Filter by target date if found
            if date_col:
                df['date'] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')
                df = df[df['date'] == target_date]
            
            if not df.empty:
                all_data.append(df)
                logger.info(f"✓ Loaded {len(df)} records from {csv_file.name}")
            else:
                logger.warning(f"  No records for {target_date} in {csv_file.name}")
                
        except Exception as e:
            logger.error(f"Error loading {csv_file.name}: {e}")
            continue
    
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        logger.info(f"✓ Total manual records loaded: {len(combined_df)}")
        return combined_df
    else:
        logger.info("No manual data found for the specified date")
        return pd.DataFrame()

def normalize_stock_symbol(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize stock symbol column name and values
    
    Looks for symbol column (case-insensitive) and ensures uppercase without spaces
    """
    # Find symbol column
    symbol_col = None
    for col in df.columns:
        if 'symbol' in col.lower():
            symbol_col = col
            break
    
    if symbol_col:
        df = df.copy()
        df['symbol'] = df[symbol_col].str.strip().str.upper()
    
    return df

def merge_manual_and_scraped_data(
    scraped_data: List[Dict], 
    target_date: str = None
) -> Tuple[List[Dict], Dict]:
    """
    Merge manual and scraped stock data
    Prioritizes manual data when both are available
    
    Args:
        scraped_data: List of dicts with scraped stock data
        target_date: Date to filter for (uses today if None)
    
    Returns:
        Tuple of (merged_data, stats) where:
        - merged_data: List of dicts with combined data
        - stats: Dict with merge statistics
    """
    
    if target_date is None:
        target_date = get_nepal_date()
    
    stats = {
        "target_date": target_date,
        "manual_records": 0,
        "scraped_records": len(scraped_data),
        "used_manual": 0,
        "used_scraped": 0,
        "merged": 0,
        "conflicts": []
    }
    
    # Load manual data
    manual_df = load_manual_data_for_date(target_date)
    
    if manual_df.empty:
        logger.info("No manual data available, using scraped data only")
        stats["used_scraped"] = len(scraped_data)
        return scraped_data, stats
    
    manual_df = normalize_stock_symbol(manual_df)
    stats["manual_records"] = len(manual_df)
    
    # Create dict indexed by symbol for manual data
    manual_by_symbol = {}
    for _, row in manual_df.iterrows():
        symbol = row.get('symbol', '').upper()
        if symbol:
            manual_by_symbol[symbol] = row.to_dict()
    
    # Merge: iterate through scraped data and replace with manual where available
    merged_data = []
    used_manual_set = set()
    
    for scraped_item in scraped_data:
        symbol = scraped_item.get('symbol', '').upper()
        
        if symbol in manual_by_symbol:
            # Prioritize manual data
            manual_item = manual_by_symbol[symbol]
            
            # Check if prices differ
            scraped_close = float(scraped_item.get('close', 0))
            manual_close = float(manual_item.get('close price', 0) or manual_item.get('close', 0))
            
            if abs(scraped_close - manual_close) > 0.01:  # Tolerance for floating point
                stats["conflicts"].append({
                    "symbol": symbol,
                    "scraped_close": scraped_close,
                    "manual_close": manual_close,
                    "action": "used_manual"
                })
                logger.warning(f"  ⚠️  {symbol}: Mismatch (scraped={scraped_close}, manual={manual_close}) → Using MANUAL")
            
            # Merge: use manual data, keep scraped data as fallback
            merged_item = {**scraped_item, **manual_item}
            merged_data.append(merged_item)
            used_manual_set.add(symbol)
            stats["used_manual"] += 1
        else:
            # No manual data, use scraped
            merged_data.append(scraped_item)
            stats["used_scraped"] += 1
    
    # Add any manual records that weren't in scraped data
    for symbol, manual_item in manual_by_symbol.items():
        if symbol not in used_manual_set:
            merged_data.append(manual_item)
            stats["merged"] += 1
    
    logger.info(f"\n✓ Merge complete:")
    logger.info(f"  Used manual data: {stats['used_manual']} stocks")
    logger.info(f"  Used scraped data: {stats['used_scraped']} stocks")
    logger.info(f"  Added from manual only: {stats['merged']} stocks")
    logger.info(f"  Price conflicts found: {len(stats['conflicts'])}")
    
    return merged_data, stats

def has_manual_data_for_date(target_date: str = None) -> bool:
    """Check if manual data exists for a given date"""
    if target_date is None:
        target_date = get_nepal_date()
    
    if not MANUAL_DATA_FOLDER.exists():
        return False
    
    csv_files = list(MANUAL_DATA_FOLDER.glob("*.csv"))
    if not csv_files:
        return False
    
    # Try to load and check if any data matches the date
    try:
        manual_data = load_manual_data_for_date(target_date)
        return not manual_data.empty
    except:
        return False

def list_available_manual_data() -> Dict[str, int]:
    """List all available dates in manual data files"""
    
    if not MANUAL_DATA_FOLDER.exists():
        return {}
    
    csv_files = list(MANUAL_DATA_FOLDER.glob("*.csv"))
    dates_count = {}
    
    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file)
            df.columns = df.columns.str.strip().str.lower()
            
            # Find date column
            date_col = None
            for col in ['business date', 'date', 'business_date']:
                if col in df.columns:
                    date_col = col
                    break
            
            if date_col:
                df['date'] = pd.to_datetime(df[date_col]).dt.strftime('%Y-%m-%d')
                date_counts = df['date'].value_counts().to_dict()
                for date, count in date_counts.items():
                    dates_count[date] = dates_count.get(date, 0) + count
                    
        except:
            continue
    
    return dates_count

if __name__ == "__main__":
    # Test the merger
    logging.basicConfig(level=logging.INFO)
    
    print("Manual Stocks Data Merger - Test Mode")
    print("=" * 60)
    
    # Check available manual data
    available_dates = list_available_manual_data()
    if available_dates:
        print("\nAvailable dates in manual data:")
        for date, count in sorted(available_dates.items()):
            print(f"  {date}: {count} records")
    else:
        print("\nNo manual data files found yet.")
        print(f"Upload CSV files to: {MANUAL_DATA_FOLDER}")
    
    # Test loading today's manual data
    print(f"\nTesting load for today ({get_nepal_date()}):")
    manual = load_manual_data_for_date()
    if not manual.empty:
        print(f"✓ Loaded {len(manual)} manually entered stocks")
        print(f"  Columns: {list(manual.columns)}")
    else:
        print("  No manual data available for today yet")
