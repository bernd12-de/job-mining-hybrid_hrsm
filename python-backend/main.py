import os
import logging
import subprocess
import socket

from fastapi import FastAPI, UploadFile, File, HTTPException
from typing import List

from pydantic import BaseModel

# --- ARCHITEKTUR-IMPORTE ---
from app.core.constants import GLOBAL_BLACKLIST
from app.domain.models import AnalysisResultDTO
from app.application.job_mining_workflow_manager import JobMiningWorkflowManager
from app.infrastructure.extractor.advanced_text_extractor import AdvancedTextExtractor
from app.infrastructure.extractor.metadata_extractor import MetadataExtractor
from app.infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor
from app.infrastructure.extractor.discovery_extractor import DiscoveryExtractor
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
from app.application.services.organization_service import OrganizationService
from app.application.services.role_service import RoleService
from app.core.api_endpoints import scrape_and_analyze_url, analyse_job_ad, URLInput

# Logging Setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =========================================================
# 1. ZENTRALE PFAD-KONFIGURATION (DEINE LOKALEN ORDNER)
# =========================================================
BASE_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

PATHS = {
    "ESCO_DATA": os.path.join(BASE_DATA_DIR, "esco"),
    "DOMAINS": os.path.join(BASE_DATA_DIR, "job_domains"),
    "JOBS": os.path.join(BASE_DATA_DIR, "jobs"),
    "BOOKS": os.path.join(BASE_DATA_DIR, "source_pdfs/fachbuecher"),
    "ACADEMIA": os.path.join(BASE_DATA_DIR, "source_pdfs/modulhandbuecher")
}

# =========================================================
# 2. INITIALISIERUNG DER BASIS-KOMPONENTEN
# =========================================================

# Das Repository verwaltet Ebenen 2, 4 und 5 (ESCO + Lokale Domains)
# In main.py: Korrigierte Initialisierung passend zu hybrid_repo.py
COMPETENCE_REPOSITORY = HybridCompetenceRepository(
    kotlin_api_url=os.environ.get("KOTLIN_API_URL", "http://localhost:8080"),
    fachbuch_path=os.path.join(PATHS["DOMAINS"], "fachbuch_domain.json"),
    academia_path=os.path.join(PATHS["DOMAINS"], "academia_domain.json")
)

RULE_CLIENT = KotlinRuleClient()

# Der Manager als zentrale Factory (SSoT für alle DTOs)
WORKFLOW_MANAGER = JobMiningWorkflowManager(
    text_extractor=AdvancedTextExtractor(),
    competence_extractor=None,  # Wird unten injiziert
    organization_service=OrganizationService(rule_client=RULE_CLIENT),
    role_service=RoleService(rule_client=RULE_CLIENT),
    metadata_extractor=MetadataExtractor()
)

# =========================================================
# 3. NLP-SPEZIALISTEN (Nutzen den Manager als Factory)
# =========================================================

spacy_ext = SpaCyCompetenceExtractor(
    repository=COMPETENCE_REPOSITORY,
    manager=WORKFLOW_MANAGER
)

discovery_ext = DiscoveryExtractor(
    repository=COMPETENCE_REPOSITORY,
    manager=WORKFLOW_MANAGER
)

# Kombinierter Extractor für den Workflow
class CompetenceChef:
    def __init__(self, s_ext, d_ext,nlp_m=None):
        self.s_ext = s_ext
        self.d_ext = d_ext
         # Wir brauchen das Model hier!
        # Fallback: Wenn nlp_m nicht übergeben wurde, nimm das Modell aus dem spacy_ext
        if nlp_m:
            self.nlp = nlp_m
        elif hasattr(s_ext, 'nlp'):
            self.nlp = s_ext.nlp
        else:
            import spacy
            self.nlp = spacy.load("de_core_news_md")

    def extract_competences(self, text, role=None):
        #0. absichern
        # 1. Schritt: Rohtext EINMAL verarbeiten
        doc = self.nlp(text)

        # 1. Schritt: SpaCy findet alles aus ESCO und deinen Domänen (Ebene 2, 4, 5)
        #known_comps = self.s_ext.extract_competences(text, role)

        # 2. Schritt: Discovery findet neue Begriffe (Ebene 1)
        # Wir übergeben das SpaCy-Doc (falls im Extractor verfügbar) oder den Text
        known_comps = self.s_ext.extract_competences(doc, role)
        new_discoveries = self.d_ext.extract_discoveries(doc)

        # Kombinieren (Ebene 1-5)
        return known_comps + new_discoveries

WORKFLOW_MANAGER.competence_extractor = CompetenceChef(spacy_ext, discovery_ext)

# =========================================================
# 4. API & STARTUP
# =========================================================

app = FastAPI(title="Job Mining Backend - V2")

def ensure_playwright():
    try:
        # Prüft, ob chromium installiert ist
        subprocess.run(["playwright", "install", "chromium"], check=True)
        print("✅ Playwright Browser sind einsatzbereit.")
    except Exception as e:
        print(f"⚠️ Playwright Setup Fehler: {e}")

