
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

@dataclass
class Config:
    local_data_dir: Path = Path("data/raw/job_ads")
    gdrive_folder_id: Optional[str] = None
    gdrive_credentials: Path = Path("credentials.json")
    gdrive_token: Path = Path("token.json")
    output_dir: Path = Path("data/processed")
    competence_config: Path = Path("data/competences/config/data_sources.yaml")
    competence_model: str = "ESCO"
    competence_csv: Optional[Path] = None
    recursive_search: bool = True
    min_text_length: int = 100
    time_series_analysis: bool = True
    branch_comparison: bool = True
    role_comparison: bool = True
    clustering_enabled: bool = True
    create_dashboard: bool = False
    export_formats: List[str] = field(default_factory=lambda: ["csv", "json"])
    use_ai_interpretation: bool = False
    ai_model: str = "gpt-4"
    openai_api_key: Optional[str] = None
    log_level: str = "INFO"
    log_dir: Path = Path("logs")

    def __post_init__(self):
        self.local_data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "analysis").mkdir(exist_ok=True)
        (self.output_dir / "visualizations").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

    def validate(self) -> List[str]:
        issues = []
        if not self.local_data_dir.exists():
            issues.append(f"Datenverzeichnis nicht gefunden: {self.local_data_dir}")
        if self.gdrive_folder_id and not self.gdrive_credentials.exists():
            issues.append(f"Google Drive credentials.json nicht gefunden")
        if self.use_ai_interpretation and not self.openai_api_key:
            issues.append("OpenAI API Key fehlt für KI-Features")
        return issues
