"""
NEPSE Stock Analysis — Configuration
Supabase REST client (no SDK needed), API endpoints, and constants.
"""

import os
import logging
import requests as req
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv

# Load .env file for local development
load_dotenv()

# =========================
# LOGGING
# =========================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("nepse-analyzer")

# =========================
# SUPABASE (REST API — no SDK needed)
# =========================
SUPABASE_URL: str = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    logger.warning(
        "⚠️  SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY not set! "
        "Set them as environment variables or in a .env file."
    )

# Supabase REST base URL
SUPABASE_REST_URL = f"{SUPABASE_URL}/rest/v1"

# Headers for all Supabase REST calls
SUPABASE_HEADERS = {
    "apikey": SUPABASE_SERVICE_ROLE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}


class SupabaseClient:
    """Lightweight Supabase REST API client using requests. No SDK needed."""

    def __init__(self):
        self.base = SUPABASE_REST_URL
        self.headers = SUPABASE_HEADERS.copy()

    def select(self, table: str, columns: str = "*", filters: dict = None,
               order: str = None, limit: int = None) -> list[dict]:
        """SELECT query. filters is a dict like {\"symbol\": \"eq.NABIL\", \"is_active\": \"eq.true\"}"""
        url = f"{self.base}/{table}?select={columns}"
        if filters:
            for key, val in filters.items():
                url += f"&{key}={val}"
        if order:
            url += f"&order={order}"
        if limit:
            url += f"&limit={limit}"

        resp = req.get(url, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def insert(self, table: str, data: dict | list[dict]) -> list[dict]:
        """INSERT one or more rows."""
        url = f"{self.base}/{table}"
        if isinstance(data, dict):
            data = [data]
        resp = req.post(url, headers=self.headers, json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def upsert(self, table: str, data: dict | list[dict],
               on_conflict: str = None) -> list[dict]:
        """UPSERT (insert or update on conflict)."""
        url = f"{self.base}/{table}"
        headers = self.headers.copy()
        # Standard Supabase upsert header
        headers["Prefer"] = "return=representation,resolution=merge-duplicates"
        
        if on_conflict:
            url += f"?on_conflict={on_conflict}"
        
        if isinstance(data, dict):
            data = [data]
            
        resp = req.post(url, headers=headers, json=data, timeout=30)
        
        if resp.status_code >= 400:
            logger.error(f"Supabase Upsert Error: {resp.text}")
            resp.raise_for_status()
            
        return resp.json() if resp.status_code != 204 else []

    def update(self, table: str, data: dict, filters: dict) -> list[dict]:
        """UPDATE rows matching filters."""
        url = f"{self.base}/{table}"
        for key, val in filters.items():
            url += f"&{key}={val}" if "?" in url else f"?{key}={val}"
        resp = req.patch(url, headers=self.headers, json=data, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def rpc(self, function_name: str, params: dict = None) -> any:
        """Call a Supabase RPC (stored function)."""
        url = f"{SUPABASE_URL}/rest/v1/rpc/{function_name}"
        resp = req.post(url, headers=self.headers, json=params or {}, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def health_check(self) -> bool:
        """Check if Supabase is reachable."""
        try:
            url = f"{self.base}/stocks?select=count&limit=1"
            headers = self.headers.copy()
            headers["Prefer"] = "count=exact"
            resp = req.head(url, headers=headers, timeout=10)
            return resp.status_code in (200, 206, 416)
        except Exception:
            return False


# Global client instance
db = SupabaseClient()

# =========================
# NEPSE API ENDPOINTS (Free, no API key needed)
# =========================
NEPSE_API_BASE = "https://nepseapi.surajrimal.dev"

NEPSE_ENDPOINTS = {
    "price_volume": f"{NEPSE_API_BASE}/PriceVolume",
    "live_market": f"{NEPSE_API_BASE}/LiveMarket",
    "summary": f"{NEPSE_API_BASE}/Summary",
    "company_list": f"{NEPSE_API_BASE}/CompanyList",
    "top_gainers": f"{NEPSE_API_BASE}/TopGainers",
    "top_losers": f"{NEPSE_API_BASE}/TopLosers",
    "nepse_index": f"{NEPSE_API_BASE}/NepseIndex",
    "supply_demand": f"{NEPSE_API_BASE}/SupplyDemand",
}

# Fallback: ShareSansar web scraping
SHARESANSAR_TODAY_PRICE = "https://www.sharesansar.com/today-share-price"

# =========================
# NEPAL TIMEZONE
# =========================
NPT = timezone(timedelta(hours=5, minutes=45))

def get_nepal_time() -> datetime:
    return datetime.now(NPT)

def get_nepal_date_str() -> str:
    return get_nepal_time().strftime("%Y-%m-%d")

def is_trading_day() -> bool:
    """NEPSE trades: Sunday(6), Monday(0), Tuesday(1), Wednesday(2), Thursday(3)"""
    day = get_nepal_time().weekday()
    return day in [6, 0, 1, 2, 3]

def get_latest_trading_date() -> str:
    """
    Get the date of the latest available market data
    
    CRITICAL LOGIC for Nepal Stock Market (11 AM - 3 PM trading):
    - If current time < 11:00 AM → Today's market hasn't opened yet
                                  → Latest available data is from YESTERDAY
    - If current time >= 11:00 AM → Today's market is open or closed
                                   → Latest available data is from TODAY
    
    Also skips non-trading days (Friday & Saturday)
    
    Examples:
        10:30 AM Thursday → 2026-04-01 (Yesterday)
        11:30 AM Thursday → 2026-04-02 (Today)
        11:00 AM Friday   → 2026-04-02 (Thursday - no trading Friday)
    
    Returns:
        str: Date in format "YYYY-MM-DD"
    """
    MARKET_OPEN_HOUR = 11  # 11:00 AM
    
    nepal_now = get_nepal_time()
    current_hour = nepal_now.hour
    
    # Before 11 AM: use yesterday's date
    if current_hour < MARKET_OPEN_HOUR:
        check_date = nepal_now - timedelta(days=1)
        logger.debug(f"Before market open (11 AM). Using yesterday's data: {check_date.strftime('%Y-%m-%d')}")
    else:
        # After 11 AM: use today's date
        check_date = nepal_now
        logger.debug(f"After market open (11 AM). Using today's data: {check_date.strftime('%Y-%m-%d')}")
    
    # Skip non-trading days (Friday=4, Saturday=5, Sunday=6)
    # Trading days: Monday(0), Tuesday(1), Wednesday(2), Thursday(3), Sunday(6)
    while check_date.weekday() in [4, 5]:  # Friday or Saturday
        logger.debug(f"  {check_date.strftime('%A, %Y-%m-%d')} - Not a trading day, going back")
        check_date = check_date - timedelta(days=1)
    
    return check_date.strftime('%Y-%m-%d')

# =========================
# ML MODEL CONFIG
# =========================
MODEL_VERSION = "rf_alpha_v1"
MIN_HISTORY_DAYS = 60
IDEAL_HISTORY_DAYS = 250
TOP_PICKS_COUNT = 5
FORWARD_DAYS = 5
RF_N_ESTIMATORS = 150
RF_MAX_DEPTH = 12
RF_RANDOM_STATE = 42
RSI_PERIOD = 14
SMA_SHORT_PERIOD = 50
SMA_LONG_PERIOD = 200
EMA_SHORT_PERIOD = 12
EMA_LONG_PERIOD = 26

# =========================
# REQUEST CONFIG
# =========================
REQUEST_TIMEOUT = 30
REQUEST_HEADERS = {
    "User-Agent": "NEPSE-Stock-Analyzer/1.0 (Educational Project)",
    "Accept": "application/json",
}
