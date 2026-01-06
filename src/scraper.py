import os, zipfile, json, time
from datetime import datetime
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

AUTH_FILE = "outputs/auth.json"

def scrape_amazon_node(state):
    """Scrapes Amazon. Shows window for OTP if needed."""
    search_query = state["query"]
    results = []
    os.makedirs("outputs", exist_ok=True)
    
    with sync_playwright() as p:
        # Visible browser to allow manual OTP entry
        browser = p.chromium.launch(headless=False, args=["--no-sandbox"]) 
        context = browser.new_context(storage_state=AUTH_FILE) if os.path.exists(AUTH_FILE) else browser.new_context()
        page = context.new_page()

        page.goto("https://www.amazon.in")
        try:
            if not os.path.exists(AUTH_FILE):
                print("⚠️ PLEASE LOGIN & SUBMIT OTP ON SCREEN...")
                page.wait_for_selector("#twotabsearchtextbox", timeout=120000)
                context.storage_state(path=AUTH_FILE)

            page.fill("#twotabsearchtextbox", search_query)
            page.press("#twotabsearchtextbox", "Enter")
            page.wait_for_selector("[data-component-type='s-search-result']")

            for i in range(1, 3): # Scrape 2 pages
                soup = BeautifulSoup(page.content(), "html.parser")
                for item in soup.find_all("div", {"data-component-type": "s-search-result"}):
                    name = item.find("h2").text.strip() if item.find("h2") else "N/A"
                    price = item.find("span", {"class": "a-price-whole"}).text.strip() if item.find("span", {"class": "a-price-whole"}) else "N/A"
                    if name != "N/A": results.append({"name": name, "price": price})
                
                next_btn = page.query_selector("a.s-pagination-next")
                if next_btn: next_btn.click(); time.sleep(2)
                else: break
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            browser.close()
    return {"raw_data": results, "filtered_data": results}

def zip_exporter_node(state):
    """Saves ONLY the filtered data to the outputs folder."""
    os.makedirs("outputs", exist_ok=True)
    timestamp = datetime.now().strftime("%H%M%S")
    zip_path = os.path.join("outputs", f"amazon_data_{timestamp}.zip")
    json_path = zip_path.replace(".zip", ".json")

    data = state.get("filtered_data", state["raw_data"])
    with open(json_path, "w") as f: json.dump(data, f, indent=4)
    with zipfile.ZipFile(zip_path, 'w') as zf: zf.write(json_path, arcname="data.json")
    os.remove(json_path)
    return {"answer": f"📦 ZIP created: {zip_path}"}