from fastapi import FastAPI, UploadFile, File, HTTPException, Depends

from advanced_text_extractor import AdvancedTextExtractor
from fuzzy_competence_extractor import FuzzyCompetenceExtractor
from interfaces import IJobMiningWorkflowManager, ITextExtractor, ICompetenceExtractor
from job_mining_workflow_manager import JobMiningWorkflowManager
from repositories.hybrid_competence_repository import HybridCompetenceRepository

app = FastAPI()

# Definiert, wie FastAPI den Workflow Manager erzeugt (Dependency Injection)
def get_workflow_manager() -> IJobMiningWorkflowManager:
    # 1. ESCO-Wissensbasis laden (nur einmal)
    competence_repo = HybridCompetenceRepository()

    # 2. Extraktoren: Die konkreten Implementierungen erstellen
    # Wir übergeben das Repository an den Extractor
    text_extractor: ITextExtractor = AdvancedTextExtractor()
    competence_extractor: ICompetenceExtractor = FuzzyCompetenceExtractor(repository=competence_repo)

    # 3. Den Workflow Manager injizieren (DI-Prinzip)
    return JobMiningWorkflowManager(
        text_extractor=text_extractor,
        competence_extractor=competence_extractor
    )
@app.post("/analyse")
async def analyse_job_ad(
        file: UploadFile = File(...),
        manager: IJobMiningWorkflowManager = Depends(get_workflow_manager)
):
    try:
        # 1. Datei-Stream übergeben
        analysis_result = manager.run_full_analysis(file.file, file.filename)
        return analysis_result

    except Exception as e:
        # Robustes Fehlerhandling (wie in Ihren Best Practices)
        raise HTTPException(status_code=500, detail=f"Analysefehler: {str(e)}")

# ... uvicorn run ...
