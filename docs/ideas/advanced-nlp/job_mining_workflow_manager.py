# job_mining_workflow_manager.py

import hashlib
from typing import BinaryIO, Optional

from metadata_extractor import MetadataExtractor
from normalize import parse_date
from domain.services.organization_service import OrganizationService
from domain.services.role_service import RoleService

from interfaces import IJobMiningWorkflowManager, ITextExtractor, ICompetenceExtractor
from models import AnalysisResultDTO
from pathlib import Path
from typing import List


class JobMiningWorkflowManager(IJobMiningWorkflowManager):
    """Orchestrierung der Analyse-Pipeline (CRISP-DM Zyklus)."""

    def __init__(self,
                 text_extractor: ITextExtractor,
                 competence_extractor: ICompetenceExtractor,
                 organization_service: OrganizationService,
                 role_service: RoleService
                 ):
        self.text_extractor = text_extractor
        self.competence_extractor = competence_extractor
        self.organization_service = organization_service
        self.role_service = role_service

    def _run_analysis_from_text(self, raw_text: str, source_name: str) -> AnalysisResultDTO:
        # 1. Hashing für Idempotenz
        raw_text_hash = hashlib.sha256(raw_text.encode('utf-8')).hexdigest()

        # 2. Metadaten-Extraktion (isoliert Aufgaben und Profil)
        self.meta_extractor = MetadataExtractor()
        metadata = self.meta_extractor.extract_all(raw_text, filename=source_name)

        # --- KERN-FIX: FALLBACK-LOGIK FÜR DEN ANALYSE-TEXT ---
        tasks_clean = metadata.get('tasks_clean', '')
        requirements_clean = metadata.get('requirements_clean', '')

        # Versuche, nur relevante Sektionen zu nutzen
        clean_text_for_esco = (tasks_clean + " " + requirements_clean).strip()

        # Wenn die Segmentierung fehlschlug (Text zu kurz), nutze den gesamten Rohtext
        if len(clean_text_for_esco) < 50:
            print(f"DEBUG: Segmentierung fehlgeschlagen ({len(clean_text_for_esco)} Zeichen). Nutze Fallback: Rohtext.")
            clean_text_for_esco = raw_text
        else:
            print(f"DEBUG: Nutze segmentierten Text ({len(clean_text_for_esco)} Zeichen) für Skill-Extraktion.")

        # 3. KOMPETENZ-EXTRAKTION mit dem validierten Text
        competences = self.competence_extractor.extract_competences(clean_text_for_esco)

        # 4. Branchen- und Rollen-Klassifizierung (DB-gestützt)
        industry = self.organization_service.classify_industry(raw_text)
        job_role = self.role_service.classify_role(
            job_text=raw_text,
            job_title=metadata.get('job_title', source_name)
        )

        # Datum-Parsing
        iso_date, _, _ = parse_date(raw_text)
        posting_date = iso_date or "2024-12-01"

        # KERN-FIX: Das Flag aus dem MetadataExtractor übernehmen
        is_segmented = metadata.get('is_segmented', False)

        # 5. Zusammenbau des Resultats
        return AnalysisResultDTO(
            title=metadata.get('job_title') or source_name,
            job_role=job_role,
            region=metadata.get('location') or "Unbekannt",
            industry=industry,
            posting_date=posting_date,
            raw_text_hash=raw_text_hash,
            raw_text=raw_text,
            is_segmented=is_segmented,
            competences=competences
        )

    def run_full_analysis(self, file_stream: BinaryIO, filename: str) -> AnalysisResultDTO:
        """Verarbeitet PDF/DOCX Dateien."""
        raw_text = self.text_extractor.extract_text(file_stream, filename)
        cleaned_raw_text = raw_text.replace('\x00', '')
        return self._run_analysis_from_text(cleaned_raw_text, filename)

    def run_analysis_from_scraped_text(self, cleaned_text: str, source_name: str) -> AnalysisResultDTO:
        """Verarbeitet Text von URLs."""
        return self._run_analysis_from_text(cleaned_text, source_name)

    def process_local_directory(self) -> List[AnalysisResultDTO]:
        """
        Ebene: Batch-Verarbeitung.
        Scannt den Ordner 'data/job_ads' und analysiert jede .txt Datei.
        """
        results = []
        # Pfad zu deinem lokalen Test-Ordner
        job_dir = Path("data/job_ads")

        if not job_dir.exists():
            print(f"⚠️ Batch-Fehler: Verzeichnis {job_dir.absolute()} existiert nicht.")
            return []

        # Wir suchen alle Textdateien
        files = list(job_dir.glob("*.txt"))
        print(f"🚀 Starte Batch-Analyse für {len(files)} Dateien...")

        for file_path in files:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Nutzt deine bereits vorhandene Logik für die Analyse
                    analysis = self._run_analysis_from_text(content, source_name=file_path.name)
                    results.append(analysis)
            except Exception as e:
                print(f"❌ Fehler bei Datei {file_path.name}: {e}")

        return results
