import requests
import json
from bs4 import BeautifulSoup

def main():
    url = "https://www.reuters.com/business/energy/military-activity-hits-water-supply-zaporizhzhia-nuclear-plant-nearby-town-iaea-2026-07-23/"
    
    # Query Wayback Machine API for availability
    api_url = f"https://archive.org/wayback/available?url={url}"
    try:
        resp = requests.get(api_url, timeout=10)
        data = resp.json()
        snapshots = data.get("archived_snapshots", {})
        if "closest" in snapshots:
            closest = snapshots["closest"]
            if closest.get("available"):
                snapshot_url = closest["url"]
                print("Found snapshot:", snapshot_url)
                
                # Fetch snapshot
                page_resp = requests.get(snapshot_url, timeout=15)
                print("Fetch status:", page_resp.status_code)
                soup = BeautifulSoup(page_resp.text, "html.parser")
                paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
                paragraphs = [p for p in paragraphs if len(p.split()) > 5]
                print(f"Parsed {len(paragraphs)} paragraphs from archive.")
                if paragraphs:
                    print("First paragraph:")
                    print("-", paragraphs[0])
                return
        print("No archive snapshot found.")
    except Exception as e:
        print("Archive lookup failed:", e)

if __name__ == "__main__":
    main()
