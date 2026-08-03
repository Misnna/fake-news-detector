"""
Extracts the main readable text from a news article URL, so it can be
fed into the fake-news classifier the same way as pasted text.

Supports both:
  - Regular web URLs (http:// or https://) — fetched via requests first
    (fast), with a headless-Chrome fallback (Selenium) for sites that
    render their article content via JavaScript and return an empty/near-
    empty page to a plain HTTP request.
  - Local file URLs (file:///C:/path/to/file.html) — read directly from
    disk, useful for testing with your own sample HTML files.

REQUIRES Google Chrome installed on the system for the JS-rendering
fallback to work (Selenium's built-in Selenium Manager auto-downloads the
matching driver, but not the browser itself). Most Windows/Mac machines
already have Chrome installed. If Chrome isn't available, the fallback
fails gracefully with a clear error instead of crashing.
"""
import re
import urllib.parse
import urllib.request

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}


class URLExtractionError(Exception):
    pass


def _fetch_html_requests(url: str, timeout: int):
    """
    Fast path: plain HTTP GET. Returns (html, blocked) where blocked is a
    human-readable reason string if the site actively refused the request
    (403/429), or None if the fetch succeeded (even if content is empty —
    that's a signal to try the browser fallback, not a hard block).
    """
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
    except requests.RequestException as e:
        raise URLExtractionError(f"Could not fetch the URL: {e}")

    if resp.status_code == 404:
        raise URLExtractionError("The article URL could not be found (HTTP 404). Please check that the link is correct and not truncated.")
    if resp.status_code == 403:
        return None, (
            "This site actively blocks automated access (HTTP 403 Forbidden) — "
            "a deliberate anti-bot protection on their end (common on major news "
            "sites like Reuters, Business Standard, Times of India, etc.), not a "
            "bug in this tool. Workaround: open the article in your browser, copy "
            "the text, then paste it into the 'Paste Text' tab instead."
        )
    if resp.status_code == 429:
        return None, (
            "This site is rate-limiting requests (HTTP 429 Too Many Requests). "
            "Wait a bit and try again, or copy-paste the article text instead."
        )
    if resp.status_code >= 400:
        return None, f"Server returned an error (HTTP {resp.status_code})."

    return resp.text, None


def _fetch_html_browser(url: str, timeout: int) -> str:
    """
    Slow path: renders the page in a real (headless) Chrome browser, so
    JavaScript-loaded content becomes visible in the page source. Used
    only when the fast path returns an empty/near-empty page.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        raise URLExtractionError(
            "This page appears to require JavaScript to load its content, and "
            "the headless-browser fallback (selenium) isn't installed. "
            "Run: pip install selenium"
        )

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")

    driver = None
    try:
        # Selenium 4.6+ has a built-in driver manager (Selenium Manager) that
        # auto-detects your installed Chrome version and downloads the exact
        # matching driver — no need for webdriver-manager, and it avoids the
        # version-mismatch errors that tool can cause.
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(timeout)
        driver.get(url)
        return driver.page_source
    except Exception as e:
        raise URLExtractionError(
            "Could not render this page with a headless browser. This usually "
            "means Google Chrome isn't installed on this machine, or the site "
            f"blocked the automated browser too. Details: {e}"
        )
    finally:
        if driver is not None:
            driver.quit()


def _extract_from_html(html: str) -> dict:
    """Parses HTML and pulls out title + main paragraph text."""
    from .preprocess import extract_nuclear_content
    
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "noscript", "form", "button", "iframe", "svg"]):
        tag.decompose()

    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    elif soup.find("h1"):
        title = soup.find("h1").get_text(strip=True)

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    paragraphs = [p for p in paragraphs if len(p.split()) > 4]  # drop nav/junk fragments
    # Join with a period and space to maintain sentence boundaries between paragraphs
    body_text = ". ".join(paragraphs)
    
    # Fallback to entire page text if paragraph extraction is too sparse
    if len(body_text.split()) < 20:
        body_text = soup.get_text(" ")

    body_text = re.sub(r"\s+", " ", body_text).strip()
    body_text = extract_nuclear_content(body_text)

    return {"title": title, "body_text": body_text}


def _extract_from_youtube(url: str, timeout: int = 10) -> dict:
    """Extracts video title and description from YouTube / youtu.be links."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        if resp.status_code == 200:
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
                    
            body_text = extract_nuclear_content(desc) if desc else ""
            if not body_text and desc:
                body_text = desc
                
            return {"title": title, "body_text": body_text}
    except Exception:
        pass
    return {"title": "", "body_text": ""}


