"""
Quick smoke-test for NepseUnofficialApi.
Run this after installing the package to verify connectivity.

Usage: python test_nepse_live.py
"""

def main():
    print("🔍 Testing NepseUnofficialApi...")

    try:
        from nepse import Nepse
    except ImportError:
        print("❌ 'nepse' not installed. Run:")
        print("   pip install git+https://github.com/basic-bgnr/NepseUnofficialApi")
        return

    nepse = Nepse()
    nepse.setTLSVerification(False)

    # --- Company list ---
    print("\n[1] Company List (first 3):")
    try:
        companies = nepse.getCompanyList()
        for c in (companies or [])[:3]:
            print(f"    {c}")
        print(f"    Total companies: {len(companies or [])}")
    except Exception as e:
        print(f"    ERROR: {e}")

    # --- Live market summary ---
    print("\n[2] Market Summary:")
    try:
        summary = nepse.getSummary()
        print(f"    {summary}")
    except Exception as e:
        print(f"    ERROR: {e}")

    # --- NEPSE Index ---
    print("\n[3] NEPSE Index:")
    try:
        idx = nepse.getNepseIndex()
        print(f"    {idx}")
    except Exception as e:
        print(f"    ERROR: {e}")

    # --- Price/Volume (today's live prices) ---
    print("\n[4] Price/Volume (first 3 stocks):")
    try:
        pv = nepse.getPriceVolume()
        for item in (pv or [])[:3]:
            print(f"    {item}")
        print(f"    Total stocks with live price: {len(pv or [])}")
    except Exception as e:
        print(f"    ERROR: {e}")

    # --- Top Gainers ---
    print("\n[5] Top Gainers (top 3):")
    try:
        gainers = nepse.getTopGainers()
        for g in (gainers or [])[:3]:
            print(f"    {g}")
    except Exception as e:
        print(f"    ERROR: {e}")

    print("\n✅ Test complete!")

if __name__ == "__main__":
    main()
