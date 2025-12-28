"""
Job Mining Pipeline v2.0 - COMPLETE
====================================

Vollständige Pipeline:
1. Multi-Format Parsing (PDF, DOCX, Google Docs)
2. Competence Extraction (135+ Skills)
3. Analysis & Export

Autor: Job Mining Project
Datum: 2025-11-01
"""

import json
import logging
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass, asdict
import csv

# Import unserer Module
from multi_format_parser import MultiFormatParser, ParsedDocument
from competence_extractor_v2 import CompetenceExtractorV2, Competence

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class JobAnalysisResult:
    """Result für eine analysierte Stellenanzeige"""
    filename: str
    file_type: str  # pdf, docx, gdoc
    word_count: int
    competences: List[Competence]
    competence_count: int
    categories: Dict[str, int]
    avg_confidence: float
    text_preview: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'filename': self.filename,
            'file_type': self.file_type,
            'word_count': self.word_count,
            'competence_count': self.competence_count,
            'categories': self.categories,
            'avg_confidence': self.avg_confidence,
            'competences': [c.to_dict() for c in self.competences],
            'text_preview': self.text_preview
        }


class JobMiningPipeline:
    """
    Vollständige Job Mining Pipeline v2.0
    
    Features:
    - Multi-Format Support (PDF, DOCX, Google Docs)
    - 135+ Custom Skills
    - Batch-Processing
    - Export zu JSON/CSV/HTML
    - Statistiken & Visualisierung
    """
    
    def __init__(self, 
                 skills_path: str = "custom_skills_extended.json"):
        """Initialize Pipeline mit Parser und Extractor"""
        self.parser = MultiFormatParser()
        self.extractor = CompetenceExtractorV2(skills_path)
        logger.info("JobMiningPipeline v2.0 initialized")
    
    def analyze_file(self, file_path: str) -> JobAnalysisResult:
        """
        Analysiert eine einzelne Stellenanzeige
        
        Args:
            file_path: Pfad zur Datei (.pdf, .docx)
        
        Returns:
            JobAnalysisResult mit allen Daten
        """
        logger.info(f"Analyzing: {file_path}")
        
        # Step 1: Parse Document
        parsed_doc = self.parser.parse_file(file_path)
        
        # Step 2: Extract Competences
        competences = self.extractor.extract_competences(parsed_doc.text)
        
        # Step 3: Calculate Statistics
        categories = {}
        for comp in competences:
            categories[comp.category] = categories.get(comp.category, 0) + 1
        
        avg_confidence = (
            sum(c.confidence for c in competences) / len(competences)
            if competences else 0.0
        )
        
        # Step 4: Create Result
        result = JobAnalysisResult(
            filename=parsed_doc.filename,
            file_type=parsed_doc.file_type,
            word_count=parsed_doc.word_count,
            competences=competences,
            competence_count=len(competences),
            categories=categories,
            avg_confidence=round(avg_confidence, 3),
            text_preview=parsed_doc.text[:200] if parsed_doc.text else ""
        )
        
        logger.info(f"✓ Found {len(competences)} competences in {parsed_doc.filename}")
        return result
    
    def batch_analyze(self, 
                     directory: str,
                     pattern: str = "*",
                     recursive: bool = True) -> List[JobAnalysisResult]:
        """
        Analysiert alle Stellenanzeigen in einem Verzeichnis
        
        Args:
            directory: Verzeichnis mit Stellenanzeigen
            pattern: Datei-Pattern (*, *.pdf, *.docx)
            recursive: Unterverzeichnisse durchsuchen
        
        Returns:
            Liste von JobAnalysisResult
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"BATCH ANALYSIS STARTED")
        logger.info(f"{'='*60}")
        logger.info(f"Directory: {directory}")
        logger.info(f"Pattern: {pattern}")
        logger.info(f"Recursive: {recursive}")
        
        # Parse all documents
        documents = self.parser.batch_parse(directory, pattern, recursive)
        
        if not documents:
            logger.warning("No documents found!")
            return []
        
        # Analyze each document
        results = []
        for doc in documents:
            try:
                # Extract competences
                competences = self.extractor.extract_competences(doc.text)
                
                # Calculate stats
                categories = {}
                for comp in competences:
                    categories[comp.category] = categories.get(comp.category, 0) + 1
                
                avg_confidence = (
                    sum(c.confidence for c in competences) / len(competences)
                    if competences else 0.0
                )
                
                # Create result
                result = JobAnalysisResult(
                    filename=doc.filename,
                    file_type=doc.file_type,
                    word_count=doc.word_count,
                    competences=competences,
                    competence_count=len(competences),
                    categories=categories,
                    avg_confidence=round(avg_confidence, 3),
                    text_preview=doc.text[:200] if doc.text else ""
                )
                
                results.append(result)
                logger.info(f"✓ {doc.filename}: {len(competences)} skills")
            
            except Exception as e:
                logger.error(f"✗ Failed to analyze {doc.filename}: {e}")
        
        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"BATCH ANALYSIS COMPLETE")
        logger.info(f"{'='*60}")
        logger.info(f"Documents analyzed: {len(results)}")
        logger.info(f"Total competences: {sum(r.competence_count for r in results)}")
        logger.info(f"Avg competences/job: {sum(r.competence_count for r in results) // len(results) if results else 0}")
        
        return results
    
    def export_to_json(self, 
                      results: List[JobAnalysisResult],
                      output_path: str):
        """Exportiert Ergebnisse als JSON"""
        data = {
            'metadata': {
                'version': '2.0',
                'total_jobs': len(results),
                'total_competences': sum(r.competence_count for r in results),
                'avg_competences_per_job': (
                    sum(r.competence_count for r in results) / len(results)
                    if results else 0
                )
            },
            'results': [r.to_dict() for r in results]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported to JSON: {output_path}")
    
    def export_to_csv(self,
                     results: List[JobAnalysisResult],
                     output_path: str):
        """Exportiert Ergebnisse als CSV (flat structure)"""
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Filename', 'File Type', 'Word Count',
                'Competence Count', 'Avg Confidence',
                'Top Category', 'Top Category Count',
                'All Skills'
            ])
            
            # Data
            for result in results:
                top_category = max(result.categories.items(), 
                                 key=lambda x: x[1]) if result.categories else ('', 0)
                
                all_skills = ', '.join(c.name for c in result.competences)
                
                writer.writerow([
                    result.filename,
                    result.file_type,
                    result.word_count,
                    result.competence_count,
                    result.avg_confidence,
                    top_category[0],
                    top_category[1],
                    all_skills
                ])
        
        logger.info(f"Exported to CSV: {output_path}")
    
    def export_detailed_csv(self,
                           results: List[JobAnalysisResult],
                           output_path: str):
        """
        Exportiert detailliertes CSV (eine Zeile pro Skill)
        Besser für weitere Analysen
        """
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Filename', 'File Type', 'Word Count',
                'Skill ID', 'Skill Name', 'Category', 'Type',
                'Confidence', 'ESCO Code'
            ])
            
            # Data
            for result in results:
                for comp in result.competences:
                    writer.writerow([
                        result.filename,
                        result.file_type,
                        result.word_count,
                        comp.id,
                        comp.name,
                        comp.category,
                        comp.type,
                        comp.confidence,
                        comp.esco_code
                    ])
        
        logger.info(f"Exported detailed CSV: {output_path}")
    
    def create_summary_report(self, results: List[JobAnalysisResult]) -> str:
        """Erstellt Text-Report mit Zusammenfassung"""
        if not results:
            return "No results to report"
        
        # Calculate statistics
        total_jobs = len(results)
        total_comps = sum(r.competence_count for r in results)
        avg_comps = total_comps / total_jobs if total_jobs else 0
        avg_confidence = sum(r.avg_confidence for r in results) / total_jobs if total_jobs else 0
        
        # File types
        file_types = {}
        for r in results:
            file_types[r.file_type] = file_types.get(r.file_type, 0) + 1
        
        # All categories
        all_categories = {}
        for r in results:
            for cat, count in r.categories.items():
                all_categories[cat] = all_categories.get(cat, 0) + count
        
        # Top skills
        all_skills = {}
        for r in results:
            for comp in r.competences:
                all_skills[comp.name] = all_skills.get(comp.name, 0) + 1
        
        top_skills = sorted(all_skills.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # Build report
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║              JOB MINING ANALYSIS REPORT v2.0                         ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

SUMMARY
{'='*70}
Total Job Ads Analyzed:        {total_jobs}
Total Competences Found:       {total_comps}
Average Competences per Job:   {avg_comps:.1f}
Average Confidence Score:      {avg_confidence:.3f} ({avg_confidence*100:.1f}%)

FILE TYPES
{'='*70}
"""
        for ftype, count in sorted(file_types.items()):
            percentage = (count / total_jobs * 100) if total_jobs else 0
            report += f"{ftype.upper():10} {count:3} jobs ({percentage:5.1f}%)\n"
        
        report += f"""
COMPETENCE CATEGORIES
{'='*70}
"""
        for cat, count in sorted(all_categories.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_comps * 100) if total_comps else 0
            report += f"{cat[:40]:40} {count:4} ({percentage:5.1f}%)\n"
        
        report += f"""
TOP 20 SKILLS
{'='*70}
"""
        for skill, count in top_skills:
            percentage = (count / total_jobs * 100) if total_jobs else 0
            report += f"{skill[:40]:40} {count:3} jobs ({percentage:5.1f}%)\n"
        
        report += f"""
{'='*70}
Report generated by Job Mining Pipeline v2.0
{'='*70}
"""
        return report


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_usage():
    """Beispiel für die Verwendung der Pipeline"""
    
    print(f"\n{'='*70}")
    print("JOB MINING PIPELINE v2.0 - EXAMPLE")
    print(f"{'='*70}\n")
    
    # Initialize Pipeline
    pipeline = JobMiningPipeline("custom_skills_extended.json")
    
    # Beispiel 1: Einzelne Datei analysieren
    print("Example 1: Analyzing single file...")
    print("-" * 70)
    
    try:
        result = pipeline.analyze_file("/home/claude/test_job_ad.docx")
        
        print(f"File: {result.filename}")
        print(f"Type: {result.file_type}")
        print(f"Words: {result.word_count}")
        print(f"Skills found: {result.competence_count}")
        print(f"Avg confidence: {result.avg_confidence}")
        print(f"\nSkills by category:")
        for cat, count in sorted(result.categories.items(), key=lambda x: x[1], reverse=True):
            print(f"  - {cat}: {count}")
        
        print(f"\nAll skills:")
        for comp in result.competences:
            print(f"  ✓ {comp.name} ({comp.category}) - Confidence: {comp.confidence}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    print(f"\n{'='*70}\n")
    
    # Beispiel 2: Batch-Analyse (wenn Dateien vorhanden)
    print("Example 2: Batch analysis...")
    print("-" * 70)
    print("(Would analyze all PDFs and DOCX files in a directory)")
    print("Usage:")
    print("  results = pipeline.batch_analyze('/path/to/job_ads')")
    print("  pipeline.export_to_json(results, 'output.json')")
    print("  pipeline.export_to_csv(results, 'output.csv')")
    
    print(f"\n{'='*70}")
    print("✓ Example complete!")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    print("="*70)
    print("JOB MINING PIPELINE v2.0")
    print("="*70)
    print("Features:")
    print("  ✓ Multi-Format Support (PDF, DOCX, Google Docs)")
    print("  ✓ 135+ Custom Skills")
    print("  ✓ Batch Processing")
    print("  ✓ Export (JSON, CSV)")
    print("  ✓ Analysis Reports")
    print("="*70)
    
    example_usage()
