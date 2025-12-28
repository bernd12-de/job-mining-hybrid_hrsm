"""
Async Playwright Scraper for JavaScript-heavy pages
"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


async def scrape_with_rendering(url: str, timeout: int = 30000) -> str:
    """
    Scrapes a URL with Playwright (async) for JS rendering

    Args:
        url: The URL to scrape
        timeout: Timeout in milliseconds (default 30s)

    Returns:
        Extracted text from the page

    Raises:
        ImportError: If Playwright is not installed
        Exception: On scraping errors
    """
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        raise ImportError(
            "Playwright not installed. "
            "Please run: pip install playwright && playwright install chromium"
        )

    logger.info(f"Scraping with Playwright: {url}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Navigate and wait for network idle
            await page.goto(url, wait_until='networkidle', timeout=timeout)

            # Wait for main content (optional, with timeout)
            try:
                await page.wait_for_selector('h1, .job-title, .title', timeout=5000)
            except Exception as e:
                logger.warning(f"Main content selector not found: {e}")

            # Extract all text from body
            text = await page.inner_text('body')

            logger.info(f"Scraping successful: {len(text)} characters")

            return text

        except Exception as e:
            logger.error(f"Playwright scraping failed for {url}: {e}")
            raise

        finally:
            await page.close()
            await browser.close()
