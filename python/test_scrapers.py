import requests
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings()

headers = {"User-Agent": "Mozilla/5.0"}

def test_nepalipaisa():
    print("Testing Nepalipaisa...")
    try:
        r = requests.get('https://nepalipaisa.com/live-market', headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table')
        if not table:
            print("No table found")
            return
        rows = table.find_all('tr')
        if len(rows) > 1:
            cols = rows[1].find_all('td')
            print("Row 1 cols:", [c.text.strip() for c in cols])
        else:
            print("Table empty")
    except Exception as e:
        print("Error:", e)

def test_sharesansar():
    print("Testing ShareSansar Live Trading...")
    try:
        r = requests.get('https://www.sharesansar.com/live-trading', headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table')
        if not table:
            print("No table found")
            return
        rows = table.find_all('tr')
        if len(rows) > 1:
            cols = rows[1].find_all('td')
            print("Row 1 cols:", [c.text.strip() for c in cols])
    except Exception as e:
        print("Error:", e)

def test_merolagani():
    print("Testing Merolagani...")
    try:
        r = requests.get('https://www.merolagani.com/LatestMarket.aspx', headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        table = soup.find('table', class_='table')
        if not table:
            print("No table found")
            return
        rows = table.find_all('tr')
        if len(rows) > 1:
            cols = rows[1].find_all('td')
            print("Row 1 cols:", [c.text.strip() for c in cols])
    except Exception as e:
        print("Error:", e)

def test_nepalstock():
    print("Testing NepalStock Floor Sheet...")
    try:
        r = requests.get('https://www.nepalstock.com/floor-sheet', headers=headers, verify=False, timeout=10)
        soup = BeautifulSoup(r.text, 'lxml')
        # nepalstock is likely Angular SSR or CSR, let's see if there's any table
        table = soup.find('table')
        if table:
            rows = table.find_all('tr')
            if len(rows) > 1:
                cols = rows[1].find_all('td')
                print("Row 1 cols (SSR):", [c.text.strip() for c in cols])
        else:
            print("NepalStock requires API intercept. Length of HTML:", len(r.text))
            if "app-root" in r.text or "ng-version" in r.text:
                 print("NepalStock is an Angular app. We must find its API.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    test_nepalipaisa()
    test_sharesansar()
    test_merolagani()
    test_nepalstock()
