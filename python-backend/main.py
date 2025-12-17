# main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends

# --- INFRASTRUKTUR & DOMAIN IMPORTS ---
from advanced_text_extractor import AdvancedTextExtractor
from interfaces import IJobMiningWorkflowManager, ITextExtractor, ICompetenceExtractor
from job_mining_workflow_manager import JobMiningWorkflowManager

from repositories.hybrid_competence_repository import HybridCompetenceRepository
from infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor
from infrastructure.clients.kotlin_rule_client import KotlinRuleClient
from api_endpoints import scrape_and_analyze_url, analyse_job_ad, batch_process_local_jobs, URLInput

from domain.services.organization_service import OrganizationService
from domain.services.role_service import RoleService
from job_directory_processor import JobDirectoryProcessor
from typing import List
from models import AnalysisResultDTO
# =========================================================
# 1. Globale Instanziierung (SINGLETONS)
# =========================================================

# Infrastruktur-Clients
RULE_CLIENT = KotlinRuleClient()
TEXT_EXTRACTOR: ITextExtractor = AdvancedTextExtractor()

# Domain/Repository (injiziert den Client)
# KERN-FIX: Das Repository lädt jetzt ALLES (ESCO + Custom) selbständig intern
COMPETENCE_REPOSITORY = HybridCompetenceRepository(rule_client=RULE_CLIENT)

# Extractor (injiziert das Repository)
COMPETENCE_EXTRACTOR: ICompetenceExtractor = SpaCyCompetenceExtractor(repository=COMPETENCE_REPOSITORY)

# Services
ORGANIZATION_SERVICE = OrganizationService(rule_client=RULE_CLIENT)
ROLE_SERVICE = RoleService(rule_client=RULE_CLIENT)



# Workflow Manager
WORKFLOW_MANAGER: IJobMiningWorkflowManager = JobMiningWorkflowManager(
    text_extractor=TEXT_EXTRACTOR,
    competence_extractor=COMPETENCE_EXTRACTOR,
    organization_service=ORGANIZATION_SERVICE,
    role_service=ROLE_SERVICE
)

# Instanziierung (Der Prozessor braucht den WorkflowManager)
# 1. Den Prozessor erstellen und den vorhandenen WORKFLOW_MANAGER übergeben
# Stelle sicher, dass "JobDirectoryProcessor" importiert wurde
DIRECTORY_PROCESSOR = JobDirectoryProcessor(
    manager=WORKFLOW_MANAGER,
    base_path="data/jobs")

app = FastAPI()

# --- DEPENDENCY INJECTION ---
def get_workflow_manager() -> IJobMiningWorkflowManager:
    return WORKFLOW_MANAGER

# --- ENDPUNKTE ---

@app.post("/analyse")
async def handle_analyse(file: UploadFile = File(...), manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)):
    return analyse_job_ad(file=file, manager=manager)

@app.post("/scrape-url")
async def handle_scrape(url_input: URLInput, manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)):
    return scrape_and_analyze_url(url_input=url_input, manager=manager)

# 2. Den Endpunkt für Kotlin registrieren
@app.post("/batch-process", response_model=List[AnalysisResultDTO])
async def run_batch_analysis():
    """
    Dieser Endpunkt wird von Kotlin aufgerufen.
    Er triggert den Batch-Lauf über den DirectoryProcessor.
    """
    # Ruft die Methode auf, die du vorhin in der Datei JobDirectoryProcessor hattest
    return DIRECTORY_PROCESSOR.process_all_jobs()

# In main.py hinzufügen:
@app.get("/health")
async def  health_check():
    return {"status": "online"}

@app.get("/health/esco-count")
async def get_esco_count():
    """Gibt die geladene ESCO-Kompetenzanzahl direkt aus dem Repository zurück."""
    return {
        "status": "OK",
        "esco_label_count": len(COMPETENCE_REPOSITORY.get_all_skills()),
        "custom_label_count": len(COMPETENCE_REPOSITORY.get_custom_only()),
        "total_competences": len(COMPETENCE_REPOSITORY.get_all_skills())
    }



