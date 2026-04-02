"""Check actual confidence values in database"""
from config import db

# Get ALL predictions and filter by date
preds = db.select('predictions', columns='stock_id, predicted_close, confidence_score, prediction_date', limit=500)

# Filter for 2026-04-02
preds_today = [p for p in preds if p.get('prediction_date') == '2026-04-02']

print(f"Found {len(preds_today)} predictions for 2026-04-02")
print("\nSample predictions with confidence values:")
for i, p in enumerate(preds_today[:5]):
    stock_id = p.get('stock_id')
    conf = p.get('confidence_score')
    pred_close = p.get('predicted_close')
    print(f"  {i+1}. Stock ID {stock_id}: confidence_score = {conf} (type: {type(conf).__name__}), predicted_close = {pred_close}")
