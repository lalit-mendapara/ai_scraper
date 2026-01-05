from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def run_scraper(url: str):
    """
    Uses Playwright to navigate and BeautifulSoup to parse.
    """
    with sync_playwright() as p:
        # 1. ADD USER-AGENT: This tells the website you are a real Chrome browser, not a bot.
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled", # Hides the automation flag
                "--no-sandbox"
            ]
        )
        # Create a context with the user agent
        context = browser.new_context(user_agent=user_agent)
        page = context.new_page()

        print(f"Opening browser to: {url}")
        try:
            # Navigate with a generous timeout for heavy pages
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            # 2. WAIT FOR CONTENT: Instead of just 'body', wait for article-related tags
            page.wait_for_selector("p", timeout=10000) 
            
            html = page.content()
            soup = BeautifulSoup(html, "html.parser")
            
            # 3. EXTRACTION LOGIC: Actually find and clean the text
            # We look for all paragraph tags and join them into one string
            paragraphs = soup.find_all('p') # Web-element
            text_content = " ".join([p.get_text() for p in paragraphs])
            
            # Basic check: if we got very little text, we might be blocked
            if len(text_content) < 100:
                print("Warning: Very little text found. The site might be blocking us.")
                return "Error: Content could not be extracted (possibly blocked)."

            # Return the first 2000 characters so we don't exceed AI token limits
            return text_content[:2000]

        except Exception as e:
            print(f"Scraping failed: {e}")
            return "Error: Could not load page"
        finally:
            browser.close()