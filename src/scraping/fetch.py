from typing import Optional

from playwright.async_api import Page

from src.app.config import get_settings


async def fetch_page(page: Page, url: str) -> Optional[str]:
    settings = get_settings()
    await page.goto(url, wait_until="domcontentloaded", timeout=settings.playwright_nav_timeout_ms)
    await page.wait_for_timeout(settings.playwright_delay_ms)
    content = await page.content()
    return content
