"""
Targeted single-stock predictor debug — skips the full 337-stock loop.
Runs on NABIL (or first stock found) with full verbose output.
"""
import logging
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", stream=sys.stdout)
logger = logging.getLogger("debug-predictor")

from config import db, MIN_HISTORY_DAYS, IDEAL_HISTORY_DAYS, get_nepal_date_str
from indicators import TechnicalIndicators

indicator_calc = TechnicalIndicators()
today = get_nepal_date_str()

FEATURE_COLUMNS = [
    "close", "volume", "change_pct",
    "high_low_spread", "close_open_spread",
    "rsi_14", "sma_50", "sma_200", "ema_12", "ema_26",
    "price_vs_sma50", "price_vs_sma200",
    "volume_sma_ratio",
    "macd", "macd_signal", "bb_position",
    "momentum_5", "momentum_10",
]

# Pick a stock known to have data
stock = db.select("stocks", "id,symbol", {"is_active": "eq.true"}, limit=1)[0]
stock_id, symbol = stock["id"], stock["symbol"]
logger.info(f"Testing on stock: {symbol} (id={stock_id})")

rows = db.select(
    "daily_prices", "*",
    {"stock_id": f"eq.{stock_id}"},
    order="date.desc",
    limit=IDEAL_HISTORY_DAYS + 50,
)
logger.info(f"Fetched {len(rows)} rows from DB (min needed: {MIN_HISTORY_DAYS})")

if not rows or len(rows) < MIN_HISTORY_DAYS:
    logger.error(f"Not enough data: {len(rows)} rows")
    sys.exit(1)

df = pd.DataFrame(rows)
logger.info(f"DataFrame columns: {df.columns.tolist()}")
logger.info(f"First row sample: {df.iloc[0].to_dict()}")

for col in ["open", "high", "low", "close", "prev_close", "volume",
             "turnover", "change_pct", "rsi_14", "sma_50", "sma_200", "ema_12", "ema_26"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.sort_values("date").reset_index(drop=True).dropna(subset=["close"])
logger.info(f"After close-dropna: {len(df)} rows. Date range: {df['date'].min()} to {df['date'].max()}")

closes = df["close"]
df["high_low_spread"] = ((df.get("high", closes) - df.get("low", closes)) / closes * 100).fillna(0)
df["close_open_spread"] = ((closes - df.get("open", closes)) / closes * 100).fillna(0)
df["rsi_14"] = indicator_calc.compute_rsi_series(closes, 14)
df["sma_50"] = indicator_calc.compute_sma_series(closes, 50)
df["sma_200"] = indicator_calc.compute_sma_series(closes, 200)
df["ema_12"] = indicator_calc.compute_ema_series(closes, 12)
df["ema_26"] = indicator_calc.compute_ema_series(closes, 26)
df["price_vs_sma50"] = np.where(df["sma_50"] > 0, (closes - df["sma_50"]) / df["sma_50"] * 100, 0)
df["price_vs_sma200"] = np.where(df["sma_200"] > 0, (closes - df["sma_200"]) / df["sma_200"] * 100, 0)
vol_sma = df["volume"].rolling(window=20, min_periods=5).mean() if "volume" in df.columns else pd.Series(1, index=df.index)
df["volume_sma_ratio"] = np.where(vol_sma > 0, df.get("volume", 1) / vol_sma, 1.0)
macd_line, signal_line = indicator_calc.compute_macd(closes)
df["macd"] = macd_line
df["macd_signal"] = signal_line
upper, middle, lower = indicator_calc.compute_bollinger_bands(closes)
bb_range = upper - lower
df["bb_position"] = np.where(bb_range > 0, (closes - lower) / bb_range, 0.5)
df["momentum_5"] = closes.pct_change(periods=5) * 100
df["momentum_10"] = closes.pct_change(periods=10) * 100
if "change_pct" not in df.columns or df["change_pct"].isna().all():
    df["change_pct"] = closes.pct_change() * 100

available_features = [c for c in FEATURE_COLUMNS if c in df.columns]
logger.info(f"Available features: {available_features}")
df_trimmed = df.dropna(subset=available_features)
logger.info(f"After feature dropna: {len(df_trimmed)} rows (min needed: {MIN_HISTORY_DAYS})")

df_trimmed["target"] = df_trimmed["close"].shift(-1)
train_df = df_trimmed.dropna(subset=["target"])
logger.info(f"Train rows: {len(train_df)}")

if len(train_df) >= MIN_HISTORY_DAYS:
    logger.info("✅ Stock has enough data to generate a prediction.")
else:
    logger.error(f"❌ Not enough training rows after all filters: {len(train_df)} < {MIN_HISTORY_DAYS}")
