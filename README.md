# 📊 NEPSE Stock Analyzer

> AI-powered stock analysis and prediction platform for the Nepal Stock Exchange (NEPSE). Built with Python, Next.js, Supabase, and GitHub Actions.

**100% Free Stack** — No paid APIs, no server costs.

---

## 🚀 Quick Start

### For First-Time Setup (10 minutes)

👉 **See [QUICKSTART.md](QUICKSTART.md)** for step-by-step instructions!

```bash
# 1. Install Python dependencies
cd python
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# 2. Install Node.js dependencies
cd ../web
npm install

# 3. Run data pipeline
python main.py --force

# 4. Start web server
npm run dev
# Open http://localhost:3000
```

### For Daily Operations (5 minutes/day)

```bash
# Check system health
cd python
python system_status.py

# Manual pipeline run (if needed)
python main.py --force

# Start frontend
cd ../web
npm run dev
```

---

## 📚 Documentation

| Document | Purpose | When to Use |
|----------|---------|-------------|
| **[QUICKSTART.md](QUICKSTART.md)** | 10-minute setup guide | First-time setup, quick reference |
| **[SETUP_GUIDE.md](SETUP_GUIDE.md)** | Comprehensive manual | Detailed setup, troubleshooting, deep dive |
| **[SYSTEM_ANALYSIS.md](SYSTEM_ANALYSIS.md)** | Technical analysis | Understanding architecture, optimization |
| **[FINAL_STATUS.md](FINAL_STATUS.md)** | Current status report | Today's system state, action items |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Actions (Daily Cron)               │
│                    8:00 AM NPT, Sun–Thu                      │
│                                                              │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────────┐     │
│  │ Scraper  │──▶│  Technical   │──▶│  ML Predictor    │     │
│  │ (API +   │   │  Indicators  │   │  (Random Forest) │     │
│  │ Fallback)│   │  RSI, SMA,   │   │  Price Prediction│     │
│  └──────────┘   │  EMA, MACD   │   │  + Buy Ranking   │     │
│                  └──────────────┘   └──────────────────┘     │
│                           │                   │              │
│                           ▼                   ▼              │
│                  ┌────────────────────────────────┐          │
│                  │     Supabase (PostgreSQL)      │          │
│                  │  stocks │ daily_prices │ etc.  │          │
│                  └────────────────────────────────┘          │
└─────────────────────────────┬───────────────────────────────┘
                              │
                      ┌───────▼────────┐
                      │  Next.js App   │
                      │  (Vercel)      │
                      │  Dashboard     │
                      └────────────────┘
```

## 📁 Project Structure (Monorepo)

```
stock-webapp/
├── .github/
│   └── workflows/
│       └── daily-stock-update.yml    # GitHub Actions cron job
├── python/
│   ├── config.py                     # Supabase client + constants
│   ├── scraper.py                    # Data fetching (API + fallback)
│   ├── indicators.py                 # RSI, SMA, EMA, MACD, Bollinger
│   ├── predictor.py                  # Random Forest ML model
│   ├── main.py                       # Pipeline orchestrator
│   ├── requirements.txt              # Python dependencies
│   └── .env.example                  # Environment template
├── supabase/
│   └── schema.sql                    # Database schema
├── app/                              # Next.js dashboard (coming soon)
├── .gitignore
└── README.md
```

---

## 🚀 Setup Guide (Step by Step)

### Step 1: Create a Supabase Project (Free)

1. **Go to** [https://supabase.com](https://supabase.com) and click **"Start your project"**
2. **Sign up** with your GitHub account (recommended)
3. Click **"New Project"**
4. Fill in:
   - **Name**: `nepse-analyzer` (or anything you want)
   - **Database Password**: Generate a strong password and **save it somewhere safe**
   - **Region**: Choose the closest to Nepal → **Singapore** or **Mumbai**
   - **Pricing Plan**: **Free** (this is plenty for our use case)
5. Click **"Create new project"** and wait ~2 minutes for it to provision

### Step 2: Run the Database Schema

1. In your Supabase dashboard, click **"SQL Editor"** in the left sidebar
2. Click **"New Query"**
3. **Copy the entire contents** of `supabase/schema.sql` and paste it into the editor
4. Click **"Run"** (or press Ctrl+Enter)
5. You should see: `Success. No rows returned` — this means all tables were created!

**Verify**: Click on **"Table Editor"** in the sidebar. You should see these 5 tables:
- `stocks`
- `daily_prices`
- `predictions`
- `model_accuracy`
- `market_summary`

### Step 3: Get Your Supabase Keys

1. In Supabase dashboard, go to **Settings** → **API**
2. You need TWO values:
   - **Project URL**: `https://xxxxx.supabase.co` — copy this
   - **service_role key** (under "Project API keys"): This is the **secret** key → copy this

