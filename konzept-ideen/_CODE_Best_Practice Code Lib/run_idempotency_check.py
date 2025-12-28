# job-mining/run_idempotency_check.py (KORRIGIERT für Repository Pattern)

from core.entities.job_posting import JobPosting
from core.entities.competence import Competence
# ALTE IMPORTS ENTFERNEN: from infrastructure.storage.db_service import save_job_posting, fetch_all_job_postings, get_engine, setup_db
# NEUE IMPORTS HINZUFÜGEN:
from infrastructure.storage.db_service import get_engine, setup_db, sessionmaker
from infrastructure.storage.job_repository import JobRepository
import os

# --- 0. Setup Repository und Session ---
engine = get_engine()
setup_db(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- 1. Vorbereitung ---
print("--- 1. Vorbereitung: Datenbank bereinigen ---")
db_file = "job_mining_local.db"

# Engine einmal holen (falls sie existiert) und dispose() aufrufen
try:
    engine = get_engine()
    engine.dispose() # WICHTIG: Erzwingt das Schließen aller Verbindungen
except Exception:
    pass # Fehler ignorieren, falls Engine noch nicht erstellt wurde

if os.path.exists(db_file):
    os.remove(db_file)
    print(f"Datenbankdatei {db_file} gelöscht.")

# NEU: Wir initialisieren die Engine erst HIER, nachdem die Datei physisch gelöscht wurde.
engine = get_engine()
setup_db(engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# --- 2. Erstellen von Testdaten ---
# (Die Definition von test_competences, job_v1, job_v2 bleibt hier gleich)
test_competences = [
    Competence(original_skill="Python-Kenntnisse", esco_match="Python", score=0.9, category="Skill", context_section="Anforderungen")
]
job_v1 = JobPosting(
    source_id="DE_12345", source_path="/raw/job1.pdf", title="Data Scientist (Original)",
    company="TechCorp", region="Berlin", year=2025, branch="IT", raw_text="Langer Text...",
    competences=test_competences
)
job_v2 = JobPosting(
    source_id="DE_12345", source_path="/raw/job1_updated.pdf", title="Senior Data Scientist (UPDATE)",
    company="TechCorp", region="Berlin", year=2025, branch="IT", raw_text="Langer Text...",
    competences=[
        Competence(original_skill="Python-Kenntnisse", esco_match="Python", score=0.95, category="Skill", context_section="Anforderungen"),
        Competence(original_skill="MLOps", esco_match="ML Engineer", score=0.8, category="Skill", context_section="Aufgaben")
    ]
)
# --- Ende 2. Erstellen von Testdaten ---


# --- 3. Test der Idempotenz ---
print("\n--- 3. Testlauf: Speichere Job V1 ---")
with SessionLocal() as session:
    # NEU: Repository mit der aktuellen Session erstellen
    repo = JobRepository(session=session)
    repo.save_job_posting(job_v1) # Methode auf dem Repository aufrufen

# Nach dem Commit muss eine neue Session für den Abruf verwendet werden
with SessionLocal() as session:
    repo = JobRepository(session=session)
    current_jobs = repo.fetch_all_job_postings() # Methode auf dem Repository aufrufen
    print(f"Aktuelle Jobs in DB: {len(current_jobs)}")


# --- 4. Testlauf: Speichere Job V2 (gleiche Source ID) ---
print("\n--- 4. Testlauf: Speichere Job V2 (gleiche Source ID) ---")
with SessionLocal() as session:
    repo = JobRepository(session=session)
    repo.save_job_posting(job_v2) # Methode auf dem Repository aufrufen

with SessionLocal() as session:
    repo = JobRepository(session=session)
    current_jobs = repo.fetch_all_job_postings()
    print(f"Aktuelle Jobs in DB nach Update: {len(current_jobs)}")


# --- 5. Validierung der Korrektheit ---
print("\n--- 5. Validierung der Datenintegrität ---")
if len(current_jobs) == 1:
    final_job = current_jobs[0]
    # ... (Rest der Validierungs-Logik bleibt gleich) ...

    if final_job['title'] == "Senior Data Scientist (UPDATE)" and len(final_job['competences']) == 2:
        print("✅ SUCCESS: Idempotenz (Upsert) erfolgreich validiert. Der alte Job wurde ersetzt.")
    else:
        print("❌ FAILURE: Idempotenz-Logik ist fehlerhaft.")
else:
    print("❌ FAILURE: Es wurden mehr als 1 Job in der Datenbank gefunden (Duplikate).")
