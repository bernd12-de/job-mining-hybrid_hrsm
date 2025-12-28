"""
Job Mining Workflow Manager v2.0
=================================

Automatisierter Workflow für:
1. Manuelle Upload neuer Stellenanzeigen (PDF/DOCX/Google Docs)
2. Automatische Verarbeitung
3. Auswertung & Report-Generierung
4. Trendanalyse über Zeit

Autor: Job Mining Project
Datum: 2025-11-01
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
import shutil

from job_mining_pipeline_v2 import JobMiningPipeline, JobAnalysisResult

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class JobMiningWorkflowManager:
    """
    Workflow Manager für kontinuierliche Stellenanzeigen-Analyse
    
    Workflow:
    1. Neue Stellenanzeigen in 'incoming/' ablegen
    2. Automatische Verarbeitung
    3. Ergebnisse in 'results/' speichern
    4. Archivierung in 'archive/'
    5. Report-Generierung
    6. Trend-Analyse über Zeit
    """
    
    def __init__(self, base_dir: str = "/home/claude/job_mining_workflow"):
        """
        Initialize Workflow Manager
        
        Args:
            base_dir: Basis-Verzeichnis für Workflow
        """
        self.base_dir = Path(base_dir)
        self.setup_directories()
        
        # Initialize Pipeline
        self.pipeline = JobMiningPipeline()
        
        logger.info(f"Workflow Manager initialized at {self.base_dir}")
    
    def setup_directories(self):
        """Erstellt Verzeichnisstruktur"""
        self.dirs = {
            'incoming': self.base_dir / 'incoming',      # Neue Stellenanzeigen hier ablegen
            'processing': self.base_dir / 'processing',  # Temporär während Verarbeitung
            'archive': self.base_dir / 'archive',        # Archiv nach Verarbeitung
            'results': self.base_dir / 'results',        # JSON/CSV Ergebnisse
            'reports': self.base_dir / 'reports',        # HTML/Text Reports
            'logs': self.base_dir / 'logs',              # Log-Dateien
        }
        
        for name, path in self.dirs.items():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"  ✓ {name}: {path}")
    
    def add_job_ad(self, file_path: str, metadata: Optional[Dict] = None) -> str:
        """
        Fügt eine neue Stellenanzeige hinzu (manueller Upload)
        
        Args:
            file_path: Pfad zur Stellenanzeige (PDF/DOCX)
            metadata: Optional - zusätzliche Metadaten
                {
                    'company': 'Firma GmbH',
                    'position': 'UX Designer',
                    'date_posted': '2025-11-01',
                    'source': 'LinkedIn',
                    'url': 'https://...'
                }
        
        Returns:
            Pfad zur kopierten Datei im incoming-Verzeichnis
        """
        source = Path(file_path)
        
        if not source.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Prüfe Format
        if source.suffix.lower() not in ['.pdf', '.docx', '.doc']:
            raise ValueError(f"Unsupported format: {source.suffix}")
        
        # Timestamp-basierter Dateiname
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{timestamp}_{source.name}"
        destination = self.dirs['incoming'] / new_filename
        
        # Kopiere Datei
        shutil.copy2(source, destination)
        logger.info(f"Added job ad: {new_filename}")
        
        # Speichere Metadata (falls vorhanden)
        if metadata:
            metadata_file = destination.with_suffix('.meta.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            logger.info(f"  ✓ Metadata saved: {metadata_file.name}")
        
        return str(destination)
    
    def process_incoming(self) -> List[JobAnalysisResult]:
        """
        Verarbeitet alle neuen Stellenanzeigen im incoming-Verzeichnis
        
        Returns:
            Liste von JobAnalysisResult
        """
        incoming_files = list(self.dirs['incoming'].glob("*"))
        incoming_files = [
            f for f in incoming_files 
            if f.suffix.lower() in ['.pdf', '.docx', '.doc']
        ]
        
        if not incoming_files:
            logger.info("No new job ads to process")
            return []
        
        logger.info(f"\n{'='*70}")
        logger.info(f"PROCESSING {len(incoming_files)} NEW JOB ADS")
        logger.info(f"{'='*70}\n")
        
        results = []
        
        for file_path in incoming_files:
            try:
                # Move to processing
                processing_path = self.dirs['processing'] / file_path.name
                shutil.move(str(file_path), str(processing_path))
                
                # Load metadata (if exists)
                metadata_file = file_path.with_suffix('.meta.json')
                custom_metadata = {}
                if metadata_file.exists():
                    with open(metadata_file, 'r', encoding='utf-8') as f:
                        custom_metadata = json.load(f)
                    shutil.move(str(metadata_file), 
                              str(self.dirs['processing'] / metadata_file.name))
                
                # Analyze
                logger.info(f"Processing: {file_path.name}")
                result = self.pipeline.analyze_file(str(processing_path))
                
                # Add custom metadata to result
                if custom_metadata:
                    result.metadata = custom_metadata
                
                results.append(result)
                logger.info(f"  ✓ Found {result.competence_count} skills\n")
                
                # Move to archive
                timestamp = datetime.now().strftime("%Y-%m")
                archive_subdir = self.dirs['archive'] / timestamp
                archive_subdir.mkdir(exist_ok=True)
                
                shutil.move(str(processing_path), 
                          str(archive_subdir / processing_path.name))
                
                # Move metadata too
                meta_processing = self.dirs['processing'] / metadata_file.name
                if meta_processing.exists():
                    shutil.move(str(meta_processing),
                              str(archive_subdir / metadata_file.name))
                
            except Exception as e:
                logger.error(f"✗ Error processing {file_path.name}: {e}")
                # Move failed file back to incoming
                if processing_path.exists():
                    shutil.move(str(processing_path), str(file_path))
        
        # Summary
        logger.info(f"\n{'='*70}")
        logger.info(f"PROCESSING COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Successfully processed: {len(results)}/{len(incoming_files)}")
        logger.info(f"Total competences found: {sum(r.competence_count for r in results)}")
        
        return results
    
    def save_results(self, results: List[JobAnalysisResult]):
        """
        Speichert Ergebnisse in verschiedenen Formaten
        
        Args:
            results: Liste von JobAnalysisResult
        """
        if not results:
            logger.warning("No results to save")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON (detailed)
        json_path = self.dirs['results'] / f"results_{timestamp}.json"
        self.pipeline.export_to_json(results, str(json_path))
        
        # CSV (summary)
        csv_path = self.dirs['results'] / f"results_summary_{timestamp}.csv"
        self.pipeline.export_to_csv(results, str(csv_path))
        
        # CSV (detailed)
        csv_detailed_path = self.dirs['results'] / f"results_detailed_{timestamp}.csv"
        self.pipeline.export_detailed_csv(results, str(csv_detailed_path))
        
        logger.info(f"\n{'='*70}")
        logger.info(f"RESULTS SAVED")
        logger.info(f"{'='*70}")
        logger.info(f"JSON:          {json_path.name}")
        logger.info(f"CSV (summary): {csv_path.name}")
        logger.info(f"CSV (detail):  {csv_detailed_path.name}")
    
    def generate_report(self, results: List[JobAnalysisResult]):
        """
        Generiert Text- und HTML-Reports
        
        Args:
            results: Liste von JobAnalysisResult
        """
        if not results:
            logger.warning("No results for report")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Text Report
        text_report = self.pipeline.create_summary_report(results)
        text_path = self.dirs['reports'] / f"report_{timestamp}.txt"
        
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text_report)
        
        logger.info(f"Report saved: {text_path.name}")
        
        # HTML Report (einfach)
        html_report = self._create_html_report(results, timestamp)
        html_path = self.dirs['reports'] / f"report_{timestamp}.html"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        logger.info(f"HTML Report: {html_path.name}")
        
        return text_path, html_path
    
    def _create_html_report(self, results: List[JobAnalysisResult], 
                           timestamp: str) -> str:
        """Erstellt HTML-Report"""
        
        # Statistics
        total_jobs = len(results)
        total_skills = sum(r.competence_count for r in results)
        avg_skills = total_skills / total_jobs if total_jobs else 0
        avg_confidence = sum(r.avg_confidence for r in results) / total_jobs if total_jobs else 0
        
        # Categories
        all_categories = {}
        for r in results:
            for cat, count in r.categories.items():
                all_categories[cat] = all_categories.get(cat, 0) + count
        
        top_categories = sorted(all_categories.items(), 
                              key=lambda x: x[1], reverse=True)[:10]
        
        # Top Skills
        all_skills = {}
        for r in results:
            for comp in r.competences:
                all_skills[comp.name] = all_skills.get(comp.name, 0) + 1
        
        top_skills = sorted(all_skills.items(), 
                          key=lambda x: x[1], reverse=True)[:20]
        
        # Build HTML
        html = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Job Mining Report - {timestamp}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .section {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h2 {{
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        th, td {{
            text-align: left;
            padding: 12px;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        .bar {{
            background: #667eea;
            height: 20px;
            border-radius: 10px;
            margin-top: 5px;
        }}
        .jobs-list {{
            list-style: none;
            padding: 0;
        }}
        .job-item {{
            padding: 15px;
            border-left: 4px solid #667eea;
            margin-bottom: 15px;
            background: #f8f9fa;
        }}
        .footer {{
            text-align: center;
            color: #666;
            margin-top: 30px;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Job Mining Analysis Report</h1>
        <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{total_jobs}</div>
            <div class="stat-label">Job Ads Analyzed</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{total_skills}</div>
            <div class="stat-label">Total Skills Found</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{avg_skills:.1f}</div>
            <div class="stat-label">Avg Skills per Job</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{avg_confidence:.1%}</div>
            <div class="stat-label">Avg Confidence</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Top Skill Categories</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Count</th>
                <th>Percentage</th>
                <th>Visual</th>
            </tr>
"""
        
        for cat, count in top_categories:
            percentage = (count / total_skills * 100) if total_skills else 0
            bar_width = percentage
            html += f"""
            <tr>
                <td><strong>{cat}</strong></td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
                <td>
                    <div class="bar" style="width: {bar_width}%;"></div>
                </td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>⭐ Top 20 Skills</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Skill</th>
                <th>Frequency</th>
                <th>In % of Jobs</th>
            </tr>
"""
        
        for rank, (skill, count) in enumerate(top_skills, 1):
            percentage = (count / total_jobs * 100) if total_jobs else 0
            html += f"""
            <tr>
                <td>{rank}</td>
                <td><strong>{skill}</strong></td>
                <td>{count}</td>
                <td>{percentage:.1f}%</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>📋 Analyzed Job Ads</h2>
        <ul class="jobs-list">
"""
        
        for result in results:
            top_cat = max(result.categories.items(), 
                         key=lambda x: x[1])[0] if result.categories else 'N/A'
            
            html += f"""
            <li class="job-item">
                <strong>{result.filename}</strong> ({result.file_type.upper()})
                <br>
                Skills: {result.competence_count} | 
                Top Category: {top_cat} | 
                Confidence: {result.avg_confidence:.1%}
            </li>
"""
        
        html += """
        </ul>
    </div>
    
    <div class="footer">
        <p>Generated by Job Mining Pipeline v2.0 Multi-Format Edition</p>
        <p>Supports: PDF, DOCX, Google Docs | 135+ Skills</p>
    </div>
</body>
</html>
"""
        return html
    
    def run_workflow(self):
        """
        Führt kompletten Workflow aus:
        1. Verarbeite neue Jobs
        2. Speichere Ergebnisse
        3. Generiere Reports
        """
        logger.info(f"\n{'='*70}")
        logger.info("STARTING JOB MINING WORKFLOW")
        logger.info(f"{'='*70}\n")
        
        # Step 1: Process
        results = self.process_incoming()
        
        if not results:
            logger.info("No new jobs to process. Workflow complete.")
            return
        
        # Step 2: Save
        self.save_results(results)
        
        # Step 3: Report
        text_path, html_path = self.generate_report(results)
        
        # Summary
        logger.info(f"\n{'='*70}")
        logger.info("WORKFLOW COMPLETE")
        logger.info(f"{'='*70}")
        logger.info(f"Processed: {len(results)} job ads")
        logger.info(f"Found: {sum(r.competence_count for r in results)} skills")
        logger.info(f"\nResults:")
        logger.info(f"  📊 {self.dirs['results'].relative_to(self.base_dir)}/")
        logger.info(f"  📝 {self.dirs['reports'].relative_to(self.base_dir)}/")
        logger.info(f"  📁 {self.dirs['archive'].relative_to(self.base_dir)}/")
        logger.info(f"\nView HTML Report: file://{html_path}")
        logger.info(f"{'='*70}\n")
    
    def get_statistics(self) -> Dict:
        """Gibt Statistiken über alle verarbeiteten Jobs zurück"""
        archive_files = list(self.dirs['archive'].rglob("*"))
        archive_files = [
            f for f in archive_files 
            if f.suffix.lower() in ['.pdf', '.docx', '.doc']
        ]
        
        result_files = list(self.dirs['results'].glob("results_*.json"))
        
        return {
            'total_archived': len(archive_files),
            'total_results': len(result_files),
            'incoming_pending': len(list(self.dirs['incoming'].glob("*"))),
            'last_run': max(
                [f.stat().st_mtime for f in result_files]
            ) if result_files else None
        }


