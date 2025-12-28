# tests/unit/test_03_file_integration.py

import pytest
import os
import shutil
from typing import List, Dict

# Importiere die notwendigen Komponenten
from infrastructure.storage.job_repository import JobRepository
from infrastructure.storage.db_service import Base
from core.entities.job_posting import JobPosting, Competence
from infrastructure.extractor.advanced_text_extractor import AdvancedTextExtractor

# Setup für die Dateipfade
TEST_FILES_PATH = os.path.join(os.path.dirname(__file__), '..', 'test_files')

# ----------------------------------------------------
# FIXTURES (Wir nutzen die In-Memory DB Fixtures aus test_db_unit.py)
# HINWEIS: Pytest findet die Fixtures automatisch, wenn wir sie hier nicht definieren.
# Wir müssen nur die Fixtures für diesen Test bereitstellen.
# ----------------------------------------------------

@pytest.fixture
def advanced_extractor():
    """Injiziert den AdvancedTextExtractor."""
    return AdvancedTextExtractor()

@pytest.fixture
def file_paths() -> Dict[str, str]:
    """Liefert die Pfade zu den manuell erstellten Testdateien."""

    # Stellt sicher, dass der Ordner existiert (wird durch test_db_unit.py's Fixture garantiert)
    return {
        'txt': os.path.join(TEST_FILES_PATH, "test_job_ad.txt"),
        'docx': os.path.join(TEST_FILES_PATH, "test_job_ad.docx"),
        'pdf': os.path.join(TEST_FILES_PATH, "test_job_ad.pdf"),
    }


# ----------------------------------------------------
# INTEGRATION TESTS (Parsing)
# ----------------------------------------------------

def test_01_txt_file_parsing(advanced_extractor: AdvancedTextExtractor, file_paths: Dict[str, str]):
    """Prüft das Auslesen der einfachen TXT-Datei."""

    txt_path = file_paths['txt']
    if not os.path.exists(txt_path):
        pytest.skip(f"TXT-Test übersprungen: Datei nicht gefunden unter {txt_path}")

    raw_text = advanced_extractor.extract_text(txt_path)
    assert raw_text is not None
    assert len(raw_text) > 10
    assert "Rohtext-Basis" in raw_text # Prüft den erwarteten Inhalt (aus der automatischen Erstellung)


def test_02_docx_file_parsing(advanced_extractor: AdvancedTextExtractor, file_paths: Dict[str, str]):
    """Prüft das Auslesen der DOCX-Datei."""

    docx_path = file_paths['docx']
    if not os.path.exists(docx_path):
        pytest.skip(f"DOCX-Test übersprungen: Datei nicht gefunden unter {docx_path}. Bitte manuell erstellen!")

    raw_text = advanced_extractor.extract_text(docx_path)
    assert raw_text is not None
    assert len(raw_text) > 10
    # Hier könntest du prüfen: assert "Dokumentlesung erfolgreich" in raw_text


def test_03_pdf_file_parsing(advanced_extractor: AdvancedTextExtractor, file_paths: Dict[str, str]):
    """Prüft das Auslesen der PDF-Datei."""

    pdf_path = file_paths['pdf']
    if not os.path.exists(pdf_path):
        pytest.skip(f"PDF-Test übersprungen: Datei nicht gefunden unter {pdf_path}. Bitte manuell erstellen!")

    raw_text = advanced_extractor.extract_text(pdf_path)
    assert raw_text is not None
    assert len(raw_text) > 10
    # Hier könntest du prüfen: assert "PDF-Lesung erfolgreich" in raw_text

# Ein Test, der die Speicherung mit dem Extractor kombiniert, ist optional,
# aber die Tests oben prüfen die Parsing-Fähigkeit direkt.
