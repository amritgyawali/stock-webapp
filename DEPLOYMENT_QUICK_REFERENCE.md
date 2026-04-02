# Deployment Quick Reference Card

## 🚀 5-Minute Deployment Checklist

Use this checklist for quick reference during deployment. See COMPLETE_DEPLOYMENT_GUIDE.md for detailed steps.

---

## Prerequisites (5 min)

- [ ] GitHub account (github.com/signup)
- [ ] Vercel account (vercel.com - link with GitHub)
- [ ] Supabase account (supabase.com - link with GitHub)
- [ ] Backend platform choice (Render, AWS, GitHub Actions, or other)
- [ ] Supabase credentials saved (URL + keys)

---

## Phase 1: Database (Supabase) - 5 min

✅ **Already done if using existing Supabase project**

Quick check:
```bash
# If project exists
1. Go to supabase.com/dashboard
2. Select your project
3. Check tables exist: stocks, daily_prices, predictions, market_summary
4. Copy credentials to safe location
```

Save these credentials:
- `SUPABASE_URL` = https://xxxxx.supabase.co
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` = (use for frontend)
- `SUPABASE_SERVICE_ROLE_KEY` = (use for backend - KEEP SECRET!)

---

## Phase 2: Frontend Deployment (Vercel) - 10 min

### Step 1: Prepare project locally
```bash
cd web
npm install
npm run build      # Should succeed with no errors!
npm run start       # Test it works, then Ctrl+C to stop
```

### Step 2: Create .env.production
```bash
# In web/ directory, create .env.production:
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```

### Step 3: Push to GitHub
```bash
cd c:\Users\amrit\stock-webapp

# If first time:
git init
git add .
git commit -m "Initial deploy"
git remote add origin https://github.com/YOUR_USERNAME/stock-webapp.git
git branch -M main
git push -u origin main

# Otherwise just:
git add .
git commit -m "Deploy config"
git push
```

### Step 4: Deploy on Vercel
```
1. Go to vercel.com → Add New → Project
2. Import your GitHub repository (stock-webapp)
3. Settings:
   - Framework: Next.js ✓ (auto-detected)
   - Root Directory: ./web
   - Build: npm run build ✓
   - Install: npm install ✓
4. BEFORE deploying - add Environment Variables:
   - NEXT_PUBLIC_SUPABASE_URL = https://xxxxx.supabase.co
   - NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJhbGc...
5. Click Deploy
6. Wait 2-3 min for build
7. Click domain link to verify it works
```

✅ **Success**: Frontend URL shows stock data, no errors

---

## Phase 3: Backend Deployment - Choice of approach

### Option A: Render.com ⭐ (Easiest)

```bash
# 1. Go to render.com → New → Web Service
# 2. Connect GitHub repo
# 3. Settings:
#    - Name: nepse-pipeline
#    - Runtime: Python 3.11
#    - Build: pip install -r python/requirements.txt
#    - Start: python python/main.py --force
# 4. Add Environment Variables:
#    - SUPABASE_URL
#    - SUPABASE_SERVICE_ROLE_KEY
# 5. Deploy
# 6. For scheduling, use Cron Job option instead

# Alternative - Deploy as Cron Job (runs on schedule):
# 1. Render → New → Cron Job
# 2. Settings:
#    - Name: nepse-daily-pipeline
#    - Schedule: 0 11 * * 0-4 (11 AM, Sun-Thu)
#    - Command: python python/main.py --force
# 3. Same environment variables as above
# 4. Deploy
```

### Option B: GitHub Actions ⭐ (Simplest - Free!)

```bash
# 1. Create .github/workflows/daily-pipeline.yml
# (See template below)

# 2. Add GitHub Secrets:
#    - Settings → Secrets → Add:
#    - SUPABASE_URL
#    - SUPABASE_SERVICE_ROLE_KEY

# 3. Push the workflow file
git add .github/workflows/daily-pipeline.yml
git commit -m "Add GitHub Actions pipeline"
git push

# 4. Check Actions tab → should see workflow scheduled

