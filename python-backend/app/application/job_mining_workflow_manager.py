import logging,  hashlib
from platform import system
from typing import BinaryIO, List
from pathlib import Path
from app.application.factories.analysis_result_factory import AnalysisResultFactory
from app.core.normalize import parse_date
from app.domain.models import AnalysisResultDTO, CompetenceDTO

logger = logging.getLogger(__name__)

class JobMiningWorkflowManager:
    """
    Zentraler Orchestrator (Pipeline-Manager).
    Koordiniert den Fluss: Text -> Metadaten -> NLP -> Factory.
    """

    def __init__(self, text_extractor, competence_extractor, organization_service, role_service, metadata_extractor):
        self.text_extractor = text_extractor
        self.competence_extractor = competence_extractor
        self.organization_service = organization_service
        self.role_service = role_service
        self.metadata_extractor = metadata_extractor

    async def run_full_analysis(self, file_object: BinaryIO, filename: str):
        """Einstiegspunkt für PDF/DOCX Uploads."""
        text = self.text_extractor.extract_text(file_object, filename)
        if not text:
            raise ValueError(f"Kein Text aus {filename} extrahierbar.")
        return self._execute_pipeline(text, source_name=filename)

    def run_analysis_from_scraped_text(self, text: str, source_url: str):
        """Einstiegspunkt für Scraper/Text."""
        return self._execute_pipeline(text, source_name=source_url)

    def _execute_pipeline(self, text: str, source_name: str):
        """Die zentrale CRISP-DM Pipeline-Logik."""
        print("_execute_pipeline", text , "+",source_name)

        # 1. ID-CHECK: Erzeugung des SHA-256 Hashes für Ebene 7 (Idempotenz)
        # Dieser Hash wird in der DB als UNIQUE gefordert.
        raw_text_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()

        # A. Ebene 6: Metadaten & Kontext
        meta = self.metadata_extractor.extract_all(text, filename=source_name)

        # NORMALISIERUNG: Datum über parse_date in ISO-Format (YYYY-MM-DD) bringen
        # Wichtig für den SQL-Typ DATE und Kotlin LocalDate
        iso_date, _, _ = parse_date(text)
        posting_date = str(iso_date) if iso_date else "2024-12-01"

        industry = self.organization_service.detect_industry(text)
        role = self.role_service.classify_role(text,meta.get('job_title') or source_name)

        # B. Ebene 1-5: NLP Extraktion
        competences = self.competence_extractor.extract_competences(text=meta['processing_text'], role=role)
        print("raw_found competence in _execute pipe", competences)

        # C. Ebene 7: SSoT Transformation via Factory
        return AnalysisResultFactory.create_result(
            job_id=None, #für DB
            title=meta.get('job_title') or source_name,
            job_role=role,
            region=meta.get('region', "Unbekannt"),
            industry=industry,
            posting_date=meta.get('posting_date'),
            raw_text_hash=raw_text_hash,
            raw_text=text,
            is_segmented=meta.get('is_segmented', False),
            competences=competences
        )

    def _run_analysis_from_text(self, raw_text: str, source_name: str) -> AnalysisResultDTO:
        # 1. Idempotenz-Hash (Ebene 7)
        print("_run_analysis_from_text mit raw text", raw_text , "+",source_name)

        raw_text_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()

        # 2. Metadaten & Datum (Ebene 6)
        metadata = self.metadata_extractor.extract_all(raw_text, filename=source_name)
        iso_date, _, _ = parse_date(raw_text)
        posting_date = iso_date or "2024-12-01"



        # 1. Metadaten (Nur Segmentierung & Titel)
        meta = self.metadata_extractor.extract_all(raw_text, filename=source_name)

        # 2. Branche & Rolle (Gewinner: DB-gestützte Services)
        industry = self.organization_service.classify_industry(raw_text)
        role = self.role_service.classify_role(raw_text, meta['job_title'])

        # 3. Kompetenzen (Orchestrierung)
        skills = self.competence_extractor.extract_competences(
            text=meta['processing_text'],
            role=role
        )

        return AnalysisResultDTO(
            job_id=None, # DB vergibt ID (BigInt)
            title=meta['job_title'],
            job_role=role,
            region=meta['region'],
            industry=industry,
            posting_date=meta['posting_date'],
            raw_text=raw_text,
            raw_text_hash= raw_text_hash,
            is_segmented=meta['is_segmented'],
            competences=skills
        )
    def process_local_directory(self):
        """Batch-Verarbeitung für lokale Tests."""
        results = []
        job_dir = Path("data/jobs")
        for file_path in job_dir.glob("*.*"):
            if file_path.suffix.lower() in ['.pdf', '.docx', '.txt']:
                try:
                    with open(file_path, "rb") as f:
                        results.append(self.run_full_analysis(f, file_path.name))
                except Exception as e:
                    logger.error(f"Fehler bei Batch-Datei {file_path.name}: {e}")
        return results


    # 🚨 FIX: Die fehlende Methode für die Extraktoren
    def create_competence_dto(self, **kwargs) -> CompetenceDTO:
        """Zentrale Factory zur Erzeugung valider Kompetenz-Objekte."""
        return CompetenceDTO(**kwargs)
