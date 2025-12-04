from tools.tool import Tool
from util.logs import Log
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from util.single_string_cleaner import clean_single_string
from util.ascii_filter import filter_non_ascii
from util.app_context import App_Context
from playwright.sync_api import sync_playwright
import io
import pypdf

MAX_CHARS = 50000


def extract_plaintext_from_html(html_content):
    """
    Extracts all visible plaintext from an HTML document.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()

    # Get all text and strip leading/trailing whitespace
    plaintext = soup.get_text(separator=' ', strip=True)
    return plaintext


def extract_text_from_pdf(pdf_bytes):
    """
    Extracts text from PDF binary data.
    """
    try:
        text = ""
        # Create a file-like object from the bytes
        with io.BytesIO(pdf_bytes) as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + " "
        return text
    except Exception as e:
        return f"Error extracting PDF text: {e}"


class SiteFetcherTool(Tool):
    name = "site-fetcher-tool"
    description = """
    Accepts a single string argument, the url of a site we want to visit. Requests the html of 
    that webpage from the internet, and parses out all of the plaintext. Returns that plain text
    as a single string. This is a fairly expensive operation, so only do it for sites that appear
    extremely promising. If this tool returns False, it is usually because the site is inaccessible.
    Move on to the next site in this eventuality. For security reasons, only use this on sites you
    find as part of a provided search tool. Do not follow links that you find on any site.
    """
    alias = "Fetch Sites"
    
    HEADLESS_MODE = True

    def __init__(self, ctx: App_Context):
        self.logger = ctx.log
        self.ctx = ctx

    def _fetch_with_playwright(self, url, is_pdf=False):
        """
        Fallback method to fetch site content using a headless browser.
        Returns bytes if is_pdf is True, otherwise returns HTML string.
        """
        self.logger.log(f"[SITE FETCHER TOOL] : Attempting fallback with Playwright for {url}...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=self.HEADLESS_MODE,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-setuid-sandbox"
                    ]
                )

                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080},
                    locale='en-US',
                    timezone_id='America/New_York'
                )

                page = context.new_page()

                # Mask automation
                page.add_init_script("""
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    });
                """)

                try:
                    response = page.goto(url, wait_until="networkidle", timeout=30000)
                except Exception:
                    self.logger.log("[SITE FETCHER TOOL] : Playwright network idle timeout, attempting capture.")
                    # If timeout, we still proceed to capture what we can
                    response = page.main_frame.page

                if is_pdf:
                    # For PDFs, we need the raw response body, not the page content (which would be the viewer)
                    # Note: response object is only valid if goto succeeded or partially succeeded
                    if response:
                         content = response.body()
                    else:
                        content = None
                else:
                    # For HTML, we want the rendered page content (DOM)
                    content = page.content()
                
                browser.close()
                return content

        except Exception as e:
            self.logger.log(f"[SITE FETCHER TOOL] : Playwright error: {e}")
            return None

    def use(self, args: str):
        url = clean_single_string(args)
        is_pdf = url.lower().endswith(".pdf")
        
        # --- Attempt 1: Fast Requests ---
        session = requests.Session()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
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

        raw_content = None # Can be bytes (PDF) or str (HTML)

        try:
            resp = session.get(url, timeout=10, allow_redirects=True)
            
            if resp.status_code != 200:
                self.logger.log(f"[SITE FETCHER TOOL] : Requests returned status {resp.status_code}. Triggering fallback.")
                raise requests.RequestException(f"Status Code {resp.status_code}")
            
            # If requests works:
            if is_pdf:
                raw_content = resp.content # bytes
            else:
                raw_content = resp.text # str

        except requests.RequestException as e:
            self.logger.log(f"[SITE FETCHER TOOL] : Standard fetch failed ({e}). Switching to Browser...")
            # --- Attempt 2: Playwright Fallback ---
            raw_content = self._fetch_with_playwright(url, is_pdf=is_pdf)

        if not raw_content:
            return False

        # --- Extraction ---
        if is_pdf:
            # raw_content should be bytes here
            if isinstance(raw_content, str):
                # Edge case: If playwright returned string for PDF (unlikely with .body() but possible on error), try encoding
                raw_content = raw_content.encode('utf-8')
            out = extract_text_from_pdf(raw_content)
        else:
            # raw_content should be string here
            if isinstance(raw_content, bytes):
                raw_content = raw_content.decode('utf-8', errors='ignore')
            out = extract_plaintext_from_html(raw_content)

        out = filter_non_ascii(out)
        if len(out) > MAX_CHARS:
            return out[:MAX_CHARS]
        return out