"""
repositories/competence_repository.py
Hauptrepository für Kompetenzen

Implementiert Repository Pattern mit Adapter Pattern
Nach: Gharbi - "Trennung von Verantwortlichkeiten"
"""

import logging
import yaml
from pathlib import Path
from typing import List, Dict
from repositories.adapters.json_adapter import JsonAdapter
from repositories.adapters.csv_adapter import CsvAdapter
from repositories.adapters.api_adapter import ApiAdapter
from models.competence import Competence


class CompetenceRepository:
    """
    Zentrale Repository-Klasse für Kompetenzen
    
    Verantwortlichkeiten:
    - Lädt Daten aus verschiedenen Quellen (JSON, CSV, API)
    - Verwaltet Adapter
    - Deduplizierung
    - Caching (optional)
    
    WICHTIG: Enthält KEINE Business-Logik!
    """
    
    def __init__(self, config_path: str = None):
        self.logger = logging.getLogger(__name__)
        self.adapters = []
        self._cache = None
        
        # Lade Konfiguration
        if config_path and Path(config_path).exists():
            self.config = self._load_config(config_path)
            self._initialize_adapters()
        else:
            self.logger.warning("Keine Config gefunden, verwende Defaults")
            self.config = {}
    
    def _load_config(self, config_path: str) -> dict:
        """Lädt YAML-Konfiguration"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"✅ Config geladen: {config_path}")
            return config
        except Exception as e:
            self.logger.error(f"Config-Fehler: {e}")
            return {}
    
    def _initialize_adapters(self):
        """Initialisiert Adapter basierend auf Config"""
        sources = self.config.get('sources', [])
        
        for source in sources:
            try:
                adapter = self._create_adapter(source)
                if adapter:
                    self.adapters.append(adapter)
                    self.logger.debug(f"   ✓ Adapter hinzugefügt: {source['name']}")
            except Exception as e:
                self.logger.error(f"Fehler bei Adapter {source.get('name')}: {e}")
        
        self.logger.info(f"📦 {len(self.adapters)} Adapter initialisiert")
    
    def _create_adapter(self, source_config: dict):
        """Factory Method für Adapter-Erstellung"""
        source_type = source_config.get('type')
        enabled = source_config.get('enabled', False)
        
        if source_type == 'json':
            return JsonAdapter(
                file_pattern=source_config.get('path'),
                enabled=enabled
            )
        elif source_type == 'csv':
            return CsvAdapter(
                file_path=source_config.get('path'),
                enabled=enabled,
                mapping=source_config.get('mapping')
            )
        elif source_type == 'api':
            return ApiAdapter(
                api_url=source_config.get('url'),
                api_key=source_config.get('api_key'),
                enabled=enabled,
                rate_limit=source_config.get('rate_limit', 100)
            )
        else:
            self.logger.warning(f"Unbekannter Source-Type: {source_type}")
            return None
    
    def get_all_competences(self) -> List[Competence]:
        """
        Lädt ALLE Kompetenzen aus ALLEN aktivierten Quellen
        
        Returns:
            Liste von deduplizierten Kompetenzen
        """
        # Check Cache
        if self._cache:
            self.logger.info("💾 Verwende gecachte Kompetenzen")
            return self._cache
        
        all_competences = []
        
        self.logger.info(f"📚 Lade Kompetenzen aus {len(self.adapters)} Quellen...")
        
        for adapter in self.adapters:
            if adapter.is_enabled():
                try:
                    competences = adapter.load()
                    all_competences.extend(competences)
                except Exception as e:
                    self.logger.error(f"Fehler beim Laden: {e}")
        
        # Deduplizieren
        deduplicated = self._deduplicate(all_competences)
        
        # Cache
        cache_config = self.config.get('cache', {})
        if cache_config.get('enabled', True):
            self._cache = deduplicated
        
        self.logger.info(f"✅ Gesamt: {len(deduplicated)} Kompetenzen geladen")
        
        return deduplicated
    
    def get_by_domain(self, domain: str) -> List[Competence]:
        """Filtert Kompetenzen nach Domain (Bounded Context!)"""
        all_comps = self.get_all_competences()
        return [c for c in all_comps if c.domain == domain]
    
    def get_by_category(self, category: str) -> List[Competence]:
        """Filtert Kompetenzen nach Kategorie"""
        all_comps = self.get_all_competences()
        return [c for c in all_comps if c.category == category]
    
    def _deduplicate(self, competences: List[Competence]) -> List[Competence]:
        """
        Entfernt Duplikate (basierend auf Namen)
        Bei Duplikaten: behalte die mit höherer Confidence
        """
        unique_dict = {}
        
        for comp in competences:
            key = comp.name.lower()
            
            if key not in unique_dict:
                unique_dict[key] = comp
            else:
                # Behalte die mit höherer Confidence
                if comp.confidence_score > unique_dict[key].confidence_score:
                    unique_dict[key] = comp
        
        deduplicated = list(unique_dict.values())
        
        if len(deduplicated) < len(competences):
            removed = len(competences) - len(deduplicated)
            self.logger.debug(f"   🧹 {removed} Duplikate entfernt")
        
        return deduplicated
    
    def add_adapter(self, adapter):
        """
        Fügt neuen Adapter hinzu
        
        Implementiert Open/Closed Principle:
        Erweiterbar ohne Änderung bestehenden Codes!
        """
        self.adapters.append(adapter)
        self._cache = None  # Cache invalidieren
        self.logger.info(f"➕ Neuer Adapter hinzugefügt")
    
    def clear_cache(self):
        """Löscht Cache"""
        self._cache = None
        self.logger.info("🗑️  Cache geleert")
    
    def get_statistics(self) -> Dict:
        """Gibt Statistiken zurück"""
        comps = self.get_all_competences()
        
        from collections import Counter
        
        return {
            'total': len(comps),
            'by_domain': dict(Counter(c.domain for c in comps if c.domain)),
            'by_category': dict(Counter(c.category for c in comps)),
            'by_type': dict(Counter(c.competence_type.value for c in comps)),
            'by_source': dict(Counter(c.source for c in comps)),
            'with_alternatives': sum(1 for c in comps if c.alternative_labels)
        }
