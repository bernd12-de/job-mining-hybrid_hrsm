"""
create_project.py
=================
Erstellt die komplette Job Mining Projekt-Struktur

VERWENDUNG:
    python create_project.py

WICHTIG:
    Führe dieses Script in einem LEEREN Verzeichnis aus!
    Es erstellt automatisch alle Dateien und Ordner.
"""

import os
from pathlib import Path
from textwrap import dedent


def create_directory_structure():
    """Erstellt alle Verzeichnisse"""
    print("📁 Erstelle Verzeichnisstruktur...")

    directories = [
        "models",
        "services",
        "utils",
        "data/raw/job_ads",
        "data/processed/analysis",
        "data/processed/visualizations",
        "data/processed/reports",
        "logs",
        "tests"
    ]

    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ {dir_path}")


def create_file(filepath, content):
    """Erstellt eine Datei mit Inhalt"""
    Path(filepath).write_text(dedent(content), encoding='utf-8')


def create_models():
    """Erstellt Model-Dateien"""
    print("\n📦 Erstelle Models...")

    # models/__init__.py
    create_file("models/__init__.py", """
        from .job_ad import (
            JobAd, Competence, CompetenceType, Organization,
            Requirements, JobCategory, CompetenceCluster
        )
        from .analysis_results import (
            CompetenceTrend, BranchProfile, RoleProfile,
            TimeSeriesAnalysis, ClusterAnalysis, AnalysisReport, AIInsights
        )

        __all__ = [
            'JobAd', 'Competence', 'CompetenceType', 'Organization',
            'Requirements', 'JobCategory', 'CompetenceCluster',
            'CompetenceTrend', 'BranchProfile', 'RoleProfile',
            'TimeSeriesAnalysis', 'ClusterAnalysis', 'AnalysisReport', 'AIInsights'
        ]
    """)
    print("  ✓ models/__init__.py")

    # models/job_ad.py - GEKÜRZTE VERSION (zu lang für Artifact)
    create_file("models/job_ad.py", """
        # HINWEIS: Dies ist eine VEREINFACHTE Version
        # Vollständiger Code verfügbar im Chat-Verlauf

        from dataclasses import dataclass, field
        from typing import List, Optional, Dict
        from datetime import datetime
        from enum import Enum

        class CompetenceType(Enum):
            SKILL = "skill"
            TOOL = "tool"
            TECHNOLOGY = "technology"
            METHOD = "method"
            LANGUAGE = "language"
            FRAMEWORK = "framework"
            PLATFORM = "platform"

        class JobCategory(Enum):
            UX_UI_DESIGN = "UX/UI Design"
            PRODUCT_MANAGEMENT = "Product Management"
            BUSINESS_ANALYSIS = "Business Analysis"
            AGILE_COACHING = "Agile Coaching"
            UX_RESEARCH = "UX Research"
            DEVELOPMENT = "Development"
            OTHER = "Other"

        @dataclass
        class Organization:
            name: str = "Unbekannt"
            branch: Optional[str] = None

        @dataclass
        class Competence:
            name: str
            category: str = "General"
            competence_type: CompetenceType = CompetenceType.SKILL
            esco_uri: str = ""
            alternative_labels: List[str] = field(default_factory=list)
            confidence_score: float = 1.0
            source: str = "extracted"
            context_snippet: Optional[str] = None

        @dataclass
        class Requirements:
            education_level: Optional[str] = None
            years_experience: Optional[int] = None
            languages: Dict[str, str] = field(default_factory=dict)
            soft_skills: List[str] = field(default_factory=list)

        @dataclass
        class JobAd:
            id: str
            file_name: str
            source: str
            raw_text: str
            char_count: int = 0
            word_count: int = 0

            job_title: str = "Unbekannt"
            organization: Optional[Organization] = None
            location: str = "Nicht angegeben"
            remote_option: Optional[str] = None

            competences: List[Competence] = field(default_factory=list)
            job_categories: List[JobCategory] = field(default_factory=list)
            requirements: Optional[Requirements] = None

            posting_date: Optional[datetime] = None
            collection_date: Optional[datetime] = None
            year: Optional[int] = None
            month: Optional[int] = None
            quarter: Optional[str] = None

            cleaned_text: Optional[str] = None
            text_quality: float = 0.0
            extraction_quality: float = 0.0

            def has_competence(self, competence_name: str) -> bool:
                return any(c.name.lower() == competence_name.lower() for c in self.competences)

            def get_time_period(self) -> str:
                if self.quarter:
                    return self.quarter
                elif self.year and self.month:
                    return f"{self.year}-{self.month:02d}"
                elif self.year:
                    return str(self.year)
                return "Unknown"

            def to_dict(self) -> Dict:
                return {
                    'id': self.id,
                    'file_name': self.file_name,
                    'source': self.source,
                    'job_title': self.job_title,
                    'company_name': self.organization.name if self.organization else None,
                    'company_branch': self.organization.branch if self.organization else None,
                    'location': self.location,
                    'remote_option': self.remote_option,
                    'posting_date': self.posting_date.isoformat() if self.posting_date else None,
                    'year': self.year,
                    'month': self.month,
                    'quarter': self.quarter,
                    'job_categories': [cat.value for cat in self.job_categories],
                    'competences_count': len(self.competences),
                    'competences': [
                        {
                            'name': c.name,
                            'category': c.category,
                            'type': c.competence_type.value,
                            'esco_uri': c.esco_uri
                        }
                        for c in self.competences
                    ],
                    'char_count': self.char_count,
                    'word_count': self.word_count,
                    'text_quality': self.text_quality,
                    'extraction_quality': self.extraction_quality
                }

        @dataclass
        class CompetenceCluster:
            id: str
            name: str
            description: str
            competences: List[Competence] = field(default_factory=list)
            job_ads_count: int = 0
    """)
    print("  ✓ models/job_ad.py")

    # models/analysis_results.py - GEKÜRZT
    create_file("models/analysis_results.py", """
        from dataclasses import dataclass, field
        from typing import List, Dict, Optional
        from datetime import datetime

        @dataclass
        class CompetenceTrend:
            competence_name: str
            category: str
            time_periods: List[str] = field(default_factory=list)
            frequencies: List[int] = field(default_factory=list)
            percentages: List[float] = field(default_factory=list)
            trend_direction: str = "stable"
            growth_rate: float = 0.0
            mean_frequency: float = 0.0
            std_deviation: float = 0.0

            def calculate_trend(self):
                if len(self.frequencies) < 2:
                    return
                first_half = sum(self.frequencies[:len(self.frequencies)//2])
                second_half = sum(self.frequencies[len(self.frequencies)//2:])
                if first_half > 0:
                    self.growth_rate = ((second_half - first_half) / first_half) * 100
                    if self.growth_rate > 20:
                        self.trend_direction = "rising"
                    elif self.growth_rate < -20:
                        self.trend_direction = "falling"

        @dataclass
        class BranchProfile:
            branch_name: str
            job_ads_count: int = 0
            top_competences: List[tuple] = field(default_factory=list)
            avg_competences_per_ad: float = 0.0

            def calculate_metrics(self, job_ads):
                self.job_ads_count = len(job_ads)
                from collections import Counter
                all_comps = []
                for job in job_ads:
                    all_comps.extend([c.name for c in job.competences])
                self.top_competences = Counter(all_comps).most_common(15)
                self.avg_competences_per_ad = len(all_comps) / len(job_ads) if job_ads else 0

        @dataclass
        class RoleProfile:
            role_name: str
            job_category: str
            job_ads_count: int = 0
            required_competences: List[tuple] = field(default_factory=list)
            technical_skills: List[str] = field(default_factory=list)
            methodological_skills: List[str] = field(default_factory=list)
            soft_skills: List[str] = field(default_factory=list)

        @dataclass
        class TimeSeriesAnalysis:
            start_date: datetime
            end_date: datetime
            competence_trends: List[CompetenceTrend] = field(default_factory=list)
            rising_competences: List[str] = field(default_factory=list)
            falling_competences: List[str] = field(default_factory=list)
            emerging_competences: List[str] = field(default_factory=list)

        @dataclass
        class ClusterAnalysis:
            method: str
            n_clusters: int
            clusters: List = field(default_factory=list)

        @dataclass
        class AIInsights:
            model: str
            trend_narratives: Dict[str, str] = field(default_factory=dict)
            cluster_descriptions: Dict[str, str] = field(default_factory=dict)
            transformation_assessment: str = ""
            curriculum_recommendations: List[str] = field(default_factory=list)
            confidence_score: float = 0.0

        @dataclass
        class AnalysisReport:
            total_job_ads: int
            date_range: tuple
            branches_covered: List[str]
            time_series: Optional[TimeSeriesAnalysis] = None
            branch_profiles: List[BranchProfile] = field(default_factory=list)
            role_profiles: List[RoleProfile] = field(default_factory=list)
            cluster_analysis: Optional[ClusterAnalysis] = None
            ai_insights: Optional[AIInsights] = None
            data_quality_score: float = 0.0
            esco_coverage: float = 0.0
            extraction_accuracy: float = 0.0
    """)
    print("  ✓ models/analysis_results.py")