# ============================================================================
# EXAMPLE USAGE & CLI
# ============================================================================

def example_usage():
    """Beispiel-Verwendung des Workflow Managers"""
    
    print(f"\n{'='*70}")
    print("JOB MINING WORKFLOW MANAGER - EXAMPLE")
    print(f"{'='*70}\n")
    
    # Initialize
    manager = JobMiningWorkflowManager()
    
    print("\n1. DIRECTORY STRUCTURE CREATED:")
    print("-" * 70)
    print("  ✓ incoming/   - Neue Stellenanzeigen hier ablegen")
    print("  ✓ archive/    - Verarbeitete Dateien (nach Monat)")
    print("  ✓ results/    - JSON/CSV Ergebnisse")
    print("  ✓ reports/    - HTML/Text Reports")
    
    print("\n2. HOW TO USE:")
    print("-" * 70)
    print("  # Manuell: Neue Stellenanzeige hinzufügen")
    print("  manager.add_job_ad('path/to/job.pdf', metadata={")
    print("      'company': 'Example GmbH',")
    print("      'position': 'UX Designer'")
    print("  })")
    print("")
    print("  # Automatisch: Workflow ausführen")
    print("  manager.run_workflow()")
    
    print("\n3. STATISTICS:")
    print("-" * 70)
    stats = manager.get_statistics()
    print(f"  Archived jobs: {stats['total_archived']}")
    print(f"  Result files: {stats['total_results']}")
    print(f"  Pending jobs: {stats['incoming_pending']}")
    
    print(f"\n{'='*70}")
    print("✓ Workflow Manager ready!")
    print(f"{'='*70}\n")
    print("Next steps:")
    print("1. Place PDF/DOCX files in incoming/ directory")
    print("2. Run: manager.run_workflow()")
    print("3. Check reports/ for HTML report")


if __name__ == "__main__":
    print("="*70)
    print("JOB MINING WORKFLOW MANAGER v2.0")
    print("="*70)
    print("Features:")
    print("  ✓ Manual upload of new job ads")
    print("  ✓ Automatic processing")
    print("  ✓ Result archiving")
    print("  ✓ Report generation (HTML + Text)")
    print("  ✓ Statistics tracking")
    print("="*70)
    
    example_usage()
