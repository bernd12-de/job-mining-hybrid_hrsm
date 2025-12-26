import asyncio
import re
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Helperfunktion, um Playwright synchron aus FastAPI aufzurufen
async def scrape_with_rendering(url: str) -> str:
    """Async Wrapper für Playwright (kompatibel mit FastAPI Event Loop)."""
    # Nutzt await statt asyncio.run() -> kein Event Loop Konflikt
    return await _render_and_scrape_async(url)

async def _render_and_scrape_async(url: str) -> str:
    """
    Rendert eine URL mit JavaScript und extrahiert den Haupttext (Playwright).
    """
    TIMEOUT_SECONDS = 20

    try:
        async with async_playwright() as p:
            # Wähle Chromium als schnellen, zuverlässigen Browser
            browser = await p.chromium.launch()
            page = await browser.new_page()

            print(f"-> Playwright: Navigiere zu {url}")

            # Warte, bis das Netzwerk inaktiv ist, was bedeutet, dass JS geladen wurde
            await page.goto(url, wait_until="networkidle", timeout=TIMEOUT_SECONDS * 1000)

            # Extrahiere den gesamten sichtbaren Text vom Body
            # inner_text() liefert den gerenderten Text, den der Benutzer sieht
            raw_text = await page.main_frame.inner_text()

            await browser.close()

            # Grundlegende Bereinigung
            raw_text = re.sub(r'\s+', ' ', raw_text).strip()

            if len(raw_text) < 100:
                raise Exception("Playwright fand nicht genügend Text nach dem Rendern.")

            return raw_text

    except PlaywrightTimeoutError:
        raise TimeoutError(f"Playwright Timeout: Seite hat in {TIMEOUT_SECONDS} Sekunden nicht geladen.")
    except Exception as e:
        # Fängt alle anderen Fehler ab (z.B. DNS, SSL)
        raise Exception(f"Playwright Fehler: {e}")
