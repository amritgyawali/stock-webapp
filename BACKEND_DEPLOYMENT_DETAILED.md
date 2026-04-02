# Backend Deployment Deep Dive

## Complete Guide for Python Backend Deployment

This guide covers detailed setup for each backend deployment option. Choose ONE platform below based on your needs.

---

## Comparison Table

| Platform | Cost | Difficulty | Uptime | Best For | Cold Starts |
|----------|------|-----------|--------|----------|-------------|
| **GitHub Actions** | FREE | ⭐ Easy | 99% | Scheduled tasks, CI/CD | N/A (local) |
| **Render** | Free-$7/mo | ⭐ Easy | 99.95% | Simple backend, cron jobs | Yes (free tier) |
| **Railway** | Pay-as-you-go | ⭐⭐ Medium | 99.9% | Flexible scaling | Depends |
| **AWS EC2** | $5+/mo | ⭐⭐⭐ Hard | 99.99% | Full control, advanced | No (always running) |
| **DigitalOcean** | $5+/mo | ⭐⭐ Medium | 99.99% | Simple VPS | No (always running) |

**Recommendation for first-time users**: **GitHub Actions** (free) → **Render** (easy paid option)

---

## Option 1: GitHub Actions (100% FREE)

### Why GitHub Actions?
- ✅ Completely FREE
- ✅ No credit card needed
- ✅ Perfect for scheduled tasks
- ✅ 2000 minutes/month free (plenty for daily runs < 5 min)
- ✅ Integrated with GitHub
- ❌ Max 6 hours per job (not limiting for us)
- ❌ Not suitable for always-on APIs

### Setup (5 minutes)

#### Step 1: Create Workflow Directory

```bash
cd c:\Users\amrit\stock-webapp

# Create GitHub Actions directory
mkdir -p .github/workflows
```

#### Step 2: Create Workflow File

Create `.github/workflows/daily-pipeline.yml`:

```yaml
name: Daily NEPSE Pipeline

on:
  # Schedule: Run at 11:00 UTC
  # This is 4:45 PM Nepal time (but we adjust in code for 11 AM)
  schedule:
    - cron: '0 11 * * 0-4'  # 11 AM UTC, Sunday-Thursday
  
  # Allow manual trigger for testing
  workflow_dispatch:

jobs:
  pipeline:
    runs-on: ubuntu-latest
    timeout-minutes: 30  # Max 30 minutes (usually takes <5)
    
    steps:
    # Step 1: Checkout code
    - name: Checkout Repository
      uses: actions/checkout@v3
    
    # Step 2: Setup Python
    - name: Set up Python 3.11
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
        cache: 'pip'  # Cache pip dependencies for speed
    
    # Step 3: Install dependencies
    - name: Install Dependencies
      run: |
        cd python
        pip install --upgrade pip
        pip install -r requirements.txt
    
    # Step 4: Run dry-run test
    - name: Test Configuration (Dry Run)
      env:
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
      run: |
        cd python
        python main.py --dry-run
    
    # Step 5: Run actual pipeline
    - name: Run Daily Pipeline
      env:
        SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
        SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
      run: |
        cd python
        python main.py --force
    
    # Step 6: Notify on failure (optional)
    - name: Notify on Failure
      if: failure()
      run: |
        echo "Pipeline failed! Check logs at: https://github.com/${{ github.repository }}/actions"
```

#### Step 3: Add GitHub Secrets

1. Go to your GitHub repository
2. **Settings** (top menu)
3. **Secrets and variables** → **Actions** (left sidebar)
4. Click **"New repository secret"**
5. Add these secrets:

| Secret Name | Value |
|------------|-------|
| `SUPABASE_URL` | https://xxxxx.supabase.co |
| `SUPABASE_SERVICE_ROLE_KEY` | eyJhbGc... (from Supabase) |

Click "Add secret" for each.

#### Step 4: Commit and Deploy

```bash
# Add workflow file
git add .github/workflows/daily-pipeline.yml
git commit -m "Add GitHub Actions daily pipeline"
git push
```

#### Step 5: Verify Setup

