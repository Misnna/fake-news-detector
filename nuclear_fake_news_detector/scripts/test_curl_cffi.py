from curl_cffi import requests
from bs4 import BeautifulSoup

def main():
    url = "https://www.reuters.com/business/energy/military-activity-hits-water-supply-zaporizhzhia-nuclear-plant-nearby-town-iaea-2026-07-23/"
    try:
        # Use curl_cffi requests to impersonate a real Chrome 120 browser
        resp = requests.get(url, impersonate="chrome120", timeout=15)
        print("Status code:", resp.status_code)
        
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string if soup.title else ""
        print("Page Title:", title)
        
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        paragraphs = [p for p in paragraphs if len(p.split()) > 4]
        
        print(f"Parsed {len(paragraphs)} paragraphs.")
        if paragraphs:
            print("First paragraph:")
            print("-", paragraphs[0])
    except Exception as e:
        print("Fetch failed:", e)

if __name__ == "__main__":
    main()
