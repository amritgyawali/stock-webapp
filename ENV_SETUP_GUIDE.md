# Environment Variables Setup Guide

## 🔐 Security Important!

**NEVER commit .env files to Git!**

Create these files locally and in deployment platforms only. They contain sensitive credentials.

---

## Frontend Environment (.env.production)

**Location**: `web/.env.production`

**When to use**: Vercel production deployment (publicly safe - only contains public ANON key)

```env
# Supabase Configuration
# Use ANON key (safe for frontend - can be public)
NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Optional: Python Backend API URL
# Keep commented if not using custom API
# NEXT_PUBLIC_API_BASE_URL=https://api.yourdomain.com
```

### How to get these values:

1. Go to [supabase.com](https://supabase.com/dashboard)
2. Select your project
3. **Settings** → **API**
4. Copy:
   - **Project URL** → `NEXT_PUBLIC_SUPABASE_URL`
   - **Anon Key** → `NEXT_PUBLIC_SUPABASE_ANON_KEY`

### Where to add:

**Local Development**:
```bash
cd web
# Create .env.production file with values above
echo 'NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co' > .env.production
echo 'NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...' >> .env.production
```

**Vercel Cloud**:
```
Vercel Dashboard
  └─ Your Project
     └─ Settings
        └─ Environment Variables
           ├─ NEXT_PUBLIC_SUPABASE_URL = https://xxxxx.supabase.co
           ├─ NEXT_PUBLIC_SUPABASE_ANON_KEY = eyJhbGc...
           └─ Environment: Production, Preview, Development (as needed)
```

Click **"Save"** for each variable.

---

## Backend Environment (python/.env)

**Location**: `python/.env`

**When to use**: Local development and Python backend deployment (KEEP SECRET!)

```env
# ============================================
# SUPABASE CONFIGURATION (BACKEND)
# ⚠️ NEVER COMMIT THIS FILE TO GIT!
# ============================================

# Use SERVICE_ROLE key (private - backend only!)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# ============================================
# OPTIONAL: Additional Configuration
# ============================================

# Debug mode
DEBUG=false

# Logging level: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# Number of stocks to process (for testing)
# Leave empty or omit for all stocks
# STOCK_LIMIT=50
```

### How to get SERVICE_ROLE_KEY:

1. Go to [supabase.com](https://supabase.com/dashboard)
2. Select your project
3. **Settings** → **API**
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **Service Role Secret** → `SUPABASE_SERVICE_ROLE_KEY`

⚠️ **IMPORTANT**: Service Role Key is SECRET! Never expose in frontend or public code.

### Where to add:

**Local Development**:
```bash
cd python
# Create .env file with values
cat > .env << EOF
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
DEBUG=false
EOF
```

**Render.com** (if using Render):
```
Render Dashboard
  └─ Your Service
     └─ Environment
        ├─ SUPABASE_URL
        ├─ SUPABASE_SERVICE_ROLE_KEY
        └─ (set as secret)
```

**AWS EC2** (if using AWS):
```bash
# SSH into your instance
ssh -i your-key.pem ubuntu@your-ip

# Create .env in /home/ubuntu/stock-webapp/
nano python/.env
# Paste environment variables
# Ctrl+X, Y, Enter to save
```

**GitHub Actions** Secrets (if using GitHub Actions):
```
GitHub Repo
  └─ Settings
     └─ Secrets and variables
        └─ Actions
           ├─ SUPABASE_URL (New secret)
           ├─ SUPABASE_SERVICE_ROLE_KEY (New secret)
           └─ Save
```

Reference in workflow: `${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}`

---

## Environment Variables Summary Table

| Variable | Frontend | Backend | Value | Secret? |
|----------|----------|---------|-------|---------|
| `NEXT_PUBLIC_SUPABASE_URL` | ✓ | ✗ | `https://xxxxx.supabase.co` | No |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | ✓ | ✗ | `eyJhbGc...` (Anon key) | No |
| `SUPABASE_URL` | ✗ | ✓ | `https://xxxxx.supabase.co` | Yes |
| `SUPABASE_SERVICE_ROLE_KEY` | ✗ | ✓ | `eyJhbGc...` (Service key) | Yes |
| `DEBUG` | ✗ | ✓ | `false` or `true` | No |
| `LOG_LEVEL` | ✗ | ✓ | `INFO`, `DEBUG` | No |

---

## Step-by-Step Setup

### For Frontend (Vercel)

```bash
# 1. Create .env.production in web directory
cd web
echo 'NEXT_PUBLIC_SUPABASE_URL=https://xxxxx.supabase.co' > .env.production
echo 'NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGc...' >> .env.production

# 2. Verify file was created
cat .env.production

# 3. Add same to Vercel dashboard (see above)

# 4. Commit and push (git will ignore .env files automatically)
cd ..
git add web/.env.production  # Or leave out if in .gitignore
git commit -m "Add environment variables"
git push
```

### For Backend (Python)

**Local Setup**:
```bash
# 1. Create .env in python directory
cd python

# 2. Using PowerShell (Windows):
@'
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
DEBUG=false
'@ | Out-File -Encoding UTF8 .env

# 3. Or using bash/Linux:
cat > .env << EOF
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
DEBUG=false
EOF

# 4. Test it works
source venv/bin/activate  # Linux/Mac
# OR: .\venv\Scripts\activate  # Windows

python -c "from config import logger, SUPABASE_URL; print(f'✓ Config loaded: {SUPABASE_URL}')"

# 5. IMPORTANT: Do NOT commit .env to Git
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Add .env to gitignore"
```

**Remote Setup (e.g., AWS EC2)**:
```bash
# SSH into your server
ssh -i your-key.pem ubuntu@your-instance-ip

# Go to application directory
cd /home/ubuntu/stock-webapp

# Create .env with your credentials
cat > python/.env << EOF
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGc...
DEBUG=false
EOF

# Verify it's readable
cat python/.env
```

---

## Verifying Environment Variables

### Frontend Check

```bash
cd web
npm run build

# If build succeeds, environment variables are being read correctly
# Check in browser console (F12) if SUPABASE_URL is accessible
```

### Backend Check

```bash
cd python
source venv/bin/activate  # or .\venv\Scripts\activate

# Test environment variables are loaded
python -c "
from config import SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, logger
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    print('✓ All environment variables loaded successfully')
    print(f'  SUPABASE_URL: {SUPABASE_URL[:50]}...')
else:
    print('✗ Missing environment variables!')
    print(f'  SUPABASE_URL: {SUPABASE_URL}')
    print(f'  SUPABASE_SERVICE_ROLE_KEY: {SUPABASE_SERVICE_ROLE_KEY}')
"
```

---

## Troubleshooting

### Error: "SUPABASE_URL not set"

**Solution**:
```bash
# 1. Verify .env file exists in python directory
ls python/.env

# 2. Check file has correct content
cat python/.env

# 3. Reload environment (restart terminal/IDE)
# 4. In Render/AWS: verify secrets added to dashboard
# 5. Restart service if using systemd:
sudo systemctl restart nepse-pipeline
```

### Error: "Missing NEXT_PUBLIC_SUPABASE_URL"

**Solution**:
```bash
# 1. Verify .env.production exists in web directory
ls web/.env.production

# 2. Check Vercel dashboard has environment variables set
# 3. Redeploy on Vercel (settings → deployments → redeploy)
```

### Frontend shows "Not authenticated" but variables look correct

**Solution**:
```bash
# 1. Check you're using ANON key (not Service Role key)
# 2. Verify key starts with "eyJhbGc" (JWT format)
# 3. Check for typos in URLs
# 4. Clear browser cache: Ctrl+Shift+Del
# 5. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
```

### Python script can't connect to Supabase

**Solution**:
```bash
# 1. Test connectivity directly:
python -c "
import requests
import json

url = 'https://xxxxx.supabase.co/rest/v1/stocks?select=*&limit=1'
headers = {'apikey': 'YOUR_ANON_KEY'}

try:
    resp = requests.get(url, headers=headers, timeout=5)
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        print('✓ Connection successful')
    else:
        print(f'✗ Error: {resp.text}')
except Exception as e:
    print(f'✗ Connection failed: {e}')
"

# 2. Verify .env has SUPABASE_SERVICE_ROLE_KEY (not ANON key)
# 3. Check firewall/network allows HTTPS connections
```

---

## Best Practices

✅ **DO**:
- Store .env in `.gitignore`
- Use different keys for frontend (ANON) and backend (SERVICE_ROLE)
- Rotate keys regularly
- Keep Service Role key private
- Enable IP whitelist in Supabase if possible
- Use environment-specific variables (dev, staging, prod)

❌ **DON'T**:
- Commit .env files to Git
- Use Service Role key in frontend
- Hard-code credentials in code
- Share .env files over unencrypted channels
- Use same key for all environments
- Log sensitive credentials

---

## Quick Command Reference

```bash
# Check if variables are set (Linux/Mac)
echo $SUPABASE_URL
echo $SUPABASE_SERVICE_ROLE_KEY

# Check if variables are set (Windows PowerShell)
$env:SUPABASE_URL
$env:SUPABASE_SERVICE_ROLE_KEY

# Create .env from template
cp python/.env.example python/.env

# Add secret to Vercel from CLI
vercel env add NEXT_PUBLIC_SUPABASE_URL

# List all environment variables (Vercel)
vercel env list
```

---

Last Updated: April 2, 2026
