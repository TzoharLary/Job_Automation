import asyncio
from typing import Callable, Iterable, List, Optional

from playwright.async_api import Page, async_playwright

from src.app.config import get_settings


async def with_page(browser_name: str, fn: Callable[[Page], asyncio.Future]):
    async with async_playwright() as p:
        browser_type = getattr(p, browser_name)
        browser = await browser_type.launch(headless=True)
        page = await browser.new_page()
        try:
            return await fn(page)
        finally:
            await browser.close()


async def fetch_html(url: str) -> Optional[str]:
    settings = get_settings()

    async def _fn(page: Page):
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=settings.playwright_nav_timeout_ms)
            await page.wait_for_timeout(settings.playwright_delay_ms)
            return await page.content()
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    return await with_page(settings.playwright_browser, _fn)


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
