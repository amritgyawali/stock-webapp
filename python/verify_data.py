import pandas as pd
import logging
from collections import Counter
from multi_scraper import scrape_all_sources
from config import db, get_nepal_date_str

logger = logging.getLogger("verify-data")
logging.basicConfig(level=logging.INFO, format="%(message)s")

def verify_and_sync():
    logger.info("===========================================")
    logger.info("🚀 Starting Multi-Source Cross-Validation")
    logger.info("===========================================")
    
    # 1. Scrape all sources
    results = scrape_all_sources()
    
    if not any(not df.empty for df in results.values()):
        logger.error("❌ All sources failed to return data.")
        return

    # 2. Extract specific data
    source_dfs = {}
    for source, raw_df in results.items():
        if isinstance(raw_df, pd.DataFrame):
            df = raw_df
        elif isinstance(raw_df, dict):
            # Fallback if extract_standard_df returned a dict of dfs
            if source in raw_df:
                df = raw_df[source]
            else:
                df = list(raw_df.values())[0] if raw_df else pd.DataFrame()
        else:
            df = raw_df
            
        if not df is None and not df.empty:
            if 'symbol' in df.columns and 'close' in df.columns:
                # Clean symbol
                df['symbol'] = df['symbol'].astype(str).str.strip().str.upper()
                df = df.drop_duplicates(subset=['symbol'])
                source_dfs[source] = df.set_index('symbol')
                logger.info(f"✅ {source.capitalize()} returned {len(df)} symbols.")
            else:
                logger.warning(f"⚠️ {source.capitalize()} dataframe missing required columns.")

    # 3. Get universal list of symbols
    all_symbols = set()
    for df in source_dfs.values():
        all_symbols.update(df.index.tolist())

    logger.info(f"\n🔍 Cross-validating {len(all_symbols)} unique symbols across {len(source_dfs)} sources...")
    
    discrepancies_found = 0
    validated_records = []
    today_str = get_nepal_date_str()

    for symbol in sorted(all_symbols):
        source_prices = {}
        for source, df in source_dfs.items():
            if symbol in df.index:
                close_val = df.loc[symbol, 'close']
                try:
                    close_val = float(str(close_val).replace(',', ''))
                    source_prices[source] = close_val
                except (ValueError, TypeError):
                    pass
        
        if not source_prices:
            continue
            
        # Count frequency of each price
        prices = list(source_prices.values())
        counts = Counter(prices)
        
        # Identify discrepancies
        if len(counts) > 1:
            discrepancies_found += 1
            if discrepancies_found <= 10:  # Print max 10 to avoid terminal spam
                logger.warning(f"⚠️ DISCREPANCY on {symbol}: {source_prices}")
        
        # Pick consensus (mode)
        # If there's a tie, Counter.most_common(1) picks the first one encountered (often the priority one)
        # Assuming our priority is ShareSansar, let's inject priority logic:
        consensus_price = counts.most_common(1)[0][0]
        
        # We also need volume and change_pct. Let's just grab the row from the source that had the consensus price.
        consensus_source = next((src for src, p in source_prices.items() if p == consensus_price), None)
        
        if consensus_source:
            row = source_dfs[consensus_source].loc[symbol]
            vol = row.get('volume', 0)
            chg = row.get('change_pct', 0)
            try: vol = int(str(vol).replace(',', '')) if pd.notnull(vol) else 0
            except: vol = 0
            
            try: chg = float(str(chg).replace('%', '')) if pd.notnull(chg) else 0.0
            except: chg = 0.0
            
            validated_records.append({
                "symbol": symbol,
                "close": consensus_price,
                "volume": vol,
                "change_pct": chg
            })

    logger.info(f"\n📊 cross-validation Complete.")
    logger.info(f"Discrepancies found: {discrepancies_found}/{len(all_symbols)} symbols.")
    logger.info(f"Generating {len(validated_records)} consensus records for {today_str}...")

    # 4. Save Consensus data to Supabase (mimicking main.py behavior)
    stored_count = 0
    for record in validated_records:
        symbol = record.pop("symbol")
        
        # Look up stock_id
        stock_result = db.select("stocks", "id", {"symbol": f"eq.{symbol}"}, limit=1)
        if not stock_result:
            try:
                db.upsert("stocks", {"symbol": symbol, "name": symbol, "is_active": True}, on_conflict="symbol")
                stock_result = db.select("stocks", "id", {"symbol": f"eq.{symbol}"}, limit=1)
            except Exception:
                continue
                
        if stock_result:
            stock_id = stock_result[0]["id"]
            db_record = {
                "stock_id": stock_id,
                "date": today_str,
                "close": record["close"],
                "volume": record["volume"],
                "change_pct": record["change_pct"]
            }
            try:
                db.upsert("daily_prices", db_record, on_conflict="uq_daily_prices_stock_date")
                stored_count += 1
            except Exception as e:
                logger.debug(f"Error storing {symbol}: {e}")

    logger.info(f"💾 Successfully stored {stored_count} consensus records in Supabase.")

if __name__ == "__main__":
    verify_and_sync()
