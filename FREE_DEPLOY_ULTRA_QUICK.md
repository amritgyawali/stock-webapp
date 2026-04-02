# ⚡ FREE DEPLOYMENT - ULTRA QUICK START

**Copy & Paste Your Way to Production in 1 Hour (All FREE)**

---

## 🎯 The 6 Steps

### ✅ STEP 1: Verify Your Setup (5 min)

```powershell
# Run these commands:
python --version
node --version
git --version

# Test Python backend
cd c:\Users\amrit\stock-webapp\python
.\venv\Scripts\activate
python main.py --dry-run
deactivate
cd ..

# Test frontend builds
cd web
npm run build
cd ..
```

**Expected**: All commands work, no errors

---

### ✅ STEP 2: GitHub Setup (5 min)

```powershell
# 1. Create GitHub account at github.com/signup
# 2. Create repo at github.com/new → name: stock-webapp
# 3. Push code:

cd c:\Users\amrit\stock-webapp
git init
git add .
git commit -m "Initial deployment"

# REPLACE YOUR_USERNAME with your actual GitHub username:
git remote add origin https://github.com/YOUR_USERNAME/stock-webapp.git
git branch -M main
git push -u origin main
```

**Expected**: Code appears on GitHub

---

### ✅ STEP 3: Supabase Database (5 min)

**ALREADY HAVE SUPABASE? SKIP TO GETTING CREDENTIALS**

1. Go to https://supabase.com
2. Sign up with GitHub
3. Create project (name: nepse-stock)
4. Wait 2-3 minutes

**Then get credentials:**
1. Supabase → Settings → API
2. Copy these 3 values and SAVE:
```
SUPABASE_URL = https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJhbGc...
SUPABASE_SERVICE_ROLE_KEY = eyJhbGc...
```

**Status**: ✅ Database ready

---

### ✅ STEP 4: Deploy Frontend to Vercel (10 min)

```
1. Go to https://vercel.com
2. Sign up with GitHub
3. Click "Add New" → "Project"
4. Click "Import Git Repository"
5. Select stock-webapp
6. Change Root Directory to: ./web
7. DON'T click deploy yet!
```

**Create .env.production file first:**

Create `web/.env.production`:
```
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```
(Use YOUR values from Step 3)

**Then in Vercel:**
```
8. Add Environment Variables (same as above)
9. Click DEPLOY
10. Wait 2-3 minutes
11. Click domain link
12. Should see dashboard! ✅
```

**Status**: ✅ Frontend live

---

### ✅ STEP 5: GitHub Actions Backend (20 min)

**Create workflow file:**

```powershell
# Create the directory structure
mkdir -p .github/workflows
```

**Create `.github/workflows/daily-pipeline.yml` with this content:**

```yaml
name: Daily NEPSE Pipeline

on:
  schedule:
    - cron: '0 11 * * 0-4'
  workflow_dispatch:

jobs:
  pipeline:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    steps:
    - uses: actions/checkout@v3
    - uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'
    - run: |
        cd python
        pip install --upgrade pip
        pip install -r requirements.txt
    - name: Run Pipeline
      env:
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
      run: |
        cd python
        python main.py --force
```

**Add GitHub Secrets:**

```
1. GitHub repo → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Create 2 secrets:

   Secret 1:
   Name: SUPABASE_URL
   Value: https://xxxxx.supabase.co

   Secret 2:
   Name: SUPABASE_SERVICE_ROLE_KEY
   Value: eyJhbGc...
```

**Commit and push:**

```powershell
cd c:\Users\amrit\stock-webapp

git add .github/workflows/daily-pipeline.yml
git commit -m "Add GitHub Actions pipeline"
git push
```

**Test it:**

```
1. GitHub repo → Actions tab
2. Click "Daily NEPSE Pipeline"
3. Click "Run workflow" button
4. Watch it run (should take 2-3 min)
5. Should see green checkmark ✅
```

**Status**: ✅ Backend scheduled

---

### ✅ STEP 6: Verify Everything (10 min)

