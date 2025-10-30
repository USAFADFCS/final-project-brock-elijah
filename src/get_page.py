"""
Playwright Page Manager using Singleton Pattern

This module provides a singleton-based approach to managing Playwright
browser and page instances, ensuring only one browser window and page
exist at a time.

SETUP:
pip install playwright
playwright install chromium
"""

import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page, Playwright


class BrowserManager:
    """
    Singleton class to manage a single Playwright browser and page instance.
    
    This ensures that multiple calls to get_page() return the same page
    instance, preventing unnecessary browser windows from being created.
    """
    
    _instance: Optional['BrowserManager'] = None
    _playwright: Optional[Playwright] = None
    _browser: Optional[Browser] = None
    _page: Optional[Page] = None
    _lock: asyncio.Lock = asyncio.Lock()
    
    def __new__(cls):
        """Ensure only one instance of BrowserManager exists."""
        if cls._instance is None:
            cls._instance = super(BrowserManager, cls).__new__(cls)
        return cls._instance
    
    async def get_page(self) -> Page:
        """
        Get the singleton page instance.
        
        If no browser exists, creates a new browser.
        If browser exists but no page, creates a new page.
        Otherwise, returns the existing page.
        
        Returns:
            Page: The singleton Playwright page instance.
        """
        async with self._lock:
            # Initialize playwright if needed
            if self._playwright is None:
                self._playwright = await async_playwright().start()
            
            # Check if browser exists and is connected
            if self._browser is None or not self._browser.is_connected():
                await self._create_browser()
            
            # Check if page exists and is not closed
            if self._page is None or self._page.is_closed():
                await self._create_page()
            
            return self._page
    
    async def _create_browser(self):
        """Create a new browser instance."""
        if self._browser is not None:
            try:
                await self._browser.close()
            except Exception:
                pass  # Browser already closed
        
        # Launch browser with fullscreen options
        self._browser = await self._playwright.chromium.launch(
            headless=False,  # Set to True for headless mode
            args=[
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--start-maximized',  # Start maximized
                '--kiosk'  # Fullscreen mode
            ]
        )
        self._page = None  # Reset page when creating new browser
    
    async def _create_page(self):
        """Create a new page in the existing browser."""
        if self._browser is None:
            await self._create_browser()
        
        # Get screen dimensions for true fullscreen
        # Create a new context and page with maximized viewport
        context = await self._browser.new_context(
            viewport=None,  # Use full screen size
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            no_viewport=True  # Disable viewport to use full screen
        )
        self._page = await context.new_page()
    
    async def close(self):
        """Close the browser and clean up resources."""
        async with self._lock:
            if self._page is not None and not self._page.is_closed():
                await self._page.close()
                self._page = None
            
            if self._browser is not None:
                await self._browser.close()
                self._browser = None
            
            if self._playwright is not None:
                await self._playwright.stop()
                self._playwright = None


# Global singleton instance
_browser_manager = BrowserManager()


async def get_page() -> Page:
    """
    Get the singleton Playwright page instance.
    
    This function implements the singleton pattern, ensuring that only
    one browser window and page exist throughout the application lifecycle.
    
    Returns:
        Page: The singleton Playwright page instance.
    
    Example:
        >>> page = await get_page()
        >>> await page.goto('https://example.com')
        >>> 
        >>> # Later in the code...
        >>> same_page = await get_page()  # Returns the same page instance
        >>> assert page is same_page  # True
    """
    return await _browser_manager.get_page()


async def close_browser():
    """
    Close the singleton browser instance and clean up resources.
    
    This should be called when shutting down the application to ensure
    proper cleanup of browser resources.
    
    Example:
        >>> await close_browser()
    """
    await _browser_manager.close()


# Example usage
async def main():
    """Example usage of the singleton page manager."""
    
    try:
        # First call - creates browser and page
        print("Getting page for the first time...")
        page1 = await get_page()
        await page1.goto('https://example.com')
        print(f"Page 1 URL: {page1.url}")
        
        # Second call - returns the same page
        print("\nGetting page again...")
        page2 = await get_page()
        print(f"Page 2 URL: {page2.url}")
        
        # Verify they're the same instance
        print(f"\nAre they the same page? {page1 is page2}")
        
        # Navigate to a different URL
        await page2.goto('https://www.python.org')
        print(f"\nPage 1 URL after navigation: {page1.url}")
        print(f"Page 2 URL after navigation: {page2.url}")
        
        # You can also get the page content
        title = await page1.title()
        print(f"\nPage title: {title}")
        
        # Wait for user to close the browser window
        print("\n" + "="*50)
        print("Browser is now open in fullscreen mode.")
        print("Close the browser window when you're done...")
        print("="*50 + "\n")
        
        # Keep the script running until the browser is closed
        while not page1.is_closed():
            await asyncio.sleep(0.5)
        
        print("\nBrowser window was closed by user.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Clean up
        print("Cleaning up resources...")
        await close_browser()
        print("Done!")


if __name__ == '__main__':
    asyncio.run(main())