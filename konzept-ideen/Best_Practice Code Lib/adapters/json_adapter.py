"""
repositories/adapters/json_adapter.py
JSON File Adapter - lädt Kompetenzen aus JSON
"""

import json
import glob
import logging
from pathlib import Path
from typing import List
from repositories.base_repository import BaseRepository
from models.competence import Competence
from models.enums import CompetenceType


class JsonAdapter(BaseRepository):
    """
    Lädt Kompetenzen aus JSON-Dateien
    
    Implementiert Adapter Pattern für verschiedene Datenquellen
    Nach: ML Engineering with Python - "Open/Closed Principle"
    """
    
    def __init__(self, file_pattern: str, enabled: bool = True):
        self.file_pattern = file_pattern
        self.enabled = enabled
        self.logger = logging.getLogger(__name__)
    
    def is_enabled(self) -> bool:
        """Prüft ob Adapter aktiviert ist"""
        return self.enabled
    
    def load(self) -> List[Competence]:
        """Lädt Kompetenzen aus JSON-Dateien"""
        if not self.enabled:
            return []
        
        competences = []
        files = glob.glob(self.file_pattern)
        
        self.logger.info(f"📂 Lade JSON-Dateien: {len(files)} gefunden")
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                domain = data.get('domain', 'Unknown')
                
                for comp_data in data.get('competences', []):
                    comp = self._parse_competence(comp_data, domain, file_path)
                    competences.append(comp)
                
                self.logger.debug(f"   ✓ {file_path}: {len(data.get('competences', []))} Kompetenzen")
                
            except Exception as e:
                self.logger.error(f"   ✗ Fehler beim Laden von {file_path}: {e}")
        
        self.logger.info(f"✅ JSON-Adapter: {len(competences)} Kompetenzen geladen")
        return competences
    
    def _parse_competence(self, data: dict, domain: str, source_file: str) -> Competence:
        """Parst einzelne Kompetenz aus JSON"""
        
        # Type mapping
        type_str = data.get('type', 'skill').upper()
        try:
            comp_type = CompetenceType[type_str]
        except KeyError:
            self.logger.warning(f"Unbekannter Type: {type_str}, verwende SKILL")
            comp_type = CompetenceType.SKILL
        
        return Competence(
            name=data['name'],
            category=data.get('category', 'General'),
            competence_type=comp_type,
            alternative_labels=data.get('alternative_labels', []),
            esco_uri=data.get('esco_uri', ''),
            esco_code=data.get('esco_code'),
            confidence_score=data.get('confidence', 1.0),
            source=f"json:{Path(source_file).name}",
            domain=domain
        )
