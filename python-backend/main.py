import os
import logging
import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from typing import List, Dict

# --- 1. KORREKTE IMPORTE (Mit 'app.' Prefix) ---
from app.domain.models import AnalysisResultDTO
from app.interfaces.interfaces import IJobMiningWorkflowManager

# Infrastruktur
from app.infrastructure.clients.kotlin_rule_client import KotlinRuleClient
from app.infrastructure.repositories.hybrid_competence_repository import HybridCompetenceRepository
from app.infrastructure.extractor.advanced_text_extractor import AdvancedTextExtractor
from app.infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor
from app.infrastructure.extractor.metadata_extractor import MetadataExtractor
from app.infrastructure.io.job_directory_processor import JobDirectoryProcessor

# Domain Services
from app.application.services.organization_service import OrganizationService
from app.application.services.role_service import RoleService

# Orchestrator
from app.application.job_mining_workflow_manager import JobMiningWorkflowManager

# API Helper
from app.core.api_endpoints import scrape_and_analyze_url, URLInput

# --- 2. SETUP & LOGGING ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("JobMiningBackend")

BASE_DATA_DIR = os.getenv("BASE_DATA_DIR", "data")
JOB_DIR = os.path.join(BASE_DATA_DIR, "jobs")

app = FastAPI(title="Job Mining Python Analysis Engine", version="2.3.0")

# =========================================================
# 3. SYSTEM-VERDRAHTUNG (WIRING)
# =========================================================
logger.info("🔧 Initialisiere Komponenten...")

# A. Basis (SSoT)
RULE_CLIENT = KotlinRuleClient()

# Repository (Keine Selbst-Importe mehr!)
COMPETENCE_REPOSITORY = HybridCompetenceRepository(rule_client=RULE_CLIENT)

# B. Extraktoren
TEXT_EXTRACTOR = AdvancedTextExtractor()
METADATA_EXTRACTOR = MetadataExtractor()

# C. Services (FIX: RuleClient wird übergeben!)
ORG_SERVICE = OrganizationService(rule_client=RULE_CLIENT)

# RoleService (Fehlerabfangung, falls alte Version ohne Client)
try:
    ROLE_SERVICE = RoleService(rule_client=RULE_CLIENT)
except TypeError:
    logger.info("ℹ️ RoleService nutzt Standard-Init (kein RuleClient).")
    ROLE_SERVICE = RoleService()

# D. NLP
COMPETENCE_EXTRACTOR = SpaCyCompetenceExtractor(repository=COMPETENCE_REPOSITORY)

# E. Manager
WORKFLOW_MANAGER = JobMiningWorkflowManager(
    text_extractor=TEXT_EXTRACTOR,
    competence_extractor=COMPETENCE_EXTRACTOR,
    organization_service=ORG_SERVICE,
    role_service=ROLE_SERVICE,
    metadata_extractor=METADATA_EXTRACTOR
)

# F. Batch
DIRECTORY_PROCESSOR = JobDirectoryProcessor(
    manager=WORKFLOW_MANAGER,
    base_path=JOB_DIR
)

logger.info("✅ System erfolgreich verdrahtet.")


# =========================================================
# 4. API ENDPUNKTE (ANGEPASST AN KOTLIN-ERWARTUNG)
# =========================================================

@app.on_event("startup")
async def startup_event():
    logger.info("🚀 API startet...")
    if not os.path.exists(JOB_DIR):
        os.makedirs(JOB_DIR, exist_ok=True)

    # Check Repo
    if len(COMPETENCE_REPOSITORY.get_all_skills()) == 0:
        logger.warning("⚠️ Repository leer. Trigger Nachladen...")
        if hasattr(COMPETENCE_REPOSITORY, "_load_data"):
            COMPETENCE_REPOSITORY._load_data()


# --- PFAD-FIX 1: /analyse/file statt /analyse ---
@app.post("/analyse/file", response_model=AnalysisResultDTO)
async def analyze_file(file: UploadFile = File(...)):
    """Upload-Endpunkt für Kotlin (PDF/DOCX)."""
    logger.info(f"📥 [POST /analyse/file] Datei: {file.filename}")
    try:
        return await WORKFLOW_MANAGER.run_full_analysis(file.file, file.filename)
    except Exception as e:
        logger.error(f"❌ Fehler: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# --- PFAD-FIX 2: /analyse/scrape-url statt /scrape-url ---
@app.post("/analyse/scrape-url", response_model=AnalysisResultDTO)
async def scrape_url_endpoint(url_input: URLInput):
    """Scraping-Endpunkt."""
    logger.info(f"🌍 [POST /analyse/scrape-url] URL: {url_input.url}")
    return scrape_and_analyze_url(url_input, manager=WORKFLOW_MANAGER)


# --- PFAD-FIX 3: /system/status statt /health ---
@app.get("/system/status")
def system_status():
    """Health-Check für Kotlin."""
    return {
        "status": "UP",
        "service": "python-backend",
        "skills_loaded": len(COMPETENCE_REPOSITORY.get_all_skills())
    }

# --- PFAD-FIX 4: /role-mappings (NEU) ---
@app.get("/role-mappings")
def get_role_mappings():
    """
    Gibt die aktiven Rollen-Mappings zurück, damit Kotlin den Status prüfen kann.
    """
    # Versuche Mappings aus dem RoleService oder RuleClient zu holen
    mappings = {}
    if hasattr(ROLE_SERVICE, 'role_mappings'):
        mappings = ROLE_SERVICE.role_mappings
    elif hasattr(RULE_CLIENT, '_get_static_fallback_role_mappings'):
        mappings = RULE_CLIENT._get_static_fallback_role_mappings()

    return {
        "count": len(mappings),
        "mappings": mappings
    }


# Bestehende Pfade (waren bereits korrekt/grün)
@app.post("/batch-process")
async def trigger_batch():
    logger.info("📦 [POST /batch-process] Starte...")
    results = DIRECTORY_PROCESSOR.process_all_jobs()
    return {
        "status": "completed",
        "count": len(results),
        "message": f"{len(results)} Dateien analysiert."
    }

@app.post("/internal/admin/refresh-knowledge")
def refresh_knowledge():
    logger.info("🔄 [POST /refresh-knowledge] Refresh...")
    if hasattr(COMPETENCE_REPOSITORY, "_load_data"):
        COMPETENCE_REPOSITORY._load_data()
        COMPETENCE_REPOSITORY._load_custom_skills()
        COMPETENCE_REPOSITORY._load_dynamic_blacklist()

    global COMPETENCE_EXTRACTOR, WORKFLOW_MANAGER
    COMPETENCE_EXTRACTOR = SpaCyCompetenceExtractor(repository=COMPETENCE_REPOSITORY)
    WORKFLOW_MANAGER.competence_extractor = COMPETENCE_EXTRACTOR

    return {"status": "refreshed", "skills": len(COMPETENCE_REPOSITORY.get_all_skills())}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
