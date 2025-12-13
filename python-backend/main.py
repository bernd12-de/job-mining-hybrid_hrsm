from fastapi import FastAPI, UploadFile, File, HTTPException, Depends

# --- INFRASTRUKTUR & DOMAIN IMPORTS ---
from advanced_text_extractor import AdvancedTextExtractor

from interfaces import IJobMiningWorkflowManager, ITextExtractor, ICompetenceExtractor
from job_mining_workflow_manager import JobMiningWorkflowManager
from repositories.hybrid_competence_repository import HybridCompetenceRepository
from infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor
from infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor
# --- NEU: MODULARE ENDPUNKTE IMPORTIEREN ---
from api_endpoints import scrape_and_analyze_url, analyse_job_ad, batch_process_local_jobs, URLInput

app = FastAPI()

# --- DEPENDENCY INJECTION (DI) ---
# Definiert, wie FastAPI den Workflow Manager erzeugt (Dependency Injection)
def get_workflow_manager() -> IJobMiningWorkflowManager:
    # 1. ESCO-Wissensbasis laden
    competence_repo = HybridCompetenceRepository()

    # 2. Extraktoren: Die konkreten Implementierungen erstellen
    text_extractor: ITextExtractor = AdvancedTextExtractor()

    # 🚨 KERN-FIX: Übergib das Repository an den SpaCyExtractor, damit dieser es als Attribut speichern kann!

    competence_extractor: ICompetenceExtractor = SpaCyCompetenceExtractor(repository=competence_repo) # <--- ÄNDERUNG HIER

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

# Endpoint 4: ESCO Health Check (Erfüllt den Wunsch nach einem schnellen Test)
@app.get("/health/esco-count")
async def get_esco_count(manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)):
    """
    Gibt die geladene ESCO-Kompetenzanzahl zurück.
    Dieser Aufruf zwingt das HybridCompetenceRepository, die Daten zu laden und den Zähler in der Konsole auszugeben.
    """
    repo = manager.competence_extractor.repository
    return {
        "status": "OK",
        "esco_label_count": len(repo.get_esco_only()),
        "custom_label_count": len(repo.get_custom_only()),
        "total_competences": len(repo.get_all_skills()),
        "loading_source": "JSON Cache oder CSV Fallback"
    }
