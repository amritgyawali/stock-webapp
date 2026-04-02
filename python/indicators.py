"""
NEPSE Stock Analysis — Technical Indicators
Calculates RSI, SMA, EMA from historical price data.
"""

import pandas as pd
import numpy as np
from typing import Optional

from config import (
    logger,
    db,
    RSI_PERIOD,
    SMA_SHORT_PERIOD,
    SMA_LONG_PERIOD,
    EMA_SHORT_PERIOD,
    EMA_LONG_PERIOD,
    get_nepal_date_str,
)


class TechnicalIndicators:
    """Calculates and stores technical indicators for all active stocks."""

    def __init__(self):
        self.today = get_nepal_date_str()

    def calculate_all_indicators(self) -> int:
        """Calculate RSI, SMA, EMA for all active stocks and update daily_prices."""
        logger.info("🧮 Calculating technical indicators...")

        stocks = db.select("stocks", "id,symbol", {"is_active": "eq.true"})
        if not stocks:
            logger.warning("No active stocks found.")
            return 0

        updated = 0
        for stock in stocks:
            stock_id = stock["id"]
            symbol = stock["symbol"]
            try:
                indicators = self._calculate_for_stock(stock_id)
                if indicators:
                    self._update_daily_price(stock_id, indicators)
                    updated += 1
            except Exception as e:
                logger.error(f"Error calculating indicators for {symbol}: {e}")

        logger.info(f"✅ Updated indicators for {updated}/{len(stocks)} stocks")
        return updated

    def _calculate_for_stock(self, stock_id: int) -> Optional[dict]:
        """Calculate all indicators for a single stock."""
        rows = db.select(
            "daily_prices",
            "date,close,high,low,volume",
            {"stock_id": f"eq.{stock_id}"},
            order="date.desc",
            limit=SMA_LONG_PERIOD + 50,
        )

        if not rows or len(rows) < 2:
            return None

        df = pd.DataFrame(rows)
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["high"] = pd.to_numeric(df["high"], errors="coerce")
        df["low"] = pd.to_numeric(df["low"], errors="coerce")
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
        df = df.sort_values("date").reset_index(drop=True)
        df = df.dropna(subset=["close"])

        if len(df) < 2:
            return None

        closes = df["close"]
        indicators = {}

        if len(closes) >= RSI_PERIOD + 1:
            indicators["rsi_14"] = self._compute_rsi(closes, RSI_PERIOD)
        if len(closes) >= SMA_SHORT_PERIOD:
            indicators["sma_50"] = round(float(closes.tail(SMA_SHORT_PERIOD).mean()), 2)
        if len(closes) >= SMA_LONG_PERIOD:
            indicators["sma_200"] = round(float(closes.tail(SMA_LONG_PERIOD).mean()), 2)
        if len(closes) >= EMA_SHORT_PERIOD:
            indicators["ema_12"] = round(float(closes.ewm(span=EMA_SHORT_PERIOD, adjust=False).mean().iloc[-1]), 2)
        if len(closes) >= EMA_LONG_PERIOD:
            indicators["ema_26"] = round(float(closes.ewm(span=EMA_LONG_PERIOD, adjust=False).mean().iloc[-1]), 2)

        return indicators if indicators else None

    def _update_daily_price(self, stock_id: int, indicators: dict):
        """Update today's daily_prices record with indicator values."""
        try:
            db.update("daily_prices", indicators, {
                "stock_id": f"eq.{stock_id}",
                "date": f"eq.{self.today}",
            })
        except Exception as e:
            logger.error(f"Error updating indicators for stock_id={stock_id}: {e}")

    # ─────────────────────────────────────────────
    # STATIC INDICATOR CALCULATIONS
    # ─────────────────────────────────────────────

    @staticmethod
    def _compute_rsi(closes: pd.Series, period: int = 14) -> float:
        """Compute RSI using Exponential Moving Average method (Wilder's smoothing)."""
        delta = closes.diff()
        gains = delta.where(delta > 0, 0.0)
        losses = (-delta).where(delta < 0, 0.0)
        avg_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return round(float(rsi.iloc[-1]), 4)

    @staticmethod
    def compute_rsi_series(closes: pd.Series, period: int = 14) -> pd.Series:
        """Compute RSI as a full series."""
        delta = closes.diff()
        gains = delta.where(delta > 0, 0.0)
        losses = (-delta).where(delta < 0, 0.0)
        avg_gain = gains.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = losses.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def compute_sma_series(closes: pd.Series, period: int) -> pd.Series:
        return closes.rolling(window=period, min_periods=period).mean()

    @staticmethod
    def compute_ema_series(closes: pd.Series, period: int) -> pd.Series:
        return closes.ewm(span=period, adjust=False).mean()

    @staticmethod
    def compute_macd(closes: pd.Series) -> tuple[pd.Series, pd.Series]:
        """Returns (macd_line, signal_line)."""
        ema_12 = closes.ewm(span=12, adjust=False).mean()
        ema_26 = closes.ewm(span=26, adjust=False).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        return macd_line, signal_line

    @staticmethod
    def compute_bollinger_bands(closes: pd.Series, period: int = 20, std_dev: float = 2.0):
        """Returns (upper_band, middle_band, lower_band)."""
        middle = closes.rolling(window=period).mean()
        std = closes.rolling(window=period).std()
        upper = middle + (std_dev * std)
        lower = middle - (std_dev * std)
        return upper, middle, lower
