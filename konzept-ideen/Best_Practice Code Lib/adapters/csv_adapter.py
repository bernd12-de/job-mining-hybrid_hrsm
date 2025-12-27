"""
repositories/adapters/csv_adapter.py
CSV File Adapter - lädt Kompetenzen aus CSV (z.B. ESCO)
"""

import csv
import logging
from typing import List, Dict
from pathlib import Path
from repositories.base_repository import BaseRepository
from models.competence import Competence
from models.enums import CompetenceType


class CsvAdapter(BaseRepository):
    """
    Lädt Kompetenzen aus CSV-Dateien
    Hauptsächlich für ESCO-Import
    """
    
    def __init__(self, file_path: str, enabled: bool = False, 
                 mapping: Dict[str, str] = None):
        self.file_path = file_path
        self.enabled = enabled
        self.mapping = mapping or {
            'name_column': 'preferredLabel',
            'category_column': 'skillType',
            'type_column': 'type',
            'uri_column': 'conceptUri',
            'alternatives_column': 'altLabels'
        }
        self.logger = logging.getLogger(__name__)
    
    def is_enabled(self) -> bool:
        return self.enabled
    
    def load(self) -> List[Competence]:
        """Lädt Kompetenzen aus CSV"""
        if not self.enabled:
            return []
        
        if not Path(self.file_path).exists():
            self.logger.warning(f"CSV-Datei nicht gefunden: {self.file_path}")
            return []
        
        competences = []
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row in reader:
                    comp = self._parse_row(row)
                    if comp:
                        competences.append(comp)
            
            self.logger.info(f"✅ CSV-Adapter: {len(competences)} Kompetenzen geladen")
            
        except Exception as e:
            self.logger.error(f"Fehler beim CSV-Laden: {e}")
        
        return competences
    
    def _parse_row(self, row: dict) -> Competence:
        """Parst CSV-Zeile zu Competence"""
        try:
            name = row.get(self.mapping['name_column'], '').strip()
            if not name:
                return None
            
            category = row.get(self.mapping['category_column'], 'General')
            type_str = row.get(self.mapping['type_column'], 'skill')
            uri = row.get(self.mapping['uri_column'], '')
            
            # Alternative Labels parsen (z.B. durch | getrennt)
            alt_str = row.get(self.mapping['alternatives_column'], '')
            alternatives = [a.strip() for a in alt_str.split('|') if a.strip()]
            
            # Type mapping
            try:
                comp_type = CompetenceType[type_str.upper()]
            except KeyError:
                comp_type = CompetenceType.SKILL
            
            return Competence(
                name=name,
                category=category,
                competence_type=comp_type,
                alternative_labels=alternatives,
                esco_uri=uri,
                source="csv:esco",
                domain="ESCO"
            )
            
        except Exception as e:
            self.logger.debug(f"Fehler beim Parsen einer Zeile: {e}")
            return None