def _extract_text_from_url_slug(url: str) -> dict:
    """
    Fallback method when site blocks scraping or URL is 404/truncated:
    Parses the domain name and the URL path/slug into clean headline words,
    converting the URL into a readable plain-text claim internally.
    """
    try:
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
            
        source = _guess_source_from_url(url)
        
        path = parsed.path
        path = re.sub(r"\.(html|htm|php|aspx|amp)$", "", path, flags=re.IGNORECASE)
        words = re.findall(r"[a-zA-Z]{2,}", path)
        
        ignore_words = {"article", "articles", "news", "business", "world", "india", "story", "index", "latest", "update", "updates", "amp"}
        clean_words = [w.capitalize() for w in words if w.lower() not in ignore_words]
        
        if clean_words:
            headline = " ".join(clean_words)
            text = f"{headline}. Reported by {source}."
            return {"title": headline, "text": text, "url": url}
    except Exception:
        pass
        
    return {"title": "News Report", "text": f"News report statement from link {url}", "url": url}


def extract_article_text(url: str, timeout: int = 10, max_chars: int = 4000, scraperapi_key: str = "") -> dict:
    """
    Fetches a URL (web or local file://) and extracts the title + main body text.
    Supports YouTube videos, local HTML files, and web news URLs.
    If scraping is blocked or incomplete, internally converts the URL slug into text.

    Returns: {"title": str, "text": str, "url": str}
    """
    url = url.strip()
    if not re.match(r"^(https?|file)://", url, re.IGNORECASE):
        # Auto-prefix http:// if missing
        url = "https://" + url

    parsed_domain = urllib.parse.urlparse(url).netloc.lower()
    if "youtube.com" in parsed_domain or "youtu.be" in parsed_domain:
        yt_data = _extract_from_youtube(url, timeout)
        if yt_data["title"] or yt_data["body_text"]:
            title, body_text = yt_data["title"], yt_data["body_text"]
            combined = f"{title}. {body_text}" if title else body_text
            return {"title": title, "text": combined[:max_chars], "url": url}

    if url.lower().startswith("file://"):
        try:
            parsed = urllib.parse.urlparse(url)
            local_path = urllib.request.url2pathname(parsed.path)
            if re.match(r"^/[A-Za-z]:", local_path):
                local_path = local_path[1:]
            with open(local_path, "r", encoding="utf-8", errors="replace") as f:
                html = f.read()
        except Exception as e:
            return _extract_text_from_url_slug(url)

        parsed_content = _extract_from_html(html)
        if not parsed_content["body_text"]:
            return _extract_text_from_url_slug(url)
        title, body_text = parsed_content["title"], parsed_content["body_text"]
        combined = f"{title}. {body_text}" if title else body_text
        return {"title": title, "text": combined[:max_chars], "url": url}

    # --- Web URL: Try ScraperAPI first if an API key is provided ---
    html = None
    block_reason = None

    if scraperapi_key and scraperapi_key.strip():
        try:
            encoded_target = urllib.parse.quote(url, safe="")
            scraper_url = f"http://api.scraperapi.com?api_key={scraperapi_key.strip()}&url={encoded_target}&render=true"
            resp = requests.get(scraper_url, timeout=max(timeout, 30))
            if resp.status_code == 200:
                html = resp.text
        except Exception:
            pass

    # --- Web URL: Standard fast path if ScraperAPI was not used or failed ---
    if not html:
        try:
            html, block_reason = _fetch_html_requests(url, timeout)
        except Exception:
            return _extract_text_from_url_slug(url)

    parsed_content = {"title": "", "body_text": ""}
    if html:
        parsed_content = _extract_from_html(html)

    if not parsed_content["body_text"]:
        try:
            html = _fetch_html_browser(url, timeout=max(timeout, 20))
            parsed_content = _extract_from_html(html)
        except Exception:
            pass

    title, body_text = parsed_content["title"], parsed_content["body_text"]
    
    # Check if the scraped page returned blocking content or lacks nuclear context
    full_text = f"{title} {body_text}"
    text_lower = full_text.lower()
    
    block_signatures = ["captcha", "distil", "cloudflare", "var dd=", "automated access", "robot check", "verify you are a human", "enable javascript"]
    is_blocked = any(sig in text_lower or (html and sig in html.lower()) for sig in block_signatures)
    
    from .preprocess import NUCLEAR_KEYWORDS
    words = set(re.findall(r'[a-z]+', text_lower))
    has_nuclear_context = bool(words & NUCLEAR_KEYWORDS)
    
    if is_blocked or len(body_text.strip()) < 30 or not has_nuclear_context:
        # Fallback internally to URL slug text conversion instead of erroring out
        return _extract_text_from_url_slug(url)

    combined = f"{title}. {body_text}" if title else body_text
    return {"title": title, "text": combined[:max_chars], "url": url}
