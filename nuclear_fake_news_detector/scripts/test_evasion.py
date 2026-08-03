from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def main():
    options = Options()
    # options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")

    driver = webdriver.Chrome(options=options)
    
    # Hide webdriver flag using CDP script injection
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    })

    try:
        url = "https://www.reuters.com/business/energy/military-activity-hits-water-supply-zaporizhzhia-nuclear-plant-nearby-town-iaea-2026-07-23/"
        driver.get(url)
        html = driver.page_source
        
        soup = BeautifulSoup(html, "html.parser")
        title = soup.title.string if soup.title else ""
        print("Page Title:", title)
        
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        paragraphs = [p for p in paragraphs if len(p.split()) > 4]
        
        print(f"Found {len(paragraphs)} paragraphs.")
        if paragraphs:
            print("First 3 paragraphs:")
            for p in paragraphs[:3]:
                print("-", p)
        else:
            print("No paragraphs found.")
            # Print first 200 chars of body
            if soup.body:
                print("Body snippet:", soup.body.get_text()[:300])
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
