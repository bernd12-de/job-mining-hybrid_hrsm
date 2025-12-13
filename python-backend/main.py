from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel # NEU: Für URL-Input
import requests             # NEU: Für HTTP-Anfragen
from bs4 import BeautifulSoup   # NEU: Für HTML-Parsing
from typing import Optional # <--- WICHTIGER IMPORT FÜR URLInput
from advanced_text_extractor import AdvancedTextExtractor
from fuzzy_competence_extractor import FuzzyCompetenceExtractor
from interfaces import IJobMiningWorkflowManager, ITextExtractor, ICompetenceExtractor
from job_directory_processor import JobDirectoryProcessor
from job_mining_workflow_manager import JobMiningWorkflowManager
from repositories.hybrid_competence_repository import HybridCompetenceRepository

# NEU: Import des Playwright-Scrapers
from js_scraper import scrape_with_rendering

app = FastAPI()

# Input-Modell für den Scraper-Endpunkt (JETZT MIT OPTION)
class URLInput(BaseModel):
    url: str
    render_js: Optional[bool] = False # <--- NEU: Option für Headless Browser

# Definiert, wie FastAPI den Workflow Manager erzeugt (Dependency Injection)
def get_workflow_manager() -> IJobMiningWorkflowManager:
    # 1. ESCO-Wissensbasis laden (nur einmal)
    competence_repo = HybridCompetenceRepository()

    # NEU: EXPLIZITER ZÄHLER (BESTÄTIGT, dass die neuen CSVs geladen wurden)
    print(f"*** ESCO-Integration erfolgreich: {len(competence_repo.get_esco_only())} ESCO Skills geladen ***")
    # ENDE EXPLIZITER ZÄHLER

    # 2. Extraktoren: Die konkreten Implementierungen erstellen
    text_extractor: ITextExtractor = AdvancedTextExtractor()
    competence_extractor: ICompetenceExtractor = FuzzyCompetenceExtractor(repository=competence_repo)

    # 3. Den Workflow Manager injizieren (DI-Prinzip)
    return JobMiningWorkflowManager(
        text_extractor=text_extractor,
        competence_extractor=competence_extractor
    )

def _extract_job_content(soup: BeautifulSoup) -> str:
    """Extrahiert den relevanten Text aus dem HTML (Web-Scraping Best Practice)."""

    # ... (Die robuste Logik, die Sie bereits implementiert haben)
    for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'noscript']):
        tag.decompose()

    article_body = soup.find('div', id='content')

    if article_body:
        return article_body.get_text(separator=' ', strip=True)

    return soup.body.get_text(separator=' ', strip=True) if soup.body else soup.get_text(separator=' ', strip=True)

# Bestehender Endpunkt für Dateiuploads
@app.post("/analyse")
async def analyse_job_ad(
        file: UploadFile = File(...),
        manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)
):
    """Analysiert ein hochgeladenes Dokument (PDF/DOCX)."""
    try:
        analysis_result = manager.run_full_analysis(file.file, file.filename)
        return analysis_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysefehler: {str(e)}")

# Endpoint 2: Web-Scraping
@app.post("/scrape-url")
async def scrape_and_analyze_url(
        url_input: URLInput,
        manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)
):
    """Ruft eine URL ab, extrahiert den Text und analysiert ihn."""
    url = url_input.url
    raw_text = ""

    if url_input.render_js:
        # BEST PRACTICE: Playwright-Rendering verwenden
        try:
            print(f"-> Starte Scraping für URL: {url} (JS RENDERING MODE)")
            raw_text = scrape_with_rendering(url) # <--- RUFT DAS NEUE JS-MODUL AUF

        except Exception as e:
            # Fehler im Playwright-Scraping fangen (z.B. Timeout)
            raise HTTPException(status_code=500, detail=f"Rendering-Fehler amin.py: {str(e)}")
            raise HTTPException(status_code=501, detail="Funktion 'render_js' ist noch nicht mit Headless Browser (Playwright) implementiert.")

    else:
        # STATIC MODE: requests+BeautifulSoup (wie zuvor)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            print(f"-> Starte Scraping für URL: {url} (Static Mode)")
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            raw_text = _extract_job_content(soup)

            if len(raw_text) < 100:
                raise HTTPException(status_code=400, detail=f"Scraping erfolgreich, aber zu wenig Text gefunden ({len(raw_text)} Zeichen). Seite ist wahrscheinlich JavaScript-gerendert. Versuche 'render_js=True'.")

        except requests.HTTPError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"HTTP-Fehler beim Abrufen der URL: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Scraping- oder Analysefehler: {str(e)}")

    # Gemeinsame Logik nach der Text-Extraktion
    cleaned_raw_text = raw_text.replace('\x00', '')
    analysis_result = manager._run_analysis_from_text(cleaned_raw_text, url)

    return analysis_result
# ... (bestehende /analyse und /batch-process Endpunkte)

# Bestehender Endpunkt für Batch-Verarbeitung
@app.post("/batch-process")
async def batch_process_local_jobs(
        manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)
):
    """Verarbeitet alle Dateien im jobs-Ordner."""
    # Muss das JobDirectoryProcessor-Modul verwenden, wenn Sie Batch-Verarbeitung aktiviert haben
    # from job_directory_processor import JobDirectoryProcessor
    # ...
    # raise HTTPException(status_code=501, detail="Batch-Verarbeitung nicht implementiert")
    #raise HTTPException(status_code=501, detail="Batch-Verarbeitung ist in dieser Version nicht implementiert.") # Platzhalter für die Batch-Logik, die Sie zuvor implementiert hatten
    processor = JobDirectoryProcessor(manager=manager)
    results = processor.process_all_jobs()
    return results
