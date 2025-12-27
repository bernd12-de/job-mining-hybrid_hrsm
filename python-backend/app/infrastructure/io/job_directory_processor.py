# python-backend/infrastructure/io/job_directory_processor.py
import os
import logging
from typing import List
from app.interfaces.interfaces import IJobMiningWorkflowManager
from app.domain.models import AnalysisResultDTO

logger = logging.getLogger(__name__)

class JobDirectoryProcessor:
    """
    Verarbeitet Massendaten aus lokalen Ordnern.
    Ermöglicht die longitudinale Analyse (2011-2024).
    """

    def __init__(self, manager: IJobMiningWorkflowManager, base_path: str = "data/jobs"):
        self.manager = manager
        self.base_path = os.path.abspath(base_path)

    def process_all_jobs(self) -> List[AnalysisResultDTO]:
        """Iteriert über alle Dateien im Verzeichnis und führt die 7-Ebenen-Analyse aus."""
        results: List[AnalysisResultDTO] = []

        if not os.path.isdir(self.base_path):
            logger.error(f"❌ Verzeichnis nicht gefunden: {self.base_path}")
            raise FileNotFoundError(f"Pfad {self.base_path} existiert nicht.")

        # Sortierung hilft, die Analyse chronologisch zu loggen
        files = sorted([f for f in os.listdir(self.base_path) if f.endswith(('.pdf', '.docx', '.txt'))])

        print(f"🚀 Batch-Verarbeitung gestartet: {len(files)} Dateien in {self.base_path}")

        for filename in files:
            full_path = os.path.join(self.base_path, filename)
            print(f"🔍 Analysiere: {filename}...")

            try:
                with open(full_path, 'rb') as f:
                    # Der WorkflowManager übernimmt hier:
                    # 1. Text-Extraktion
                    # 2. Metadaten (Datum, Branche)
                    # 3. Kompetenzen (Ebene 1-5)
                    result = self.manager.run_full_analysis(f, filename)
                    results.append(result)
                    print(f"   ✅ Erfolg: {len(result.competences)} Kompetenzen gefunden.")
            except Exception as e:
                print(f"   ❌ Fehler bei {filename}: {str(e)}")
                logger.error(f"Fehler bei Datei {filename}: {e}")

        print(f"🏁 Batch beendet. {len(results)} Dokumente erfolgreich prozessiert.")
        return results
