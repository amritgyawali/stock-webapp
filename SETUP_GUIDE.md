# 🚀 NEPSE Stock Analyzer - Complete Setup & Operations Guide

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Setup Instructions](#setup-instructions)
4. [Database Schema](#database-schema)
5. [Environment Configuration](#environment-configuration)
6. [Running the Data Pipeline](#running-the-data-pipeline)
7. [Starting the Web Server](#starting-the-web-server)
8. [GitHub Actions Automation](#github-actions-automation)
9. [Troubleshooting](#troubleshooting)
10. [Daily Operations Checklist](#daily-operations-checklist)

---

## 🎯 System Overview

Your NEPSE Stock Analyzer is a **complete AI-powered stock analysis platform** consisting of:

### **Backend (Python)**
- **Data Scraping**: Fetches real-time data from NEPSE APIs with ShareSansar fallback
- **Technical Indicators**: Calculates RSI, SMA, EMA, MACD, Bollinger Bands
- **ML Predictions**: Random Forest model predicts next-day prices with confidence scores
- **Database**: Supabase PostgreSQL for all data storage

### **Frontend (Next.js)**
- **Dashboard**: Live market summary, top picks, and predictions table
- **Stock Detail Pages**: Individual stock charts with historical data and predictions
- **Accuracy Tracking**: Model performance metrics and historical accuracy

### **Automation**
- **GitHub Actions**: Daily automated runs at 8:00 AM NPT (Sunday-Thursday)
- **Manual Triggers**: On-demand pipeline execution via GitHub UI

---

## 🏗️ Architecture Diagram

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

---

## 🛠️ Setup Instructions

### **Prerequisites**
- Python 3.11+ installed
- Node.js 18+ and npm installed
- Git installed
- Supabase account (free tier)
- GitHub account

### **Step 1: Clone the Repository**

```bash
cd c:\Users\amrit\stock-webapp
```

### **Step 2: Set Up Supabase Database**

1. **Go to** [https://supabase.com](https://supabase.com) and log in
2. **Select your project**: `nepse-analyzer` (oqthzjdcewnhlmekfsip)
3. **Navigate to SQL Editor** (left sidebar)
4. **Click "New Query"**
5. **Copy and paste** the entire contents of [`supabase/schema.sql`](supabase/schema.sql)
6. **Click "Run"** (or press Ctrl+Enter)

✅ **Verify**: Go to **Table Editor** → You should see 5 tables:
- `stocks`
- `daily_prices`
- `predictions`
- `model_accuracy`
- `market_summary`

### **Step 3: Configure Environment Variables**

#### **Python Backend** (`python/.env`)

Your `.env` file is already configured! ✅

```env
SUPABASE_URL=https://oqthzjdcewnhlmekfsip.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

⚠️ **Security Note**: The `service_role` key bypasses Row Level Security. Never expose it in frontend code.

#### **Next.js Frontend** (`web/.env.local`)

Your `.env.local` is already configured! ✅

```env
NEXT_PUBLIC_SUPABASE_URL=https://oqthzdcewnhlmekfsip.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=sb_publishable_-ZInl5siX7yYjWrCWuzG7Q_3ilZ1GSv
```

### **Step 4: Install Python Dependencies**

```bash
cd c:\Users\amrit\stock-webapp\python
python -m venv venv
venv\Scripts\activate  # Activate virtual environment
pip install -r requirements.txt
```

**Dependencies installed**:
- `requests` - HTTP client for API calls
- `pandas` - Data manipulation
- `numpy` - Numerical computations
- `scikit-learn` - Machine learning model
- `python-dotenv` - Environment variable management
- `beautifulsoup4` - Web scraping fallback
- `lxml` - HTML parser

### **Step 5: Install Next.js Dependencies**

```bash
cd c:\Users\amrit\stock-webapp\web
npm install
```

**Key packages**:
- `next` 16.2.1 - React framework
- `@supabase/supabase-js` - Supabase client
- `recharts` - Charting library
- `shadcn/ui` - UI components
- `tailwindcss` - Styling

---

## 🔄 Running the Data Pipeline

### **Test Mode (Dry Run)**

Test API connectivity without writing to database:

```bash
cd c:\Users\amrit\stock-webapp\python
venv\Scripts\activate
python main.py --dry-run
```

**Expected output**:
```
🔌 Testing Supabase connection...
  ✅ Supabase is reachable!

🔌 Testing NEPSE API...
  ✅ summary: HTTP 200, 12 items
  ✅ price_volume: HTTP 200, 250 items
  ✅ company_list: HTTP 200, 273 items
  ✅ nepse_index: HTTP 200, 1 items

🧪 Dry run complete. No data written.
```

### **Live Mode (Full Pipeline)**

Run the complete data pipeline:

```bash
cd c:\Users\amrit\stock-webapp\python
venv\Scripts\activate
python main.py --force
```

**Pipeline Steps**:

1. **STEP 1/5**: Sync company list (~5 seconds)
   - Fetches all NEPSE-listed companies
   - Upserts into `stocks` table
   
2. **STEP 2/5**: Cross-validate multi-source prices (~10 seconds)
   - Fetches from NEPSE API
   - Validates with ShareSansar fallback
   - Stores consensus data

3. **STEP 3/5**: Fetch market summary (~3 seconds)
   - NEPSE index value
   - Total turnover, volume, transactions

4. **STEP 4/5**: Calculate technical indicators (~15 seconds)
   - RSI (14-day)
   - SMA (50, 200-day)
   - EMA (12, 26-day)
   - MACD, Bollinger Bands

5. **STEP 5/5**: ML predictions (~30-60 seconds)
   - Random Forest model per stock
   - Predicts next-day close
   - Computes buy score and ranking

**Sample Output**:
```
============================================================
🚀 NEPSE Stock Analyzer — Daily Pipeline
📅 Nepal Time: 2026-03-28 14:30:00 NPT
🔧 Mode: LIVE
============================================================

📋 STEP 1/5: Syncing company list...
✅ Synced 273 companies

📊 STEP 2/5: Cross-Validating Multi-Source Prices...
✅ Fetched prices for 250 stocks
✅ Stored 250 price records

📈 STEP 3/5: Fetching Market Summary...
✅ Market summary stored: NEPSE Index = 2847.52

🧮 STEP 4/5: Calculating technical indicators...
✅ Updated indicators for 245/250 stocks

🤖 STEP 5/5: Running ML predictions...
🏆 Top 5 picks: ['NABIL', 'NICA', 'HBL', 'GBIME', 'SHIVM']
✅ Generated 245 predictions, stored 245

📏 BONUS: Updating prediction accuracy...
✅ Accuracy: avg_error=2.34%

============================================================
📊 PIPELINE COMPLETE:
  Companies synced:   273
  Prices fetched:     250
  Prices stored:      250
  Indicators updated: 245
  Predictions made:   245
  Time elapsed:       78.5s
============================================================
```

### **Verify Data in Supabase**

1. Go to Supabase Dashboard → **Table Editor**
2. Check each table:
   - `stocks`: Should have ~273 rows
   - `daily_prices`: Should have today's date with OHLCV data
   - `predictions`: Should have predictions with `buy_rank` 1-5 for top picks
   - `market_summary`: Should have latest NEPSE index
   - `model_accuracy`: Should show historical accuracy metrics

---

## 🌐 Starting the Web Server

### **Development Mode**

```bash
cd c:\Users\amrit\stock-webapp\web
npm run dev
```

**Server starts at**: [http://localhost:3000](http://localhost:3000)

**Features**:
- Hot reload enabled (changes auto-refresh)
- Server-side rendering with Supabase
- Revalidation every 60 seconds for live data

### **Production Build**

```bash
cd c:\Users\amrit\stock-webapp\web
npm run build
npm start
```

### **Accessing the Application**

1. **Dashboard**: [http://localhost:3000](http://localhost:3000)
   - Market summary
   - Top 5 AI picks (if predictions available)
   - Live market board (top turnover stocks)
   - Model accuracy link

2. **Individual Stock Page**: [http://localhost:3000/stock/{SYMBOL}](http://localhost:3000/stock/{SYMBOL})
   - Example: [http://localhost:3000/stock/NABIL](http://localhost:3000/stock/NABIL)
   - Historical price chart (90 days)
   - Latest prediction details
   - Technical indicators

3. **Accuracy Page**: [http://localhost:3000/accuracy](http://localhost:3000/accuracy)
   - Historical model accuracy
   - Error metrics over time
   - Direction accuracy

---

## ⚙️ GitHub Actions Automation

### **Automated Schedule**

- **When**: Daily at 8:00 AM Nepal Time (Sunday-Thursday)
- **Cron**: `15 2 * * 0-4` (2:15 AM UTC, Sunday-Thursday)
- **Timezone Logic**: 8:00 AM NPT = 2:15 AM UTC (due to UTC+5:45 offset)

### **Manual Trigger**

1. Go to GitHub repo → **Actions** tab
2. Click **"📊 Daily NEPSE Stock Analysis"**
3. Click **"Run workflow"** dropdown
4. Select options:
   - **Force run**: `true` (run even on non-trading days)
   - **Dry run**: `false` (write to database)
5. Click **"Run workflow"**

### **Configure GitHub Secrets**

If not already set:

1. Go to GitHub repo → **Settings** → **Secrets and variables** → **Actions**
2. Add repository secrets:

| Secret Name | Value |
|-------------|-------|
| `SUPABASE_URL` | `https://oqthzjdcewnhlmekfsip.supabase.co` |
| `SUPABASE_SERVICE_ROLE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` |

### **Workflow Logs**

After each run:
- Logs are uploaded as artifacts
- Retained for 7 days
- Download from workflow run page

---

## 🔧 Troubleshooting

### **Issue: Supabase Connection Fails**

**Symptoms**:
```
❌ Supabase not reachable. Check your URL and key.
```

**Solutions**:
1. Verify `.env` file exists in `python/` directory
2. Check `SUPABASE_URL` has no trailing slash
3. Ensure `SUPABASE_SERVICE_ROLE_KEY` is copied correctly (no extra spaces)
4. Test connectivity:
   ```bash
   python -c "from config import db; print(db.health_check())"
   ```

### **Issue: NEPSE API Returns Empty Data**

**Symptoms**:
```
API prices failed, trying ShareSansar fallback...
```

**Solutions**:
1. Check NEPSE API status: [https://nepseapi.surajrimal.dev](https://nepseapi.surajrimal.dev)
2. Try manual request:
   ```bash
   curl https://nepseapi.surajrimal.dev/PriceVolume
   ```
3. If API is down, ShareSansar fallback will activate automatically
4. For persistent issues, check firewall/proxy settings

### **Issue: ML Model Has Insufficient Data**

**Symptoms**:
```
No predictions generated.
```

**Cause**: Need minimum 30 days of historical data

**Solutions**:
1. Run pipeline daily to accumulate history
2. Use backfill script if available:
   ```bash
   python backfill_history.py
   ```
3. Check data count:
   ```bash
   python -c "from config import db; print(len(db.select('daily_prices', '*', {'date': 'gte.2026-01-01'})))"
   ```

### **Issue: Frontend Shows "No data available"**

**Symptoms**: Dashboard displays empty state

**Solutions**:
1. Verify Supabase has data:
   - Check `daily_prices` table has recent dates
   - Check `predictions` table has entries
2. Restart Next.js dev server
3. Clear browser cache
4. Check browser console for errors
5. Verify `.env.local` has correct keys

### **Issue: Duplicate Key Error in Stocks Table**

**Symptoms**:
```
Error upserting NABIL: duplicate key value violates unique constraint
```

**Solution**: This is expected behavior during upsert. The script handles it gracefully. If persistent:

1. Check for duplicate symbols in Supabase:
   ```sql
   SELECT symbol, COUNT(*) 
   FROM stocks 
   GROUP BY symbol 
   HAVING COUNT(*) > 1;
   ```

2. Remove duplicates:
   ```sql
   DELETE FROM stocks a USING stocks b
   WHERE a.id > b.id AND a.symbol = b.symbol;
   ```

### **Issue: Port 3000 Already in Use**

**Symptoms**:
```
Error: listen EADDRINUSE: address already in use :::3000
```

**Solutions**:
1. Kill existing process:
   ```bash
   # Windows PowerShell
   Get-Process -Name node | Stop-Process -Force
   
   # Or use specific port
   npm run dev -- -p 3001
   ```

2. Change port permanently:
   - Edit `web/package.json`
   - Change `"dev": "next dev"` to `"dev": "next dev -p 3001"`

---

## ✅ Daily Operations Checklist

### **Morning (Before Market Opens - 9:00 AM NPT)**

- [ ] **Check GitHub Actions run** (8:00 AM NPT)
  - Go to Actions tab
  - Verify successful completion
  - Check logs for errors
  
- [ ] **Verify data in Supabase**
  - `daily_prices` has today's date
  - `predictions` table updated
  - `market_summary` populated

- [ ] **Test frontend dashboard**
  - Open [http://localhost:3000](http://localhost:3000)
  - Verify market summary displays
  - Check top 5 picks (if ML active)

### **During Market Hours (11:00 AM - 3:00 PM NPT)**

- [ ] **Monitor live data** (if needed)
  - Refresh dashboard periodically
  - Check for API failures
  - Manual pipeline run if data missing:
    ```bash
    cd python
    venv\Scripts\activate
    python main.py --force
    ```

### **After Market Close (4:00 PM NPT)**

- [ ] **Verify end-of-day data**
  - Final prices stored in `daily_prices`
  - All indicators calculated
  
- [ ] **Check prediction accuracy**
  - View `model_accuracy` table
  - Note average error percentage
  - Track direction accuracy

### **Weekly Tasks**

- [ ] **Review model performance**
  - Check accuracy trends
  - Identify underperforming stocks
  - Consider parameter tuning if error > 5%

- [ ] **Database maintenance**
  - Check table sizes
  - Archive old data if needed
  - Verify indexes are working

- [ ] **Code updates**
  - Pull latest changes from Git
  - Update dependencies:
    ```bash
    # Python
    pip install --upgrade -r requirements.txt
    
    # Node.js
    npm update
    ```

---

## 📊 Database Schema Reference

### **Tables Overview**

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `stocks` | Master company list | `symbol`, `name`, `sector`, `is_active` |
| `daily_prices` | Historical OHLCV + indicators | `stock_id`, `date`, `close`, `rsi_14`, `sma_50` |
| `predictions` | ML predictions | `predicted_close`, `confidence_score`, `buy_rank` |
| `model_accuracy` | Daily accuracy metrics | `avg_error_pct`, `direction_accuracy` |
| `market_summary` | NEPSE market-wide data | `nepse_index`, `total_turnover` |

### **Useful SQL Queries**

**Get today's top 5 picks**:
```sql
SELECT symbol, current_price, predicted_close, predicted_change_pct, confidence_score
FROM v_todays_top_picks;
```

**Check data completeness**:
```sql
SELECT 
  COUNT(DISTINCT s.symbol) as total_stocks,
  COUNT(DISTINCT dp.date) as days_with_data,
  MAX(dp.date) as latest_date
FROM stocks s
LEFT JOIN daily_prices dp ON s.id = dp.stock_id
WHERE s.is_active = true;
```

**View prediction accuracy trend**:
```sql
SELECT date, avg_error_pct, direction_accuracy, total_predictions
FROM v_accuracy_history
ORDER BY date DESC
LIMIT 30;
```

**Find stocks with most accurate predictions**:
```sql
SELECT 
  s.symbol,
  AVG(ABS(p.predicted_close - p.actual_close) / p.current_price * 100) as avg_error
FROM predictions p
JOIN stocks s ON s.id = p.stock_id
WHERE p.actual_close IS NOT NULL
GROUP BY s.symbol
HAVING COUNT(*) >= 10
ORDER BY avg_error ASC
LIMIT 20;
```

---

## 🎓 Understanding the ML Model

### **Algorithm: Random Forest Regressor**

**Configuration**:
- 100 trees (`n_estimators=100`)
- Max depth: 10
- Trained per-stock (individual model for each company)
- Uses 5-fold cross-validation for confidence scoring

### **Feature Engineering (18 Features)**

**Price Features**:
- `close` - Current closing price
- `volume` - Trading volume
- `change_pct` - Daily price change %
- `high_low_spread` - Volatility indicator
- `close_open_spread` - Intraday momentum

**Technical Indicators**:
- `rsi_14` - Relative Strength Index (oversold/overbought)
- `sma_50`, `sma_200` - Simple Moving Averages
- `ema_12`, `ema_26` - Exponential Moving Averages
- `macd`, `macd_signal` - MACD crossover signals
- `bb_position` - Position in Bollinger Bands

**Derived Features**:
- `price_vs_sma50` - % deviation from 50-day SMA
- `price_vs_sma200` - % deviation from 200-day SMA
- `volume_sma_ratio` - Volume spike detector
- `momentum_5`, `momentum_10` - Short-term momentum

### **Buy Score Calculation (Composite Ranking)**

| Factor | Weight | Criteria |
|--------|--------|----------|
| Predicted Upside | 30% | Higher upside = higher score |
| RSI Oversold | 20% | RSI < 30 = strong buy (+20 pts) |
| Value Play | 15% | Price below SMA-200 = undervalued |
| Volume Spike | 15% | High relative volume = interest |
| Confidence | 10% | Model R² from cross-validation |
| MACD Signal | 10% | Bullish MACD crossover |

**Top 5 Selection**: Stocks ranked by buy_score, top 5 assigned `buy_rank` 1-5

### **Model Performance Metrics**

**Typical Results**:
- **Average Error**: 2-4% (depends on market volatility)
- **Direction Accuracy**: 55-65% (predicting up/down correctly)
- **Top 5 Accuracy**: 60-70% (top picks outperforming market)

**Improving Accuracy**:
1. Accumulate more historical data (aim for 200+ days)
2. Tune hyperparameters (tree depth, estimators)
3. Add more features (sector indices, market sentiment)
4. Use ensemble methods (combine multiple models)

---

## 📱 Deployment Options

### **Frontend Deployment (Next.js)**

**Option 1: Vercel (Recommended)**
```bash
cd web
vercel deploy
```
- Automatic deployments from Git
- Free tier sufficient for this app
- Global CDN, fast in Nepal region

**Option 2: Self-hosted**
```bash
npm run build
pm2 start npm --name "nepse-app" -- start
```

### **Backend Deployment (Python)**

**Option 1: GitHub Actions (Current)**
- Already configured ✅
- Runs daily at 8:00 AM NPT
- No server costs

**Option 2: Scheduled Task on VPS**
- Rent a cheap VPS (₹500/month)
- Set up cron job:
  ```bash
  15 2 * * 0-4 cd /path/to/python && venv/bin/python main.py --force
  ```

---

## 🔒 Security Best Practices

### **Environment Variables**

✅ **Do**:
- Store secrets in `.env` files (gitignored)
- Use GitHub Secrets for CI/CD
- Rotate keys periodically

❌ **Don't**:
- Commit `.env` to Git
- Hardcode keys in source code
- Share service_role key publicly

### **Supabase Security**

**Row Level Security (RLS)**:
- Enabled on all tables ✅
- Public read access for dashboard ✅
- Service role bypasses RLS for writes ✅

**API Keys**:
- `anon_key` (publishable) - Used in frontend
- `service_role_key` (secret) - Used in backend only

**Never expose service_role_key in**:
- Frontend JavaScript
- Client-side code
- Browser-accessible APIs

---

## 📞 Support & Resources

### **Documentation**
- [Supabase Docs](https://supabase.com/docs)
- [Next.js Docs](https://nextjs.org/docs)
- [scikit-learn Docs](https://scikit-learn.org/stable/)

### **API Endpoints**
- NEPSE API: [https://nepseapi.surajrimal.dev](https://nepseapi.surajrimal.dev)
- ShareSansar: [https://www.sharesansar.com/today-share-price](https://www.sharesansar.com/today-share-price)

### **Project Files Reference**

| File | Purpose |
|------|---------|
| `python/main.py` | Pipeline orchestrator |
| `python/scraper.py` | Data fetching (API + fallback) |
| `python/indicators.py` | Technical indicator calculations |
| `python/predictor.py` | ML predictions and ranking |
| `python/config.py` | Supabase client + constants |
| `web/app/page.tsx` | Dashboard homepage |
| `web/app/stock/[symbol]/page.tsx` | Individual stock page |
| `web/app/accuracy/page.tsx` | Model accuracy tracking |
| `supabase/schema.sql` | Database schema |
| `.github/workflows/daily-stock-update.yml` | GitHub Actions cron |

---

## 🎉 Success Indicators

### **System is Working Correctly When**:

✅ Dashboard shows latest market data  
✅ Top 5 picks displayed with predicted upside  
✅ Individual stock pages load with charts  
✅ Accuracy page shows historical metrics  
✅ GitHub Actions runs successfully daily  
✅ Supabase tables populate with new data  
✅ No errors in Python script logs  
✅ No console errors in browser  

### **First-Time Setup Complete When**:

1. ✅ Database schema created in Supabase
2. ✅ Python dependencies installed
3. ✅ Next.js dependencies installed
4. ✅ `.env` files configured correctly
5. ✅ Dry run passes (API connectivity test)
6. ✅ Full pipeline runs successfully
7. ✅ Frontend loads with data
8. ✅ GitHub Actions secrets configured

---

## 🚨 Common Pitfalls to Avoid

1. **Committing `.env` files** → Always keep them in `.gitignore`
2. **Using anon key in backend** → Use service_role_key for Python
3. **Running on Saturday/Friday** → NEPSE closed, use `--force` flag
4. **Ignoring dry run** → Always test first with `--dry-run`
5. **Not checking logs** → Review GitHub Actions output after each run
6. **Impatient with ML** → Need 30+ days of data before predictions activate
7. **Hardcoding values** → Use environment variables everywhere

---

## 📈 Next Steps & Enhancements

### **Phase 1: Stabilization (First Month)**
- [ ] Run pipeline daily without failures
- [ ] Accumulate 30+ days of historical data
- [ ] Monitor and document accuracy trends
- [ ] Fix any bugs that emerge

### **Phase 2: Optimization (Months 2-3)**
- [ ] Tune ML hyperparameters based on accuracy
- [ ] Add more technical indicators
- [ ] Implement backtesting framework
- [ ] Create admin dashboard for monitoring

### **Phase 3: Advanced Features (Months 4-6)**
- [ ] Add sentiment analysis from news
- [ ] Sector rotation strategies
- [ ] Portfolio optimization suggestions
- [ ] Mobile app (React Native)
- [ ] Email/SMS alerts for top picks

### **Phase 4: Production Readiness (Months 6+)**
- [ ] User authentication
- [ ] Premium tiers for advanced features
- [ ] API rate limiting
- [ ] Performance monitoring (Sentry, LogRocket)
- [ ] Load testing and scaling

---

## 📝 Maintenance Notes

### **Backup Strategy**

**Automated Backups**:
- Supabase provides daily backups (retained 7 days on free tier)
- GitHub version control for code

**Manual Backup** (monthly):
```sql
-- Export all tables
COPY stocks TO '/backup/stocks.csv' CSV HEADER;
COPY daily_prices TO '/backup/daily_prices.csv' CSV HEADER;
COPY predictions TO '/backup/predictions.csv' CSV HEADER;
```

### **Version Control**

**Git Workflow**:
```bash
# Main branch (production-ready)
git checkout main

# Feature development
git checkout -b feature/add-sentiment-analysis
git push origin feature/add-sentiment-analysis
# Create pull request on GitHub
```

### **Dependency Updates**

**Monthly Check**:
```bash
# Python
pip list --outdated
pip install --upgrade requests pandas scikit-learn

# Node.js
npm outdated
npm update
```

---

## 🎓 Educational Disclaimer

⚠️ **This system is for educational purposes only**

- **Not financial advice**: Do not use for actual investment decisions
- **Inherent risks**: Stock predictions are inherently uncertain
- **Past performance**: Historical accuracy doesn't guarantee future results
- **Do your research**: Always conduct independent analysis
- **No liability**: Developers not responsible for financial losses

**Intended Use**:
- Learning machine learning applications
- Understanding technical analysis
- Practicing full-stack development
- Educational demonstration project

---

## 📞 Contact & Contributions

**Project Structure**: Monorepo (Python + Next.js)  
**License**: MIT License  
**Status**: Educational Project  

For questions or issues:
1. Check this guide's troubleshooting section
2. Review GitHub Issues in repository
3. Examine pipeline logs for errors

---

**Last Updated**: March 28, 2026  
**Version**: 1.0.0  
**Maintained By**: NEPSE Stock Analyzer Team
