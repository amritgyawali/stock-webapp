"""
NEPSE Stock Analysis — ML Predictor (Alpha V2.2 Optimized)
Random Forest model for 5-day profit maximization with 1-year training depth.
Optimized for high-speed market-wide scans (~10-15 mins total).
"""

import json
import time
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from config import (
    logger,
    db,
    MODEL_VERSION,
    MIN_HISTORY_DAYS,
    IDEAL_HISTORY_DAYS,
    TOP_PICKS_COUNT,
    RF_N_ESTIMATORS,
    RF_MAX_DEPTH,
    RF_RANDOM_STATE,
    get_nepal_date_str,
)
from indicators import TechnicalIndicators


class StockPredictor:
    """Advanced ML-based stock price predictor targeting 5-day profit peaks."""

    FEATURE_COLUMNS = [
        "returns", "volatility", "macd_hist", "rsi", "bb_width", "obv_divergence"
    ]

    def __init__(self):
        self.today = get_nepal_date_str()
        from config import FORWARD_DAYS
        self.forward_days = FORWARD_DAYS
        self.indicator_calc = TechnicalIndicators()

    def run_predictions(self, resume: bool = True) -> int:
        """Run predictions for all active stocks with batching and resume support."""
        logger.info(f"🤖 Running Optimized Alpha Predictions (Model: {MODEL_VERSION})...")
        start_time = time.time()

        stocks = db.select("stocks", "id,symbol")
        if not stocks:
            logger.warning("No stocks found in database.")
            return 0

        # Resume logic: Get existing predictions for today
        existing_ids = set()
        if resume:
            existing = db.select("predictions", "stock_id", {
                "prediction_date": f"eq.{self.today}",
                "model_version": f"eq.{MODEL_VERSION}"
            })
            existing_ids = {item["stock_id"] for item in existing}
            if existing_ids:
                logger.info(f"⏭️ Resuming: Skipping {len(existing_ids)} already predicted stocks.")

        predictions = []
        batch_buffer = []
        processed_count = 0

        for i, stock in enumerate(stocks):
            if stock["id"] in existing_ids:
                continue

            stock_start = time.time()
            try:
                prediction = self._predict_stock(stock["id"], stock["symbol"])
                if prediction:
                    predictions.append(prediction)
                    batch_buffer.append({k: v for k, v in prediction.items() if k != "symbol"})
                    
                    # Batch Upsert every 50 stocks
                    if len(batch_buffer) >= 50:
                        db.upsert("predictions", batch_buffer, on_conflict="stock_id,prediction_date")
                        batch_buffer = []
                        logger.info(f"💾 Batched 50 predictions to database.")

                processed_count += 1
                if i % 20 == 0:
                    elapsed = time.time() - start_time
                    avg_time = elapsed / max(1, i - len(existing_ids))
                    eta_min = (avg_time * (len(stocks) - i)) / 60
                    logger.info(f"📊 Progress: {i}/{len(stocks)} | Speed: {avg_time:.2f}s/stock | ETA: {eta_min:.1f}m")

            except Exception as e:
                logger.debug(f"Error predicting {stock['symbol']}: {e}")

        # Final Batch Store
        if batch_buffer:
            db.upsert("predictions", batch_buffer, on_conflict="stock_id,prediction_date")

        if not predictions and not existing_ids:
            logger.warning("No predictions generated.")
            return 0

        # Final Rank & Store for Top 5 (Full set ranking)
        all_today_preds = db.select("predictions", "*", {
            "prediction_date": f"eq.{self.today}",
            "model_version": f"eq.{MODEL_VERSION}"
        })
        
        # Add symbols for logging
        symbol_map = {s["id"]: s["symbol"] for s in stocks}
        for p in all_today_preds:
            p["symbol"] = symbol_map.get(p["stock_id"], "Unknown")

        ranked = self._rank_stocks(all_today_preds)
        stored = self._store_predictions(ranked)
        
        total_time = (time.time() - start_time) / 60
        logger.info(f"✅ Full Analysis Complete in {total_time:.2f} minutes.")
        return stored

    def _predict_stock(self, stock_id: int, symbol: str) -> Optional[dict]:
        """Build features and predict 5-day max upside for a single stock."""
        rows = db.select(
            "daily_prices", "*",
            {"stock_id": f"eq.{stock_id}"},
            order="date.desc",
            limit=IDEAL_HISTORY_DAYS + 50,
        )

        if not rows or len(rows) < MIN_HISTORY_DAYS:
            return None

        df = pd.DataFrame(rows)
        for col in ["open", "high", "low", "close", "volume"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        df = df.sort_values("date").reset_index(drop=True).dropna(subset=["close"])
        
        df['high'] = df['high'].fillna(df['close'])
        df['low'] = df['low'].fillna(df['close'])
        df['open'] = df['open'].fillna(df['close'])
        df['volume'] = df['volume'].fillna(0)

        df['returns'] = df['close'].pct_change().fillna(0)
        
        # Volatility
        tr = np.maximum(df['high'] - df['low'], 
                         np.maximum(np.abs(df['high'] - df['close'].shift()), 
                                    np.abs(df['low'] - df['close'].shift())))
        df['atr'] = tr.rolling(window=14, min_periods=1).mean().ffill()
        df['volatility'] = (df['atr'] / (df['close'] + 1e-9)).fillna(0)
        
        # MACD
        ema12 = df['close'].ewm(span=12, adjust=False).mean()
        ema26 = df['close'].ewm(span=26, adjust=False).mean()
        macd = ema12 - ema26
        signal = macd.ewm(span=9, adjust=False).mean()
        df['macd_hist'] = macd - signal
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        rs = gain / (loss + 1e-9)
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # OBV
        obv = [0.0]
        for i in range(1, len(df)):
            if df['close'].iloc[i] > df['close'].iloc[i-1]:
                obv.append(obv[-1] + float(df['volume'].iloc[i]))
            elif df['close'].iloc[i] < df['close'].iloc[i-1]:
                obv.append(obv[-1] - float(df['volume'].iloc[i]))
            else:
                obv.append(obv[-1])
        df['obv'] = obv
        obv_sma = df['obv'].rolling(window=20, min_periods=1).mean()
        df['obv_divergence'] = np.where(np.abs(obv_sma) > 0, (df['obv'] - obv_sma) / np.abs(obv_sma), 0)
        
        sma_20 = df['close'].rolling(window=20, min_periods=1).mean()
        std_20 = df['close'].rolling(window=20, min_periods=1).std()
        df['bb_width'] = (std_20 * 4) / (sma_20 + 1e-9)

        # Target: Max high in next N days
        df['target'] = ((df['high'].shift(-self.forward_days).rolling(window=self.forward_days, min_periods=1).max() - df['close']) / df['close'] * 100).fillna(0)
        
        features = self.FEATURE_COLUMNS
        available_features = [c for c in features if c in df.columns]
        
        train_df = df.iloc[:-self.forward_days].dropna(subset=available_features + ['target'])
        if len(train_df) < MIN_HISTORY_DAYS:
            return None

        X = train_df[available_features].values
        y = train_df['target'].values

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = RandomForestRegressor(
            n_estimators=RF_N_ESTIMATORS,
            max_depth=RF_MAX_DEPTH,
            random_state=RF_RANDOM_STATE,
            n_jobs=-1,
        )
        model.fit(X_scaled, y)

        latest_row = df.dropna(subset=available_features).iloc[-1:]
        if len(latest_row) == 0:
            return None
            
        latest_features = latest_row[available_features].values
        latest_scaled = scaler.transform(latest_features)
        
        pred_upside = float(model.predict(latest_scaled)[0])
        current_price = float(latest_row['close'].iloc[-1])
        predicted_high = round(current_price * (1 + pred_upside/100), 2)

        # Fast Confidence Score (Train R2)
        confidence = max(0.01, min(0.99, float(model.score(X_scaled, y))))

        volatility = float(latest_row['volatility'].iloc[-1])
        alpha_score = (pred_upside * confidence) / (volatility + 0.001)

        return {
            "stock_id": stock_id,
            "symbol": symbol,
            "prediction_date": self.today,
            "predicted_close": predicted_high,
            "current_price": current_price,
            "predicted_change_pct": round(pred_upside, 4),
            "confidence_score": confidence,
            "buy_score": alpha_score,
            "model_version": MODEL_VERSION,
            "features_used": json.dumps({col: float(latest_row[col].iloc[-1]) for col in available_features}),
        }

    def _rank_stocks(self, predictions: list[dict]) -> list[dict]:
        """Rank by buy_score (Alpha Score), assign top-5."""
        predictions.sort(key=lambda x: x.get("buy_score", 0), reverse=True)
        for i, pred in enumerate(predictions):
            pred["buy_rank"] = i + 1 if i < TOP_PICKS_COUNT else None
        top_symbols = [p["symbol"] for p in predictions[:TOP_PICKS_COUNT]]
        logger.info(f"🏆 Top {TOP_PICKS_COUNT} picks: {top_symbols}")
        return predictions

    def _store_predictions(self, predictions: list[dict]) -> int:
        """Batch store final ranked predictions."""
        records = [{k: v for k, v in pred.items() if k != "symbol"} for pred in predictions]
        try:
            db.upsert("predictions", records, on_conflict="stock_id,prediction_date")
            return len(records)
        except Exception as e:
            logger.error(f"Error storing predictions: {e}")
            return 0

if __name__ == "__main__":
    predictor = StockPredictor()
    predictor.run_predictions(resume=True)
