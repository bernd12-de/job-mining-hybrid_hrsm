import os
from interfaces import IJobMiningWorkflowManager
from typing import List
from models import AnalysisResultDTO

class JobDirectoryProcessor:
    """Verarbeitet alle Job-Dateien in einem festgelegten lokalen Ordner."""

    def __init__(self, manager: IJobMiningWorkflowManager, base_path: str = "data/jobs"):
        self.manager = manager
        # Basis-Pfad, der von Docker aus gesehen wird
        self.base_path = base_path

    def process_all_jobs(self) -> List[AnalysisResultDTO]:
        """Iteriert über alle Dateien und führt die Analyse aus."""
        results: List[AnalysisResultDTO] = []
        full_directory_path = os.path.join(os.getcwd(), self.base_path)

        if not os.path.isdir(full_directory_path):
            raise FileNotFoundError(f"Das Verzeichnis {full_directory_path} existiert nicht.")

        for filename in os.listdir(full_directory_path):
            if filename.endswith(('.pdf', '.docx')):
                full_path = os.path.join(full_directory_path, filename)
                print(f"-> Verarbeite Datei: {filename}")

                try:
                    with open(full_path, 'rb') as f:
                        # Übergibt den Dateistream an den bestehenden Workflow Manager
                        result = self.manager.run_full_analysis(f, filename)
                        results.append(result)
                except Exception as e:
                    print(f"❌ Fehler bei der Verarbeitung von {filename}: {e}")

        return results
