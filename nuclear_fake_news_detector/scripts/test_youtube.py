import requests
import json
import re
from bs4 import BeautifulSoup

def main():
    url = 'https://www.youtube.com/watch?v=jmHLJwPzwxs'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    resp = requests.get(url, headers=headers)
    print('Status:', resp.status_code)

    title_match = re.search(r'<title>(.*?)</title>', resp.text)
    if title_match:
        print('Title:', title_match.group(1))

    soup = BeautifulSoup(resp.text, 'html.parser')
    
    title = ""
    og_title = soup.find('meta', property='og:title')
    if og_title and og_title.get('content'):
        title = og_title['content']
    elif soup.title:
        title = soup.title.string.replace('- YouTube', '').strip()
        
    desc = ""
    og_desc = soup.find('meta', property='og:description')
    if og_desc and og_desc.get('content'):
        desc = og_desc['content']
    else:
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            desc = meta_desc['content']
            
    print("Extracted Title:", title)
    print("Extracted Description:", desc)
    print("Combined length:", len(f"{title}. {desc}"))

if __name__ == '__main__':
    main()
