from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, args=["--disable-blink-features=AutomationControlled"])
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        viewport={"width": 1920, "height": 1080}
    )
    page = context.new_page()
    page.goto("https://www.nepalstock.com/robots.txt", wait_until="commit", timeout=30000)
    page.wait_for_timeout(2000)
    
    # Try fetching via page.evaluate
    js_code = """
    () => fetch('https://www.nepalstock.com/api/nots/nepse-data/todays-price/?businessDate=2026-03-26', {
            method: 'POST',
            body: JSON.stringify({ "id": 147, "businessDate": "2026-03-26" }),
            headers: {
                'Accept': 'application/json, text/plain, */*',
                'Content-Type': 'application/json'
            }
        }).then(res => res.text()).catch(e => "ERROR: " + e.toString())
    """
    
    csv = page.evaluate(js_code)
    print("Fetched CSV Sample:")
    print(csv[:300] if csv else "None")
    
    browser.close()
