# 🚀 DEPLOYMENT ROADMAP

## Your Step-by-Step Path to Production

**Estimated Time**: 1.5 - 2.5 hours  
**Total Cost (Month 1)**: Free (all free tiers available)  
**Technical Level**: Beginner to Intermediate

---

## 📚 Documentation Map

Before starting, understand which document covers what:

| Document | Use When | Time | Difficulty |
|----------|----------|------|------------|
| **DEPLOYMENT_QUICK_REFERENCE.md** | Quick overview & checklists | 5 min | ⭐ Easy |
| **COMPLETE_DEPLOYMENT_GUIDE.md** | Detailed step-by-step instructions | 30 min | ⭐⭐ Medium |
| **ENV_SETUP_GUIDE.md** | Setting up environment variables | 10 min | ⭐ Easy |
| **BACKEND_DEPLOYMENT_DETAILED.md** | Choosing & setting up backend | 20 min | ⭐⭐ Medium |
| **TESTING_VERIFICATION_GUIDE.md** | Verifying each component works | 15 min | ⭐⭐ Medium |

---

## 🎯 Quick Start (First Time Here?)

1. ✅ Read this page (5 min)
2. ✅ Run local verification (15 min) - see "Phase 0" below
3. ✅ Follow the roadmap step-by-step
4. ✅ Use DEPLOYMENT_QUICK_REFERENCE.md as a checklist
5. ✅ Refer to detailed guides when needed

---

## Phase 0: Pre-Deployment Verification ✓

**Time**: 15-30 minutes  
**Goal**: Ensure everything works locally before deploying

### Step 0.1: Check Local Shell Setup

```bash
# Open PowerShell in c:\Users\amrit\stock-webapp

# Verify Python
python --version  # Should be 3.10 or higher

# Verify Node.js
node --version    # Should be 18+
npm --version     # Should be 11+

# Verify Git
git --version     # Should work
```

✅ All commands above should return version numbers without errors.

### Step 0.2: Verify Existing Environment

```bash
# Check if .env already exists
cd python
if (Test-Path .env) { "✓ .env exists" } else { "✗ Create .env" }

# Test Python environment
cd python
.\venv\Scripts\activate
python -c "import supabase, pandas, numpy; print('✓ All packages installed')"
deactivate
```

✅ Should see "✓ All packages installed"

### Step 0.3: Quick Dry-Run

```bash
cd python
.\venv\Scripts\activate
python main.py --dry-run
```

✅ Should complete successfully and show connection tests passed.

---

## 🏗️ Main Deployment Roadmap

### Phase 1: Prepare Your GitHub Repository (10 min)

**Goal**: Code is on GitHub, ready for Vercel

**Reference**: COMPLETE_DEPLOYMENT_GUIDE.md → Phase 2, Step 2.3

#### Step 1.1: Initialize Git (if first time)
```bash
cd c:\Users\amrit\stock-webapp
git init
git add .
git commit -m "Initial commit - NEPSE Stock Analyzer"
```

