# 🎯 100% FREE Deployment Guide (1 Hour)

## Deploy Everything for $0/month

This guide uses **ONLY free tiers** to deploy your complete application:
- ✅ **Vercel** - Next.js frontend (FREE: 100GB/month)
- ✅ **Supabase** - PostgreSQL database (FREE: 500MB)
- ✅ **GitHub Actions** - Python pipeline (FREE: 2000 min/month)

**Total Cost**: $0/month forever  
**Time to Deploy**: 1 hour  
**Difficulty**: ⭐ Easy

---

## Prerequisites (5 minutes)

Check you have these (you probably do):

```bash
# 1. Check Python is installed
python --version

# 2. Check Node.js is installed  
node --version

# 3. Check Git is installed
git --version
```

If any fail, install from [python.org](https://www.python.org), [nodejs.org](https://nodejs.org), or [git-scm.com](https://git-scm.com)

---

## Step 1: Verify Local Setup (5 minutes)

```bash
cd c:\Users\amrit\stock-webapp

# 1. Test Python backend
cd python
.\venv\Scripts\activate
python main.py --dry-run
# Should show: "✓ Supabase connection: OK" and "✓ NEPSE API connection: OK"

deactivate
cd ..

# 2. Test frontend builds
cd web
npm run build
# Should complete with: "✓ Compiled successfully"

cd ..
```

✅ Both should work without errors.

---

## Step 2: Create GitHub Accounts & Connect (5 minutes)

### 2.1: GitHub Account (if you don't have)

1. Go to [github.com/signup](https://github.com/signup)
2. Create account
3. Verify email

### 2.2: Create GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. **Repository name**: `stock-webapp`
3. **Description**: NEPSE Stock Analyzer
4. Click **"Create repository"**

### 2.3: Push Your Code to GitHub

```bash
cd c:\Users\amrit\stock-webapp

# Initialize git (if first time)
git init

# Add all files
git add .

# First commit
git commit -m "Initial NEPSE Stock Analyzer deployment"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/stock-webapp.git

# Create main branch and push
git branch -M main
git push -u origin main
```

✅ All code is now on GitHub

---

## Step 3: Supabase Database Setup (5 minutes)

**Already have Supabase? Skip to Step 3.2**

### 3.1: Create Supabase Account

1. Go to [supabase.com](https://supabase.com)
2. Click **"Start your project"**
3. Sign in with GitHub
4. Create project:
   - **Name**: `nepse-stock`
   - **Password**: Create strong password
   - **Region**: Choose closest to you

### 3.2: Verify Tables Exist

1. Supabase dashboard → **SQL Editor**
2. Run:
```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

Should show: `stocks`, `daily_prices`, `predictions`, `market_summary`

If NOT, run schema from `supabase/schema.sql`:
1. Supabase → SQL Editor → New Query
2. Paste entire `supabase/schema.sql` content
3. Click "Run"

### 3.3: Get Credentials

Go to **Settings** → **API**

Copy and **SAVE these 3 values** (you'll need them soon):

```
SUPABASE_URL = https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJhbGc... (Anon key)
SUPABASE_SERVICE_ROLE_KEY = eyJhbGc... (Service role key)
```

✅ Database is ready

---

## Step 4: Deploy Frontend to Vercel (10 minutes)

### 4.1: Create Vercel Account

1. Go to [vercel.com](https://vercel.com)
2. Click **"Sign Up"**
3. Choose **"GitHub"** option
4. Authorize Vercel

### 4.2: Create .env.production

In `web/` directory, create file `.env.production`:

```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```

(Replace with YOUR values from Step 3.3)

### 4.3: Import Project to Vercel

1. Vercel dashboard → **"Add New..."** → **"Project"**
2. Click **"Import Git Repository"**
3. Find and select `stock-webapp`
4. **Root Directory**: Change to `./web` ← IMPORTANT!
5. Click **"Deploy"** (don't worry about environment variables yet)

### 4.4: Add Environment Variables During Deploy

When Vercel asks for environment variables:

```
NEXT_PUBLIC_SUPABASE_URL = https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJhbGc...
```

Click **"Deploy"**

### 4.5: Wait for Deployment

- Takes 2-3 minutes
- Should see ✓ Ready status
- Click the domain link
- Dashboard should load! ✅

---

## Step 5: Deploy Backend to GitHub Actions (20 minutes)

GitHub Actions runs your Python pipeline for FREE! ⭐

### 5.1: Create Workflow File

Create `.github/workflows/daily-pipeline.yml`:

```bash
mkdir -p .github/workflows
```

Copy this to `.github/workflows/daily-pipeline.yml`:

```yaml
name: Daily NEPSE Pipeline

on:
  # Schedule: 11 AM UTC every day except Friday/Saturday
  schedule:
    - cron: '0 11 * * 0-4'
  
  # Allow manual trigger for testing
  workflow_dispatch:

jobs:
  pipeline:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    
    steps:
    - name: Checkout Repository
      uses: actions/checkout@v3
    
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'
    
    - name: Install Dependencies
      run: |
        cd python
        pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run Daily Pipeline
      env:
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
      run: |
        cd python
        python main.py --force
```

### 5.2: Add GitHub Secrets

1. Go to your GitHub repo
2. **Settings** (top menu) → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Create TWO secrets:

**Secret 1:**
- Name: `SUPABASE_URL`
- Value: `https://xxxxx.supabase.co` (from Step 3.3)
- Click "Add secret"

**Secret 2:**
- Name: `SUPABASE_SERVICE_ROLE_KEY`
- Value: `eyJhbGc...` (Service role key from Step 3.3)
- Click "Add secret"

### 5.3: Commit and Push Workflow

```bash
cd c:\Users\amrit\stock-webapp

git add .github/workflows/daily-pipeline.yml
git commit -m "Add GitHub Actions daily pipeline"
git push
```

### 5.4: Test the Workflow

1. Go to your GitHub repo
2. Click **"Actions"** tab
3. Click **"Daily NEPSE Pipeline"** workflow
4. Click **"Run workflow"** → **"Run workflow"** (test it now)
5. Watch it run (should take 2-3 minutes)
6. Should see green checkmark ✅

---

## Step 6: Verify Everything Works (10 minutes)

### 6.1: Check Frontend

1. Visit your Vercel URL: `https://stock-webapp-xxx.vercel.app`
2. Should see dashboard with stock data
3. Open F12 (developer console)
4. Check for any red errors
5. ✅ Should look good!

### 6.2: Check Backend Ran

1. Go to GitHub Actions tab
2. Check workflow runs
3. Should see your manual test run completed successfully
4. ✅ Backend works!

### 6.3: Verify Data Flow

Wait 1 minute after backend runs, then:

1. Refresh your Vercel frontend (Ctrl+Shift+R)
2. Check if prices/predictions display
3. Go to Supabase dashboard
4. Click **Table Editor** → select `daily_prices`
5. Should see recent entries with today's date
6. ✅ Data flows correctly!

---

## 🎉 You're Done! 

Your application is now **fully deployed and FREE**!

### What's Running:

✅ **Frontend**: Live at `https://stock-webapp-xxx.vercel.app`  
✅ **Database**: Supabase PostgreSQL with all data  
✅ **Backend**: Runs automatically every day at 11 AM UTC  

### What Happens Automatically:

**Every day at 11 AM UTC** (4:45 PM Nepal + market hours logic):
1. GitHub Actions automatically starts
2. Python pipeline runs
3. Fetches latest NEPSE data
4. Calculates predictions
5. Stores in Supabase
6. Frontend auto-updates

You don't have to do anything! ✅

---

## 📊 Cost Breakdown

| Component | Free Tier | Your Monthly Usage | Cost |
|-----------|-----------|-------------------|------|
| **Vercel** | 100 GB bandwidth | ~2 GB | $0 ✅ |
| **Supabase** | 500 MB database | ~50 MB | $0 ✅ |
| **GitHub Actions** | 2,000 min/month | ~150 min | $0 ✅ |
| **TOTAL** | | | **$0/month** ✅ |

**These free tiers are completely sufficient for 1-2 years of operation!**

---

## 🧪 Testing the System

### Test 1: Manual Backend Run (Now)

```bash
cd python
.\venv\Scripts\activate
python main.py --force
```

Should complete successfully. ✅

### Test 2: Check Frontend Data

1. Wait 1 minute after above completes
2. Visit Vercel URL
3. Refresh page
4. Should show updated data ✅

### Test 3: Wait for Scheduled Run

Next day at 11 AM UTC:
1. Go to GitHub Actions
2. Should see automatic workflow run
3. Check logs for success ✅

---

## 📝 Maintenance (30 seconds/day)

Just monitor, nothing to do!

```
Daily (2 minutes):
  - Visit dashboard, verify data updated
  - If error, check GitHub Actions logs

Weekly (5 minutes):
  - Check Vercel analytics
  - Verify no errors in console

Monthly (10 minutes):
  - Review logs
  - Check database usage (should be <100 MB)
  - Verify backend ran all days
```

---

## ⚡ Quick Commands Reference

```bash
# Test locally
cd python && python main.py --force

# Force backend to run (GitHub Actions)
# Go to: GitHub repo → Actions → Daily NEPSE Pipeline → Run workflow

# Check logs
# GitHub: repo → Actions → workflow run → See logs
# Frontend: Vercel → Deployments → logs
# Database: Supabase → Logs

# Update application
git add .
git commit -m "Your message"
git push
# Vercel auto-deploys! ✅
```

---

## 🆘 Something Not Working?

### "Frontend won't load"
```
1. Check Vercel deployment status (should be ✓ Ready)
2. Check environment variables in Vercel
3. Vercel dashboard → Settings → Environment Variables
4. Ensure both variables are there and correct
```

### "Backend didn't run"
```
1. Check GitHub Actions tab
2. Click workflow → should see run
3. If no run, workflow might not be set for right time
4. Go to .github/workflows/daily-pipeline.yml
5. Check cron: 0 11 * * 0-4
```

### "No data in frontend"
```
1. Did backend run? Check GitHub Actions
2. Manually run: GitHub Actions → Run workflow
3. Wait 1-2 minutes
4. Refresh frontend with Ctrl+Shift+R
5. Check Supabase → Table Editor → daily_prices
```

### "SUPABASE_URL not set error"
```
1. Check GitHub secrets are created (Settings → Secrets)
2. Redeploy: Vercel → Deployments → right-click latest → Redeploy
3. Or push new commit: git commit --allow-empty && git push
```

---

## 📚 Files You Modified

For reference, here's what was changed:

```
✅ Created:
  .github/workflows/daily-pipeline.yml    (GitHub Actions workflow)
  web/.env.production                      (Frontend config)

✅ Used:
  python/.env                              (Backend config - already existed)
  supabase/schema.sql                      (Database tables)
  python/main.py                           (Backend pipeline)
  web/                                     (Frontend Next.js app)
```

---

## 🚀 You Now Have

- ✅ Production-grade frontend on Vercel
- ✅ Cloud PostgreSQL database on Supabase
- ✅ Automated daily Python pipeline on GitHub Actions
- ✅ Zero ongoing costs
- ✅ Automatic scaling (free tiers handle 10,000+ users)
- ✅ Professional monitoring and logs

---

## 📞 Next Steps

1. **Wait for tomorrow 11 AM UTC** - See automatic pipeline run
2. **Monitor for 1 week** - Verify everything runs smoothly
3. **Share with others** - Your live URL works!
4. **Optional upgrades** - Only if you hit free tier limits (unlikely)

---

## ✅ Success Checklist

Mark these as you complete:

- [ ] Code pushed to GitHub
- [ ] Supabase database has tables
- [ ] Vercel frontend deployed
- [ ] Vercel URL loads without errors
- [ ] GitHub Actions workflow created
- [ ] GitHub secrets added (SUPABASE_URL, SERVICE_ROLE_KEY)
- [ ] Manual workflow test succeeded
- [ ] Data visible in Supabase
- [ ] Frontend displays data after refresh
- [ ] Scheduled workflow will run tomorrow

**All checked?** You're completely deployed! 🎉

---

## 🎯 Architecture (What You Just Built)

```
┌────────────────────┐
│  Your Computer     │
│  (Development)     │
└────────────────────┘

        ↓ (git push)

┌────────────────────┐
│  GitHub            │
│  (Code + Workflow) │
└────────────────────┘

        ├─→ ┌─────────────────────┐
        │   │  Vercel             │
        │   │  (Frontend)         │
        │   │  https://app.vercel │
        │   └─────────────────────┘
        │
        └─→ ┌─────────────────────┐
            │  GitHub Actions     │
            │  (Backend)          │
            │  (Daily at 11 AM)   │
            └─────────────────────┘
                       │
                       ↓
            ┌─────────────────────┐
            │  Supabase           │
            │  (Database)         │
            │  PostgreSQL         │
            └─────────────────────┘
                       │
                       ↓
            ┌─────────────────────┐
            │  Vercel Frontend    │
            │  (Shows latest data)│
            └─────────────────────┘
```

---

## 🎊 Congratulations!

You successfully deployed a **production-grade stock market analysis platform**:
- ✅ Fully automated
- ✅ Zero cost
- ✅ Scalable
- ✅ Professional
- ✅ Live on the internet

**Total time spent**: ~1 hour  
**Total cost**: $0  
**Total effort**: Minimal (mostly copy-paste!)

Enjoy your deployed application! 🚀

---

Last Updated: April 2, 2026
For Free Deployment Only (No Premium Services Needed)
