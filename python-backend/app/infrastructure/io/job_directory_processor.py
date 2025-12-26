import os
from typing import List

# Domain & Interface Imports
from app.domain.models import AnalysisResultDTO
from app.interfaces.interfaces import IJobMiningWorkflowManager

class JobDirectoryProcessor:
    """
    Verantwortlich für die Batch-Verarbeitung lokaler Dateien.
    Scannt einen Ordner und füttert den WorkflowManager Datei für Datei.
    """

    def __init__(self, manager: IJobMiningWorkflowManager, base_path: str = "data/jobs"):
        self.manager = manager
        self.base_path = base_path

    def process_all_jobs(self) -> List[AnalysisResultDTO]:
        """
        Iteriert über alle validen Dateien im Zielordner und startet die Analyse.
        """
        results: List[AnalysisResultDTO] = []

        # Pfad-Logik: Wir gehen davon aus, dass das Skript vom Projekt-Root (python-backend/) ausgeführt wird.
        # Das ist Standard in Docker und IntelliJ.
        if os.path.isabs(self.base_path):
            full_directory_path = self.base_path
        else:
            full_directory_path = os.path.abspath(self.base_path)

        # Sicherheits-Check
        if not os.path.isdir(full_directory_path):
            print(f"⚠️ Batch-Fehler: Ordner '{full_directory_path}' existiert nicht.")
            return []

        print(f"🚀 Starte Batch-Scan in: {full_directory_path}")

        # Iteration
        for filename in os.listdir(full_directory_path):
            # 1. Filter: Nur unterstützte Dokumente (Ignoriert Bilder/Systemdateien)
            if not filename.lower().endswith(('.pdf', '.docx', '.txt', '.csv')):
                continue

            file_path = os.path.join(full_directory_path, filename)
            print(f"-> Verarbeite: {filename}")

            try:
                # 2. Datei im Binärmodus öffnen (wichtig für PDF/DOCX!)
                with open(file_path, 'rb') as f:
                    # 3. Übergabe an den Manager (Die Brücke)
                    # Der Manager übernimmt ab hier die Verantwortung.
                    result = self.manager.run_full_analysis(file_object=f, filename=filename)

                    if result:
                        results.append(result)
                        print(f"   ✅ Analyse erfolgreich. ({len(result.competences)} Skills gefunden)")
                    else:
                        print("   ⚠️ Analyse lieferte kein Ergebnis.")

            except Exception as e:
                print(f"❌ Fehler bei Batch-Datei '{filename}': {e}")
                # Wir fangen den Fehler hier ab, damit der Batch nicht für alle Dateien abbricht!

        return results
