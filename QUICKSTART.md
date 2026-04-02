# 🚀 Quick Start - NEPSE Stock Analyzer

## ⚡ 5-Minute Setup (If Starting Fresh)

### 1. Database Setup (2 minutes)
```bash
# Go to Supabase Dashboard → SQL Editor
# Paste contents of supabase/schema.sql
# Click "Run"
```

### 2. Install Dependencies (3 minutes)
```bash
# Python Backend
cd c:\Users\amrit\stock-webapp\python
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Next.js Frontend
cd c:\Users\amrit\stock-webapp\web
npm install
```

### 3. Run Data Pipeline (1 minute)
```bash
cd python
venv\Scripts\activate
python main.py --force  # First time: use --force
```

### 4. Start Web Server (1 minute)
```bash
cd web
npm run dev
# Open http://localhost:3000
```

---

## 📅 Daily Operations (5 minutes/day)

### Morning Routine (8:05 AM NPT)

**Check Automated Run**:
1. GitHub → Actions tab
2. Verify last run succeeded ✅
3. If failed, click "Run workflow" manually

**Quick Verification**:
```bash
cd python
venv\Scripts\activate
python main.py --dry-run  # Test connectivity
```

### During Market Hours

**Manual Data Refresh** (if needed):
```bash
python main.py --force
```

### Evening Check (4:00 PM NPT)

**Verify Data**:
- Open dashboard: http://localhost:3000
- Check latest date in market summary
- Confirm predictions updated

---

## 🔧 Common Commands

### Python Backend

```bash
# Activate virtual environment
cd c:\Users\amrit\stock-webapp\python
venv\Scripts\activate

# Test APIs only (no DB writes)
python main.py --dry-run

# Full pipeline run
python main.py --force

# Run on trading day (normal mode)
python main.py

# Check specific stock data
python -c "from config import db; print(db.select('stocks', '*', {'symbol': 'eq.NABIL'}))"

# View recent predictions
python -c "from config import db; preds = db.select('predictions', '*', order='prediction_date.desc', limit=5); print(preds)"
```

### Next.js Frontend

```bash
# Development server (hot reload)
cd c:\Users\amrit\stock-webapp\web
npm run dev

# Production build
npm run build
npm start

# Change port (if 3000 busy)
npm run dev -- -p 3001
```

### Git & GitHub Actions

```bash
# Push updates
git add .
git commit -m "Description"
git push origin main

# Trigger manual workflow
# Go to: GitHub → Actions → "📊 Daily NEPSE Stock Analysis" → "Run workflow"
```

---

## 🎯 Key URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard** | http://localhost:3000 | Main homepage |
| **Stock Detail** | http://localhost:3000/stock/NABIL | Individual stock |
| **Accuracy** | http://localhost:3000/accuracy | Model metrics |
| **Supabase** | https://supabase.com/dashboard | Database admin |
| **GitHub Actions** | https://github.com/.../actions | Automation logs |
| **NEPSE API** | https://nepseapi.surajrimal.dev | Data source |

---

## 🚨 Emergency Fixes

### System Not Working?

**Reset Everything**:
```bash
# 1. Kill all processes
Get-Process -Name node,python | Stop-Process -Force

# 2. Restart from scratch
cd c:\Users\amrit\stock-webapp\python
venv\Scripts\activate
python main.py --force

# 3. Restart frontend
cd ..\web
npm run dev
```

### Data Missing?

**Check Supabase**:
1. Go to Table Editor
2. Verify `daily_prices` has today's date
3. If empty, run pipeline manually

### Frontend Shows "No Data"?

**Quick Fix**:
```bash
# Clear cache and restart
cd web
rm -rf .next
npm run dev
```

### GitHub Actions Failing?

**Debug Steps**:
1. Click failed workflow run
2. Expand error logs
3. Common issues:
   - ❌ Expired secrets → Update SUPABASE keys
   - ❌ API down → Check nepseapi.surajrimal.dev
   - ❌ DB constraint → Check for duplicates

---

## 📊 Health Check Script

Create `health_check.py`:

