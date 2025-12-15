# main.py (FINALE KORREKTUR FÜR SAUBERE DI)

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
from domain.services.role_service import RoleService # NEU IMPORT
# =========================================================
# 1. Globale Instanziierung (SINGLETONS)
#    Die Komponenten werden HIER nur einmal erstellt.
# =========================================================

# Infrastruktur-Clients
RULE_CLIENT = KotlinRuleClient()
TEXT_EXTRACTOR: ITextExtractor = AdvancedTextExtractor()

# Domain/Repository (injiziert den Client)
# 🚨 FIX: Übergibt den RULE_CLIENT
COMPETENCE_REPOSITORY = HybridCompetenceRepository(rule_client=RULE_CLIENT)

# Extractor (injiziert das Repository)
COMPETENCE_EXTRACTOR: ICompetenceExtractor = SpaCyCompetenceExtractor(repository=COMPETENCE_REPOSITORY)

# 🚨 NEU: Instanziierung des Organization Service
ORGANIZATION_SERVICE = OrganizationService(rule_client=RULE_CLIENT)

# 🚨 NEU: Instanziierung des Role Service
ROLE_SERVICE = RoleService(rule_client=RULE_CLIENT)

# Workflow Manager (injiziert die Extraktoren)
# 🚨 NEU: Manager wird hier direkt als Singleton erstellt
WORKFLOW_MANAGER: IJobMiningWorkflowManager = JobMiningWorkflowManager(
    text_extractor=TEXT_EXTRACTOR,
    competence_extractor=COMPETENCE_EXTRACTOR,
    organization_service=ORGANIZATION_SERVICE,
    role_service=ROLE_SERVICE
)

app = FastAPI()

# --- DEPENDENCY INJECTION (DI) ---
# Die DI-Funktion muss nun NICHTS mehr erstellen, sondern nur noch das Singleton zurückgeben.
def get_workflow_manager() -> IJobMiningWorkflowManager:
    """Gibt die globale, einmalig erstellte Instanz des Managers zurück."""
    return WORKFLOW_MANAGER

# --- ENDE DER SAUBEREN DI ---


# --- ENDPUNKT-REGISTRIERUNG ---

# Dateiupload
@app.post("/analyse")
async def handle_analyse(file: UploadFile = File(...), manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)):
    return analyse_job_ad(file=file, manager=manager)

# Web-Scraping
@app.post("/scrape-url")
async def handle_scrape(url_input: URLInput, manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)):
    return scrape_and_analyze_url(url_input=url_input, manager=manager)

# Batch-Verarbeitung
@app.post("/batch-process")
async def handle_batch(manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)):
    return batch_process_local_jobs(manager=manager)

# Endpoint 4: ESCO Health Check
@app.get("/health/esco-count")
async def get_esco_count(manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)):
    """
    Gibt die geladene ESCO-Kompetenzanzahl zurück und testet die Ladestrategie.
    """
    repo = manager.competence_extractor.repository
    return {
        "status": "OK",
        "esco_label_count": len(repo.get_esco_only()),
        "custom_label_count": len(repo.get_custom_only()),
        "total_competences": len(repo.get_all_skills()),
        "loading_source": "API-gestützte Regeln und JSON Cache"
    }