1. Go to your GitHub repo
2. Click **"Actions"** tab
3. Should see "Daily NEPSE Pipeline" workflow listed
4. Click it → **"Run workflow"** → **"Run workflow"** (test manually)
5. Should see job starts running (orange circle)
6. Wait 2-3 minutes for completion
7. Should see green checkmark if successful

#### Monitoring

```
GitHub repo
  → Actions tab
    → Daily NEPSE Pipeline
      → Select workflow run
        → Check logs in real-time
```

---

## Option 2: Render.com (EASY PAID)

### Why Render?
- ✅ Python-friendly
- ✅ Cron jobs support
- ✅ Auto-deploys from GitHub
- ✅ Free tier available (limited)
- ✅ Simple dashboard
- ❌ Free tier has cold starts
- ❌ Free tier sleeps after 15 min inactivity

### Setup (10 minutes)

#### Step 1: Create Render Account

1. Go to [render.com](https://render.com)
2. Click **"Sign up"**
3. Choose **"GitHub"** (link your GitHub account)
4. Authorize Render to access your repos

#### Step 2: Deploy as Cron Job

1. Render dashboard → **"New +"** (top right)
2. Select **"Cron Job"**
3. Configuration:

```
Name: nepse-daily-pipeline
Language: Python 3.11
Repository: stock-webapp (your fork)
Branch: main
Root Directory: ./  (leave as is)
Build Command: pip install -r python/requirements.txt
Start Command: python python/main.py --force
```

4. Scroll down → **"Schedule"**:
```
0 11 * * 0-4
↑ ↑ ↑ ↑ ↑
│ │ │ │ └─ Day of week (0-6): 0-4 = Sun-Thu
│ │ │ └─── Month (1-12): * = every month
│ │ └───── Day of month: * = every day
│ └─────── Hour (0-23): 11
└───────── Minute: 0
```

5. Click **"Create Cron Job"** (don't worry about free tier warning)

#### Step 3: Add Environment Variables

1. In Render dashboard, select your service
2. **"Settings"** → **"Environment"** (left sidebar)
3. Click **"Add Environment Variable"**
4. Add:

```
SUPABASE_URL = https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY = eyJhbGc...
```

5. Mark as **"Secret"** (toggle the secret button)
6. Click **"Save Changes"**

#### Step 4: Test Deployment

1. In Render dashboard
2. Click **"Manual Trigger"** (or wait for schedule)
3. Watch logs in **"Events"** tab
4. Should see job run instantly
5. Check for success/failure in logs

#### Monitoring

```
Render dashboard
  → Your service
    → Events (shows past runs)
    → Logs (real-time output)
    → Health (status page)
```

---

## Option 3: AWS EC2 (POWERFUL BUT COMPLEX)

### Why AWS EC2?
- ✅ Full control over environment
- ✅ Always-running instance (no cold starts)
- ✅ Cheap ($5-12/month for micro)
- ✅ Scalable for future growth
- ❌ Requires system administration
- ❌ More complex setup
- ❌ Need to manage security, updates

### Setup (30-45 minutes)

#### Phase 1: Create EC2 Instance (10 min)

1. Go to [aws.amazon.com/console](https://console.aws.amazon.com/)
2. Search for **"EC2"** in services
3. Click **"Launch Instance"**

Configuration:
```
Name: nepse-stock-backend
AMI: Ubuntu 22.04 LTS (check "Free tier eligible")
Instance type: t2.micro (free tier)
Key pair: NEW → nepse-key → Download nepse-key.pem
    ⚠️ SAVE THIS FILE! You'll need it to login
Security group: Create new
    Inbound rules:
    - SSH (22) from 0.0.0.0/0 (or your IP only)
    - HTTP (80) from 0.0.0.0/0
    - HTTPS (443) from 0.0.0.0/0
Storage: 20 GB (free tier)
```

5. Click **"Launch"**
6. Wait 2-3 minutes for instance startup
7. Copy **Public IPv4 address** (shown in Instances list)

#### Phase 2: Connect via SSH (5 min)

**Windows PowerShell**:
```powershell
# If you don't have SSH installed, install via WSL:
# Or use PuTTY

# Set permissions on key
icacls "C:\path\to\nepse-key.pem" /grant:r "$($env:USERNAME):(F)"

# Remove other permissions
icacls "C:\path\to\nepse-key.pem" /inheritance:r

# SSH into instance (replace with your instance IP)
ssh -i "C:\path\to\nepse-key.pem" ubuntu@54.123.45.67
```

**Linux/Mac**:
```bash
# Set key permissions
chmod 600 ~/Downloads/nepse-key.pem

# SSH into instance
ssh -i ~/Downloads/nepse-key.pem ubuntu@54.123.45.67
```

✅ Should now be logged into the server

#### Phase 3: Setup Python Environment (10 min)

```bash
# 1. Update system
sudo apt update && sudo apt upgrade -y

# 2. Install Python and dependencies
sudo apt install -y python3-pip python3-venv git curl

# 3. Create application directory
mkdir -p /home/ubuntu/stock-webapp
cd /home/ubuntu/stock-webapp

# 4. Clone your GitHub repository
git clone https://github.com/YOUR_USERNAME/stock-webapp.git .
# If private repo, use: git clone https://YOUR_TOKEN@github.com/...

# 5. Create virtual environment
python3 -m venv venv

# 6. Activate virtual environment
source venv/bin/activate

# 7. Install Python dependencies
pip install --upgrade pip
pip install -r python/requirements.txt
```

#### Phase 4: Configure .env File (5 min)

```bash
# Create .env file
sudo nano python/.env

# Paste your environment variables:
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
DEBUG=false

# Save: Ctrl+X, then Y, then Enter
```

Verify it worked:
```bash
source /home/ubuntu/stock-webapp/venv/bin/activate
cd /home/ubuntu/stock-webapp
python -c "from config import SUPABASE_URL; print(f'✓ Loaded: {SUPABASE_URL}')"
```

#### Phase 5: Setup Systemd Service (Auto-start)

```bash
# Create service file
sudo nano /etc/systemd/system/nepse-pipeline.service
```

Paste this:
```ini
[Unit]
Description=NEPSE Stock Pipeline Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/stock-webapp
Environment="PATH=/home/ubuntu/stock-webapp/venv/bin"
ExecStart=/home/ubuntu/stock-webapp/venv/bin/python /home/ubuntu/stock-webapp/python/main.py --force
Restart=on-failure
RestartSec=300  # Retry after 5 minutes if fails

[Install]
WantedBy=multi-user.target
```

Save: Ctrl+X, Y, Enter

#### Phase 6: Setup Cron for Scheduling

```bash
# Open crontab editor
crontab -e

# Add this line (runs at 5:15 UTC = 11 AM Nepal time+daylight adjustment)
# Actually use 11:00 UTC for Nepal 4:45 PM, but code adjusts
15 5 * * 0-4 cd /home/ubuntu/stock-webapp && source venv/bin/activate && python python/main.py --force >> /tmp/nepse-pipeline.log 2>&1

# Save: Ctrl+X, Y, Enter
```

#### Phase 7: Enable and Start Service

```bash
# Enable service to auto-start on reboot
sudo systemctl enable nepse-pipeline.service

# Start service now
sudo systemctl start nepse-pipeline.service

# Check status
sudo systemctl status nepse-pipeline.service

# View service logs
sudo journalctl -u nepse-pipeline -f
```

#### Phase 8: Verify Everything Works

```bash
# Manually trigger pipeline
source /home/ubuntu/stock-webapp/venv/bin/activate
cd /home/ubuntu/stock-webapp
python python/main.py --force

# Check logs
tail -f /tmp/nepse-pipeline.log

# Exit tail: Ctrl+C
```

#### Monitoring

```bash
# Check service status
sudo systemctl status nepse-pipeline

# View recent logs
sudo journalctl -u nepse-pipeline -n 50

# View cron execution logs
grep CRON /var/log/syslog

# Monitor resource usage
top
# Press 'q' to quit
```

---

## Comparison: Running Pipeline

### GitHub Actions
```bash
# Nothing to do! Runs automatically on schedule
# To manually trigger:
# 1. Go to GitHub repo → Actions tab
# 2. Select workflow
# 3. Click "Run workflow"
```

### Render
```bash
# To manually trigger:
# 1. Go to Render dashboard
# 2. Select your cron job
# 3. Click "Manual Trigger"

# Check logs: Events tab in dashboard
```

### AWS EC2
```bash
# Manually run (for testing):
ssh -i nepse-key.pem ubuntu@your-ip
source /home/ubuntu/stock-webapp/venv/bin/activate
cd /home/ubuntu/stock-webapp
python python/main.py --force

# Check cron logs:
sudo journalctl -u nepse-pipeline -f
```

---

## Troubleshooting by Platform

### GitHub Actions Issues

**Problem**: "Workflow not running"
```
Solution:
1. Check Actions tab - should show workflow
2. Click workflow → "Run workflow" → test manually
3. Verify schedule syntax: 0 11 * * 0-4
4. Check secrets are set (Settings → Secrets)
```

**Problem**: "ModuleNotFoundError"
```
Solution:
1. Verify python/requirements.txt is correct
2. Check step installs: pip install -r python/requirements.txt
3. Try manual: python -m pip install -r python/requirements.txt
```

### Render Issues

**Problem**: "Cron job won't run"
```
Solution:
1. Check "Events" tab - shows execution history
2. Verify schedule: 0 11 * * 0-4
3. Click "Manual Trigger" to test
4. Check "Logs" tab for error messages
```

**Problem**: "Build fails"
```
Solution:
1. Go to render.yml → Build command
2. Verify: pip install -r python/requirements.txt
3. Check python/requirements.txt exists and is valid
4. Try manual deploy: git push (triggers rebuild)
```

### AWS EC2 Issues

**Problem**: "Can't SSH into instance"
```
Solution:
1. Check key permissions: chmod 600 nepse-key.pem
2. Verify public IP didn't change
3. Check security group allows SSH port 22
4. Try: ssh -i nepse-key.pem -v ubuntu@ip (verbose mode)
```

**Problem**: "Service won't start"
```
Solution:
1. Check status: sudo systemctl status nepse-pipeline
2. Check logs: sudo journalctl -u nepse-pipeline -n 20
3. Verify .env file exists: ls -la python/.env
4. Test manually: python python/main.py --force
```

**Problem**: "Cron not running at scheduled time"
```
Solution:
1. Check crontab: crontab -l
2. Verify time format is correct
3. Check system timezone: date
4. View cron logs: grep CRON /var/log/syslog
5. Test job manually to ensure it works
```

---

## Cost Breakdown

### GitHub Actions (RECOMMENDED FOR START)
```
Monthly Cost: $0 (FREE!)
- 2000 free minutes/month
- Each run: ~2-3 minutes
- Total runs possible: ~600/month
- Our usage: ~30/month (1 per day)

Perfect for: Scheduled tasks, testing
```

### Render
```
Free Tier: $0/month
- Cron jobs run
- Limited resources
- Cold starts (~30 sec warmup)

Paid Tier: $7/month
- Always-running instance
- No cold starts
- Better performance
```

### AWS EC2
```
Monthly Cost: $5-12/month
- t2.micro: ~$10-12/month (eligible for 1 year free)
- Data transfer: usually minimal
- Storage: 20GB included

Perfect for: Always-on services, high traffic
```

---

## Quick Command Reference

```bash
# GitHub Actions - Check status
# (Go to GitHub repo → Actions tab)

# Render - Test
curl -X GET https://api.render.com/v1/services  # Check if deployed

# AWS - Check service
sudo systemctl status nepse-pipeline
sudo journalctl -u nepse-pipeline -n 20

# AWS - Check cron
crontab -l
sudo journalctl -n 100 | grep CRON

# All - Test pipeline manually
cd python
source venv/bin/activate
python main.py --dry-run
python main.py --force
```

---

## Next Steps After Deployment

1. Monitor first few runs to ensure data flows correctly
2. Set up alerts for failures (platform-specific)
3. Document your setup for future reference
4. Plan backup strategy
5. Consider horizontal scaling as usage grows

---

Last Updated: April 2, 2026
