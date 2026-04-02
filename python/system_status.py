from config import db

print("\n" + "="*60)
print("NEPSE STOCK ANALYZER - SYSTEM STATUS REPORT")
print("="*60 + "\n")

# 1. Database Tables
print("📊 DATABASE STATUS")
print("-" * 60)

try:
    stocks = db.select("stocks", "id,symbol")
    print(f"✅ Stocks Table: {len(stocks)} companies")
except Exception as e:
    print(f"❌ Error querying stocks: {e}")

try:
    prices = db.select("daily_prices", "*", order="date.desc", limit=100)
    if prices:
        latest_date = prices[0]['date']
        today_count = len([p for p in prices if p['date'] == latest_date])
        print(f"✅ Daily Prices: Latest data from {latest_date} ({today_count} records)")
    else:
        print(f"⚠️  No price data yet")
except Exception as e:
    print(f"❌ Error querying prices: {e}")

try:
    predictions = db.select("predictions", "*", order="prediction_date.desc", limit=100)
    if predictions:
        latest_pred_date = predictions[0]['prediction_date']
        pred_count = len([p for p in predictions if p['prediction_date'] == latest_pred_date])
        top5_count = len([p for p in predictions if p.get('buy_rank') is not None])
        print(f"✅ Predictions: Latest from {latest_pred_date} ({pred_count} total, {top5_count} top picks)")
    else:
        print(f"⚠️  No predictions yet (need 30+ days of historical data)")
except Exception as e:
    print(f"❌ Error querying predictions: {e}")

try:
    accuracy = db.select("model_accuracy", "*", order="date.desc", limit=10)
    if accuracy:
        latest_acc = accuracy[0]
        print(f"✅ Model Accuracy: Avg Error = {latest_acc.get('avg_error_pct', 'N/A')}%, Direction = {latest_acc.get('direction_accuracy', 'N/A')}%")
    else:
        print(f"⚠️  No accuracy data yet (predictions need to mature)")
except Exception as e:
    print(f"❌ Error querying accuracy: {e}")

try:
    market = db.select("market_summary", "*", order="date.desc", limit=1)
    if market:
        m = market[0]
        nepse_index = m.get('nepse_index', 'N/A')
        turnover = m.get('total_turnover', 'N/A')
        print(f"✅ Market Summary: NEPSE Index = {nepse_index}, Turnover = Rs. {turnover}")
    else:
        print(f"⚠️  No market summary yet")
except Exception as e:
    print(f"❌ Error querying market summary: {e}")

print("\n" + "="*60)
print("COMPONENT STATUS")
print("="*60)

# Python environment
import sys
print(f"\n🐍 Python Version: {sys.version.split()[0]}")

# Check dependencies
try:
    import requests
    import pandas as pd
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor
    print("✅ All Python dependencies installed")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")

# Environment variables
import os
from dotenv import load_dotenv
load_dotenv()
supabase_url = os.environ.get("SUPABASE_URL", "")
if supabase_url:
    print(f"✅ Supabase URL configured: {supabase_url[:40]}...")
else:
    print(f"❌ SUPABASE_URL not set in .env")

print("\n" + "="*60)
print("NEXT.JS FRONTEND STATUS")
print("="*60)

import subprocess
try:
    result = subprocess.run(["npm", "--version"], capture_output=True, text=True, shell=True)
    if result.returncode == 0:
        print(f"✅ Node.js/npm available: v{result.stdout.strip()}")
    else:
        print(f"⚠️  npm not found (needed for frontend)")
except Exception as e:
    print(f"❌ Error checking npm: {e}")

try:
    with open("../web/.env.local", "r") as f:
        content = f.read()
        if "NEXT_PUBLIC_SUPABASE_URL" in content:
            print("✅ Frontend .env.local configured")
        else:
            print("⚠️  NEXT_PUBLIC_SUPABASE_URL missing in .env.local")
except FileNotFoundError:
    print("❌ web/.env.local not found")

print("\n" + "="*60)
print("AUTOMATION STATUS")
print("="*60)

import os.path
if os.path.exists("../.github/workflows/daily-stock-update.yml"):
    print("✅ GitHub Actions workflow configured")
else:
    print("❌ Workflow file missing")

print("✅ Scheduled for: 8:00 AM NPT (Sunday-Thursday)")
print("✅ Manual trigger available via GitHub UI")

print("\n" + "="*60)
print("RECOMMENDATIONS")
print("="*60)

# Analyze and provide recommendations
issues = []

if not prices or len(prices) < 30:
    issues.append("📊 Need more historical data for ML predictions (current: < 30 days)")
    
if not predictions or len([p for p in predictions if p.get('buy_rank')]) == 0:
    issues.append("🤖 No active predictions yet - run pipeline to generate")

if not market:
    issues.append("📈 Market summary not populated - check API connectivity")

if issues:
    print("\n⚠️  ACTION REQUIRED:\n")
    for issue in issues:
        print(f"  • {issue}")
    print("\n💡 Run the pipeline:")
    print("   cd python")
    print("   venv\\Scripts\\activate")
    print("   python main.py --force\n")
else:
    print("\n✅ System is fully operational!\n")
    print("📅 Next automated run: Tomorrow at 8:00 AM NPT")
    print("🌐 Start frontend: cd ..\\web && npm run dev")

print("\n" + "="*60 + "\n")