# Workflow file content:
```

Create `.github/workflows/daily-pipeline.yml`:
```yaml
name: Daily NEPSE Pipeline
on:
  schedule:
    - cron: '0 11 * * 0-4'  # 11 AM UTC, Sun-Thu
  workflow_dispatch:
jobs:
  pipeline:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install -r python/requirements.txt
    - name: Run pipeline
      env:
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
      run: python python/main.py --force
```

### Option C: AWS EC2

```bash
# 1. AWS Console → EC2 → Launch Instance
#    - Name: nepse-backend
#    - AMI: Ubuntu 22.04 LTS
#    - Instance type: t2.micro (free tier)
#    - Download key pair (.pem file)
#    - Configure security group: Allow SSH (22)
#    - Launch

# 2. SSH into instance:
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Setup on server:
sudo apt update && sudo apt install python3-pip python3-venv git
mkdir ~/stock-webapp && cd ~/stock-webapp
git clone https://github.com/YOUR_USERNAME/stock-webapp.git .
python3 -m venv venv
source venv/bin/activate
pip install -r python/requirements.txt

# 4. Create .env file:
nano python/.env
# Paste your credentials, save with Ctrl+X, Y, Enter

# 5. Add to crontab:
crontab -e
# Add line: 0 5 * * 0-4 cd ~/stock-webapp && ./venv/bin/python python/main.py --force

# 6. Exit SSH: exit
```

---

## Phase 4: Verify Everything Works - 5 min

### Frontend Check
1. Visit your Vercel URL: https://stock-webapp-xxx.vercel.app
2. ✅ Should show dashboard with stock data
3. ✅ No errors in browser console (F12)

### Backend Check (run manually first)
```bash
cd python
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Test with dry-run first
python main.py --dry-run

# Then run full pipeline
python main.py --force
```

✅ Should complete without errors

### Integration Check
1. Refresh frontend after pipeline runs
2. ✅ Should show updated stock data
3. Go to Supabase → Table Editor
4. ✅ Verify daily_prices has new entries with today's date

---

## Environment Variables - Just Copy These

### For Vercel (Frontend - PUBLIC)
```
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...
```

### For Backend (KEEP SECRET!)
```
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
```

---

## Common Commands

```bash
# Build frontend locally
cd web && npm run build

# Test pipeline locally
cd python && python main.py --dry-run
cd python && python main.py --force

# Deploy to GitHub (triggers Vercel auto-deploy)
git push

# Quick trigger on Vercel
vercel --prod

# Check Vercel deployment status
vercel ls

# View Vercel logs
vercel logs
```

---

## Verification URLs

After deployment, check these:

| Check | URL |
|-------|-----|
| **Frontend** | `https://stock-webapp-xxx.vercel.app` |
| **Supabase** | `https://supabase.com/dashboard` → your project |
| **Vercel Logs** | `https://vercel.com` → project → deployments |
| **Backend Logs** | Render/AWS/GitHub depending on choice |

---

## Troubleshooting Quick Fixes

| Problem | Solution |
|---------|----------|
| Frontend won't load | Check Vercel env vars set correctly |
| "SUPABASE_URL not set" | Add env vars to Render/AWS/Secrets |
| Pipeline doesn't run | Check cron time is correct for your timezone |
| Data doesn't appear | Run `python main.py --force` manually to test |
| Connection timeout | Check NEPSE API is accessible, retry later |
| "ModuleNotFoundError" | Run pip install -r python/requirements.txt again |

---

## Post-Deployment

After everything works:

1. ✅ Enable monitoring (Vercel Analytics)
2. ✅ Set up alerts (errors, downtime)
3. ✅ Configure automatic backups (Supabase)
4. ✅ Document your setup (save this checklist!)
5. ✅ Plan maintenance schedule

---

## Support Links

- Vercel Docs: https://vercel.com/docs
- Supabase Docs: https://supabase.com/docs
- Next.js Docs: https://nextjs.org/docs
- Python Deployment: See COMPLETE_DEPLOYMENT_GUIDE.md

---

**Time to Deployment**: 30-45 minutes total  
**Est. Cost (Month 1)**: $0 (all free tiers)  
**Est. Cost (Ongoing)**: $0-20/mo depending on usage

Last Updated: April 2, 2026
