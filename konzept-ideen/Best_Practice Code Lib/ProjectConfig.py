"""
ProjectConfig.py
Konfiguration für die REFACTORED Architektur

Basiert auf:
- Clean Architecture Prinzipien
- Separation of Concerns
- CRISP-DM Prozessmodell
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class ProjectConfig:
    """
    Zentrale Projektkonfiguration für REFACTORED Architektur
    
    WICHTIG: Nutzt jetzt Repository Pattern!
    Keine fest-kodierten Kompetenzen mehr!
    """
    
    # ========== DATENQUELLEN ==========
    
    # Lokale Stellenanzeigen
    local_data_dir: Path = Path("data/raw/job_ads")
    recursive_search: bool = True
    
    # Google Drive (optional)
    gdrive_folder_id: Optional[str] = None
    
    # Output
    output_dir: Path = Path("data/processed")
    
    # ========== COMPETENCE EXTRACTION (REFACTORED!) ==========
    
    # Repository Konfiguration (NEU!)
    competence_config: Path = Path("data/competences/config/data_sources.yaml")
    
    # Matching Konfiguration (NEU!)
    matching_config: Dict = field(default_factory=lambda: {
        'use_word_boundaries': True,
        'case_sensitive': False,
        'minimum_confidence': 0.7
    })
    
    # Alte Parameter (DEPRECATED)
    competence_model: str = "Repository"  # Nicht mehr relevant
    competence_csv: Optional[Path] = None  # Nicht mehr verwendet
    
    # ========== ANALYSE ==========
    
    time_series_analysis: bool = True
    branch_comparison: bool = True
    role_comparison: bool = True
    
    # ========== VISUALISIERUNG ==========
    
    create_dashboard: bool = True
    export_formats: List[str] = field(default_factory=lambda: ["csv", "json", "excel"])
    
    # ========== KI-UNTERSTÜTZUNG ==========
    
    use_ai_interpretation: bool = False
    ai_model: str = "gpt-4"
    
    # ========== LOGGING ==========
    
    log_level: str = "INFO"
    log_dir: Path = Path("logs")
    
    def __post_init__(self):
        """Erstellt notwendige Verzeichnisse"""
        
        # Datenverzeichnisse
        self.local_data_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Output Unterverzeichnisse
        (self.output_dir / "analysis").mkdir(exist_ok=True)
        (self.output_dir / "visualizations").mkdir(exist_ok=True)
        (self.output_dir / "reports").mkdir(exist_ok=True)
        
        # Logging
        self.log_dir.mkdir(exist_ok=True)
        
        # Competence Repository Verzeichnisse (NEU!)
        competence_base = Path("data/competences")
        (competence_base / "domains").mkdir(parents=True, exist_ok=True)
        (competence_base / "sources").mkdir(parents=True, exist_ok=True)
        (competence_base / "config").mkdir(parents=True, exist_ok=True)
    
    def validate(self) -> List[str]:
        """
        Validiert Konfiguration
        
        Returns:
            Liste von Fehlern (leer = alles OK)
        """
        errors = []
        
        # Prüfe Competence Config
        if not self.competence_config.exists():
            errors.append(f"Competence Config fehlt: {self.competence_config}")
        
        # Prüfe ob Domain-Dateien existieren
        domain_dir = Path("data/competences/domains")
        if not domain_dir.exists():
            errors.append(f"Domain-Verzeichnis fehlt: {domain_dir}")
        else:
            json_files = list(domain_dir.glob("*.json"))
            if not json_files:
                errors.append(f"Keine Domain-Dateien in: {domain_dir}")
        
        return errors
    
    def to_dict(self) -> Dict:
        """Konvertiert zu Dictionary"""
        return {
            'local_data_dir': str(self.local_data_dir),
            'output_dir': str(self.output_dir),
            'competence_config': str(self.competence_config),
            'matching_config': self.matching_config,
            'time_series_analysis': self.time_series_analysis,
            'branch_comparison': self.branch_comparison,
            'role_comparison': self.role_comparison,
            'create_dashboard': self.create_dashboard,
            'use_ai_interpretation': self.use_ai_interpretation,
            'log_level': self.log_level
        }


def create_default_config() -> ProjectConfig:
    """
    Erstellt Standard-Konfiguration
    
    Returns:
        ProjectConfig mit sinnvollen Defaults
    """
    return ProjectConfig(
        local_data_dir=Path("data/raw/job_ads"),
        output_dir=Path("data/processed"),
        competence_config=Path("data/competences/config/data_sources.yaml"),
        time_series_analysis=True,
        branch_comparison=True,
        role_comparison=True,
        create_dashboard=True,
        use_ai_interpretation=False,
        log_level="INFO"
    )


def create_test_config() -> ProjectConfig:
    """
    Erstellt Test-Konfiguration
    
    Returns:
        ProjectConfig für Tests
    """
    return ProjectConfig(
        local_data_dir=Path("tests/data/job_ads"),
        output_dir=Path("tests/output"),
        competence_config=Path("tests/data/test_config.yaml"),
        time_series_analysis=False,
        branch_comparison=False,
        role_comparison=False,
        create_dashboard=False,
        use_ai_interpretation=False,
        log_level="DEBUG"
    )


def load_config_from_file(config_file: Path) -> ProjectConfig:
    """
    Lädt Konfiguration aus YAML/JSON
    
    Args:
        config_file: Pfad zur Config-Datei
    
    Returns:
        ProjectConfig
    """
    import yaml
    import json
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config nicht gefunden: {config_file}")
    
    # Lade Datei
    with open(config_file, 'r') as f:
        if config_file.suffix == '.yaml' or config_file.suffix == '.yml':
            data = yaml.safe_load(f)
        elif config_file.suffix == '.json':
            data = json.load(f)
        else:
            raise ValueError(f"Unsupported format: {config_file.suffix}")
    
    # Erstelle Config
    return ProjectConfig(**data)


def main():
    """Demo der Konfiguration"""
    
    print("="*80)
    print("📋 PROJECT CONFIGURATION (REFACTORED)")
    print("="*80)
    
    # 1. Default Config
    print("\n1️⃣  Default Config:")
    config = create_default_config()
    print(f"   - Competence Config: {config.competence_config}")
    print(f"   - Matching: Word Boundaries={config.matching_config['use_word_boundaries']}")
    print(f"   - Analysis: Time Series={config.time_series_analysis}")
    
    # 2. Validierung
    print("\n2️⃣  Validierung:")
    errors = config.validate()
    if errors:
        print("   ❌ Fehler gefunden:")
        for err in errors:
            print(f"      - {err}")
    else:
        print("   ✅ Konfiguration valide")
    
    # 3. Export
    print("\n3️⃣  Export:")
    config_dict = config.to_dict()
    print("   Config als Dict:")
    for key, value in config_dict.items():
        print(f"      - {key}: {value}")
    
    # 4. Test Config
    print("\n4️⃣  Test Config:")
    test_config = create_test_config()
    print(f"   - Output Dir: {test_config.output_dir}")
    print(f"   - Log Level: {test_config.log_level}")
    
    print("\n" + "="*80)
    print("✅ CONFIG DEMO ABGESCHLOSSEN")
    print("="*80)


if __name__ == "__main__":
    main()
