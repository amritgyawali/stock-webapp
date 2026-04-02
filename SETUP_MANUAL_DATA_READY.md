# ✅ Manual Stock Data System - READY TO USE

## What's Been Set Up

### 📁 Folder Created
```
c:\Users\amrit\stock-webapp\manual stocks data\
```

**Purpose**: Upload your daily NEPSE official stock price CSVs here. The system will automatically detect, load, and use them.

---

## How to Use

### Step 1: Save Your Daily CSV
From official NEPSE website, save the daily price list as CSV:
```
Filename: Today's Price - 2026-04-02.csv
(or any name ending in .csv)

Location: c:\Users\amrit\stock-webapp\manual stocks data\
```

### Step 2: Run the Pipeline
```bash
cd c:\Users\amrit\stock-webapp\python
python main.py --force
```

### Step 3: System Automatically
- ✅ Detects your CSV in the folder
- ✅ Loads the official NEPSE prices
- ✅ Compares with any scraped data
- ✅ Uses manual data (official) as priority
- ✅ Uploads verified prices to database
- ✅ Frontend refreshes with correct prices

---

## 📊 What You Get

| Before | After |
|--------|-------|
| Possibly stale prices | ✅ Official NEPSE prices |
| Mix of sources | ✅ Prioritized manual data |
| No conflict checking | ✅ Detects & logs mismatches |
| Scraper dependency | ✅ Manual data takes priority |

---

## 📝 CSV Format

Your CSV just needs these columns (names are flexible, case-insensitive):

| Column | Examples | What It Does |
|--------|----------|-------------|
| **Symbol** | SHEL, KKHC, HBL | Stock identifier |
| **Business Date** | 2026-04-02 | Trading date (YYYY-MM-DD) |
| **Close Price** | 315.0 | Closing price |
| **Open Price** | 329 | (optional) |
| **High Price** | 333 | (optional) |
| **Low Price** | 311 | (optional) |
| **Volume** | 475191 | (optional) Trading quantity |
| **Turnover** | 151061691.4 | (optional) Total value |

### Example CSV Content
```csv
Symbol,Business Date,Open Price,High Price,Low Price,Close Price,Total Traded Quantity,Total Traded Value
SHEL,2026-04-02,329,333,311,315,475191,151061691.4
KKHC,2026-04-02,288,290,285,285.8,45000,12861000
HBL,2026-04-02,218,218,206.8,208.9,145294,30462367.3
```

---

## 🔄 How It Works

```
1. CSV Upload
   ↓
2. System Detection
   "Found: Today's Price - 2026-04-02.csv"
   ↓
3. Load Manual Data
   Extracted: 268 stocks from CSV
   ↓
4. Compare with Scraped (if available)
   SHEL: Manual=315.0 vs Scraped=314.5 → Use Manual ✓
   ↓
5. Merge Data
   260 from manual + 5 from scraper = 265 total
   ↓
6. Upload to Database
   INSERT INTO daily_prices
   ↓
7. Frontend Updates
   User sees: SHEL = 315.0 ✅
```

---

## 📂 Files Created

### Python Scripts
```
python/
├── manual_data_merger.py         ← Core merge engine
├── integration_helper.py         ← Pipeline integration
└── demo_manual_data_processing.py ← Visual walkthrough
```

### Documentation
```
manual stocks data/
└── README.md                     ← Detailed CSV format guide

root/
├── MANUAL_DATA_SETUP.md          ← Quick start
└── MANUAL_DATA_COMPLETE_SETUP.md ← Full documentation
```

---

## 🧪 Test It

### See Full Workflow Demo
```bash
cd python
python demo_manual_data_processing.py
```

Output shows:
- Scraped data vs Manual data
- Conflict detection
- Merge decisions
- Final results

### Check Current Status
```bash
python -c "from manual_data_merger import list_available_manual_data; print(list_available_manual_data())"
```

Returns available dates in uploaded CSVs:
```
{'2026-04-02': 268, '2026-04-01': 265}
```

### Verify for Today
```bash
python -c "from integration_helper import check_manual_data_status; print(check_manual_data_status())"
```

---

## ⚙️ System Behavior

### Scenario 1: Only Manual Data Available
```
CSV uploaded, no scraper running
→ System uses ALL manual data
→ Frontend shows official NEPSE prices ✅
```

### Scenario 2: Both Manual and Scraped
```
CSV uploaded, scraper also ran
→ System merges both
→ Prioritizes manual where both exist
→ Uses scraper as fallback for missing stocks
→ Logs any price conflicts
```

### Scenario 3: Only Scraped Data
```
No CSV uploaded, scraper ran
→ System uses scraper data
→ Works like before (no manual override)
```

### Scenario 4: Neither Manual nor Scraped
```
No CSV, no scraper, database already has data
→ Uses existing database data
→ Continues to show old prices (no new data)
```

---

## 🎯 Priority Order

The system uses data in this order:
1. **Manual CSV** (Official NEPSE data) ← HIGHEST PRIORITY
2. Scraped web data (fallback)
3. Existing database data (if no new data)

**Result**: Your app always tries to use official NEPSE data first!

---

## 📢 Notifications

When prices differ, system logs:
```
⚠️ SHEL: Manual=315.0 vs Scraped=314.5 → Using MANUAL
✓ Merged: 260 from manual + 5 from scraper = 265 total
✓ Uploaded to database
```

You can see all conflicts in the merge statistics.

---

## 🚀 Ready to Go!

Your system is now production-ready:

✅ Folder created: `manual stocks data/`
✅ Python scripts: manual_data_merger, integration_helper, demo
✅ Documentation: Multiple guides included
✅ Tested: Full demo workflow verified

### Next Steps:
1. Download daily NEPSE CSV
2. Save to `manual stocks data/` folder  
3. Run `python main.py --force`
4. Check frontend for updated prices

---

## 💡 Tips

- **Multiple CSVs?** No problem! Save multiple dates, system handles all
- **Column names?** System auto-detects (case-insensitive)
- **Missing data?** Falls back to scraper gracefully
- **Format issues?** Check `manual stocks data/README.md`
- **Troubleshooting?** See `MANUAL_DATA_COMPLETE_SETUP.md`

---

**The system is ready! Upload your first CSV and test it out.** 🎉
