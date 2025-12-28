"""
Competence Extractor v2.0 - Hybrid Approach
============================================

Erweitert die v4.1 Implementation mit:
- 135+ Custom Skills (vs. 40 in v4.1)
- ESCO-Mapping Vorbereitung (3 → 180-200 Ziel)
- Confidence Scoring
- Bessere Pattern Recognition

Basierend auf:
- KOTLIN_CODING_STATUS_KOMPLETT.md
- Exposé: Job Mining - Kompetenzen im Wandel
- Chat: Kotlin coding instructions and status

Autor: Job Mining Project
Datum: 2025-11-01
"""

import re
import json
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Competence:
    """Domain Model für Kompetenzen"""
    id: str
    name: str
    category: str
    type: str  # Tool, Method, Skill, Framework, Language, etc.
    confidence: float
    context: str = ""  # Text-Context wo gefunden
    esco_code: str = ""  # ESCO Mapping Code
    alternatives: List[str] = None
    
    def __post_init__(self):
        if self.alternatives is None:
            self.alternatives = []
    
    def to_dict(self) -> Dict:
        return asdict(self)


class CompetenceExtractorV2:
    """
    Erweiterte Kompetenz-Extraktion mit Hybrid-Ansatz
    
    Features:
    - 135+ Custom Skills (regex-basiert)
    - ESCO-Mapping Support
    - Confidence Scoring
    - Context-Awareness
    - Deduplizierung
    """
    
    def __init__(self, custom_skills_path: str = "custom_skills_extended.json"):
        """Initialize mit erweiterter Skills-Bibliothek"""
        self.custom_skills = self._load_custom_skills(custom_skills_path)
        self.compiled_patterns = self._compile_patterns()
        logger.info(f"Loaded {len(self.custom_skills)} custom skills")
    
    def _load_custom_skills(self, path: str) -> List[Dict]:
        """Lädt Custom Skills aus JSON"""
        skills_path = Path(path)
        if not skills_path.exists():
            logger.warning(f"Skills file not found: {path}")
            return []
        
        with open(skills_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Flatten skills from categories
        all_skills = []
        for category_obj in data.get('skills', []):
            category = category_obj.get('category', 'Unknown')
            for skill in category_obj.get('skills', []):
                skill['category'] = category
                all_skills.append(skill)
        
        return all_skills
    
    def _compile_patterns(self) -> Dict[str, Tuple[re.Pattern, Dict]]:
        """Kompiliert Regex-Pattern für bessere Performance"""
        compiled = {}
        for skill in self.custom_skills:
            pattern_str = skill.get('pattern', '')
            if pattern_str:
                try:
                    pattern = re.compile(pattern_str, re.IGNORECASE)
                    compiled[skill['id']] = (pattern, skill)
                except re.error as e:
                    logger.error(f"Invalid pattern for {skill['id']}: {e}")
        
        return compiled
    
    def extract_competences(self, text: str) -> List[Competence]:
        """
        Hauptmethode: Extrahiert alle Kompetenzen aus Text
        
        Args:
            text: Stellenanzeigen-Text
        
        Returns:
            Liste von Competence-Objekten
        """
        if not text:
            return []
        
        logger.debug(f"Extracting competences from {len(text)} chars")
        
        # Phase 1: Custom Skills (regex-basiert)
        custom_competences = self._extract_custom_skills(text)
        
        # Phase 2: ESCO Skills (keyword-basiert) - TODO
        # esco_competences = self._extract_esco_skills(text)
        
        # Phase 3: NLP-basierte Extraktion (optional) - TODO
        # nlp_competences = self._extract_nlp_skills(text)
        
        # Combine und Deduplizierung
        all_competences = custom_competences  # + esco_competences + nlp_competences
        deduplicated = self._deduplicate(all_competences)
        
        logger.info(f"Extracted {len(deduplicated)} unique competences")
        return deduplicated
    
    def _extract_custom_skills(self, text: str) -> List[Competence]:
        """Extrahiert Custom Skills via Regex"""
        found_competences = []
        
        for skill_id, (pattern, skill) in self.compiled_patterns.items():
            matches = pattern.finditer(text)
            
            for match in matches:
                # Extract context (50 chars before and after)
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].strip()
                
                competence = Competence(
                    id=skill_id,
                    name=skill['name'],
                    category=skill['category'],
                    type=skill['type'],
                    confidence=skill.get('confidence', 0.8),
                    context=context,
                    esco_code=skill.get('esco_mapping', ''),
                    alternatives=skill.get('alternatives', [])
                )
                
                found_competences.append(competence)
        
        return found_competences
    
    def _extract_esco_skills(self, text: str) -> List[Competence]:
        """
        Extrahiert ESCO Skills (keyword-basiert)
        TODO: Implementierung mit erweiterter ESCO-Bibliothek
        
        Ziel: 180-200 ESCO Skills statt aktuell 3
        """
        # Placeholder für zukünftige Implementation
        logger.debug("ESCO extraction not yet implemented")
        return []
    
    def _deduplicate(self, competences: List[Competence]) -> List[Competence]:
        """
        Entfernt Duplikate basierend auf:
        1. Gleiche ID
        2. Ähnliche Namen (Levenshtein)
        3. Confidence Scoring
        """
        if not competences:
            return []
        
        # Simple Deduplizierung nach ID (beste Confidence behält)
        seen = {}
        for comp in competences:
            if comp.id not in seen or comp.confidence > seen[comp.id].confidence:
                seen[comp.id] = comp
        
        return list(seen.values())
    
    def get_statistics(self, competences: List[Competence]) -> Dict:
        """Berechnet Statistiken über gefundene Kompetenzen"""
        if not competences:
            return {
                'total': 0,
                'by_category': {},
                'by_type': {},
                'avg_confidence': 0.0
            }
        
        categories = {}
        types = {}
        
        for comp in competences:
            # Count by category
            categories[comp.category] = categories.get(comp.category, 0) + 1
            # Count by type
            types[comp.type] = types.get(comp.type, 0) + 1
        
        avg_confidence = sum(c.confidence for c in competences) / len(competences)
        
        return {
            'total': len(competences),
            'by_category': categories,
            'by_type': types,
            'avg_confidence': round(avg_confidence, 3),
            'top_categories': sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def export_to_json(self, competences: List[Competence], output_path: str):
        """Exportiert Kompetenzen als JSON"""
        data = {
            'metadata': {
                'total_competences': len(competences),
                'version': '2.0',
                'extractor': 'CompetenceExtractorV2'
            },
            'statistics': self.get_statistics(competences),
            'competences': [comp.to_dict() for comp in competences]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Exported {len(competences)} competences to {output_path}")
    
    def export_to_csv(self, competences: List[Competence], output_path: str):
        """Exportiert Kompetenzen als CSV"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'ID', 'Name', 'Category', 'Type', 
                'Confidence', 'ESCO Code', 'Context'
            ])
            
            for comp in competences:
                writer.writerow([
                    comp.id,
                    comp.name,
                    comp.category,
                    comp.type,
                    comp.confidence,
                    comp.esco_code,
                    comp.context[:100]  # Limit context length
                ])
        
        logger.info(f"Exported {len(competences)} competences to {output_path}")


# ============================================================================
# EXAMPLE USAGE & TESTING
# ============================================================================

def test_extractor():
    """Test-Funktion mit Beispiel-Text"""
    
    # Beispiel-Text aus Stellenanzeige
    sample_text = """
    Wir suchen einen UX/UI Designer (m/w/d) mit Erfahrung in:
    
    - Figma, Sketch, Adobe XD für Design
    - User Research und Usability Testing
    - Prototyping und Wireframing
    - Agile Arbeitsweise (Scrum, Kanban)
    - Zusammenarbeit mit Product Owners
    - HTML, CSS, JavaScript Grundkenntnisse
    - Design Systems und Component Libraries
    
    Tools: Jira, Confluence, Miro
    Sprachen: Deutsch, Englisch
    
    Nice to have:
    - React, Vue.js Erfahrung
    - Analytics (Google Analytics, Hotjar)
    - A/B Testing
    """
    
    # Initialize Extractor
    extractor = CompetenceExtractorV2("custom_skills_extended.json")
    
    # Extract Competences
    competences = extractor.extract_competences(sample_text)
    
    # Print Results
    print(f"\n{'='*60}")
    print(f"FOUND {len(competences)} COMPETENCES:")
    print(f"{'='*60}\n")
    
    for comp in sorted(competences, key=lambda x: x.category):
        print(f"✓ {comp.name:30} | {comp.category:20} | {comp.type:15} | Conf: {comp.confidence}")
    
    # Print Statistics
    stats = extractor.get_statistics(competences)
    print(f"\n{'='*60}")
    print("STATISTICS:")
    print(f"{'='*60}")
    print(f"Total: {stats['total']}")
    print(f"Avg Confidence: {stats['avg_confidence']}")
    print(f"\nTop Categories:")
    for cat, count in stats['top_categories']:
        print(f"  - {cat}: {count}")
    
    # Export
    extractor.export_to_json(competences, "test_output.json")
    extractor.export_to_csv(competences, "test_output.csv")
    
    return competences


if __name__ == "__main__":
    print("="*60)
    print("COMPETENCE EXTRACTOR V2.0 - TESTING")
    print("="*60)
    
    competences = test_extractor()
    
    print(f"\n✓ Test completed successfully!")
    print(f"✓ Check test_output.json and test_output.csv for results")
