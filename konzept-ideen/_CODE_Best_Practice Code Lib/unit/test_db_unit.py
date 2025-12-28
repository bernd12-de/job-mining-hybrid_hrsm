# tests/unit/test_db_unit.py

import pytest
import os
import shutil
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Importiere Core-Entitäten und Infrastructure-Funktionen
from infrastructure.storage.job_repository import JobRepository
from infrastructure.storage.db_service import Base
from core.entities.job_posting import JobPosting, Competence
from infrastructure.extractor.advanced_text_extractor import AdvancedTextExtractor

# In-Memory SQLite URL
IN_MEMORY_DB_URL = "sqlite:///:memory:"
TEST_FILES_PATH = os.path.join(os.path.dirname(__file__), '..', 'test_files')

# ----------------------------------------------------
# 1. FIXTURES (Pytest Setup)
# ----------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def setup_test_files():
    """Stellt sicher, dass der Testordner und eine funktionierende TXT-Datei existieren."""

    os.makedirs(TEST_FILES_PATH, exist_ok=True)
    txt_path = os.path.join(TEST_FILES_PATH, "test_job_ad.txt")

    # Datei nur erstellen, wenn sie NICHT existiert (Garantie)
    if not os.path.exists(txt_path):
        print(f"\n[Test Setup] Erstelle fehlende TXT-Datei: {txt_path}")
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("Dies ist die automatisch erstellte, funktionierende Rohtext-Basis. Dieser Satz dient nur dazu, die Mindestlänge von 100 Zeichen für die Validierung von Stellenanzeigen in der Pipeline zu erreichen und die Konsistenz der Testumgebung sicherzustellen.")
    else:
        print(f"\n[Test Setup] Verwende vorhandene TXT-Datei: {txt_path}")

    yield
    # Wir behalten den Ordner und die Dateien, um manuelle Tests zu ermöglichen.

"""
@pytest.fixture(scope="session")
def db_engine():
    ##"Erstellt eine Engine, die nur im RAM existiert.##
    engine = create_engine(IN_MEMORY_DB_URL)
    Base.metadata.create_all(engine)
    return engine
"""
@pytest.fixture(scope="function")
def job_repository(db_engine):
    """Stellt eine neue Repository-Instanz mit einer isolierten In-Memory Session bereit."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()

    repo = JobRepository(session=session)

    yield repo

    # Nach dem Test: Rollback, um die Änderungen im Speicher zu löschen
    session.rollback()
    session.close()

@pytest.fixture
def sample_job_posting():
    """Erstellt ein JobPosting-Objekt für die Tests (mit korrigiertem 'branch')."""
    competences = [
        Competence(original_skill="SQL", esco_match="SQL", score=0.9, category="Skill", context_section="Anforderungen"),
    ]
    return JobPosting(
        source_id="UNIT_TEST_001",
        source_path="/unit/test.txt",
        title="Unit Test Job",
        company="PyTest GmbH",
        region="Memory",
        year=2025,
        raw_text="Test content for in-memory DB.",
        branch="IT/Consulting",
        competences=competences
    )

# ----------------------------------------------------
# 2. UNIT TESTS
# ----------------------------------------------------

def test_01_save_and_fetch_job(job_repository: JobRepository, sample_job_posting: JobPosting):
    """Testet das Speichern und Abrufen eines einzelnen Jobs."""

    job_repository.save_job_posting(sample_job_posting)

    jobs = job_repository.fetch_all_job_postings()

    assert len(jobs) == 1
    assert jobs[0]['source_id'] == "UNIT_TEST_001"
    assert jobs[0]['title'] == "Unit Test Job"
    assert len(jobs[0]['competences']) == 1

def test_02_idempotency_upsert_logic(job_repository: JobRepository, sample_job_posting: JobPosting):
    """Testet, ob die Idempotenz (Upsert) in der In-Memory DB korrekt funktioniert."""

    # 1. Job V1 speichern
    job_repository.save_job_posting(sample_job_posting)

    # 2. Job V2 (gleiche ID, neuer Titel) erstellen und speichern
    # NEU: Das Objekt muss mit der aktuellen Dataclass-Definition neu erstellt werden
    job_v2 = JobPosting(
        source_id=sample_job_posting.source_id,
        source_path=sample_job_posting.source_path,
        title="Unit Test Job V2 (Updated)",
        company=sample_job_posting.company,
        region=sample_job_posting.region,
        year=sample_job_posting.year,
        raw_text=sample_job_posting.raw_text,
        branch=sample_job_posting.branch,
        competences=[
            Competence(original_skill="Refactored Code", esco_match="Refactoring", score=1.0, category="Skill", context_section="Aufgaben")
        ]
    )

    job_repository.save_job_posting(job_v2)

    # Abrufen und Prüfen
    jobs = job_repository.fetch_all_job_postings()

    assert len(jobs) == 1
    assert jobs[0]['title'] == "Unit Test Job V2 (Updated)"
    assert len(jobs[0]['competences']) == 1