**Check Frontend:**
```
1. Visit: https://stock-webapp-xxx.vercel.app
2. Should see dashboard
3. Press F12, check console (no red errors)
4. ✅ Works!
```

**Check Backend:**
```
1. GitHub → Actions tab
2. Should see workflow run
3. Check logs (should be green)
4. ✅ Works!
```

**Check Data Flow:**
```
1. Wait 1-2 minutes after backend completes
2. Visit Vercel URL
3. Refresh: Ctrl+Shift+R
4. Should show stock data
5. Go to Supabase → Table Editor → daily_prices
6. Should see new entries with today's date
7. ✅ Everything connected!
```

---

## 🎉 DONE! 

Your FREE production deployment is complete!

### What Now Happens Automatically:

**Every day at 11 AM UTC** (= 4:45 PM Nepal, plus market hours logic):
- GitHub Actions triggers automatically
- Python pipeline runs
- Fetches latest NEPSE data
- Calculates predictions
- Stores in Supabase
- Frontend auto-updates
- **You do nothing!** ✅

---

## 💰 Total Cost

| Service | Free Tier | Your Usage | Cost |
|---------|-----------|-----------|------|
| Vercel | 100 GB/mo | ~2 GB | $0 |
| Supabase | 500 MB | ~50 MB | $0 |
| GitHub Actions | 2000 min/mo | ~150 min | $0 |
| **TOTAL** | | | **$0/month** ✅ |

**Completely FREE forever!** (or for many years of normal usage)

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Frontend shows old data | Refresh: Ctrl+Shift+R |
| "SUPABASE_URL not set" | Check Vercel → Environment Variables |
| Backend didn't run | Check GitHub Actions → workflow logs |
| Can't connect to database | Verify both SUPABASE_* values in secrets |
| Frontend won't build | Check web/.env.production exists |

---

## 📋 Success Checklist

```
STEP 1 - Setup:
  ☐ python --version works
  ☐ node --version works
  ☐ git --version works
  ☐ python main.py --dry-run passed
  ☐ npm run build passed

STEP 2 - GitHub:
  ☐ GitHub account created
  ☐ Repository created
  ☐ Code pushed to GitHub

STEP 3 - Database:
  ☐ Supabase project created
  ☐ All 4 tables exist
  ☐ 3 credentials saved

STEP 4 - Frontend:
  ☐ web/.env.production created
  ☐ Vercel project created
  ☐ Root Directory set to ./web
  ☐ Environment variables added
  ☐ Deployment completed
  ☐ Vercel URL loads without errors

STEP 5 - Backend:
  ☐ .github/workflows/daily-pipeline.yml created
  ☐ Pushed to GitHub
  ☐ GitHub secrets created (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
  ☐ Manual workflow test succeeded
  ☐ Logs showed success

STEP 6 - Verify:
  ☐ Frontend loads and displays data
  ☐ Backend ran at least once
  ☐ Supabase has new data entries
  ☐ Frontend shows data after refresh

ALL CHECKED? ✅ YOU'RE LIVE!
```

---

## 🚀 Your Live URLs

After deployment, you'll have:

```
Frontend:    https://stock-webapp-xxx.vercel.app
GitHub Repo: https://github.com/YOUR_USERNAME/stock-webapp
Supabase:    https://supabase.com/dashboard
```

**Share the Vercel URL with anyone!** It works publicly! 🎉

---

## 📞 Need Help?

See full guide: `FREE_DEPLOYMENT_GUIDE.md` in your repo root

All questions answered there with detailed explanations!

---

## ⏱️ Timeline

```
0-5 min:   Verify local setup
5-10 min:  Push code to GitHub
10-15 min: Supabase database credentials
15-25 min: Vercel frontend deployment
25-45 min: GitHub Actions backend setup
45-60 min: Testing & verification
────────────────────
60 min:    ✅ LIVE IN PRODUCTION!
```

---

**You Did It! 🎉 Welcome to Production!**

Your app is now live, free, and fully automated!

Last Updated: April 2, 2026
