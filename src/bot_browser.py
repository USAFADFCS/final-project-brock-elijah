import asyncio
from playwright.async_api import Page, Browser, Playwright, Error, async_playwright
import sys
from typing import Any, List, Set
import random 
import platform

def ran_wait():
    return random.gauss(1, 0.5)

async def human_wait(logger=print):
    wait_time = abs(ran_wait())
    await asyncio.sleep(wait_time)
    logger(f'Searcher executed human-like wait of {wait_time} s')

# --- Utility Functions (Unchanged) ---

async def user_close(page: Page):
    """
    Asynchronously waits until the Playwright page is closed by the user.
    """
    print("\n[User Wait] Waiting for you to close the browser window...")
    print("[User Wait] You must manually close the browser window to proceed with cleanup.")
    try:
        # FIX: Ensure indefinite wait without the internal timeout issue.
        await page.wait_for_event('close') 
        print("[User Wait] Browser window closed. Proceeding with resource cleanup.")
    except Exception as e:
        if "Timeout" in str(e):
             print("[User Wait] Timeout occurred, assuming page was already closed or session is unstable. Proceeding with cleanup.")
        elif "Target closed" in str(e):
             print("[User Wait] Target closed unexpectedly. Proceeding with cleanup.")
        else:
             print(f"[User Wait] An unexpected error occurred while waiting for closure: {e}")

    print("[User Wait] Performing safe close...")
    await (await BrowserManager.get_instance()).close()
    
async def close_browser():
    """
    Safely closes the browser only if a fully initialized instance exists.
    """
    # 💥 FIX: Check the static class variable _instance directly.
    manager = BrowserManager._instance
    
    if manager and manager._is_initialized:
        # Only call close if an initialized instance is found.
        await manager.close()
    else:
        # If the browser was already closed/reset, or never opened, do nothing.
        print("[BrowserManager] Cleanup skipped: Browser instance was already closed or never initialized.")
    

# --- Singleton Implementation Class ---

class BrowserManager:
    _instance = None
    _page: Page | None = None
    _browser: Browser | None = None
    _playwright: Playwright | None = None
    _is_initialized: bool = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(BrowserManager, cls).__new__(cls)
        return cls._instance

    @classmethod
    async def get_instance(cls) -> 'BrowserManager':
        manager = cls()
        if not manager._is_initialized:
            await manager._initialize()
            manager._is_initialized = True
        return manager

    async def _initialize(self):
        print("[BrowserManager] Initializing new Browser and Page instance (with all evasions)...")
        try:
            self._playwright = await async_playwright().start()
            
            self._browser = await self._playwright.chromium.launch(
                headless=False,
                args=[
                    '--start-maximized', 
                    '--window-position=0,0',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--ignore-certificate-errors',
                ],
            )
            context = await self._browser.new_context(
                viewport=None,
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
                timezone_id="America/New_York",
                locale="en-US",
            )
            self._page = await context.new_page()
            
            await self._page.add_init_script("""
                function stealth() {
                    Object.defineProperty(navigator, 'webdriver', { get: () => false });
                    if (window.chrome) { window.chrome = window.chrome; }
                    Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                    const getParameter = WebGLRenderingContext.prototype.getParameter;
                    WebGLRenderingContext.prototype.getParameter = function(parameter) {
                        if (parameter === 37445) { return 'Google Inc. (NVIDIA)'; }
                        if (parameter === 37446) { return 'NVIDIA Corporation'; }
                        return getParameter.call(this, parameter);
                    };
                    Object.defineProperty(navigator, 'plugins', {
                        get: () => [
                            { description: 'Portable Document Format', filename: 'internal-pdf-viewer', name: 'Chrome PDF Plugin' },
                            { description: '', filename: 'internal-nacl-plugin', name: 'Native Client' },
                        ],
                    });
                }
                stealth();
            """)
            
            print("[BrowserManager] Browser and Page successfully initialized with all evasions.")

        except Error as e:
            print(f"[BrowserManager] Playwright Error during initialization: {e}", file=sys.stderr)
            await self.close()
            raise
        except Exception as e:
            print(f"[BrowserManager] Unexpected Error during initialization: {e}", file=sys.stderr)
            await self.close()
            raise

    def get_page(self) -> Page:
        if self._page is None:
            raise RuntimeError("BrowserManager was not initialized. Call get_instance() first.")
        return self._page

    async def close(self):
        """Clean up the browser and Playwright resources with explicit stopping."""
        print("[BrowserManager] Closing browser...")
        
        # 1. Close the browser cleanly
        if self._browser:
            try:
                # 💥 Ensure the browser is closed
                await self._browser.close()
            except Exception as e:
                # Catch the specific error indicating the connection is already gone
                if "Target closed" not in str(e) and "'NoneType' object has no attribute 'send'" not in str(e):
                    print(f"[BrowserManager] Error during browser close: {e}")
        
        # 2. Stop the Playwright instance (Crucial for subprocess cleanup)
        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception as e:
                # Ignore the "Event loop is closed" error here, as we tried our best.
                if "Event loop is closed" not in str(e):
                    print(f"[BrowserManager] Error during Playwright stop: {e}")

        # Reset singleton state (Crucial for safe termination)
        BrowserManager._instance = None
        BrowserManager._page = None
        BrowserManager._browser = None
        BrowserManager._playwright = None
        self._is_initialized = False
        print("[BrowserManager] Resources cleaned up.")