#### Step 1.2: Create GitHub Repository
1. Go to [github.com/new](https://github.com/new)
2. Create repository named: `stock-webapp`
3. Copy the repository URL

#### Step 1.3: Connect and Push
```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/stock-webapp.git
git branch -M main
git push -u origin main
```

#### Step 1.4: Verify
- Go to your GitHub repository
- Should see all files including `python/`, `web/`, `supabase/` folders

✅ **Phase Complete**: Your code is on GitHub

---

### Phase 2: Setup Supabase Database (10 min)

**Goal**: Cloud database ready with tables and credentials

**Reference**: COMPLETE_DEPLOYMENT_GUIDE.md → Phase 1

#### Step 2.1: Check Existing Project

If project already exists (likely from previous conversation):
```bash
# Just verify it's working
1. Go to supabase.com/dashboard
2. Select your project
3. Check tables: stocks, daily_prices, predictions, market_summary
4. All should exist ✓
```

If NOT:
1. Create new project at supabase.com
2. Wait 2-3 minutes for setup
3. Verify tables exist

#### Step 2.2: Save Credentials

From Supabase dashboard → Settings → API, copy and save:
```
SUPABASE_URL = https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJhbGc... (starts with eyJ)
SUPABASE_SERVICE_ROLE_KEY = eyJhbGc... (different eyJ string)
```

**IMPORTANT**: Keep SERVICE_ROLE_KEY secret! Don't share or commit.

#### Step 2.3: Create .env File

In `python/` directory:
```bash
# Create python/.env
cd python

# On Windows PowerShell:
@'
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
'@ | Out-File -Encoding UTF8 .env

# Verify file was created
Get-Content .env
```

✅ **Phase Complete**: Database ready, credentials saved

---

### Phase 3: Deploy Frontend to Vercel (15 min)

**Goal**: Your dashboard live at `https://stock-webapp-xxx.vercel.app`

**Reference**: COMPLETE_DEPLOYMENT_GUIDE.md → Phase 2

#### Step 3.1: Create Environment Files

In `web/` directory, create `.env.production`:
```env
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```

#### Step 3.2: Verify Local Build

```bash
cd web
npm install
npm run build
```

✅ Should complete with "✓ Compiled successfully"

#### Step 3.3: Create Vercel Account (if needed)

1. Go to [vercel.com](https://vercel.com)
2. Click "Sign Up"
3. Choose "GitHub" option
4. Authorize Vercel to access your repositories

#### Step 3.4: Import Project to Vercel

1. Vercel Dashboard → "Add New..." → "Project"
2. "Import Git Repository"
3. Select `stock-webapp`
4. Configuration:
   - **Root Directory**: `./web` ← IMPORTANT!
   - **Framework**: Next.js (auto-detected)
   - Leave other settings default

#### Step 3.5: Add Environment Variables

**BEFORE clicking Deploy:**

1. Scroll to "Environment Variables"
2. Add these:
   - Name: `NEXT_PUBLIC_SUPABASE_URL` → Value: `https://xxxxx.supabase.co`
   - Name: `NEXT_PUBLIC_SUPABASE_ANON_KEY` → Value: `eyJhbGc...`

3. Click "Deploy"

#### Step 3.6: Wait and Verify

- Wait 2-3 minutes for build
- Should see "✓ Ready" status
- Click the domain link
- Dashboard should load with stock data ✅

If errors:
- See TESTING_VERIFICATION_GUIDE.md → Troubleshooting → Frontend

✅ **Phase Complete**: Frontend is live on Vercel!

---

### Phase 4: Deploy Backend (Choose One - 20-30 min)

**Goal**: Python pipeline runs automatically on schedule

**Reference**: BACKEND_DEPLOYMENT_DETAILED.md

#### Option A: GitHub Actions (⭐ RECOMMENDED for beginners)

**Time**: 10 minutes | **Cost**: FREE

```bash
# 1. Create workflow file
mkdir -p .github/workflows

# 2. Create .github/workflows/daily-pipeline.yml
# (Copy template from BACKEND_DEPLOYMENT_DETAILED.md → Option 1)

# 3. Commit and push
git add .github/workflows/daily-pipeline.yml
git commit -m "Add GitHub Actions workflow"
git push

# 4. Add secrets to GitHub
# GitHub repo → Settings → Secrets → New:
#   - SUPABASE_URL
#   - SUPABASE_SERVICE_ROLE_KEY

# 5. Test workflow
# GitHub repo → Actions → Daily NEPSE Pipeline → Run workflow
```

**Verify**: 
- Go to Actions tab
- Should see workflow runs
- First run should complete successfully ✓

#### Option B: Render.com (⭐ Alternative if you want always-on)

**Time**: 15 minutes | **Cost**: Free-$7/month

```
1. Go to render.com → Sign up with GitHub
2. New → Cron Job
3. Configuration:
   - Name: nepse-daily-pipeline
   - Repository: stock-webapp
   - Build: pip install -r python/requirements.txt
   - Command: python python/main.py --force
   - Schedule: 0 11 * * 0-4
4. Add environment variables:
   - SUPABASE_URL
   - SUPABASE_SERVICE_ROLE_KEY
5. Deploy
```

**Verify**:
- Render dashboard should show "Active"
- Click "Manual Trigger" to test
- Should complete successfully ✓

#### Option C: AWS EC2 (⭐ If you want full control)

**Time**: 30-45 minutes | **Cost**: $5-12/month

See BACKEND_DEPLOYMENT_DETAILED.md → Option 3 for detailed SSH and setup instructions.

✅ **Phase Complete**: Backend runs automatically!

---

### Phase 5: Integration & Testing (15 min)

**Goal**: Verify all three components work together

**Reference**: TESTING_VERIFICATION_GUIDE.md

#### Step 5.1: Test Frontend-Database Connection

```bash
cd python
.\venv\Scripts\activate
python -c "
from config import db
stocks = db.select('stocks', limit=1)
print(f'✓ Database has {len(stocks)} records')
print(f'✓ Sample: {stocks[0] if stocks else \"empty\"}')
"
```

✅ Should show data from database

#### Step 5.2: Manual Pipeline Run

```bash
cd python
python main.py --force
```

✅ Should complete successfully in 3-5 minutes

#### Step 5.3: Verify Data in Frontend

1. Wait 1 minute for pipeline to complete
2. Visit your Vercel URL
3. Refresh page (Ctrl+Shift+R to clear cache)
4. Dashboard should show latest data ✅

#### Step 5.4: Verify Scheduled Execution

Wait for next scheduled time (or manually trigger):
- GitHub Actions: Go to Actions tab
- Render: Render dashboard
- AWS: Check logs via SSH

Should see successful execution ✓

✅ **Phase Complete**: All components integrated and working!

---

## 🎉 Deployment Success Indicators

Your deployment is complete when you see ALL of these:

- [ ] ✓ Frontend accessible at Vercel URL
- [ ] ✓ Dashboard displays stock data with charts
- [ ] ✓ Database has fresh prices/predictions
- [ ] ✓ Backend service shows as "Running" or "Scheduled"
- [ ] ✓ Manual backend trigger succeeds
- [ ] ✓ Scheduled backend run executed successfully
- [ ] ✓ No errors in browser console (F12)
- [ ] ✓ Supabase shows recent data updates

---

## 🔄 Daily Operation (After Deployment)

### What happens automatically:

1. **Every day at 11 AM Nepal time**:
   - Backend pipeline starts
   - Fetches latest NEPSE data
   - Runs ML predictions
   - Stores in Supabase

2. **Frontend automatically**:
   - Fetches latest data from database
   - Displays on dashboard
   - Updates charts

3. **Monitoring**:
   - Check Vercel analytics
   - Check backend logs (GitHub Actions / Render / AWS)
   - Ensure no errors appear

### Manual operations:

```bash
# Force pipeline to run now (not waiting for schedule)
cd python
python main.py --force

# Test configuration (doesn't modify database)
python main.py --dry-run

# Check what data is in database
# Go to Supabase dashboard → Table Editor
```

---

## 📊 Monitoring Dashboard

After deployment, monitor these:

### ✅ Vercel Monitoring
```
Vercel.com → Your Project
  → Analytics (page load time, errors)
  → Deployments (version history)
  → Settings → Function Logs (errors)
```

### ✅ Supabase Monitoring
```
Supabase.com → Your Project
  → Database → Replication Lag
  → SQL Editor → Run queries to verify data
  → Logs → Database logs
```

### ✅ Backend Monitoring
```
GitHub Actions:
  Actions tab → Workflow runs → Check if latest succeeded

Render:
  Dashboard → Events tab → Check execution history

AWS:
  SSH into instance → sudo journalctl -u nepse-pipeline
```

---

## 🚨 Common Post-Deployment Issues

### "Data not updating"
```
1. Did the backend run? Check logs
2. Is pipeline configured to run at right time?
3. Try manual: python main.py --force
4. Check Supabase for new data
5. Refresh frontend: Ctrl+Shift+R
```

### "Frontend shows old data"
```
1. Check if new data in database
2. Check network requests (F12 → Network tab)
3. Clear browser cache: Ctrl+Shift+Del
4. Force refresh: Ctrl+Shift+R
5. Check Supabase is returning latest data
```

### "Backend service not running"
```
GitHub Actions:
  - Check Actions tab for red X
  - Check logs for error messages
  
Render:
  - Check "Last run" timestamp
  - Manually trigger to test
  
AWS:
  - SSH in: sudo systemctl status nepse-pipeline
  - Check: sudo journalctl -u nepse-pipeline
```

See COMPLETE_DEPLOYMENT_GUIDE.md → Troubleshooting for more.

---

## 💰 Cost Breakdown (Month 1 and Ongoing)

### Month 1: $0 (all free tiers)
- Vercel: 100GB bandwidth free
- Supabase: 500MB database free
- GitHub Actions: 2000 minutes/month free
- Render: Free tier available (with limitations)

### Month 2+: $0-20/month
- Continue free tiers (recommended for startup)
- OR upgrade to paid for better reliability
  - Supabase Pro: $25/month (1 GB database)
  - Render: $7/month (no cold starts)

---

## 📞 Need Help?

| Issue | Resource |
|-------|----------|
| Frontend won't build | COMPLETE_DEPLOYMENT_GUIDE.md → Frontend Issues |
| Database connection fails | COMPLETE_DEPLOYMENT_GUIDE.md → Database Issues |
| Backend won't start | BACKEND_DEPLOYMENT_DETAILED.md → Troubleshooting |
| Data not appearing | TESTING_VERIFICATION_GUIDE.md → Integration Testing |
| Environment variables | ENV_SETUP_GUIDE.md |
| General overview | DEPLOYMENT_QUICK_REFERENCE.md |

---

## ✅ Final Verification Checklist

Before considering deployment complete:

```
FRONTEND
  ☐ Vercel deployment shows "Ready" status
  ☐ Can visit and access dashboard
  ☐ No errors in browser console
  ☐ Stock data displays with correct values
  ☐ Charts render properly

DATABASE
  ☐ Supabase project exists and is accessible
  ☐ Tables contain data (stocks, prices, predictions)
  ☐ Can verify data from Supabase console

BACKEND
  ☐ Service deployed to chosen platform
  ☐ Environment variables configured
  ☐ Manual trigger test succeeded
  ☐ Automated schedule is set (and verified working)
  ☐ Recent logs show successful executions

INTEGRATION
  ☐ Backend → Database: Data flows correctly
  ☐ Database → Frontend: Frontend displays latest data
  ☐ End-to-end: Automatic update happens on schedule
  
MONITORING
  ☐ Can access logs for debugging
  ☐ Know how to check if system ran
  ☐ Know how to manually trigger if needed
```

---

## 🎓 Next Steps & Learning

After successful deployment, consider:

1. **Set up monitoring alerts**: Get notified if pipeline fails
2. **Add SSL certificate**: Ensure HTTPS (Vercel does this automatically)
3. **Enable backups**: Set Supabase backup schedule
4. **Implement caching**: Improve frontend performance
5. **Add user authentication**: Restrict dashboard access
6. **Optimize queries**: Monitor and improve database performance
7. **Auto-scaling**: Prepare for growth

---

## 📝 Troubleshooting Quick Reference

```bash
# Test all components
php://frontend
  npm run build          # Build without errors
  npm run dev           # Should load at localhost:3000

php://backend
  python main.py --dry-run      # Test connectivity
  python main.py --force        # Full run

php://database
  # Go to Supabase dashboard and query tables directly
```

---

## Summary

You're now ready to:
1. ✅ Deploy to production
2. ✅ Monitor your system
3. ✅ Troubleshoot issues
4. ✅ Scale as needed

**Total deployment time**: 1.5 - 2.5 hours  
**Total cost**: FREE (Month 1 and many months after)  
**Success rate**: Very high following this guide!

---

## 🚀 Ready to Deploy?

**Start with**: Phase 0 (verification) → Phase 1 (GitHub) → Phase 2 (Database) → Phase 3 (Frontend) → Phase 4 (Backend) → Phase 5 (Testing)

**Use these documents in order**:
1. This file (roadmap)
2. DEPLOYMENT_QUICK_REFERENCE.md (checklist)
3. COMPLETE_DEPLOYMENT_GUIDE.md (detailed steps)
4. Specific guides as needed (ENV, Backend, Testing)

**Questions?** Refer to the appropriate guide above.

---

**Good luck with your deployment! 🎉**

*Last Updated: April 2, 2026*
