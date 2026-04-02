# Complete Vercel + Python Backend Deployment Guide
## NEPSE Stock Analyzer - Full Stack Production Deployment

**Last Updated**: April 2, 2026  
**Target Stack**: Next.js Frontend (Vercel) + Supabase Database + Python ML Backend  
**Estimated Time**: 2-3 hours for complete setup

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Database Setup (Supabase)](#phase-1-database-setup-supabase)
4. [Phase 2: Frontend Deployment (Vercel)](#phase-2-frontend-deployment-vercel)
5. [Phase 3: Python Backend Deployment](#phase-3-python-backend-deployment)
6. [Phase 4: Integration & Testing](#phase-4-integration--testing)
7. [Phase 5: Production Optimization](#phase-5-production-optimization)
8. [Deployment Checklist](#deployment-checklist)
9. [Troubleshooting Guide](#troubleshooting-guide)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR APPLICATION STACK                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────┐         ┌────────────────────┐  │
│  │   VERCEL FRONTEND      │         │   PYTHON BACKEND   │  │
│  │   (Next.js app)        │────────▶│   (Data Pipeline)  │  │
│  │   - Dashboard          │         │   - Scraper        │  │
│  │   - Stock Charts       │         │   - ML Predictor   │  │
│  │   - Accuracy Reports   │         │   - Indicators     │  │
│  └────────────────────────┘         └────────────────────┘  │
│           │                                     │              │
│           │                                     │              │
│           └─────────────────┬──────────────────┘              │
│                             │                                  │
│                    ┌────────▼────────┐                       │
│                    │  SUPABASE DB    │                       │
│                    │  (PostgreSQL)   │                       │
│                    │  - Stocks table │                       │
│                    │  - Prices table │                       │
│                    │  - Predictions  │                       │
│                    └─────────────────┘                       │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Purpose | Deployment Platform |
|-----------|---------|---------------------|
| **Next.js Frontend** | User interface, dashboards, charts | Vercel (Free tier available) |
| **Supabase Database** | Store stocks, prices, predictions | Supabase Cloud (Free tier: 500MB) |
| **Python Backend** | Data scraping, ML predictions | VPS/Cloud VM (Options below) |
| **Scheduled Tasks** | Daily pipeline execution | External Services |

---

## Prerequisites

### Required Accounts (Create if you don't have)

- [x] GitHub account (for Vercel deployment)
- [ ] Vercel account (link with GitHub)
- [ ] Supabase account (PostgreSQL database)
- [ ] Python backend hosting (choose ONE):
  - DigitalOcean App Platform
  - AWS EC2 / Lightsail
  - Render.com
  - Railway.app
  - Heroku (legacy but working)

### Local Requirements

- Git (version control)
- Node.js 18+ and npm
- Python 3.10+
- VS Code or similar editor

### Skills Needed

- Basic command line usage
- Git basics (clone, push, commit)
- Environment variables
- REST API understanding

---

## Phase 1: Database Setup (Supabase)

### Step 1.1: Create/Configure Supabase Project

**If you already have a Supabase project, skip to Step 1.2**

1. Go to [supabase.com](https://supabase.com)
2. Click "Start your project"
3. Sign in with GitHub
4. Create a new project with details:
   - **Project name**: `nepse-stock-prod` (or your preference)
   - **Database password**: Create strong password (save it!)
   - **Region**: Choose closest to your target users
   - **Pricing**: Free tier is fine for startup

5. Wait for project creation (2-3 minutes)

### Step 1.2: Verify Database Schema

1. Go to your Supabase dashboard
2. Click **SQL Editor** in left sidebar
3. Verify these tables exist (from `supabase/schema.sql`):
   - `stocks` - Company information
   - `daily_prices` - Historical and live prices
   - `predictions` - ML predictions
   - `market_summary` - Daily market data

**If tables don't exist:**
```
1. Go to SQL Editor
2. Click "New Query"
3. Paste content from supabase/schema.sql
4. Click "Run"
5. Verify no errors
```

### Step 1.3: Get Production Credentials

1. Go to **Settings** → **API**
2. Copy and save these values (you'll need them soon):
   - **Project URL**: `https://xxxxx.supabase.co`
   - **Anon key**: `eyJhbGc...` (public, safe to share)
   - **Service role key**: `eyJhbGc...` (KEEP SECRET - use only in backend)

3. Store these somewhere safe (you'll add to Vercel & Python backend)

### Step 1.4: Set Up Row Level Security (RLS) - Optional but Recommended

1. Go to **Authentication** → **Policies**
2. Review current RLS settings
3. For public read (stock data):
   ```sql
   CREATE POLICY "Public read access" ON daily_prices
   FOR SELECT USING (true);
   ```

---

## Phase 2: Frontend Deployment (Vercel)

### Step 2.1: Prepare Next.js Project for Production

From your project root:

```bash
cd web

# 1. Ensure all dependencies are installed
npm install

# 2. Build locally to catch errors
npm run build

# 3. Test production build
npm run start
# Visit http://localhost:3000 - should work perfectly

# Stop with Ctrl+C
```

**Troubleshooting local build:**
- If build fails, check for TypeScript errors: `npm run lint`
- Clear cache: `rm -rf .next && npm run build`

### Step 2.2: Create `.env.production` for Vercel

In `/web` directory, create `.env.production` file:

```env
# Supabase - Use ANON key (safe to expose to frontend)
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...

# Optional: API endpoints for Python backend
NEXT_PUBLIC_API_BASE_URL=https://your-api.example.com
```

**Replace with YOUR actual credentials from Step 1.3**

### Step 2.3: Push to GitHub

```bash
cd c:\Users\amrit\stock-webapp

# 1. Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit - NEPSE Stock Analyzer"

# 2. Create repository on GitHub:
#    - Go to github.com/new
#    - Name: stock-webapp
#    - Description: NEPSE Stock Analysis Platform
#    - Leave public/private as you prefer
#    - Create

# 3. Connect and push (replace <USERNAME> with your GitHub username):
git remote add origin https://github.com/<USERNAME>/stock-webapp.git
git branch -M main
git push -u origin main
```

**Verify**: Go to your GitHub repo, should see all files

### Step 2.4: Connect Vercel to GitHub

1. Go to [vercel.com](https://vercel.com)
2. Click **"Add New..."** → **"Project"**
3. Click **"Import Git Repository"**
4. Find your `stock-webapp` repo and click **"Import"**
5. Configuration:
   - **Framework**: Automatically detects Next.js ✓
   - **Root Directory**: `./web` (IMPORTANT!)
   - **Build Command**: `npm run build` (default)
   - **Install Command**: `npm install` (default)

6. Click **"Deploy"** (wait 2-3 minutes)

### Step 2.5: Add Environment Variables in Vercel

After deployment starts:

1. Go to **Project Settings** → **Environment Variables**
2. Add these variables:

| Name | Value | Type |
|------|-------|------|
| `NEXT_PUBLIC_SUPABASE_URL` | `https://xxxxx.supabase.co` | Production, Preview |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | `eyJhbGc...` (from Step 1.3) | Production, Preview |
| `NEXT_PUBLIC_API_BASE_URL` | Your Python API URL (we'll add this later) | Production |

3. Click **"Save"** for each

### Step 2.6: Verify Frontend Deployment

1. Wait for deployment to complete (Status shows "✓ Ready")
2. Click the domain link (should be `https://stock-webapp.vercel.app` or similar)
3. Verify:
   - [ ] Dashboard loads
   - [ ] Stock data displays
   - [ ] Charts render
   - [ ] No console errors (F12 → Console tab)

**If errors occur**, check Vercel logs:
- In Vercel dashboard, click **"Deployments"** → latest deployment
- Click **"View Function Logs"** to see errors

---

## Phase 3: Python Backend Deployment

### Overview: Choose Your Backend Platform

| Platform | Cost | Pros | Cons |
|----------|------|------|------|
| **DigitalOcean App Platform** | $5-12/mo | Easy, Good docs | Overkill for small app |
| **Render** | Free-$7/mo | Simple, Python-friendly | Cold starts on free |
| **Railway** | Pay-as-you-go | Developer friendly | Billing can surprise |
| **AWS Lambda** | Minimal | Scalable, Serverless | Complex setup |
| **VPS (Linode/Vultr)** | $5/mo | Full control | Requires maintenance |
| **GitHub Actions** | Free | Already have GitHub | Limited runtime (6h) |

**Recommendation for beginners**: **Render.com** (free tier available)

---

### Option A: Deploy to Render.com (RECOMMENDED)

#### Step 3A.1: Prepare Python App for Render

1. Create `render.yaml` in project root:

```yaml
services:
  - type: cron
    name: nepse-pipeline
    runtime: python311
    startCommand: "./venv/Scripts/python.exe python python/main.py --force"
    schedule: "0 11 * * 0-4"  # 11 AM daily, Sun-Thu
    envVars:
      - key: SUPABASE_URL
        scope: env
      - key: SUPABASE_SERVICE_ROLE_KEY
        scope: env
```

2. Or for continuous backend API, create `web-backend/app.py`:

```python
from flask import Flask, jsonify
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/predict/<symbol>', methods=['GET'])
def predict(symbol):
    from config import get_latest_trading_date
    from predictor import StockPredictor
    
    predictor = StockPredictor()
    prediction = predictor.predict_single(symbol)
    return jsonify(prediction)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
```

3. Create `requirements-web.txt`:

```
Flask==3.0.0
python-dotenv==1.0.0
requests>=2.31.0
supabase==2.0.5
pandas>=2.1.0
scikit-learn>=1.4.0
nepse>=1.1.0
```

#### Step 3A.2: Create Render Account & Link GitHub

1. Go to [render.com](https://render.com)
2. Click **"New +"** (top right)
3. Choose based on what you're running:
   - **Web Service** (if running Flask/API backend)
   - **Scheduled Job** (if just running daily Python script)

#### Step 3A.3: Deploy (Example: Scheduled Job)

1. From Render dashboard, **"New +"** → **"Cron Job"**
2. Select your GitHub repository
3. Configuration:
   - **Name**: `nepse-daily-pipeline`
   - **Command**: `python python/main.py --force`
   - **Schedule**: `0 11 * * 0-4` (11 AM, Sun-Thu)
   - **Environment**: Python 3.11

4. Add Environment Variables:
   - `SUPABASE_URL`: Your Supabase URL
   - `SUPABASE_SERVICE_ROLE_KEY`: Your service role key (from Step 1.3)

5. Click **"Create Cron Job"**
6. Verify in **"Events"** tab - should show scheduled runs

---

### Option B: Deploy to AWS EC2 + GitHub Actions

#### Step 3B.1: Create AWS EC2 Instance

1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Search for **EC2** in services
3. Click **"Launch Instance"**:
   - **Name**: `nepse-python-backend`
   - **AMI**: Ubuntu 22.04 LTS (Free tier eligible)
   - **Instance type**: `t2.micro` (free tier)
   - **Key pair**: Create new (save the .pem file!)
   - **Security group**: Allow SSH (port 22), HTTP (80), HTTPS (443)
   - **Storage**: 20 GB (free tier eligible)
   - Click **"Launch"**

4. Wait 2-3 minutes for instance to start
5. Copy **Public IPv4 address** (you'll need it)

#### Step 3B.2: SSH into Instance

```bash
# Windows (PowerShell):
$keyPath = "C:\path\to\your\key.pem"
ssh -i $keyPath ubuntu@your-instance-ip

# Or use PuTTY on Windows
# - Load the .pem file in PuTTYgen
# - Save as .ppk
# - Use PuTTY to connect
```

#### Step 3B.3: Setup Python Environment on EC2

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install -y python3-pip python3-venv git

# Create app directory
mkdir -p /home/ubuntu/stock-webapp
cd /home/ubuntu/stock-webapp

# Clone your GitHub repo
git clone https://github.com/<USERNAME>/stock-webapp.git .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r python/requirements.txt

# Create .env file
nano python/.env
# Paste your environment variables, then Ctrl+X, Y, Enter to save
```

#### Step 3B.4: Create Systemd Service (Auto-start on reboot)

```bash
# Create service file
sudo nano /etc/systemd/system/nepse-pipeline.service
```

Paste this content:

```ini
[Unit]
Description=NEPSE Stock Pipeline
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/stock-webapp
Environment="PATH=/home/ubuntu/stock-webapp/venv/bin"
ExecStart=/home/ubuntu/stock-webapp/venv/bin/python python/main.py --force
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Save and enable
sudo systemctl daemon-reload
sudo systemctl enable nepse-pipeline.service
sudo systemctl start nepse-pipeline.service

# Check status
sudo systemctl status nepse-pipeline.service
```

#### Step 3B.5: Setup Cron for Daily Runs

```bash
# Edit crontab
crontab -e

# Add this line (runs at 11 AM Nepal time = 5:15 AM UTC):
0 5 * * 0-4 cd /home/ubuntu/stock-webapp && ./venv/bin/python python/main.py --force >> /tmp/nepse.log 2>&1
```

---

### Option C: GitHub Actions (Free, No Server Needed)

#### Step 3C.1: Create GitHub Actions Workflow

In your repository, create `.github/workflows/daily-pipeline.yml`:

```yaml
name: Daily NEPSE Pipeline

on:
  schedule:
    # Run at 11:00 AM UTC (which is 4:45 PM Nepal Standard Time)
    - cron: '0 11 * * 0-4'
  workflow_dispatch:  # Manual trigger

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
      run: |
        cd python
        pip install -r requirements.txt
    
    - name: Run pipeline
      env:
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
      run: |
        cd python
        python main.py --force
```

#### Step 3C.2: Add GitHub Secrets

1. Go to your GitHub repo
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **"New repository secret"**
4. Add:
   - `SUPABASE_URL`: Your Supabase project URL
   - `SUPABASE_SERVICE_ROLE_KEY`: Your service role key

5. Click **"Add secret"**

#### Step 3C.3: Test Workflow

1. Push this file to GitHub:
```bash
git add .github/workflows/daily-pipeline.yml
git commit -m "Add GitHub Actions daily pipeline"
git push
```

2. Go to **Actions** tab in GitHub
3. Click the workflow and select **"Run workflow"** → **"Run workflow"**
4. Wait and check logs for success

**Limitation**: GitHub Actions free tier allows max 6 hours total per month, but your job likely takes <5 minutes, so you're fine for ~72 daily runs/month.

---

## Phase 4: Integration & Testing

### Step 4.1: Test Frontend-Database Connection

1. Go to your Vercel deployment URL
2. Open browser console (F12)
3. Check:
   - [ ] No errors in Console tab
   - [ ] Network tab shows successful Supabase requests
   - [ ] Dashboard displays stock data
   - [ ] Charts render properly

### Step 4.2: Test Python Backend Connection

**If using Render/AWS/GitHub Actions:**

```bash
# Manually run pipeline to test
cd python
source venv/bin/activate  # or .\venv\Scripts\activate on Windows

# Test with dry-run first
python main.py --dry-run

# Then do full run
python main.py --force
```

Expected output:
```
====================================================
🚀 NEPSE Stock Analyzer — Daily Pipeline
📅 Nepal Time: 2026-04-02 11:30:00 NPT
🔧 Mode: LIVE
====================================================
📋 STEP 1/5: Syncing company list...
✓ Synced 624 companies
📊 STEP 2/5: Cross-Validating Multi-Source Prices...
✓ Stored 268 prices
...
```

### Step 4.3: Verify Data Flow

1. After pipeline runs, check Supabase:
   - Go to your Supabase dashboard
   - **Table Editor** → select `daily_prices`
   - Should see new entries with today's date
   - Check specific stocks: SHEL, KKHC, NABIL

2. Refresh Vercel frontend
3. Verify dashboard shows latest data

### Step 4.4: Test Scheduled Execution

**If using GitHub Actions:**
- Go to GitHub repo → **Actions**
- Should see workflow runs at scheduled times
- Check logs to ensure no failures

**If using Render/AWS:**
- Check if jobs executed at scheduled time
- Verify database was updated
- Check frontend shows new data

---

## Phase 5: Production Optimization

### Step 5.1: Enable Caching on Vercel

1. In Vercel dashboard, go to **Project Settings** → **Functions**
2. Set **Serverless Function Max Duration**: 60 seconds
3. Enable ISR (Incremental Static Regeneration) in `next.config.ts`:

```typescript
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  revalidate: 3600,  // Revalidate every hour
};

export default nextConfig;
```

### Step 5.2: Database Optimization

In Supabase:

1. **Performance** → **Query Performance**
   - Review slow queries
   - Add indexes on frequently filtered columns

2. Add indexes for your queries:
```sql
CREATE INDEX idx_daily_prices_date ON daily_prices(date DESC);
CREATE INDEX idx_daily_prices_symbol ON daily_prices(symbol);
CREATE INDEX idx_predictions_date ON predictions(date DESC);
```

3. Enable **Full Text Search** if needed:
```sql
ALTER TABLE stocks ADD COLUMN search_text tsvector;
UPDATE stocks SET search_text = to_tsvector('english', symbol || ' ' || name);
CREATE INDEX search_idx ON stocks USING gin(search_text);
```

### Step 5.3: Monitor Performance

**Vercel Monitoring:**
- Dashboard → **Analytics**
- Track: Page load time, Web Vitals, Error rate

**Supabase Monitoring:**
- Dashboard → **Database** → **Replication Lag**
- Check connection count and query performance

### Step 5.4: Enable Auto-Scaling (Advanced)

**For Python backend on AWS/Render:**
- Configure auto-scaling if approaching resource limits
- Set up alerts for high CPU/memory usage
- Enable logging and error tracking (Sentry.io)

### Step 5.5: Backup Strategy

**Supabase Backups:**
1. Pro plan includes daily backups
2. Manual backup: **Settings** → **Backups** → **Request backup**

**GitHub Code Backup:**
- GitHub automatically backs up your code
- Additionally, backup locally: `git clone --mirror <your-repo-url>`

---

## Deployment Checklist

Use this checklist to track your deployment progress:

### Prerequisites
- [ ] GitHub account created
- [ ] All accounts (Vercel, Supabase, backend platform) created
- [ ] Project locally builds and runs (`npm run build`, `npm run start`)

### Phase 1: Database
- [ ] Supabase project created
- [ ] Database tables verified (stocks, daily_prices, predictions)
- [ ] Credentials saved safely
- [ ] Test query runs successfully

### Phase 2: Frontend
- [ ] Local build succeeds (`npm run build`)
- [ ] `.env.production` created with Supabase credentials
- [ ] Code pushed to GitHub
- [ ] Vercel project created and linked to GitHub
- [ ] Environment variables added to Vercel
- [ ] Frontend deployment successful
- [ ] Vercel domain loads correctly
- [ ] No console errors in browser

### Phase 3: Python Backend
- [ ] Backend platform account created (Render/AWS/GitHub Actions)
- [ ] `.env` file configured with Supabase credentials
- [ ] Local pipeline runs successfully (`python python/main.py --force`)
- [ ] Deployment configured (cron job / schedule / service)
- [ ] Test run confirms data is stored in database

### Phase 4: Integration
- [ ] Frontend connects to Supabase
- [ ] Backend has stored data in database
- [ ] Frontend displays backend data correctly
- [ ] All three components communicate successfully

### Phase 5: Production
- [ ] Caching enabled on Vercel
- [ ] Database indexes created
- [ ] Backups configured
- [ ] Monitoring set up
- [ ] Error tracking in place
- [ ] Documentation updated

### Final Verification
- [ ] Visit Vercel frontend URL - loads without errors
- [ ] Dashboard displays current stock data
- [ ] Scheduled pipeline has executed at least once
- [ ] No errors in Supabase logs
- [ ] No errors in Vercel function logs
- [ ] Data updates automatically on schedule

---

## Troubleshooting Guide

### Frontend Issues

#### Problem: "NEXT_PUBLIC_SUPABASE_URL not set"
```
Solution:
1. Go to Vercel → Project Settings → Environment Variables
2. Verify NEXT_PUBLIC_SUPABASE_URL is set
3. Redeploy: Vercel → Deployments → right-click latest → Redeploy
```

#### Problem: Vercel deployment fails with typescript errors
```
Solution:
1. Run locally: npm run build
2. Fix errors shown
3. Commit and push changes
4. Vercel will automatically redeploy
```

#### Problem: Frontend loads but shows no data
```
Solution:
1. Open browser F12 → Network tab
2. Check if Supabase requests show 200 status
3. If error, verify:
   - Supabase URL is correct
   - Anon key is correct
   - Database has data
4. Check browser Console for specific errors
```

### Database Issues

#### Problem: Supabase queries timeout
```
Solution:
1. Check table row count: SELECT COUNT(*) FROM daily_prices;
2. Add indexes (see Phase 5.1)
3. Optimize query filters
```

#### Problem: "This API key was not found"
```
Solution:
1. Supabase dashboard → Settings → API
2. Verify you're using the correct key:
   - Frontend: ANON key (NEXT_PUBLIC_*)
   - Backend: SERVICE_ROLE key
3. Never expose service role key in frontend!
```

### Python Backend Issues

#### Problem: Pipeline fails with "SUPABASE_URL not set"
```
Solution:
1. Verify .env file exists in python/ directory
2. Check file contains: SUPABASE_URL=...
3. Ensure file is NOT in .gitignore (it shouldn't be in production!)
4. For Render/AWS: Add environment variables in their dashboards
```

#### Problem: "Connection timeout to NEPSE API"
```
Solution:
1. Check internet connection: curl -I https://www.nepalstock.com
2. The NEPSE API may be temporarily down
3. Pipeline should retry automatically
4. Check logs for specific error message
5. Consider adding retry logic with exponential backoff
```

#### Problem: "Scheduled job didn't run"
```
Solution:
1. Verify cron schedule is correct:
   - Format: minute hour day month day-of-week
   - Example: 0 11 * * 0-4 (11 AM, Sun-Thu)
2. Check timezone settings (UTC vs Nepal time)
3. In GitHub Actions/Render, check "Events" or "Logs" tab
4. Manually trigger to test if configuration works
```

#### Problem: "ModuleNotFoundError: No module named 'nepse'"
```
Solution:
1. Ensure requirements.txt includes: nepse>=1.1.0
2. Run: pip install -r python/requirements.txt
3. For AWS: SSH into instance and reinstall
4. For Render: Update render.yaml with correct requirements file
5. Clear cache and redeploy
```

### Integration Issues

#### Problem: Frontend and backend on different domains (CORS error)
```
Solution:
1. If build new API server, add CORS headers:
   - In Flask: flask-cors
   - pip install flask-cors
   - from flask_cors import CORS; CORS(app)
2. Or use API Gateway (AWS, Render)
3. Configure allowed origins to include Vercel domain
```

#### Problem: Data not updating after scheduled run
```
Solution:
1. Manually trigger pipeline:
   cd python && python main.py --force
2. Check Supabase dashboard if data was actually inserted
3. Check frontend is fetching latest data (not using stale cache)
4. Refresh browser: Ctrl+Shift+Del (clear cache) then reload
5. Check Vercel deployment for recent changes
```

### Performance Issues

#### Problem: "Vercel function exceeded maximum duration"
```
Solution:
1. Optimize database queries
2. Limit data fetched: use pagination
3. Cache results on client
4. Consider breaking into smaller functions
5. For long operations, move to backend service (not Vercel Functions)
```

#### Problem: "Supabase hitting connection limit"
```
Solution:
1. Free tier limit: 20 concurrent connections
2. Verify no connection leaks in Python code
3. Use connection pooling for database
4. Consider upgrading to paid plan if consistently hitting limit
```

---

## Environment Variables Reference

### Frontend (.env.production)
```env
# Supabase - Safe to expose (ANON key only)
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsI...

# Optional: Backend API
NEXT_PUBLIC_API_BASE_URL=https://api.example.com
```

### Backend (python/.env - NEVER commit to Git)
```env
# Supabase - KEEP SECRET (SERVICE ROLE key)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional: Other API keys
NEPSE_API_KEY=your_key_here
DEBUG=false
```

---

## Quick Start Command Reference

### Local Development
```bash
# Install dependencies
cd web && npm install
cd ../python && pip install -r requirements.txt

# Run frontend
cd web && npm run dev
# Visit http://localhost:3000

# Run pipeline
cd python && python main.py --dry-run
cd python && python main.py --force
```

### Deployment
```bash
# Push to GitHub (triggers automatic Vercel deploy)
git add .
git commit -m "Your message"
git push

# Deploy frontend only
vercel --prod

# Manual backend deployment (varies by platform)
# Render: Check dashboard
# AWS: SSH and restart service
# GitHub Actions: Automatic on schedule
```

---

## Support & Next Steps

### Testing in Production
1. Visit `https://your-domain.vercel.app`
2. Check dashboard displays data
3. Wait for next scheduled pipeline run
4. Verify new data appears

### Monitoring
- Vercel: Dashboard → Analytics
- Supabase: Dashboard → Usage
- Backend: Platform-specific logs

### Future Improvements
- [ ] Add error tracking (Sentry.io)
- [ ] Set up alerts (PagerDuty/custom)
- [ ] Add automated tests
- [ ] Implement CI/CD best practices
- [ ] Add API documentation (Swagger)
- [ ] Scale to multiple regions
- [ ] Add user authentication
- [ ] Implement data caching strategy

---

## Common Questions

**Q: Can I run Python on Vercel?**  
A: No, Vercel is for Node.js/frontend. Use separate service for Python.

**Q: Do I need to pay for everything?**  
A: No! Use free tiers:
- Vercel: 100GB bandwidth/month free
- Supabase: 500MB database free
- Render: Free hobby tier
- GitHub Actions: 2000 minutes/month free

**Q: What if NEPSE API goes down?**  
A: Pipeline catches errors and retries. Check logs for details.

**Q: How often should pipeline run?**  
A: Currently 11 AM Nepal time (market opening), but you can adjust the schedule.

**Q: Can I run pipeline more frequently?**  
A: Yes, but NEPSE API updates ~once per hour. More frequent runs waste resources.

---

## Last Updated
April 2, 2026 - Complete deployment guide for NEPSE Stock Analyzer