# --- Public Wrapper Function and Example Usage (Unchanged) ---

async def get_page() -> Page:
    manager = await BrowserManager.get_instance()
    return manager.get_page()


# --- NEW FUNCTION ---

async def get_all_web_links(page: Page) -> List[str]:
    """
    Extracts the URLs from all <a> tags (links) on the given page using 
    native Playwright locators, without using page.evaluate().
    """
    from playwright.async_api import Locator
    
    print("\n[Link Extraction (Native)] Searching for all web links on the page using locators...")
    
    # Wait for the page to be completely stable before querying elements
    try:
        await page.wait_for_load_state('networkidle', timeout=15000) 
    except Exception as e:
        if "Timeout" in str(e):
            print("[Link Extraction (Native)] Warning: Stability timeout reached. Attempting extraction anyway.")
        else:
             print(f"[Link Extraction (Native)] Warning: Error during stability wait: {e}")

    # 1. Select all <a> elements on the page.
    # We use a base locator for all links.
    all_links: Locator = page.locator('a')
    
    # 2. Get all elements matching the locator.
    # This ensures we are working with the elements present at this moment.
    link_elements: List[Locator] = await all_links.all()
    
    # 3. Iterate through the elements and extract the 'href' attribute.
    link_hrefs: Set[str] = set()
    
    for link_locator in link_elements:
        # Use get_attribute to reliably fetch the value of 'href'
        href_value = await link_locator.get_attribute('href')
        
        if href_value:
            # Playwright's element.get_attribute('href') typically returns the 
            # raw attribute value (relative or absolute). We must convert it 
            # to an absolute URL and check if it's a web link (starts with http).
            
            # Use page.url to resolve relative URLs to absolute URLs in Python.
            # However, since this can be complex to do perfectly in Python for 
            # every edge case, a robust, native-only approach relies on filtering 
            # the absolute links provided by the page.
            
            # For simplicity and robustness (avoiding complex URL parsing in Python), 
            # we rely on filtering for absolute URLs and remove relative/local links.
            if href_value.startswith('http') or href_value.startswith('https'):
                 link_hrefs.add(href_value)
            
    unique_links_list: List[str] = sorted(list(link_hrefs))
    
    print(f"[Link Extraction (Native)] Found {len(unique_links_list)} unique web links.")
    return unique_links_list