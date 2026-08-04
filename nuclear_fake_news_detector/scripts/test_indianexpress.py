import requests
from bs4 import BeautifulSoup

def main():
    url = "https://www.bbc.co.uk/news/articles/c1112223334o"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print("Status code:", resp.status_code)
        print("Final URL:", resp.url)
        
        soup = BeautifulSoup(resp.text, "html.parser")
        title = soup.title.string if soup.title else ""
        print("Title:", title)
        
        paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
        paragraphs = [p for p in paragraphs if len(p.split()) > 4]
        print(f"Found {len(paragraphs)} paragraphs.")
        if paragraphs:
            print("First paragraph:", paragraphs[0])
    except Exception as e:
        print("Fetch error:", e)

if __name__ == "__main__":
    main()
