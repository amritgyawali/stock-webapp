# Testing & Verification Guide

## Complete Verification Procedures for Deployment

Use this guide to verify each component works before marking a phase as complete.

---

## Pre-Deployment Verification (LOCAL)

### ✅ Step 1: Database Connection Test

**Location**: Work in `python/` directory

```bash
cd python
source venv/bin/activate  # Windows: .\venv\Scripts\activate

# Test 1: Check environment variables are loaded
python -c "
from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, logger
print(f'✓ SUPABASE_URL: {SUPABASE_URL[:50]}...')
print(f'✓ SERVICE_ROLE_KEY loaded: {bool(SUPABASE_SERVICE_ROLE_KEY)}')
"

# Test 2: Test actual database connection
python -c "
from config import db
try:
    result = db.select('stocks', columns='symbol,name', limit=1)
    if result:
        print(f'✓ Database connection works!')
        print(f'✓ Sample: {result[0]}')
    else:
        print('✗ Database returned empty')
except Exception as e:
    print(f'✗ Database error: {e}')
"
```

**Expected Output**:
```
✓ SUPABASE_URL: https://xxxxx.supabase.co...
✓ SERVICE_ROLE_KEY loaded: True
✓ Database connection works!
✓ Sample: {'symbol': 'NABIL', 'name': 'Nepal Abil Bank Ltd...'}
```

**If failed**:
- [ ] Check `.env` file exists in `python/` directory
- [ ] Verify `SUPABASE_SERVICE_ROLE_KEY` is correct (from Supabase)
- [ ] Ensure Supabase project URL is correct
- [ ] Check internet connection

---

### ✅ Step 2: Frontend Build Test

**Location**: Work in `web/` directory

```bash
cd web
npm install  # Install deps if not already done

# Test 1: Check TypeScript compilation
npm run build

# Expected output should end with:
# ✓ Compiled successfully
```

**Expected**: Build completes with no errors

**If failed**:
- [ ] Check for TypeScript errors: `npm run lint`
- [ ] Ensure all imports are correct
- [ ] Clear cache: `rm -rf .next` and try again
- [ ] Check `node_modules` isn't corrupted: delete and reinstall

```bash
# Test 2: Run locally
npm run start
# Visit http://localhost:3000
# Press Ctrl+C to stop
```

**Expected**: 
- [ ] Page loads without errors
- [ ] Dashboard displays (even if no data)
- [ ] No errors in browser console (F12)

---

### ✅ Step 3: Pipeline Execution Test

**Location**: Work in `python/` directory

```bash
cd python
source venv/bin/activate

# Test 1: Dry run (no database changes)
python main.py --dry-run
```

**Expected Output**:
```
======================================================
🚀 NEPSE Stock Analyzer — Daily Pipeline
📅 Nepal Time: 2026-04-02 XX:XX:XX NPT
🔧 Mode: DRY RUN
======================================================
🧪 DRY RUN — testing connectivity only
✓ Supabase connection: OK
✓ NEPSE API connection: OK
```

**If failed**:
- [ ] Check network connection
- [ ] Verify Supabase is accessible
- [ ] Check NEPSE API isn't down

```bash
# Test 2: Full pipeline run (will modify database!)
python main.py --force
```

**Expected**: Takes 3-5 minutes, completes with:
```
====================================================
📊 PIPELINE COMPLETE:
  Companies synced:  624
  Prices stored:     268
  Predictions:       100
  Accuracy updated:  ✓
  Total time:        145.23s
====================================================
```

---

### ✅ Step 4: Data Verification

After pipeline runs, verify data was stored:

```bash
# Check what was stored
python -c "
from config import db
from datetime import datetime, timedelta
from datetime import timezone as tz

# Get today's date in Nepal timezone
nepal_offset = 5.75  # 5:45 offset
nepal_now = datetime.now(tz.utc).astimezone(tz.timezone(timedelta(hours=nepal_offset)))
today_date = nepal_now.strftime('%Y-%m-%d')

# Check daily prices
prices = db.select('daily_prices', 
                  columns='symbol,close,date',
                  filters={'date': f'eq.{today_date}'},
                  limit=5)
print(f'\n✓ Found {len(prices)} prices for {today_date}')
for p in prices:
    print(f'  {p[\"symbol\"]}: {p[\"close\"]}')

# Check predictions
preds = db.select('predictions',
                 columns='symbol,predicted_close,date',
                 filters={'date': f'eq.{today_date}'},
                 limit=5)
print(f'\n✓ Found {len(preds)} predictions for {today_date}')
for p in preds:
    print(f'  {p[\"symbol\"]}: {p[\"predicted_close\"]}')
"
```

**Expected Output**:
```
✓ Found 268 prices for 2026-04-02
  NABIL: 2850.5
  SHEL: 315.0
  KKHC: 261.9
  ...

✓ Found 100 predictions for 2026-04-02
  NABIL: 2860.0
  SHEL: 318.0
  ...
```

---

## Frontend Deployment Verification (VERCEL)

### ✅ Step 1: Deployment Success Check