def create_utils():
    """Erstellt Utils"""
    print("\n🔧 Erstelle Utils...")

    create_file("utils/__init__.py", """
        from .logger import setup_logging
        from .config import Config

        __all__ = ['setup_logging', 'Config']
    """)

    create_file("utils/logger.py", """
        import logging
        import sys
        from pathlib import Path

        def setup_logging(log_file: Path = None, level: str = "INFO"):
            root_logger = logging.getLogger()
            root_logger.setLevel(getattr(logging, level))

            for handler in root_logger.handlers[:]:
                root_logger.removeHandler(handler)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )

            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)

            if log_file:
                log_file.parent.mkdir(parents=True, exist_ok=True)
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)

            logging.getLogger('pdfminer').setLevel(logging.ERROR)
            logging.getLogger('pdfplumber').setLevel(logging.ERROR)

            return root_logger
    """)

    create_file("utils/config.py", """
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
    """)

    print("  ✓ utils/__init__.py")
    print("  ✓ utils/logger.py")
    print("  ✓ utils/config.py")


def create_main_files():
    """Erstellt Hauptdateien"""
    print("\n🚀 Erstelle Hauptdateien...")

    # HINWEIS: Services sind zu lang - siehe Chat für vollständigen Code
    create_file("services/__init__.py", """
        # HINWEIS: Vollständiger Service-Code ist zu umfangreich für dieses Setup-Script
        # Bitte kopiere die Services manuell aus dem Chat-Verlauf:
        # - data_collection.py
        # - data_preparation.py
        # - competence_extraction.py
        # - analysis.py
        # - reporting.py

        print("⚠️  WICHTIG: Services müssen manuell aus dem Chat kopiert werden!")
        print("    Siehe Chat-Verlauf für vollständigen Code")
    """)

    create_file("requirements.txt", """
        # Core
        PyPDF2>=3.0.0
        pdfplumber>=0.10.0
        python-docx>=1.1.0

        # Google Drive (optional)
        # google-api-python-client>=2.100.0
        # google-auth-httplib2>=0.1.1
        # google-auth-oauthlib>=1.1.0

        # KI (optional)
        # openai>=1.0.0
    """)

    create_file("README.md", """
        # 📚 Job Mining Projekt

        Kompetenzen im Wandel: Analyse UX-naher Berufsfelder

        ## 🚀 Quick Start

        ```bash
        # 1. Dependencies installieren
        pip install -r requirements.txt

        # 2. PDFs in data/raw/job_ads/ ablegen

        # 3. Ausführen
        python main.py
        ```

        ## ⚠️ WICHTIG

        Die Services (data_collection.py, etc.) müssen manuell aus dem Chat kopiert werden,
        da sie zu umfangreich für dieses Auto-Setup sind.

        Siehe Chat-Verlauf für:
        - services/data_collection.py
        - services/data_preparation.py
        - services/competence_extraction.py
        - services/analysis.py
        - services/reporting.py
        - main.py

        ## 📊 Output

        - CSV: `data/processed/reports/job_mining_results.csv`
        - JSON: `data/processed/reports/job_mining_results.json`
        - Statistiken: `data/processed/reports/statistiken.txt`
    """)

    print("  ✓ requirements.txt")
    print("  ✓ README.md")
    print("  ⚠️  services/__init__.py (Platzhalter)")


