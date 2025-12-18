import asyncio
import threading
import traceback
from typing import Callable, Iterable, List, Optional

from playwright.async_api import Browser, Page, async_playwright

from src.app.config import get_settings


class BrowserManager:
    """Manages a persistent browser instance for multiple page operations."""
    
    def __init__(self):
        self.settings = get_settings()
        self.playwright = None
        self.browser = None
        
    async def __aenter__(self):
        print(f"DEBUG: [TID: {threading.get_ident()}] BrowserManager entering context...", flush=True)
        self.playwright = await async_playwright().start()
        browser_type = getattr(self.playwright, self.settings.playwright_browser)
        print(f"DEBUG: Launching Browser (Persistent Instance)...", flush=True)
        self.browser = await browser_type.launch(headless=True)
        print("DEBUG: Browser launched successfully.", flush=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        print("DEBUG: BrowserManager exiting context...", flush=True)
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
        print("DEBUG: Browser closed.", flush=True)

    async def fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch HTML for a single URL using the persistent browser instance.
        Includes explicit yielding to event loop to prevent starvation.
        """
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use 'async with BrowserManager()'.")

        print(f"DEBUG: Fetching URL: {url}", flush=True)
        page = await self.browser.new_page()
        try:
            # User requested explicit timeout check
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            await page.wait_for_timeout(self.settings.playwright_delay_ms)
            html = await page.content()
            return html
        except Exception as e:
            print(f"Error scraping {url}: {e}", flush=True)
            return None
        finally:
            await page.close()
            # CRITICAL: Sleep to let SSE Heartbeat run - Increased to 1.5s per user request
            await asyncio.sleep(1.5)



# Legacy support if needed, but prefer BrowserManager for batch ops
async def fetch_html(url: str) -> Optional[str]:
    # ... (kept for backward compatibility if needed, but Pipeline should switch to BrowserManager)
    settings = get_settings()
    async with async_playwright() as p:
        browser = await getattr(p, settings.playwright_browser).launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=settings.playwright_nav_timeout_ms)
            return await page.content()
        except Exception:
            return None
        finally:
            await browser.close()



def rate_limiter(delay_ms: int):
    lock = asyncio.Lock()

    async def _wrap(coro: Callable[[], asyncio.Future]):
        async with lock:
            await asyncio.sleep(delay_ms / 1000)
            return await coro()

    return _wrap


async def bounded_map(concurrency: int, items: Iterable, fn: Callable[[any], asyncio.Future]) -> List:
    semaphore = asyncio.Semaphore(concurrency)
    results = []

    async def _run(item):
        async with semaphore:
            return await fn(item)

    tasks = [asyncio.create_task(_run(item)) for item in items]
    for t in tasks:
        results.append(await t)
    return results
