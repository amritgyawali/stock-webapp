# Market Trading Hours - Quick Reference

## 🕐 The Rule

```
Nepal Stock Market: 11:00 AM - 3:00 PM, Sun-Thu only

IF  current_time < 11:00 AM
    → Latest market data is from YESTERDAY (market hasn't opened)
    
ELSE current_time >= 11:00 AM
    → Latest market data is from TODAY (market open or closed)
    
IF  today is Friday or Saturday
    → Go back to last Thursday
```

---

## 📍 Current Status

**Time**: 10:55 AM Thursday, April 2, 2026

| Metric | Value |
|--------|-------|
| Current Time | 10:55 AM |
| Market Status | CLOSED (opens at 11:00 AM) |
| Latest Trading Date | **2026-04-01** ✓ |
| Data To Fetch | Yesterday's prices (April 1) |

---

## 🛠️ Implementation

### Frontend (page.tsx)
```typescript
// Already implemented ✓
const hour = nepalTime.getHours();
if (hour < 11) {
  tradingDate = yesterday;  // Use previous day
} else {
  tradingDate = today;      // Use current day
}
// Skip Fri/Sat
while (tradingDate.getDay() === 5 || 6) {
  tradingDate = previousDay;
}
```

### Python Backend (config.py)
```python
# Already available ✓
from config import get_latest_trading_date

trading_date = get_latest_trading_date()  # Returns correct date
# Use trading_date in all database queries
```

---

## 📊 Time Examples

| Time | Day | Result | Data Date |
|------|-----|--------|-----------|
| 10:30 AM | Thu | Before 11 AM | Yesterday (2026-04-01) |
| 11:30 AM | Thu | After 11 AM | Today (2026-04-02) |
| 2:00 PM | Thu | After 11 AM | Today (2026-04-02) |
| 10:30 AM | Fri | Before 11 AM | Wednesday (2026-04-01) |
| 11:30 AM | Fri | No trading | Thursday (2026-04-02) |
| Any time | Sat | No trading | Thursday (2026-04-02) |

---

## 💡 Usage

### In Python
```python
from config import get_latest_trading_date

date = get_latest_trading_date()
# Query database with this date
prices = db.select('daily_prices', '*', {'date': f'eq.{date}'})
```

### In TypeScript
```typescript
// Already in page.tsx - automatically handles it
// Just use the calculated todayNPT variable
```

---

## ✅ Verified Working

```bash
$ python -c "from config import get_latest_trading_date; print(get_latest_trading_date())"
2026-04-01 ✓ Correct!
```

Since it's 10:55 AM (before 11 AM), correctly returns yesterday's date.

---

## 🚨 Key Points

1. **Before 11 AM** always means yesterday's data
2. **Friday & Saturday** have no market trading
3. **Calendar date ≠ Trading date** (this was the confusion!)
4. **Frontend** has been updated with this logic
5. **Backend** has utility function ready to use

---

## 📋 Checklist

✅ Frontend (page.tsx) - Updated with market hours logic
✅ Backend (config.py) - Added get_latest_trading_date() function
✅ Testing - Verified correct behavior
✅ Documentation - Complete guides created
✅ Ready to use - No further changes needed

---

## 🎯 When to Apply

Use this logic whenever:
- Fetching stock prices from database
- Generating ML predictions
- Uploading data to database
- Displaying data on frontend
- Checking market status
- Comparing manual vs scraped data

**Always use trading date, not calendar date!**

---

## 📞 Support

Error/Question → Check:
- Time before 11 AM? → Use yesterday's date
- Is it Friday/Saturday? → Use last Thursday
- Still unsure? → Run `python market_trading_day.py`