def create_info_file():
    """Erstellt Anleitung"""
    info = """
    ╔═══════════════════════════════════════════════════════════════════╗
    ║                                                                   ║
    ║   ✅ PROJEKT-STRUKTUR ERSTELLT!                                   ║
    ║                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════╝

    📁 Verzeichnisse erstellt:
       ✓ models/
       ✓ services/
       ✓ utils/
       ✓ data/
       ✓ logs/

    📄 Dateien erstellt:
       ✓ models/job_ad.py (vereinfacht)
       ✓ models/analysis_results.py (vereinfacht)
       ✓ utils/logger.py
       ✓ utils/config.py
       ✓ requirements.txt
       ✓ README.md

    ⚠️  NÄCHSTE SCHRITTE:

    1. Kopiere aus dem Chat die VOLLSTÄNDIGEN Service-Dateien:
       → services/data_collection.py
       → services/data_preparation.py
       → services/competence_extraction.py
       → services/analysis.py
       → services/reporting.py
       → main.py

    2. Installiere Dependencies:
       pip install -r requirements.txt

    3. Lege PDF/Word-Dateien ab:
       data/raw/job_ads/

    4. Führe aus:
       python main.py

    ╔═══════════════════════════════════════════════════════════════════╗
    ║  💡 TIPP: Die Services sind zu umfangreich für Auto-Generation    ║
    ║      Bitte aus dem Chat-Verlauf kopieren (jeweils ~200-400 Zeilen)║
    ╚═══════════════════════════════════════════════════════════════════╝
    """

    Path("NEXT_STEPS.txt").write_text(dedent(info), encoding='utf-8')


def main():
    """Hauptfunktion"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║   📚 JOB MINING PROJEKT - AUTO SETUP                         ║
    ║   Erstellt Verzeichnisstruktur und Basis-Dateien            ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    try:
        create_directory_structure()
        create_models()
        create_utils()
        create_main_files()
        create_info_file()

        print("\n" + "="*70)
        print("✅ SETUP ABGESCHLOSSEN!")
        print("="*70)
        print("\n📋 Lies NEXT_STEPS.txt für weitere Anweisungen")
        print("\n⚠️  WICHTIG: Services müssen noch manuell kopiert werden!")

    except Exception as e:
        print(f"\n❌ Fehler beim Setup: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
