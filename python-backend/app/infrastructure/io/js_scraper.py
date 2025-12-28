import asyncio
import re
import subprocess
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Helperfunktion, um Playwright synchron aus FastAPI aufzurufen
async def scrape_with_rendering(url: str) -> str:
    """Async Wrapper für Playwright (kompatibel mit FastAPI Event Loop)."""
    # Nutzt await statt asyncio.run() -> kein Event Loop Konflikt
    return await _render_and_scrape_async(url)

async def _render_and_scrape_async(url: str) -> str:
    """
    Rendert eine URL mit JavaScript und extrahiert den Haupttext (Playwright).
    Spezieller Selector-Support für gängige Job-Portale (Workday, Softgarden, etc.).
    """
    TIMEOUT_SECONDS = 40

    try:
        async with async_playwright() as p:
            # Wähle Chromium als schnellen, zuverlässigen Browser
            try:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                        "--disable-gpu",
                    ],
                )
            except Exception as e:
                # Fallback: Browser nachinstallieren und erneut versuchen
                if "Executable doesn't exist" in str(e):
                    try:
                        subprocess.run(["playwright", "install", "chromium"], check=True)
                        browser = await p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]) 
                    except Exception as e2:
                        raise Exception(f"Playwright Browser-Install fehlgeschlagen: {e2}")
                else:
                    raise
            page = await browser.new_page()
            # Setze deutsche Sprache und einen realistischen UA
            await page.set_extra_http_headers({
                'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8'
            })

            print(f"-> Playwright: Navigiere zu {url}")

            # Warte, bis das Netzwerk inaktiv ist, was bedeutet, dass JS geladen wurde
            await page.goto(url, wait_until="networkidle", timeout=TIMEOUT_SECONDS * 1000)

            # Versuche Cookie-Banner zu akzeptieren (häufig OneTrust)
            try:
                await page.locator('#onetrust-accept-btn-handler').click(timeout=3000)
            except Exception:
                try:
                    await page.locator('button:has-text("Alle akzeptieren")').click(timeout=3000)
                except Exception:
                    try:
                        await page.locator('button:has-text("Akzeptieren")').click(timeout=3000)
                    except Exception:
                        pass

            # Versuche zuerst portalspezifische Selektoren
            selectors = [
                'div[data-automation="jobDescription"]',
                '[data-automation="job-description"]',
                'div[data-automation="jobPostingDescription"]',
                'section[aria-label="Job Description"]',
                '.jobDescription',
                '[role="main"]',
                'article',
            ]
            raw_text = ''
            found = False
            for sel in selectors:
                try:
                    await page.wait_for_selector(sel, timeout=8000)
                    raw_text = await page.inner_text(sel)
                    if raw_text and len(raw_text.strip()) >= 100:
                        found = True
                        break
                except Exception:
                    continue

            if not found:
                # Fallback: gesamter sichtbarer Body-Text
                raw_text = await page.inner_text('body')

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
