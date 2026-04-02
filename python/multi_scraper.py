import pandas as pd
import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger("multi-scraper")
logging.basicConfig(level=logging.INFO)

def clean_col(df, col_name, new_name):
    if col_name in df.columns:
        df[new_name] = df[col_name].astype(str).str.replace(',', '').str.replace('%', '')
        df[new_name] = pd.to_numeric(df[new_name], errors='coerce')
    return df

def extract_standard_df(html):
    try:
        dfs = pd.read_html(html)
        for df in dfs:
            cols = [str(c).lower() for c in df.columns]
            if any('symbol' in c for c in cols):
                # Standardize column names
                col_map = {}
                for c in df.columns:
                    cl = str(c).lower()
                    if 'symbol' in cl: col_map[c] = 'symbol'
                    elif 'ltp' in cl or 'close' in cl: col_map[c] = 'close'
                    elif '%' in cl or 'change' in cl: col_map[c] = 'change_pct'
                    elif 'qty' in cl or 'quant' in cl or 'vol' in cl: col_map[c] = 'volume'
                
                df = df.rename(columns=col_map)
                
                # Verify we have minimum columns
                needed = ['symbol', 'close']
                if not all(n in df.columns for n in needed):
                    continue
                    
                # Clean data
                df = clean_col(df, 'close', 'close')
                if 'change_pct' in df.columns: df = clean_col(df, 'change_pct', 'change_pct')
                if 'volume' in df.columns: df = clean_col(df, 'volume', 'volume')
                
                return df[['symbol', 'close', 'change_pct', 'volume']] if 'volume' in df.columns and 'change_pct' in df.columns else df
    except Exception as e:
        logger.error(f"Error extracting HTML table: {e}")
    return pd.DataFrame()

def scrape_all_sources():
    results = {}
    with sync_playwright() as p:
        # Launch browser headless
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = context.new_page()

        # 1. Merolagani
        try:
            logger.info("Fetching Merolagani...")
            page.goto("https://www.merolagani.com/LatestMarket.aspx", timeout=60000)
            page.wait_for_selector("table.table-hover", timeout=15000)
            results["merolagani"] = extract_standard_df(page.content())
        except Exception as e:
            logger.error(f"Merolagani failed: {e}")

        # 2. Nepalipaisa
        try:
            logger.info("Fetching Nepalipaisa...")
            page.goto("https://nepalipaisa.com/live-market", timeout=60000)
            page.wait_for_timeout(5000) # Give API time to load table
            results["nepalipaisa"] = extract_standard_df(page.content())
        except Exception as e:
            logger.error(f"Nepalipaisa failed: {e}")

        # 3. ShareSansar
        try:
            logger.info("Fetching ShareSansar...")
            page.goto("https://www.sharesansar.com/live-trading", timeout=60000)
            page.wait_for_selector("table", timeout=15000)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(page.content(), "lxml")
            table = soup.find("table")
            if table:
                records = []
                for row in table.find_all("tr")[1:]:
                    cols = row.find_all(["td", "th"])
                    if len(cols) >= 8:
                        try:
                            records.append({
                                "symbol": cols[1].get_text(strip=True).upper(),
                                "close": float(cols[2].get_text(strip=True).replace(',', '')),
                                "change_pct": float(cols[3].get_text(strip=True).replace(',', '').replace('%', '')),
                                "volume": int(cols[7].get_text(strip=True).replace(',', ''))
                            })
                        except Exception:
                            continue
                if records:
                    df = pd.DataFrame(records)
                    # Deduplicate in case
                    df = df.drop_duplicates(subset=["symbol"])
                    results["sharesansar"] = df
        except Exception as e:
            logger.error(f"ShareSansar failed: {e}")

        # 4. NepalStock
        try:
            logger.info("Fetching NepalStock...")
            page.goto("https://www.nepalstock.com/today-price", timeout=60000)
            page.wait_for_timeout(5000) # Wait for Angular
            # Select 500 pagination if possible
            try:
                page.select_option('select[name="DataTables_Table_0_length"]', value="500", timeout=3000)
                page.wait_for_timeout(3000)
            except:
                pass
            results["nepalstock"] = extract_standard_df(page.content())
        except Exception as e:
            logger.error(f"NepalStock failed: {e}")

        browser.close()
    return results

if __name__ == "__main__":
    data = scrape_all_sources()
    for name, df in data.items():
        print(f"--- {name.upper()} ---")
        if not df.empty:
            print(df.head(3))
            print(f"Total rows: {len(df)}")
        else:
            print("Failed or empty")
