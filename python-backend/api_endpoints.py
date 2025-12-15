from fastapi import UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import re
from typing import Optional

from interfaces import IJobMiningWorkflowManager
from job_directory_processor import JobDirectoryProcessor

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
def scrape_and_analyze_url(url_input: URLInput, manager: IJobMiningWorkflowManager = Depends(lambda: None)):
    url = url_input.url

    if url_input.render_js:
        raise HTTPException(status_code=501, detail="Funktion 'render_js' ist noch nicht mit Headless Browser (Playwright) implementiert.")

    # STATIC MODE
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        print(f"-> Starte Scraping für URL: {url} (Static Mode)")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        raw_text = _extract_job_content(soup)

        if len(raw_text) < 100:
            raise HTTPException(status_code=400, detail="Scraping erfolgreich, aber zu wenig Text gefunden. Seite ist JavaScript-gerendert. Versuche 'render_js=True'.")

        cleaned_raw_text = raw_text.replace('\x00', '')
        # 🚨 KERN-FIX: Ruft die NEUE, dedizierte Methode des Managers auf
        analysis_result = manager.run_analysis_from_scraped_text(cleaned_raw_text, url)

        return analysis_result

    except requests.HTTPError as e:
        raise HTTPException(status_code=e.response.status_code, detail=f"HTTP-Fehler beim Abrufen der URL: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping- oder Analysefehler: {str(e)}")


# Endpoint 3: Batch-Verarbeitung
def batch_process_local_jobs(manager: IJobMiningWorkflowManager = Depends(lambda: None)):
    processor = JobDirectoryProcessor(manager=manager)
    results = processor.process_all_jobs()
    return results
