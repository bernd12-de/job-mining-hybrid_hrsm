from fastapi import UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
from typing import Optional

from app.interfaces.interfaces import IJobMiningWorkflowManager
from app.infrastructure.io.job_directory_processor import JobDirectoryProcessor
from app.infrastructure.io.js_scraper import scrape_with_rendering

# Input-Modell für den Scraper-Endpunkt
class URLInput(BaseModel):
    url: str
    render_js: Optional[bool] = False

# Helper: Extrahiert Text aus dem HTML
def _extract_job_content(soup: BeautifulSoup) -> str:
    # ... (Implementierung wie zuvor)
    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'noscript']):
        tag.decompose()

    article_body = soup.find('div', id='content')

    if article_body:
        return article_body.get_text(separator=' ', strip=True)

    return soup.body.get_text(separator=' ', strip=True) if soup.body else soup.get_text(separator=' ', strip=True)


# --- API ENDPUNKTE (JETZT MODULAR) ---

# Endpoint 1: Datei-Upload
def analyse_job_ad(file: UploadFile = File(...), manager: IJobMiningWorkflowManager = Depends(lambda: None)):
    try:
        analysis_result = manager.run_full_analysis(file.file, file.filename)
        return analysis_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysefehler: {str(e)}")

# Endpoint 2: Web-Scraping
async def scrape_and_analyze_url(url_input: URLInput, manager: IJobMiningWorkflowManager = Depends(lambda: None)):
    url = url_input.url
    raw_text = ""

    # 1. ENTWEDER: JavaScript Rendering (Playwright)
    if url_input.render_js:
        print(f"-> Starte JS-Scraping für URL: {url}")
        try:
            raw_text = await scrape_with_rendering(url)
        except Exception as e:
            # Fallback zu statischem Scraping statt hard fail
            print(f"⚠️ JS-Rendering fehlgeschlagen, versuche statisches Scraping: {e}")
            url_input.render_js = False  # Trigger fallback

    # 2. ODER: Statischer Request (Requests) - auch als Fallback
    if not url_input.render_js or not raw_text:
        print(f"-> Starte statisches Scraping für URL: {url}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            raw_text = _extract_job_content(soup)
        except requests.HTTPError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"HTTP-Fehler beim Scraping: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Scraping-Fehler: {str(e)}")

    # 3. Validierung & Analyse (Gilt für BEIDE Wege)
    if not raw_text or len(raw_text) < 100:
        raise HTTPException(
            status_code=400,
            detail=f"Zu wenig Text extrahiert ({len(raw_text)} Zeichen). URL evtl. mit Captcha/Login geschützt."
        )

    cleaned_raw_text = raw_text.replace('\x00', '')

    # Aufruf der Analyse-Logik
    try:
        analysis_result = manager.run_analysis_from_scraped_text(cleaned_raw_text, url)
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysefehler im Workflow Manager: {str(e)}")

# Endpoint 3: Batch-Verarbeitung
def batch_process_local_jobs(manager: IJobMiningWorkflowManager = Depends(lambda: None)):
    processor = JobDirectoryProcessor(manager=manager)
    results = processor.process_all_jobs()
    return results
