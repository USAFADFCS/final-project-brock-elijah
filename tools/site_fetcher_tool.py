from tools.tool import Tool
from util.logs import Log
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
from util.single_string_cleaner import clean_single_string
from util.ascii_filter import filter_non_ascii

MAX_CHARS = 50000


def extract_plaintext_from_html(html_content):
    """
    Extracts all visible plaintext from an HTML document.

    Args:
        html_content (str): The HTML content as a string.

    Returns:
        str: The extracted plaintext.
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # Remove script and style elements, as their content is not visible plaintext
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()

    # Get all text and strip leading/trailing whitespace, joining with spaces
    plaintext = soup.get_text(separator=' ', strip=True)
    return plaintext


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

    def __init__(self, logger: Log):
        self.logger = logger

    def use(self, args: str):
        args = clean_single_string(args)
        # Create a session that looks more like a real browser and will retry transient failures
        session = requests.Session()

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,'
                      'image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Referer': args,
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        session.headers.update(headers)

        # Configure retries for transient HTTP errors
        retry_strategy = Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=(429, 500, 502, 503, 504),
            allowed_methods=("HEAD", "GET", "OPTIONS")
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        try:
            resp = session.get(args, timeout=10, allow_redirects=True)
        except requests.RequestException as e:
            self.logger.log(f"[SITE FETCHER TOOL] : Network error during fetch: {e}")
            return False

        if resp.status_code != 200:
            # Try to extract error details from the API response
            try:
                err = resp.text
                
            except Exception:
                err = {"status_code": resp.status_code, "text": resp.text}
            self.logger.log(f"[SITE FETCHER TOOL] : Server error: {err}")
            return False

        out =  extract_plaintext_from_html(resp.text)
        out = filter_non_ascii(out)
        if (len(out) > MAX_CHARS):
            return out[:MAX_CHARS]