> ⚠️ **IMPORTANT**: The `service_role` key bypasses Row Level Security. Never expose it in frontend code. It's only used in the Python script (server-side).

### Step 4: Create a GitHub Repository

1. Go to [https://github.com/new](https://github.com/new)
2. Fill in:
   - **Repository name**: `nepse-stock-analyzer` (or your preference)
   - **Description**: `AI-powered NEPSE stock analysis and predictions`
   - **Visibility**: **Public** (required for free GitHub Actions) or Private (2000 min/month free)
   - **DO NOT** check "Add a README" (we already have one)
3. Click **"Create repository"**

### Step 5: Push Code to GitHub

Open your terminal in the `stock-webapp` folder and run:

```bash
# Initialize git
git init

# Add all files
git add .

# First commit
git commit -m "🚀 Initial: Python scraper + ML model + GitHub Actions"

# Connect to your GitHub repo (replace with YOUR URL)
git remote add origin https://github.com/YOUR_USERNAME/nepse-stock-analyzer.git

# Push
git branch -M main
git push -u origin main
```

### Step 6: Add Secrets to GitHub

1. Go to your GitHub repository page
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"** and add:

| Secret Name | Value |
|---|---|
| `SUPABASE_URL` | `https://xxxxx.supabase.co` (your Project URL) |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGci...` (your service_role key) |

### Step 7: Test the Pipeline

1. Go to your GitHub repo → **Actions** tab
2. Click on **"📊 Daily NEPSE Stock Analysis"** in the left sidebar
3. Click **"Run workflow"** dropdown
4. Set **"Dry run"** to `true` for the first test
5. Click **"Run workflow"**
6. Watch the logs — you should see API responses!

Once dry run works:
1. Run again with Dry run = `false` and Force run = `true`
2. Check your Supabase **Table Editor** → you should see data in all tables!

### Step 8: Automatic Daily Runs

The GitHub Actions cron is already configured to run at **8:00 AM NPT every Sunday–Thursday**. No further setup needed! 🎉

---

## 🧪 Local Development

To run the Python script locally:

```bash
cd python

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
# Edit .env and add your Supabase URL and service_role key

# Test API connectivity (no DB writes)
python main.py --dry-run

# Full run (writes to DB)
python main.py --force

# Run on non-trading days too
python main.py --force
```

---

## 🤖 ML Model Details

### Algorithm
- **Random Forest Regressor** (100 trees, max_depth=10)
- Trained per-stock on historical data (up to 200 days)

### Features (18 total)
| Feature | Description |
|---|---|
| `close` | Current closing price |
| `volume` | Trading volume |
| `change_pct` | Daily price change % |
| `high_low_spread` | (High - Low) / Close as % |
| `close_open_spread` | (Close - Open) / Close as % |
| `rsi_14` | 14-day Relative Strength Index |
| `sma_50` | 50-day Simple Moving Average |
| `sma_200` | 200-day Simple Moving Average |
| `ema_12` | 12-day Exponential Moving Average |
| `ema_26` | 26-day Exponential Moving Average |
| `price_vs_sma50` | % deviation from SMA-50 |
| `price_vs_sma200` | % deviation from SMA-200 |
| `volume_sma_ratio` | Volume relative to 20-day avg |
| `macd` | MACD line value |
| `macd_signal` | MACD signal line |
| `bb_position` | Position within Bollinger Bands (0-1) |
| `momentum_5` | 5-day price momentum % |
| `momentum_10` | 10-day price momentum % |

### Buy Score (Composite Ranking)
| Factor | Weight | Criteria |
|---|---|---|
| Predicted Upside | 30% | Higher predicted price vs current |
| RSI Oversold | 20% | RSI < 30 = strong buy signal |
| Value Play | 15% | Price below SMA-200 |
| Volume Spike | 15% | High relative volume |
| Confidence | 10% | Model cross-validation R² |
| MACD Signal | 10% | Bullish MACD crossover |

---

## ⚠️ Disclaimer

> This project is for **educational purposes only**. It is NOT financial advice. Stock predictions are inherently unreliable. Always do your own research before investing. The developers are not responsible for any financial losses.

---

## 📝 License

MIT License — Free for personal and educational use.
#   s t o c k - w e b a p p  
 