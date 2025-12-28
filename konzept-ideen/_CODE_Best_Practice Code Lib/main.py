# job-mining/main.py

from fastapi import FastAPI
from typing import Dict, List, Any
from core.services.competence_service import CompetenceService
from infrastructure.extractor.advanced_text_extractor import AdvancedTextExtractor
from infrastructure.storage.job_repository import JobRepository
from infrastructure.storage.db_service import get_db_session
# NEU: Import des SpaCy Extractor
from infrastructure.extractor.spacy_competence_extractor import SpaCyCompetenceExtractor

# --- Dependency Injection (DI) Setup ---
# 1. Wir instanziieren die Infrastruktur-Abhängigkeiten.
text_extractor_impl = AdvancedTextExtractor()
competence_extractor_impl = SpaCyCompetenceExtractor() # NEU: NLP-Extractor instanziiert

# NEU: Session und Repository erstellen
db_session = get_db_session()
job_repository = JobRepository(session=db_session)

# 2. Services instanziieren und alle Abhängigkeiten INJIZIEREN.
competence_service = CompetenceService(
    text_extractor=text_extractor_impl,
    job_repository=job_repository,
    competence_extractor=competence_extractor_impl # NEU: Übergabe des NLP-Extractors
)

# --- Initialisierung der FastAPI-App ---
app = FastAPI(
    title="Job Mining Service API",
    description="Stellt Endpunkte für die Abfrage und Verarbeitung der analysierten Stellenanzeigen bereit.",
    version="1.0.0"
)


# --- Endpunkte (Interfaces Layer) ---

# Endpoint 1: Root
@app.get("/", response_model=Dict)
def read_root():
    return {"message": "Job Mining Service läuft erfolgreich!"}

# Endpoint 2: Abfrage aller Jobs
@app.get("/jobs/", response_model=List[Dict])
def get_all_jobs():
    # Abruf über das Repository
    jobs = job_repository.fetch_all_job_postings()
    return jobs

# Endpoint 3: Verarbeitung einer neuen Job-Anzeige
@app.post("/jobs/process/")
def process_job_data(raw_data: Dict[str, Any]):
    """Nimmt rohe Jobdaten entgegen und startet die Verarbeitungs-Pipeline."""

    # 1. Aufruf des Application Service
    processed_job = competence_service.process_job_posting(raw_data)

    # 2. Rückmeldung an den Nutzer
    return {
        "status": "success",
        "message": f"Job '{processed_job.title}' erfolgreich verarbeitet und gespeichert (ID: {processed_job.source_id}).",
        "competences_extracted": len(processed_job.competences)
    }