if __name__ == "__main__":
    ensure_playwright()

# Dependency für saubere Endpunkte
def get_manager():
    return WORKFLOW_MANAGER

# FIX: Endpunkt muss /analyse heißen, damit Kotlin ihn findet
#@app.post("/analyse")
#async def api_analyse_file(file: UploadFile = File(...)):
#    return WORKFLOW_MANAGER.run_full_analysis(file.file, file.filename)

# TÜR 1: Upload (Das war dein 500er Fehler -> Jetzt gefixt durch run_full_analysis)
@app.post("/analyse/file", response_model=AnalysisResultDTO)
async def api_analyse_file(file: UploadFile = File(...)):
    """Wird von Kotlin aufgerufen (PythonAnalysisClient).

    Wird von Kotlin aufgerufen (PythonAnalysisClient.sendDocumentForAnalysis).
    Nimmt PDF/DOCX entgegen und startet den Workflow.
    """

    print(f"📥 [API] Empfange Datei: {file.filename}")
    try:
        # Hier rufen wir den Manager auf, der alles koordiniert (Text -> Skills -> JSON)
        return await WORKFLOW_MANAGER.run_full_analysis(file.file, file.filename)
    except Exception as e:
        print(f"❌ Fehler im /analyse Endpunkt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyse/scrape-url", response_model=AnalysisResultDTO)
async def api_analyse_url(url_input: URLInput):
    """Web-Scraping - nutzt die Logik aus core/api_endpoints.py."""
    return scrape_and_analyze_url(url_input, manager=WORKFLOW_MANAGER)

# TÜR 2: Text / Scraping
class TextRequest(BaseModel):
    text: str
    source_name: str = "scraped_content"

@app.post("/analyse/text", response_model=AnalysisResultDTO)
async def api_analyse_text(req: TextRequest):
    """Direkte Text-Analyse für Scraper."""
    return WORKFLOW_MANAGER.run_analysis_from_scraped_text(req.text, req.source_name)



def get_ip():
    return socket.gethostbyname(socket.gethostname())

@app.get("/health/status")
async def health_check():
    """Wissenschaftlicher Status-Check mit IP und echtem Label-Count."""
    # FIX: Nutze .esco_skills (aus HybridCompetenceRepository) statt .reference_labels
    return {
        "status": "online",
        "ip": socket.gethostbyname(socket.gethostname()),
        "esco_labels": len(COMPETENCE_REPOSITORY.esco_skills),
        "active_patterns": "Ebenen 1-6 geladen"
    }

@app.get("/system/status")
def get_system_status():
    """Gibt Auskunft über den Ladezustand des Python-Backends."""
    skill_count = len(COMPETENCE_REPOSITORY.esco_data)
    is_ready = skill_count > 0

    return {
        "status": "ONLINE" if is_ready else "WAITING",
        "ready": is_ready,
        "skills_loaded": skill_count,
        "domains_loaded": len(COMPETENCE_REPOSITORY._academia_skills) + len(COMPETENCE_REPOSITORY._fachbuch_skills),
        "message": "System bereit für Analyse" if is_ready else "Wissensbasis leer oder lädt noch."
    }

from app.core.api_endpoints import batch_process_local_jobs # Import sicherstellen

@app.post("/batch-process")
async def api_batch_process():
    """Startet die Analyse aller Dateien im lokalen 'data/jobs' Ordner."""
    return batch_process_local_jobs(manager=WORKFLOW_MANAGER)

@app.on_event("startup")
async def startup_event():
    logger.info(f"🚀 EVENT Backend gestartet. Daten-Pfad: {BASE_DATA_DIR}")
    # Erst Browser prüfen
    ensure_playwright()
    # Hier folgen deine anderen Initialisierungen (Repository, Extractor etc.)
    print("🚀 API-Startup abgeschlossen.")

    # Prüfe ob die Pfade existieren
    for name, path in PATHS.items():
        if not os.path.exists(path):
            logger.warning(f"⚠️ StartupEvent Pfad fehlt: {name} -> {path}")


@app.post("/internal/admin/refresh-knowledge")
async def trigger_knowledge_refresh():
    """
    Wird von Kotlin aufgerufen.
    Zwingt Python, die ESCO-Daten und Regeln neu zu laden.
    """
    try:
        print("🚀 SIGNAL EMPFANGEN: Starte manuellen Reload der Wissensbasis...")

        # 1. Cache leeren & Neu laden
        COMPETENCE_REPOSITORY.load_all_data()

        return {
            "status": "success",
            "message": "Wissensbasis erfolgreich aktualisiert.",
            "current_skill_count": len(COMPETENCE_REPOSITORY.esco_data)
        }
    except Exception as e:
        print(f"❌ Fehler beim Reload: {e}")
        # Wir geben 500 zurück, damit Kotlin merkt, dass es nicht geklappt hat
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