```python
from config import db, get_nepal_date_str

today = get_nepal_date_str()

print("=== HEALTH CHECK ===")

# 1. Supabase connection
try:
    connected = db.health_check()
    print(f"✅ Supabase: {'Connected' if connected else 'Disconnected'}")
except Exception as e:
    print(f"❌ Supabase: {e}")

# 2. Today's data count
try:
    prices = db.select("daily_prices", "*", {"date": f"eq.{today}"})
    print(f"✅ Today's Prices: {len(prices)} stocks")
except Exception as e:
    print(f"❌ Prices: {e}")

# 3. Predictions
try:
    preds = db.select("predictions", "*", {"prediction_date": f"eq.{today}"})
    top5 = [p for p in preds if p.get('buy_rank')]
    print(f"✅ Predictions: {len(preds)} total, {len(top5)} top picks")
except Exception as e:
    print(f"❌ Predictions: {e}")

# 4. Market Summary
try:
    summary = db.select("market_summary", "*", order="date.desc", limit=1)
    print(f"✅ Market Summary: NEPSE Index = {summary[0].get('nepse_index', 'N/A')}")
except Exception as e:
    print(f"❌ Market Summary: {e}")
```

Run: `python health_check.py`

---

## 🎓 Learning Path

### Week 1: Basics
- [ ] Understand data flow: API → Python → Supabase → Next.js
- [ ] Run pipeline manually multiple times
- [ ] Explore Supabase tables
- [ ] Browse frontend pages

### Week 2: Deep Dive
- [ ] Read `scraper.py` code
- [ ] Understand ML model in `predictor.py`
- [ ] Study indicator calculations
- [ ] Examine database schema

### Week 3: Enhancements
- [ ] Add new technical indicator
- [ ] Modify buy score formula
- [ ] Create new dashboard widget
- [ ] Improve error handling

### Week 4: Automation
- [ ] Set up monitoring alerts
- [ ] Configure backup strategy
- [ ] Document performance metrics
- [ ] Plan advanced features

---

## 📞 Quick Reference

### Environment Variables

**Python** (`python/.env`):
```env
SUPABASE_URL=https://oqthzjdcewnhlmekfsip.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<your-key>
```

**Next.js** (`web/.env.local`):
```env
NEXT_PUBLIC_SUPABASE_URL=https://oqthzjdcewnhlmekfsip.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=<your-anon-key>
```

### Database Tables

| Table | Rows | Last Updated |
|-------|------|--------------|
| `stocks` | ~273 | Auto-sync |
| `daily_prices` | Growing daily | Daily 8 AM |
| `predictions` | Growing daily | Daily 8 AM |
| `market_summary` | ~365 | Daily 8 AM |
| `model_accuracy` | Growing | After market close |

### File Locations

```
c:\Users\amrit\stock-webapp\
├── python/
│   ├── main.py              # Pipeline entry point
│   ├── scraper.py           # Data fetching
│   ├── indicators.py        # Technical analysis
│   ├── predictor.py         # ML predictions
│   ├── config.py            # Configuration
│   └── .env                 # Environment variables
├── web/
│   ├── app/
│   │   ├── page.tsx         # Dashboard
│   │   ├── stock/[symbol]/  # Stock detail page
│   │   └── accuracy/        # Accuracy metrics
│   └── .env.local           # Frontend env vars
└── supabase/
    └── schema.sql           # Database schema
```

---

## ✅ Success Checklist

**System Ready When**:

- [ ] `.env` files exist and configured
- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] Supabase schema created
- [ ] Dry run passes
- [ ] Full pipeline completes
- [ ] Frontend loads without errors
- [ ] Dashboard shows data
- [ ] GitHub Actions configured

**Daily Success Indicators**:

- [ ] GitHub Actions ran at 8 AM
- [ ] No errors in workflow logs
- [ ] Dashboard displays today's date
- [ ] Predictions generated (if enough history)
- [ ] Market summary populated
- [ ] Frontend accessible at localhost:3000

---

## 🎉 You're Ready!

After setup:
1. ✅ Pipeline runs daily at 8:00 AM NPT
2. ✅ Frontend auto-refreshes every 60 seconds
3. ✅ Data accumulates in Supabase
4. ✅ ML predictions activate after 30 days
5. ✅ Accuracy tracking begins

**Next**: Read [`SETUP_GUIDE.md`](SETUP_GUIDE.md) for detailed documentation.

---

**Last Updated**: March 28, 2026  
**Estimated Time**: 10 minutes for full setup  
**Difficulty**: Beginner-friendly
