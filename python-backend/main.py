from fastapi import FastAPI, UploadFile, File, HTTPException, Depends

# --- INFRASTRUKTUR & DOMAIN IMPORTS ---
from advanced_text_extractor import AdvancedTextExtractor
from fuzzy_competence_extractor import FuzzyCompetenceExtractor
from interfaces import IJobMiningWorkflowManager, ITextExtractor, ICompetenceExtractor
from job_mining_workflow_manager import JobMiningWorkflowManager
from repositories.hybrid_competence_repository import HybridCompetenceRepository

# --- NEU: MODULARE ENDPUNKTE IMPORTIEREN ---
from api_endpoints import scrape_and_analyze_url, analyse_job_ad, batch_process_local_jobs, URLInput

app = FastAPI()

# --- DEPENDENCY INJECTION (DI) ---
# Definiert, wie FastAPI den Workflow Manager erzeugt (Dependency Injection)
def get_workflow_manager() -> IJobMiningWorkflowManager:
    # 1. ESCO-Wissensbasis laden (DI-Chain startet hier)
    # Das Logging passiert jetzt IN DIESEM KONSTRUKTOR
    competence_repo = HybridCompetenceRepository()

    # DIE MANUELLEN LOGGING-ZEILEN SIND HIER ENTFERNT WORDEN

    # 2. Extraktoren: Die konkreten Implementierungen erstellen
    text_extractor: ITextExtractor = AdvancedTextExtractor()
    competence_extractor: ICompetenceExtractor = FuzzyCompetenceExtractor(repository=competence_repo)

    # 3. Den Workflow Manager injizieren (DI-Prinzip)
    return JobMiningWorkflowManager(
        text_extractor=text_extractor,
        competence_extractor=competence_extractor
    )

# --- ENDPUNKT-REGISTRIERUNG ---

# Dateiupload
@app.post("/analyse")
async def handle_analyse(file: UploadFile = File(...), manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)):
    return analyse_job_ad(file=file, manager=manager)

# Web-Scraping
@app.post("/scrape-url")
async def handle_scrape(url_input: URLInput, manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)):
    return scrape_and_analyze_url(url_input=url_input, manager=manager)

# Batch-Verarbeitung (FIX FÜR 404 NOT FOUND)
@app.post("/batch-process")
async def handle_batch(manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)):
    return batch_process_local_jobs(manager=manager)
