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
from app.infrastructure.extractor.fuzzy_competence_extractor import FuzzyCompetenceExtractor
from app.infrastructure.extractor.competence_extractor import CompetenceExtractor
from app.infrastructure.extractor.discovery_extractor import DiscoveryExtractor
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
# 3. SYSTEM-VERDRAHTUNG (WIRING) MIT FEHLERBEHANDLUNG
# =========================================================
logger.info("🔧 Initialisiere Komponenten...")

try:
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

    # D. NLP components (SpaCy + Fuzzy + Discovery)
    # Create base extractors first
    SPACY_EXT = SpaCyCompetenceExtractor(repository=COMPETENCE_REPOSITORY)
    FUZZY_EXT = FuzzyCompetenceExtractor(repository=COMPETENCE_REPOSITORY)

    # E. Manager: temporarily wire SPACY_EXT as placeholder, will be replaced after Discovery is constructed
    WORKFLOW_MANAGER = JobMiningWorkflowManager(
        text_extractor=TEXT_EXTRACTOR,
        competence_extractor=SPACY_EXT,  # placeholder
        organization_service=ORG_SERVICE,
        role_service=ROLE_SERVICE,
        metadata_extractor=METADATA_EXTRACTOR
    )

    # Discovery extractor needs a reference to the manager
    DISCOVERY_EXT = DiscoveryExtractor(repository=COMPETENCE_REPOSITORY, manager=WORKFLOW_MANAGER)

    # Now build the full CompetenceExtractor (passes: Spacy, Fuzzy, Discovery)
    COMPETENCE_EXTRACTOR = CompetenceExtractor(spacy_ext=SPACY_EXT, fuzzy_ext=FUZZY_EXT, discovery_ext=DISCOVERY_EXT)
    # Inject the real competence extractor into the manager
    WORKFLOW_MANAGER.competence_extractor = COMPETENCE_EXTRACTOR

    # F. Batch
    DIRECTORY_PROCESSOR = JobDirectoryProcessor(
        manager=WORKFLOW_MANAGER,
        base_path=JOB_DIR
    )

    logger.info("✅ System erfolgreich verdrahtet.")
    
except ImportError as e:
    logger.error(f"❌ Fehler beim Importieren von Modulen: {e}")
    logger.error("   Bitte führen Sie 'pip install -r requirements.txt' aus.")
    sys.exit(1)
except Exception as e:
    logger.error(f"❌ Kritischer Fehler bei der System-Initialisierung: {e}", exc_info=True)
    logger.error("   System kann nicht gestartet werden!")
    sys.exit(1)


# =========================================================
# 4. API ENDPUNKTE (ANGEPASST AN KOTLIN-ERWARTUNG)
# =========================================================

@app.on_event("startup")
async def startup_event():
    """Startup mit umfassender Fehlerbehandlung"""
    try:
        logger.info("🚀 API startet...")
        if not os.path.exists(JOB_DIR):
            os.makedirs(JOB_DIR, exist_ok=True)

        # Check Repo mit Fehlerbehandlung
        try:
            if len(COMPETENCE_REPOSITORY.get_all_skills()) == 0:
                logger.warning("⚠️ Repository leer. Trigger Nachladen...")
                if hasattr(COMPETENCE_REPOSITORY, "_load_data"):
                    COMPETENCE_REPOSITORY._load_data()
        except Exception as e:
            logger.error(f"⚠️ Fehler beim Laden des Repositories: {e}")
            logger.info("   System läuft weiter mit Fallback-Daten...")
    except Exception as e:
        logger.error(f"❌ Kritischer Fehler beim Startup: {e}")
        logger.info("   System versucht trotzdem zu starten...")


# --- PFAD-FIX 1: /analyse/file statt /analyse ---
@app.post("/analyse/file", response_model=AnalysisResultDTO)
async def analyze_file(file: UploadFile = File(...)):
    """Upload-Endpunkt für Kotlin (PDF/DOCX) mit robuster Fehlerbehandlung."""
    logger.info(f"📥 [POST /analyse/file] Datei: {file.filename}")
    try:
        # Validierung
        if not file.filename:
            raise HTTPException(status_code=400, detail="Dateiname fehlt")
        
        # Dateiinhalt prüfen
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Datei ist leer")
        
        # Reset file pointer für weitere Verarbeitung
        from io import BytesIO
        file_obj = BytesIO(content)
        
        return await WORKFLOW_MANAGER.run_full_analysis(file_obj, file.filename)
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"❌ Validierungsfehler: {e}")
        raise HTTPException(status_code=400, detail=f"Validierungsfehler: {str(e)}")
    except Exception as e:
        logger.error(f"❌ Interner Fehler bei Dateianalyse: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analyse fehlgeschlagen: {str(e)}")


# --- PFAD-FIX 2: /analyse/scrape-url statt /scrape-url ---
@app.post("/analyse/scrape-url", response_model=AnalysisResultDTO)
async def scrape_url_endpoint(url_input: URLInput):
    """Scraping-Endpunkt mit Fehlerbehandlung."""
    logger.info(f"🌍 [POST /analyse/scrape-url] URL: {url_input.url}")
    try:
        if not url_input.url or not url_input.url.strip():
            raise HTTPException(status_code=400, detail="URL fehlt oder ist leer")
        return scrape_and_analyze_url(url_input, manager=WORKFLOW_MANAGER)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Fehler beim URL-Scraping: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Scraping fehlgeschlagen: {str(e)}")


