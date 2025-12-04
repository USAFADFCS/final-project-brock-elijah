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

    def _is_pdf_content(self, content_bytes, headers=None):
        """
        Helper to detect if content is PDF based on Magic Bytes or Headers.
        """
        # Check Magic Bytes (%PDF-)
        if content_bytes and content_bytes.startswith(b'%PDF'):
            return True
        
        # Check Headers
        if headers:
            content_type = headers.get('Content-Type', '').lower()
            if 'application/pdf' in content_type:
                return True
        return False

    def _fetch_with_playwright(self, url):
        """
        Primary method: Fetch site content using a headless browser.
        Returns (content, is_pdf_boolean).
        """
        self.logger.log(f"[SITE FETCHER TOOL] : Attempting primary fetch with Playwright for {url}...")
        
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
                    # Wait for domcontentloaded to ensure we get the response object
                    response = page.goto(url, wait_until="domcontentloaded", timeout=30000)
                except Exception:
                    self.logger.log("[SITE FETCHER TOOL] : Playwright network idle timeout, attempting capture.")
                    response = page.main_frame.page

                final_content = None
                is_pdf = False

                if response:
                    try:
                        # 1. Inspect raw body for PDF signature
                        body_bytes = response.body()
                        headers = response.all_headers()

                        if self._is_pdf_content(body_bytes, headers):
                            is_pdf = True
                            final_content = body_bytes
                        else:
                            # 2. If not PDF, wait for network idle to ensure JS rendering is done
                            try:
                                page.wait_for_load_state("networkidle", timeout=5000)
                            except:
                                pass # Proceed with what we have
                            final_content = page.content()
                    except Exception as e:
                         self.logger.log(f"[SITE FETCHER TOOL] : Error reading Playwright response body: {e}")

                browser.close()
                return final_content, is_pdf

        except Exception as e:
            self.logger.log(f"[SITE FETCHER TOOL] : Playwright error: {e}")
            return None, False

    def _fetch_with_requests(self, url):
        """
        Fallback method: Fetch site content using standard requests library.
        Returns (content, is_pdf_boolean).
        """
        self.logger.log(f"[SITE FETCHER TOOL] : Attempting fallback fetch with Requests for {url}...")
        
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

        try:
            resp = session.get(url, timeout=10, allow_redirects=True)
            
            if resp.status_code != 200:
                self.logger.log(f"[SITE FETCHER TOOL] : Requests returned status {resp.status_code}.")
                return None, False
            
            if self._is_pdf_content(resp.content, resp.headers):
                return resp.content, True # bytes
            else:
                return resp.text, False # str

        except requests.RequestException as e:
            self.logger.log(f"[SITE FETCHER TOOL] : Requests fetch failed: {e}")
            return None, False

    def use(self, args: str):
        url = clean_single_string(args)
        
        raw_content = None 
        is_pdf = False

        # --- Attempt 1: Playwright (Default) ---
        raw_content, is_pdf = self._fetch_with_playwright(url)

        # --- Attempt 2: Requests (Fallback) ---
        if not raw_content:
            self.logger.log("[SITE FETCHER TOOL] : Playwright failed to retrieve content. Switching to Requests fallback...")
            raw_content, is_pdf = self._fetch_with_requests(url)

        if not raw_content:
            return False

        # --- Extraction ---
        if is_pdf:
            # raw_content should be bytes here
            if isinstance(raw_content, str):
                raw_content = raw_content.encode('utf-8')
            out = extract_text_from_pdf(raw_content)
        else:
            # raw_content should be string here
            if isinstance(raw_content, bytes):
                raw_content = raw_content.decode('utf-8', errors='ignore')
            out = extract_plaintext_from_html(raw_content)

        out = filter_non_ascii(out)
        if len(out) > MAX_CHARS:
            out = out[:MAX_CHARS]
        
        # Add to visited sites for citation tracking
        self.ctx.all_visited_sites.append(url) 
        return out