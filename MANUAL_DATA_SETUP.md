# Manual Stock Data Setup - Quick Start

## ✅ Setup Complete

The system is now ready to accept manual stock price data!

### 📁 Folder Location
```
c:\Users\amrit\stock-webapp\manual stocks data\
```

### 📋 Steps to Use

#### 1️⃣ **Prepare Your Data**
Save the official NEPSE daily price list as a CSV file. Example:
- Filename: `Today's Price - 2026-04-02.csv`
- Or any name like: `nepse-daily.csv`, `stock-prices.csv`, etc.

Required columns (case-insensitive):
- **Symbol** (e.g., SHEL, KKHC, HBL)
- **Business Date / Date** (e.g., 2026-04-02)
- **Close Price / Close** (e.g., 315.0)
- Optional: Open, High, Low, Volume, Turnover

#### 2️⃣ **Upload the CSV**
Copy your CSV file to:
```
manual stocks data/Today's Price - 2026-04-02.csv
```

#### 3️⃣ **Run the Pipeline**
The system will automatically:
- Load your manual data
- Compare with scraped data (if it runs)
- Priority: **Manual data takes precedence over scraped**
- Upload the verified data to database

```bash
cd python
python main.py --force
```

#### 4️⃣ **View Results**
Frontend will display:
- ✅ Your manual prices (if provided)
- ✅ Filled in with scraped data (where manual is missing)
- ✅ Warnings for any price mismatches

### 🔄 Workflow

```
CSV Upload → System Detects → Compares with Scrape → 
Uses Manual Data → Uploads to DB → Frontend Updates
```

### 📊 What Happens with Each Stock

| Scenario | Action |
|----------|--------|
| Manual data × Scraped data available | ✅ Use manual (verified) |
| Manual price ≠ Scraped price | ⚠️ Use manual, log warning |
| Manual data only | ✅ Use manual |
| Scraped data only | ✅ Use scraped |
| Neither | ❌ Stock skipped |

### 🧪 Test It

To see if your CSV is being detected:
```bash
cd python
python manual_data_merger.py
```

Should show:
```
Available dates in manual data:
  2026-04-02: 268 records
```

### 📝 Example CSV Format

| Symbol | Business Date | Open Price | High Price | Low Price | Close Price | Total Traded Quantity | Total Traded Value |
|--------|---------------|-----------|-----------|----------|------------|----------------------|-------------------|
| SHEL   | 2026-04-02    | 329       | 333       | 311      | 315        | 475191               | 151061691.4        |
| KKHC   | 2026-04-02    | 288       | 290       | 285      | 285.8      | 45000                | 12861000           |

### 🔧 Technical Details

**Files involved:**
- `python/manual_data_merger.py` - Load & merge manual data
- `python/integration_helper.py` - Integration with main pipeline
- `manual stocks data/README.md` - Full documentation

**How it works:**
1. Reads CSV from `manual stocks data/` folder
2. Detects date from Business Date / Date column
3. Extracts symbol, close price, volume, turnover, etc.
4. Creates lookup table indexed by symbol
5. Merges with scraped data (manual takes priority)
6. Returns merged list with statistics

### ✨ Features

✅ Automatic date detection from CSV
✅ Flexible column naming (case-insensitive)
✅ Multiple CSV files supported (merged together)
✅ Price conflict detection and warnings
✅ Fallback to scraped data for missing stocks
✅ Full data provenance tracking

### 🚀 Ready to Use!

You're all set! Just:
1. Save your daily NEPSE CSV
2. Put it in `manual stocks data/` folder
3. Run `python main.py --force`
4. The frontend will update automatically!

---

**Need help?** Check `manual stocks data/README.md` for detailed documentation.