# --- PFAD-FIX 3: /system/status statt /health ---
@app.get("/system/status")
def system_status():
    """Health-Check für Kotlin mit robuster Fehlerbehandlung."""
    try:
        skills_count = 0
        try:
            skills_count = len(COMPETENCE_REPOSITORY.get_all_skills())
        except Exception as e:
            logger.warning(f"Fehler beim Abrufen der Skills: {e}")
        
        return {
            "status": "UP",
            "service": "python-backend",
            "skills_loaded": skills_count,
            "version": "2.3.0"
        }
    except Exception as e:
        logger.error(f"❌ Fehler im Status-Check: {e}")
        return {
            "status": "DEGRADED",
            "service": "python-backend",
            "error": str(e)
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


# --- DASHBOARD / REPORTING ENDPOINTS ---
from fastapi.responses import StreamingResponse
from app.infrastructure.reporting import build_dashboard_metrics, generate_csv_report, generate_pdf_report

@app.get("/reports/dashboard-metrics")
def get_dashboard_metrics(top_n: int = 10):
    """Aggregierte Metriken für das Dashboard (Top Skills, Domain Mix, Zeitreihen)"""
    metrics = build_dashboard_metrics(top_n=top_n)
    return metrics


@app.get("/reports/export.csv")
def download_csv_report():
    """Generiert einen CSV-Export der aktuell verarbeiteten Jobs."""
    csv_bio = generate_csv_report()
    return StreamingResponse(csv_bio, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=job_mining_data_report.csv"})


@app.get("/reports/export.pdf")
def download_pdf_report():
    """Generiert einen einfachen PDF-Report der aktuell verarbeiteten Jobs."""
    pdf_bio = generate_pdf_report()
    return StreamingResponse(pdf_bio, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=job_mining_report.pdf"})


# Bestehende Pfade (waren bereits korrekt/grün)
@app.post("/batch-process", response_model=List[AnalysisResultDTO])
async def trigger_batch():
    """Batch-Verarbeitung mit Fehlerbehandlung"""
    logger.info("📦 [POST /batch-process] Starte...")
    try:
        results = await DIRECTORY_PROCESSOR.process_all_jobs()
        logger.info(f"📦 Batch fertig: {len(results)} Dateien analysiert.")
        return results
    except Exception as e:
        logger.error(f"❌ Fehler bei Batch-Verarbeitung: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Batch-Verarbeitung fehlgeschlagen: {str(e)}")

@app.post("/internal/admin/refresh-knowledge")
def refresh_knowledge():
    """Knowledge-Base-Refresh mit umfassender Fehlerbehandlung"""
    logger.info("🔄 [POST /refresh-knowledge] Refresh...")
    try:
        errors = []
        
        # Repository-Daten neu laden
        if hasattr(COMPETENCE_REPOSITORY, "_load_data"):
            try:
                COMPETENCE_REPOSITORY._load_data()
            except Exception as e:
                logger.error(f"Fehler beim Laden der Basis-Daten: {e}")
                errors.append(f"_load_data: {str(e)}")
        
        if hasattr(COMPETENCE_REPOSITORY, "_load_custom_skills"):
            try:
                COMPETENCE_REPOSITORY._load_custom_skills()
            except Exception as e:
                logger.error(f"Fehler beim Laden der Custom Skills: {e}")
                errors.append(f"_load_custom_skills: {str(e)}")
        
        if hasattr(COMPETENCE_REPOSITORY, "_load_dynamic_blacklist"):
            try:
                COMPETENCE_REPOSITORY._load_dynamic_blacklist()
            except Exception as e:
                logger.error(f"Fehler beim Laden der Blacklist: {e}")
                errors.append(f"_load_dynamic_blacklist: {str(e)}")

        # Extractor neu initialisieren
        try:
            global COMPETENCE_EXTRACTOR, WORKFLOW_MANAGER
            COMPETENCE_EXTRACTOR = SpaCyCompetenceExtractor(repository=COMPETENCE_REPOSITORY)
            WORKFLOW_MANAGER.competence_extractor = COMPETENCE_EXTRACTOR
        except Exception as e:
            logger.error(f"Fehler beim Neuinitialisieren des Extractors: {e}")
            errors.append(f"extractor_init: {str(e)}")

        skills_count = 0
        try:
            skills_count = len(COMPETENCE_REPOSITORY.get_all_skills())
        except Exception as e:
            logger.error(f"Fehler beim Zählen der Skills: {e}")
            errors.append(f"count_skills: {str(e)}")

        result = {
            "status": "refreshed" if not errors else "partial",
            "skills": skills_count
        }
        
        if errors:
            result["errors"] = errors
            result["message"] = "Refresh teilweise erfolgreich mit Fehlern"
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Kritischer Fehler beim Refresh: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Refresh fehlgeschlagen: {str(e)}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
