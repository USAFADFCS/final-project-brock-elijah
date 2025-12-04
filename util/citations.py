import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urlparse
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from playwright.sync_api import sync_playwright
import io
import pypdf
import re

# ==========================================
# 1. Helper: Text Sanitization
# ==========================================

def clean_text(text):
    """
    Removes newlines, normalizes whitespace (tabs/multiple spaces -> single space),
    and strips leading/trailing whitespace.
    """
    if not text:
        return None
    if not isinstance(text, str):
        text = str(text)
    # .split() without arguments splits on any whitespace (space, tab, newline, return, formfeed)
    # " ".join(...) reconstructs it with single spaces
    return " ".join(text.split())

# ==========================================
# 2. Fetching Logic (Resilience & Features)
# ==========================================

def _fetch_with_playwright(url, is_pdf=False):
    """
    Fallback: Fetches content using a headless Chromium instance masquerading as a human.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--disable-blink-features=AutomationControlled",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ]
            )
            
            # Context configuration to appear human
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080},
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            page = context.new_page()

            # Hide navigator.webdriver
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            try:
                # Wait for network idle to ensure dynamic metadata loads
                response = page.goto(url, wait_until="networkidle", timeout=30000)
            except Exception:
                # If timeout, try to grab what we have
                response = page.main_frame.page

            content = None
            if is_pdf:
                # If the URL is a PDF, we need the buffer
                if response:
                    content = response.body()
            else:
                # If HTML, we want the rendered text
                content = page.content()
            
            browser.close()
            return content

    except Exception as e:
        print(f"Playwright Error: {e}")
        return None

def fetch_content(url):
    """
    Attempts to fetch URL via requests; falls back to Playwright on error/bot-detection.
    Returns: (content, is_pdf_boolean)
    """
    is_pdf = url.lower().endswith(".pdf")
    
    # Configure robust session
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Referer': url,
    }
    session.headers.update(headers)
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 503, 504),
        allowed_methods=("HEAD", "GET", "OPTIONS")
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        resp = session.get(url, timeout=15, allow_redirects=True)
        if resp.status_code != 200:
            raise requests.RequestException(f"Non-200 Status: {resp.status_code}")
        
        if is_pdf:
            return resp.content, True
        return resp.text, False

    except requests.RequestException:
        # Fallback to Playwright
        content = _fetch_with_playwright(url, is_pdf)
        return content, is_pdf

# ==========================================
# 3. Parsing Logic (HTML & PDF)
# ==========================================

def parse_pdf_date(date_str):
    """
    Parses PDF standard date format: D:YYYYMMDDHHmmSS...
    """
    if not date_str: 
        return "n.d."
    # Regex to grab the YYYYMMDD part
    match = re.search(r'D:(\d{4})(\d{2})(\d{2})', str(date_str))
    if match:
        return f"{match.group(1)}-{match.group(2)}-{match.group(3)}"
    return "n.d."

def get_metadata(url):
    content, is_pdf = fetch_content(url)
    
    if content is None:
        return {"error": "Could not fetch content from URL"}

    # Initialize with cleaned URL domain as fallback
    meta = {
        "title": "No Title",
        "site_name": clean_text(urlparse(url).netloc),
        "author": None,
        "date": "n.d.",
        "url": url,
        "access_date": datetime.now()
    }

    try:
        if is_pdf:
            # --- PDF Parsing ---
            with io.BytesIO(content) as f:
                reader = pypdf.PdfReader(f)
                info = reader.metadata
                if info:
                    if info.title: 
                        meta["title"] = clean_text(info.title)
                    if info.author: 
                        meta["author"] = clean_text(info.author)
                    if '/CreationDate' in info: 
                        meta["date"] = parse_pdf_date(info['/CreationDate'])
            
            # Fallback if title is still missing (use filename)
            if meta["title"] == "No Title" or not meta["title"]:
                path = urlparse(url).path
                filename = path.split('/')[-1] if '/' in path else "PDF Document"
                meta["title"] = clean_text(filename)

        else:
            # --- HTML Parsing ---
            soup = BeautifulSoup(content, 'html.parser')
            
            # Title
            og_title = soup.find("meta", property="og:title")
            if og_title and og_title.get("content"):
                meta["title"] = clean_text(og_title["content"])
            elif soup.title and soup.title.string:
                meta["title"] = clean_text(soup.title.string)

            # Site Name
            og_site = soup.find("meta", property="og:site_name")
            if og_site and og_site.get("content"):
                meta["site_name"] = clean_text(og_site["content"])

            # Author
            auth_meta = soup.find("meta", attrs={'name': 'author'})
            if auth_meta and auth_meta.get("content"):
                meta["author"] = clean_text(auth_meta["content"])

            # Date (Clean to YYYY-MM-DD)
            pub_date = soup.find("meta", property="article:published_time")
            if pub_date and pub_date.get("content"):
                # Usually dates don't have newlines, but good to be safe
                cleaned_date = clean_text(pub_date["content"])
                meta["date"] = cleaned_date[:10] if cleaned_date else "n.d."

    except Exception as e:
        return {"error": str(e)}

    return meta

# ==========================================
# 4. Formatter Logic
# ==========================================

def mla_date_format(date_string):
    if date_string == "n.d." or not date_string:
        return ""
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%d")
        return dt.strftime("%d %b. %Y")
    except ValueError:
        return date_string

def format_mla(data):
    if "error" in data:
        return f"Error: {data['error']}"

    # Author
    if data['author']:
        names = data['author'].split()
        if len(names) >= 2:
            author_str = f"{names[-1]}, {' '.join(names[:-1])}."
        else:
            author_str = f"{data['author']}."
    else:
        author_str = "" 

    # Date
    pub_date_str = mla_date_format(data['date'])
    if pub_date_str:
        pub_date_str = f"{pub_date_str}," 
    
    # Access Date
    acc_date_str = data['access_date'].strftime("%d %b. %Y")

    # Assembly
    citation_parts = [
        author_str,
        f'"{data["title"]}."',
        f'*{data["site_name"]}*,',
        pub_date_str,
        f'{data["url"]}.',
        f'Accessed {acc_date_str}.'
    ]
    # Filter out empty strings and join
    citation = " ".join([p for p in citation_parts if p and p.strip()])
    return citation

def format_apa(data):
    if "error" in data:
        return f"Error: {data['error']}"
    
    # Author
    if data['author']:
        author_str = f"{data['author']}."
    else:
        author_str = f"{data['site_name']}."

    # Date
    if data['date'] != "n.d." and data['date'] is not None:
        date_str = f"({data['date']})."
    else:
        date_str = "(n.d.)."

    citation = f"{author_str} {date_str} *{data['title']}*. {data['site_name']}. {data['url']}"
    return citation

# ==========================================
# 5. Entry Points
# ==========================================

def get_citation_mla(url : str):
    meta = get_metadata(url)
    return format_mla(meta).replace("*", "") 

def get_citation_apa(url : str):
    meta = get_metadata(url)
    return format_apa(meta).replace("*", "")