1. Go to [vercel.com](https://vercel.com/dashboard)
2. Select your project
3. Go to **Deployments** tab
4. Latest deployment should have:
   - [ ] Status: ✓ Ready (green checkmark)
   - [ ] Build: ✓ Passed
   - [ ] No red X marks

### ✅ Step 2: Frontend URL Access

1. Click the production domain link
2. Should load the dashboard
3. Check browser console (F12 → Console):
   - [ ] No red errors
   - [ ] No warnings about missing env vars

### ✅ Step 3: Network Connection Test

In browser console (F12 → Console), run:

```javascript
// Test Supabase connection
fetch('https://xxxxx.supabase.co/rest/v1/stocks?limit=1&select=symbol', {
  headers: {
    'apikey': 'NEXT_PUBLIC_SUPABASE_ANON_KEY'
  }
})
.then(r => r.json())
.then(data => console.log('✓ Supabase connected:', data[0]))
.catch(e => console.error('✗ Error:', e))
```

**Expected**: Should log a stock object

### ✅ Step 4: Data Display Test

On dashboard, verify all sections:
- [ ] Stock data loads
- [ ] Charts render
- [ ] Predictions display
- [ ] No "undefined" values
- [ ] Prices match what's in database

### ✅ Step 5: Environment Variables Test

In browser console:

```javascript
// This is safe - these are public values
console.log('SUPABASE_URL:', process.env.NEXT_PUBLIC_SUPABASE_URL)
console.log('Has ANON_KEY:', !!process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)
```

Should show your Supabase URL.

---

## Backend Deployment Verification (by platform)

### ✅ GitHub Actions

#### Step 1: Workflow Registration

```
GitHub Repo
  → Actions tab
    → Should show "Daily NEPSE Pipeline" in list
```

#### Step 2: Manual Trigger Test

```
Actions → Daily NEPSE Pipeline
  → Run workflow (top button)
  → Call this the "test run"
  → Wait 2-5 minutes
  → Should see green checkmark
```

#### Step 3: Scheduled Run Verification

```
After initial test:
  → Wait for next scheduled time (11 AM UTC)
  → Go to Actions tab
  → New run should appear at scheduled time
  → Should have green checkmark
```

#### Step 4: Data Update Verification

After workflow runs:
```bash
# Check if new data was stored
python -c "
from config import db
from datetime import datetime, timezone, timedelta

# Current time in Nepal
nepal_offset = timedelta(hours=5, minutes=45)
nepal_now = datetime.now(timezone.utc).astimezone(timezone(nepal_offset))
today_date = nepal_now.strftime('%Y-%m-%d')

# Count prices for today
prices = db.select('daily_prices',
                  columns='count',
                  filters={'date': f'eq.{today_date}'})
print(f'Latest prices count: {prices[0] if prices else 0}')
"
```

Should show latest data was stored.

---

### ✅ Render.com

#### Step 1: Deployment Verification

```
Render Dashboard
  → Select your cron job
    → Status should show "Active"
    → No error indicators
```

#### Step 2: Manual Test

```
Select your cron job
  → Click "Manual Trigger"
  → Go to "Events" tab
  → New event should appear
  → Wait for completion (should be green)
```

#### Step 3: Schedule Verification

```
After manual test:
  → Wait for next scheduled time
  → New event should appear automatically
  → Check logs to ensure success
```

#### Step 4: Check Logs

```
Render Dashboard
  → Your service
    → "Logs" tab
    → Should see output from main.py --force
    → Look for: "✓ PIPELINE COMPLETE"
```

---

### ✅ AWS EC2

#### Step 1: Instance Verification

```bash
# On local machine
ssh -i nepse-key.pem ubuntu@your-instance-ip
# Should connect successfully
```

#### Step 2: Service Status

```bash
# Once connected to instance
sudo systemctl status nepse-pipeline.service

# Expected output:
# ● nepse-pipeline.service - NEPSE Stock Pipeline
#    Loaded: loaded (...)
#    Active: active (running) since ...
#    ...
```

#### Step 3: Manual Test

```bash
# On instance
source /home/ubuntu/stock-webapp/venv/bin/activate
cd /home/ubuntu/stock-webapp
python python/main.py --force

# Should complete successfully
```

#### Step 4: Cron Schedule Verification

```bash
# Check crontab
crontab -l

# Should show:
# 15 5 * * 0-4 cd /home/ubuntu/stock-webapp && ...

# Check cron execution logs
sudo journalctl -u nepse-pipeline | head -50
```

---

## Integration Testing (All Components Together)

### ✅ Test 1: Full Data Flow

1. **Backend runs** (manually trigger or wait for schedule)
2. **Database gets updated** (verify in Supabase)
3. **Frontend fetches data** (visit Vercel URL)
4. **User sees latest data** (refresh dashboard)

**Verification Steps**:
```bash
# In python directory, force a run
python main.py --force

# Wait 1 minute for completion
# Then visit Vercel frontend
# Verify data displays and is recent
```

### ✅ Test 2: Specific Stock Verification

Choose a specific stock (e.g., SHEL) and trace it:

1. **Check database**:
```sql
SELECT symbol, close, date FROM daily_prices 
WHERE symbol = 'SHEL' 
ORDER BY date DESC 
LIMIT 1;
```

2. **Check prediction**:
```sql
SELECT symbol, predicted_close, date FROM predictions
WHERE symbol = 'SHEL'
ORDER BY date DESC
LIMIT 1;
```

3. **Check frontend**: Visit Vercel URL, search for SHEL, verify it matches database

### ✅ Test 3: Time-Based Logic

Verify market hours logic is working:

```python
# Test in python directory
from config import get_latest_trading_date, get_nepal_time

nepal_now = get_nepal_time()
trading_date = get_latest_trading_date()

print(f'Current Nepal time: {nepal_now}')
print(f'Trading date to use: {trading_date}')

# If time is before 11 AM, trading_date should be yesterday
# If time is after 11 AM, trading_date should be today
# If weekend, trading_date should be last trading day
```

---

## Performance Testing

### ✅ Test 1: Frontend Performance

In browser, open F12 → Performance tab:

1. Reload page
2. Click the red circle to record
3. Wait for page to fully load
4. Stop recording
5. Check metrics:
   - [ ] Page load < 3 seconds
   - [ ] FCP (First Contentful Paint) < 1.5s
   - [ ] LCP (Largest Contentful Paint) < 2.5s

### ✅ Test 2: Database Query Performance

```bash
# On instance or locally
cd python

# Time the pipeline execution
time python main.py --force

# Should complete in < 5 minutes
# If longer, database might have performance issues
```

### ✅ Test 3: API Response Time

```bash
# Test Supabase API response time
python -c "
import time
import requests as req
from config import SUPABASE_REST_URL, SUPABASE_HEADERS

start = time.time()
resp = req.get(f'{SUPABASE_REST_URL}/stocks?limit=100', 
               headers=SUPABASE_HEADERS)
elapsed = time.time() - start

print(f'Response time: {elapsed*1000:.0f}ms')
print(f'✓ Fast' if elapsed < 0.5 else f'⚠ Slow')
"
```

---

## Error Scenario Testing

### ✅ Test 1: No Internet Connection

Simulate by turning off Wi-Fi or unplugging network:

```bash
# Frontend should show graceful error
# Backend should retry on next schedule
```

### ✅ Test 2: Database Unavailable

Temporarily disable network, then re-enable:

```bash
# Frontend should show cached data or error
# Backend should handle exception and log it
```

### ✅ Test 3: NEPSE API Down

Try to fetch from NEPSE API:

```python
import requests
resp = requests.get('https://www.nepalstock.com/api/...')
print(resp.status_code)  # If 500+, API is down

# Verify backend continues (uses cached/manual data)
```

---

## Checklist: All Tests Passing

- [ ] Local database connection works
- [ ] Local frontend build succeeds
- [ ] Local pipeline execution works
- [ ] Frontend deploys to Vercel successfully
- [ ] Vercel frontend loads without errors
- [ ] Backend service is running (or scheduled)
- [ ] Backend can read/write to database
- [ ] Manual backend trigger works
- [ ] Automatic scheduled run works
- [ ] Data flows from backend to frontend
- [ ] Performance is acceptable
- [ ] Error handling works

---

## Troubleshooting Verification Failures

### "Database connection failed"
```
1. Check credentials in .env file
2. Verify Supabase project is active (not sleeping)
3. Check firewall allows HTTPS to Supabase
4. Test with: curl https://xxxxx.supabase.co/rest/v1/
```

### "Frontend build failed"
```
1. Run: npm run lint (find TypeScript errors)
2. Clear cache: rm -rf .next node_modules .next
3. Reinstall: npm install
4. Build again: npm run build
```

### "Backend service won't start"
```
1. Check service status: systemctl status nepse-pipeline
2. Check logs: journalctl -u nepse-pipeline -n 50
3. Verify .env file exists
4. Test manually: python main.py --force
```

### "No data appearing in frontend"
```
1. Check if backend ran: Did scheduled time pass?
2. Manually trigger backend: python main.py --force
3. Check database: SELECT COUNT(*) FROM daily_prices
4. Check frontend network tab (F12): Is API call succeeding?
5. Refresh frontend: Ctrl+Shift+R
```

---

## Sign-Off Checklist

When all tests pass, you can sign off on each phase:

### Database Phase ✓
- [ ] Supabase project created
- [ ] Tables exist with data
- [ ] Credentials are saved and secure
- [ ] Connection test passes

### Frontend Phase ✓
- [ ] Code commited to GitHub
- [ ] Vercel deployment succeeds
- [ ] Dashboard accessible and loads data
- [ ] No errors in console

### Backend Phase ✓
- [ ] Service running and healthy
- [ ] Manual trigger works
- [ ] Scheduled runs execute
- [ ] Data stored in database

### Integration Phase ✓
- [ ] Backend updates database
- [ ] Frontend fetches and displays data
- [ ] All components working together
- [ ] Performance is acceptable

---

Last Updated: April 2, 2026
