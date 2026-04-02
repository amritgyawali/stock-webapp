"""
Advanced NEPSE ML Profit Predictor
Built for 1-Year (250 Days) Alpha Generation targeting Top 5 forward-return stocks.
"""

import warnings
warnings.filterwarnings('ignore')

import time
import numpy as np
import pandas as pd
import json
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import KFold, cross_val_score
from sklearn.preprocessing import StandardScaler

import os
from config import db, logger, get_nepal_date_str

class AdvancedAnalyzer:
    def __init__(self):
        self.today = get_nepal_date_str()
        
    def fetch_data(self, stock_id: int):
        """Fetch ~1 year (250 trading days) of history."""
        rows = db.select(
            "daily_prices", "*",
            {"stock_id": f"eq.{stock_id}"},
            order="date.desc",
            limit=250 + 50  # Extra days for warming up
        )
        if not rows or len(rows) < 80:
            return None
        
        df = pd.DataFrame(rows)
        for col in ["open", "high", "low", "close", "prev_close", "volume", "turnover"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        
        # Ensure prices exist as fallback
        df['high'] = df['high'].fillna(df['close'])
        df['low'] = df['low'].fillna(df['close'])
        df['open'] = df['open'].fillna(df['close'])
                
        return df.sort_values("date").reset_index(drop=True).dropna(subset=["close"])

    def engineer_features(self, df):
        """Advanced technical indicator generation."""
        # Clean Volume
        df['volume'] = df['volume'].fillna(0)
        
        # Indicators
        df['returns'] = df['close'].pct_change().fillna(0)
        
        # ATR (Volatility)
        df['tr'] = np.maximum(df['high'] - df['low'], 
                             np.maximum(np.abs(df['high'] - df['close'].shift()), 
                                        np.abs(df['low'] - df['close'].shift())))
        df['atr'] = df['tr'].rolling(window=14, min_periods=1).mean().ffill()
        df['volatility'] = (df['atr'] / df['close']).fillna(0)
        
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
        
        # Rolling Max (Forward) Target - what we want to predict
        # Max high in next 5 days
        df['target'] = ((df['high'].shift(-5).rolling(window=5, min_periods=1).max() - df['close']) / df['close'] * 100).fillna(0)
        
        features = ['returns', 'volatility', 'macd_hist', 'rsi']
        return df, features

    def analyze_market(self):
        logger.info("Initializing Advanced ML Profit Pipeline...")
        start_time = time.time()
        
        stocks = db.select("stocks", "id,symbol")
        results = []
        
        # Using Random Forest for stability on small/noisy data
        model = RandomForestRegressor(n_estimators=100, max_depth=6, random_state=42)
        
        logger.info(f"Evaluating {len(stocks)} stocks...")
        
        for i, stock in enumerate(stocks):
            if i % 50 == 0:
                logger.info(f"Progress: {i}/{len(stocks)}")
            
            df = self.fetch_data(stock["id"])
            if df is None: continue
            
            df, features = self.engineer_features(df)
            
            # Predictor row (today)
            latest_row = df.iloc[-1:]
            if latest_row[features].isna().any().any(): continue
            
            # Training data (past)
            # Remove the last 5 rows because they don't have a 5-day future target yet
            train_df = df.iloc[:-5].dropna(subset=features + ['target'])
            if len(train_df) < 50: continue
            
            try:
                X = train_df[features].values
                y = train_df['target'].values
                
                model.fit(X, y)
                
                pred_upside = float(model.predict(latest_row[features].values)[0])
                current_price = float(latest_row['close'].iloc[-1])
                
                # Composite score for ranking
                alpha_score = pred_upside / (latest_row['volatility'].iloc[-1] + 0.01)
                
                results.append({
                    "symbol": stock["symbol"],
                    "current_price": current_price,
                    "target_high": current_price * (1 + pred_upside/100),
                    "upside_pct": pred_upside,
                    "alpha_score": alpha_score,
                    "volatility": float(latest_row['volatility'].iloc[-1])
                })
            except Exception as e:
                continue

        # Sort and pick top 5
        results.sort(key=lambda x: x["alpha_score"], reverse=True)
        top_5 = results[:5]
        
        logger.info(f"Execution finished in {time.time() - start_time:.2f}s. Results={len(results)}")
        
        self.save_report(top_5)
        self.save_json(results)
        return top_5

    def save_report(self, top_5):
        with open("advanced_report.md", "w") as f:
            f.write("# TOP 5 NEPSE PROFIT PICKS (AI GRADIENT)\n\n")
            f.write("| Rank | Stock | Price | Target High | Expected Upside |\n")
            f.write("|------|-------|-------|-------------|-----------------|\n")
            for i, s in enumerate(top_5, 1):
                f.write(f"| {i} | **{s['symbol']}** | Rs. {s['current_price']:.2f} | Rs. {s['target_high']:.2f} | +{s['upside_pct']:.2f}% |\n")
        logger.info("Report saved to advanced_report.md")

    def save_json(self, results):
        with open("advanced_results.json", "w") as f:
            json.dump(results, f, indent=4)

if __name__ == "__main__":
    AdvancedAnalyzer().analyze_market()
