#!/usr/bin/env python3
"""Reset SHEL to correct price of 315 and verify database"""
from config import db

print("=" * 70)
print("🔧 Fixing SHEL Price")
print("=" * 70)

# Update SHEL to correct price
try:
    result = db.update(
        'daily_prices',
        {'close': 315.0, 'open': 329.0, 'high': 333.0, 'low': 311.0},
        {'stock_id': 'eq.2934', 'date': 'eq.2026-04-02'}
    )
    print("✅ SHEL price updated to 315.0")
    
    # Verify
    shel = db.select('daily_prices', '*', {'stock_id': 'eq.2934', 'date': 'eq.2026-04-02'}, limit=1)
    if shel:
        p = shel[0]
        print(f"\n✅ SHEL (2026-04-02) - VERIFIED:")
        print(f"   Symbol: SHEL")
        print(f"   Close: {p.get('close')} (Expected: 315.0)")
        print(f"   Open: {p.get('open')} (Expected: 329.0)")
        print(f"   High: {p.get('high')} (Expected: 333.0)")
        print(f"   Low: {p.get('low')} (Expected: 311.0)")
        print(f"   Volume: {p.get('volume')} (Expected: 475191)")
        
        # Check if correct
        if p.get('close') == 315.0:
            print("\n🎯 ✅ SHEL IS NOW CORRECT: 315.0")
        else:
            print(f"\n❌ ERROR: SHEL close is still {p.get('close')}")
    else:
        print("❌ SHEL not found in database")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
