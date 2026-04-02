# Manual Stocks Data Folder

This folder is for uploading daily stock price data manually in CSV format.

## How It Works

1. **Upload CSV Files**: Place your daily stock price CSV files in this folder
2. **Automatic Detection**: The system will automatically detect and load CSV files
3. **Data Prioritization**: 
   - If **manual data** is available, it will be used
   - If **scraped data** conflicts with manual data, manual takes priority
   - If **manual data** is missing for some stocks, scraped data is used as fallback
4. **Same Data**: If manual and scraped match, they're considered verified

## CSV File Format

Your CSV files should contain at least these columns (column names are flexible, case-insensitive):

```
Symbol              (or: symbol, security symbol, sec symbol)
Business Date       (or: date, trading_date, business date)
Close Price         (or: close, close price, last price)
Open Price          (or: open, open price)
High Price          (or: high, high price, highest price)
Low Price           (or: low, low price, lowest price)
Total Traded Quantity  (or: volume, quantity, traded qty)
Total Traded Value  (or: turnover, traded value, value)
Previous Day Close Price (or: prev close, previous close)
```

## Example Format

| Symbol | Business Date | Open Price | High Price | Low Price | Close Price | Total Traded Quantity | Total Traded Value |
|--------|---------------|-----------|-----------|----------|------------|----------------------|-------------------|
| SHEL   | 2026-04-02    | 329       | 333       | 311      | 315        | 475191               | 151061691.4        |
| KKHC   | 2026-04-02    | 288       | 290       | 285      | 285.8      | 45000                | 12861000           |
| HBL    | 2026-04-02    | 218       | 218       | 206.8    | 208.9      | 145294               | 30462367.3         |

## Workflow

### Daily Process

1. Save the official NEPSE daily price list as CSV in this folder
   ```
   Filename: Today's Price - 2026-04-02.csv
   Location: manual stocks data/Today's Price - 2026-04-02.csv
   ```

2. Run the data pipeline:
   ```bash
   python main.py --force
   ```

3. The system will:
   - Load your manual CSV data
   - Compare with scraped data (if any conflicts exist, will use manual)
   - Upload the verified/merged data to the database
   - Generate warnings for price mismatches (for your review)

### Data Merge Logic

```
For each stock:
  If manual data exists
    ✓ Use manual data (prioritized)
    ⚠ Warn if scraped price differs
  Else if scraped data exists
    ✓ Use scraped data
  Else
    ✗ Stock skipped (no data available)

Result: Merged dataset with manual data taking priority
```

## File Naming

Use any of these naming patterns:
- `Today's Price - 2026-04-02.csv`
- `nepse-prices-2026-04-02.csv`
- `daily-prices-2026-04-02.csv`
- `stock-data.csv`
- Any name, as long as it's a `.csv` file

The system automatically detects the date from the CSV's "Business Date" or "Date" column.

## Verification

To see what manual data has been loaded:
```bash
python -c "from manual_data_merger import list_available_manual_data; print(list_available_manual_data())"
```

Expected output:
```
{
  '2026-04-02': 268,  # 268 stocks for April 2
  '2026-04-01': 265   # 265 stocks for April 1
}
```

## Integration with Pipeline

The manual data merger is automatically integrated into:
- `main.py` - Main data pipeline
- `predictor.py` - ML prediction pipeline
- Data upload to Supabase

## Troubleshooting

**Q: Why is my manual data not being used?**
- Check the date in the CSV matches today's date
- Verify the CSV is in the `manual stocks data` folder
- Ensure column names contain "Symbol", "Date", or "Close"

**Q: Can I mix manual data from multiple sources?**
- Yes! Place multiple CSVs in the folder, they'll be merged
- If the same stock appears in multiple files, the first match is used

**Q: What if the CSV has extra columns?**
- Extra columns are ignored automatically
- Only required columns are extracted and used

## Support

For issues or questions about the data format, check:
- `python manual_data_merger.py` - Run in test mode to see what's being loaded
- `main.py --dry-run` - Preview how data will be processed
