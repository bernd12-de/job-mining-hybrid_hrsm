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
    fast: Optional[bool] = True  # Begrenze Analyse auf kompakte Größe für Geschwindigkeit

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

    # Nutze den zentralen WebScraper mit Limits
    try:
        from app.infrastructure.crawling.web_scraper import WebScraper
        scraper = WebScraper(use_playwright=url_input.render_js)
        # Frühzeitiger Abbruch bei JS-heavy Domains ohne Rendering
        if not url_input.render_js and scraper.requires_js_rendering(url):
            # Direkt abbrechen ohne Fallback
            raise HTTPException(status_code=400, detail="Diese Domain erfordert JavaScript-Rendering. Bitte 'render_js' aktivieren.")
        content = scraper.scrape(url, force_playwright=url_input.render_js)
        raw_text = content.text or ""
    except HTTPException as he:
        # gezielt weiterreichen
        raise he
    except Exception as e:
        # Fallback auf sehr einfachen statischen Scrape
        print(f"⚠️ WebScraper fehlgeschlagen, Fallback static: {e}")
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers, timeout=8)
            response.raise_for_status()
            soup = BeautifulSoup(response.content[:1024*512], 'html.parser')  # max 512KB
            raw_text = _extract_job_content(soup)
        except requests.HTTPError as e2:
            raise HTTPException(status_code=e2.response.status_code, detail=f"HTTP-Fehler beim Scraping: {e2}")
        except Exception as e2:
            raise HTTPException(status_code=500, detail=f"Scraping-Fehler: {str(e2)}")

    # 3. Validierung & Analyse (Gilt für BEIDE Wege)
    if not raw_text or len(raw_text) < 100:
        raise HTTPException(
            status_code=400,
            detail=f"Zu wenig Text extrahiert ({len(raw_text)} Zeichen). URL evtl. mit Captcha/Login geschützt."
        )

    # Optional: fast mode begrenzt Textlänge für schnellere Analyse
    if url_input.fast:
        raw_text = raw_text[:4000]

    cleaned_raw_text = raw_text.replace('\x00', '')

    # Aufruf der Analyse-Logik
    try:
        analysis_result = manager.run_analysis_from_scraped_text(cleaned_raw_text, url)
        return analysis_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysefehler im Workflow Manager: {str(e)}")

# Endpoint 3: Batch-Verarbeitung mit Statistiken
def batch_process_local_jobs(manager: IJobMiningWorkflowManager = Depends(lambda: None)):
    """
    Batch-Verarbeitung mit Progress & Fehler-Reports
    Nutzt BatchRunner für umgebungsunabhängige Statistiken
    """
    from app.infrastructure.batch.batch_runner import BatchRunner, JobResult, JobStatus
    from pathlib import Path
    import time
    
    # Job-Verzeichnis finden
    base_dir = os.environ.get("BASE_DATA_DIR", "/app/data")
    jobs_dir = Path(base_dir) / "jobs"
    
    if not jobs_dir.exists():
        raise HTTPException(status_code=404, detail=f"Jobs-Verzeichnis nicht gefunden: {jobs_dir}")
    
    # Sammle alle Dateien
    files = list(jobs_dir.glob("**/*.pdf")) + list(jobs_dir.glob("**/*.docx")) + list(jobs_dir.glob("**/*.txt"))
    
    if not files:
        return {"status": "no_files", "message": "Keine Dateien gefunden"}
    
    # Processor-Funktion
    def process_file(file_path: Path) -> JobResult:
        start_ms = int(time.time() * 1000)
        try:
            # Nutze existierenden Processor
            processor = JobDirectoryProcessor(manager=manager)
            result = processor._process_single_file(str(file_path))
            
            return JobResult(
                filename=file_path.name,
                status=JobStatus.SUCCESS,
                competences_found=len(result.get('competences', [])),
                processing_time_ms=int(time.time() * 1000) - start_ms
            )
        except Exception as e:
            return JobResult(
                filename=file_path.name,
                status=JobStatus.FAILED,
                competences_found=0,
                processing_time_ms=int(time.time() * 1000) - start_ms,
                error_message=str(e)
            )
    
    # Batch-Run
    runner = BatchRunner()
    stats = runner.run_batch(files=files, processor_func=process_file, save_reports=True)
    
    return {
        "status": "completed",
        "run_id": stats.run_id,
        "environment": stats.environment,
        "total_files": stats.total_files,
        "successful": stats.successful,
        "failed": stats.failed,
        "skipped": stats.skipped,
        "total_competences": stats.total_competences,
        "total_time_sec": stats.total_time_ms / 1000,
        "report_path": str(runner.output_dir / f"{stats.run_id}.json"),
        "errors": stats.errors[:10]  # Max 10 Fehler in Response
    }
