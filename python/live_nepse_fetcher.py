"""
Live NEPSE Price Fetcher
Fetches real-time pricing data directly from the official NEPSE website
"""

import requests
import pandas as pd
from datetime import datetime
from config import logger, REQUEST_TIMEOUT, REQUEST_HEADERS, get_nepal_date_str

class LiveNepseFetcher:
    """Fetches live pricing data from official NEPSE endpoints"""
    
    # Official NEPSE API and website
    NEPSE_TODAY_PRICE_URL = "https://www.nepalstock.com/api/nots/trades/search"
    NEPSE_AUTHENTICATE_URL = "https://www.nepalstock.com/api/authenticate/prove"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(REQUEST_HEADERS)
        self.is_authenticated = False
    
    def authenticate(self) -> bool:
        """Authenticate with NEPSE API"""
        try:
            resp = self.session.get(
                self.NEPSE_AUTHENTICATE_URL,
                timeout=REQUEST_TIMEOUT,
                verify=False  # Disable SSL verification for dev environment
            )
            resp.raise_for_status()
            self.is_authenticated = True
            logger.info("✅ NEPSE authentication successful")
            return True
        except Exception as e:
            logger.error(f"❌ NEPSE authentication failed: {e}")
            return False
    
    def fetch_live_prices(self) -> pd.DataFrame:
        """Fetch today's prices from official NEPSE"""
        logger.info("📡 Fetching live prices from official NEPSE...")
        
        try:
            if not self.is_authenticated:
                if not self.authenticate():
                    return pd.DataFrame()
            
            # Fetch company trades for today
            today = get_nepal_date_str()
            params = {
                "size": 500,  # Get up to 500 records
                "sort": "contractSymbol,asc"
            }
            
            resp = self.session.get(
                self.NEPSE_TODAY_PRICE_URL,
                params=params,
                timeout=REQUEST_TIMEOUT,
                verify=False  # Disable SSL verification for dev environment
            )
            resp.raise_for_status()
            data = resp.json()
            
            if not data or not isinstance(data, (list, dict)):
                logger.warning("⚠️ No data returned from NEPSE")
                return pd.DataFrame()
            
            # Handle different response formats
            items = data.get("content", data) if isinstance(data, dict) else data
            
            if not isinstance(items, list):
                return pd.DataFrame()
            
            # Parse and aggregate prices by symbol
            price_map = {}
            
            for trade in items:
                symbol = trade.get("contractSymbol", "") or trade.get("symbol", "")
                if not symbol:
                    continue
                
                symbol = symbol.strip().upper()
                
                # Aggregate OHLC for the day
                ltp = self._safe_float(trade.get("lastTradedPrice", trade.get("ltp")))
                
                if symbol not in price_map:
                    price_map[symbol] = {
                        "open": ltp,
                        "high": ltp,
                        "low": ltp,
                        "close": ltp,
                        "volume": 0,
                        "turnover": 0.0,
                        "trades_count": 0,
                    }
                
                price_map[symbol]["high"] = max(
                    price_map[symbol]["high"],
                    ltp if ltp else 0
                )
                price_map[symbol]["low"] = min(
                    price_map[symbol]["low"],
                    ltp if ltp else float('inf')
                )
                price_map[symbol]["close"] = ltp
                price_map[symbol]["volume"] += self._safe_int(
                    trade.get("quantity", trade.get("totalTradeQuantity", 0))
                )
                price_map[symbol]["turnover"] += self._safe_float(
                    trade.get("amount", trade.get("totalTradeValue", 0))
                )
                price_map[symbol]["trades_count"] += 1
            
            # Convert to DataFrame
            records = []
            for symbol, data_point in price_map.items():
                records.append({
                    "symbol": symbol,
                    "open": data_point["open"],
                    "high": data_point["high"],
                    "low": data_point["low"],
                    "close": data_point["close"],
                    "volume": data_point["volume"],
                    "turnover": data_point["turnover"],
                })
            
            df = pd.DataFrame(records)
            logger.info(f"✅ Fetched live prices for {len(df)} stocks from official NEPSE")
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching live prices: {e}")
            return pd.DataFrame()
    
    def _safe_float(self, value) -> float:
        """Safely convert to float"""
        try:
            return float(value) if value is not None else 0.0
        except (ValueError, TypeError):
            return 0.0
    
    def _safe_int(self, value) -> int:
        """Safely convert to int"""
        try:
            return int(float(value)) if value is not None else 0
        except (ValueError, TypeError):
            return 0


# Global instance
live_fetcher = LiveNepseFetcher()
