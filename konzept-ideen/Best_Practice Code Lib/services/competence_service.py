# core/services/competence_service.py

from typing import Dict, Any, Optional
from core.entities.job_posting import JobPosting, Competence
from infrastructure.storage.job_repository import JobRepository
from core.text_extraction_interface import TextExtractorInterface
from core.competence_extraction_interface import CompetenceExtractorInterface # Das Interface
import uuid

class CompetenceService:
    """
    Der Application Service, der die Geschäftslogik orchestriert.
    Er empfängt alle Infrastruktur-Abhängigkeiten über den Konstruktor (DI).
    """

    def __init__(self,
                 text_extractor: TextExtractorInterface,
                 job_repository: JobRepository,
                 competence_extractor: CompetenceExtractorInterface): # NEU: Dritte Abhängigkeit

        self.text_extractor = text_extractor
        self.job_repository = job_repository
        self.competence_extractor = competence_extractor

    def process_job_posting(self, raw_data: Dict[str, Any]) -> JobPosting:
        """
        Verarbeitet rohe Jobdaten, extrahiert Kompetenzen und speichert den Job.
        """

        source_id: str = raw_data.get("source_id", str(uuid.uuid4()))
        source_path: Optional[str] = raw_data.get("source_path")

        # 1. Text-Handling (Laden des Textes aus Datei oder Body)
        raw_text: str = ""

        if source_path:
            # Nutzt den AdvancedTextExtractor (Infrastructure)
            extracted_text = self.text_extractor.extract_text(source_path)
            if extracted_text is None:
                raise ValueError(f"Datei nicht lesbar oder nicht gefunden unter Pfad: {source_path}")
            raw_text = extracted_text
        else:
            # Fallback: Nimmt den Text direkt aus dem Request-Body
            raw_text = raw_data.get("raw_text", "Kein Text verfügbar.")

        # 2. REALE EXTRAKTION (Ersetzt die Simulation!)
        # Ruft den injizierten SpaCy-Extractor auf
        competences = self.competence_extractor.extract_competences(raw_text)

        # 3. Erstellung der Core Entity
        job_entity = JobPosting(
            source_id=source_id,
            source_path=source_path or "N/A",
            title=raw_data.get("title", "Unbekannt"),
            company=raw_data.get("company", "Unbekannt"),
            region=raw_data.get("region"),
            year=raw_data.get("year"),
            branch=raw_data.get("branch"),
            raw_text=raw_text,
            competences=competences # Enthält jetzt die NLP-Ergebnisse
        )

        # 4. DELEGIERUNG ZUR PERSISTENZ
        self.job_repository.save_job_posting(job_entity)
        return job_entity
