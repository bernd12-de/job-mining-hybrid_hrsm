"""
services/data_preparation.py
Bereitet Rohdaten auf (Cleaning, Normalization)

Theoretische Grundlagen:
- Wu (2024): Data Mining with Python
- Groß (2022): Text Mining im Personalmanagement
"""

import logging
import re
from typing import List, Dict
from collections import Counter

from models.job_ad import JobAd


class TextCleaner:
    """
    Text-Bereinigung
    Nach Wu (2024): Data Mining with Python
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def clean(self, text: str) -> str:
        """Bereinigt Text"""
        if not text:
            return ""

        # URLs entfernen
        text = re.sub(r'http[s]?://\S+', '', text)

        # E-Mails entfernen
        text = re.sub(r'\S+@\S+', '', text)

        # Mehrfache Leerzeichen
        text = re.sub(r'\s+', ' ', text)

        # Mehrfache Zeilenumbrüche
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Zeilen trimmen
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        text = '\n'.join(lines)

        return text

    def calculate_text_quality(self, text: str) -> float:
        """Berechnet Textqualität"""
        if not text:
            return 0.0

        score = 0.0
        max_score = 5.0

        # Länge angemessen?
        if 500 <= len(text) <= 10000:
            score += 1.0
        elif 200 <= len(text) <= 20000:
            score += 0.5

        # Enthält deutsche/englische Wörter?
        common_words = ['und', 'der', 'die', 'das', 'in', 'mit', 'für',
                        'and', 'the', 'of', 'to', 'in', 'for']
        if any(word in text.lower() for word in common_words):
            score += 1.0

        # Satzzeichen vorhanden?
        if any(punct in text for punct in ['.', ',', ';', ':']):
            score += 1.0

        # Großbuchstaben (nicht nur uppercase)?
        upper_count = sum(1 for c in text if c.isupper())
        if 0.01 < upper_count / len(text) < 0.5:
            score += 1.0

        # Keine zu vielen Sonderzeichen
        special_count = sum(1 for c in text if not c.isalnum() and not c.isspace())
        if special_count / len(text) < 0.2:
            score += 1.0

        return score / max_score


class DataNormalizer:
    """Normalisiert Daten für konsistente Analyse"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def normalize_company_names(self, job_ads: List[JobAd]) -> List[JobAd]:
        """Normalisiert Unternehmensnamen"""
        # Mapping für Varianten
        name_mapping = {
            'Deutsche Bank AG': 'Deutsche Bank',
            'Deutsche Bank Group': 'Deutsche Bank',
            'SAP SE': 'SAP',
            'SAP AG': 'SAP',
            'BMW Group': 'BMW',
            'BMW AG': 'BMW',
        }

        for job in job_ads:
            if job.organization:
                original = job.organization.name
                normalized = name_mapping.get(original, original)
                job.organization.name = normalized

        return job_ads

    def normalize_locations(self, job_ads: List[JobAd]) -> List[JobAd]:
        """Normalisiert Standorte"""
        location_mapping = {
            'Muenchen': 'München',
            'Muenster': 'Münster',
            'Koeln': 'Köln',
            'Duesseldorf': 'Düsseldorf',
        }

        for job in job_ads:
            original = job.location
            normalized = location_mapping.get(original, original)
            job.location = normalized

        return job_ads


class DataDeduplicator:
    """Entfernt Duplikate"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def deduplicate(self, job_ads: List[JobAd]) -> List[JobAd]:
        """Entfernt doppelte Einträge"""
        seen = set()
        unique = []

        for job in job_ads:
            # Fingerprint: Dateiname + erste 100 Zeichen
            fingerprint = (job.file_name, job.raw_text[:100])

            if fingerprint not in seen:
                seen.add(fingerprint)
                unique.append(job)
            else:
                self.logger.debug(f"Duplikat entfernt: {job.file_name}")

        return unique


class DataValidator:
    """Validiert Datenqualität"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def validate(self, job_ads: List[JobAd]) -> tuple[List[JobAd], List[JobAd]]:
        """Trennt valide und invalide Job Ads"""
        valid = []
        invalid = []

        for job in job_ads:
            if self._is_valid(job):
                valid.append(job)
            else:
                invalid.append(job)
                self.logger.warning(f"Invalide Job Ad: {job.file_name}")

        return valid, invalid

    def _is_valid(self, job: JobAd) -> bool:
        """Prüft ob Job Ad valide ist"""
        # Mindestanforderungen
        if not job.raw_text or len(job.raw_text) < 100:
            return False

        if job.char_count < 100 or job.word_count < 20:
            return False

        return True


class DataPreparationService:
    """
    Hauptservice für Datenaufbereitung

    Implementiert Phase 3 des CRISP-DM: Data Preparation
    """

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Komponenten
        self.text_cleaner = TextCleaner()
        self.normalizer = DataNormalizer()
        self.deduplicator = DataDeduplicator()
        self.validator = DataValidator()

        # Statistiken
        self.stats = {
            'input_count': 0,
            'processed_count': 0,
            'cleaned_count': 0,
            'deduplicated': 0,
            'invalid': 0,
            'error_count': 0
        }

    def prepare_job_ads(self, raw_job_ads: List[JobAd]) -> List[JobAd]:
        """Bereitet Job Ads vollständig auf"""
        self.logger.info(f"🔧 Bereite {len(raw_job_ads)} Job Ads auf...")

        self.stats['input_count'] = len(raw_job_ads)

        # 1. Text-Bereinigung
        self.logger.info("   1. Text-Bereinigung...")
        job_ads = self._clean_texts(raw_job_ads)

        # 2. Deduplizierung
        self.logger.info("   2. Deduplizierung...")
        job_ads = self.deduplicator.deduplicate(job_ads)
        self.stats['deduplicated'] = len(raw_job_ads) - len(job_ads)

        # 3. Normalisierung
        self.logger.info("   3. Normalisierung...")
        job_ads = self.normalizer.normalize_company_names(job_ads)
        job_ads = self.normalizer.normalize_locations(job_ads)

        # 4. Validierung
        self.logger.info("   4. Validierung...")
        valid_job_ads, invalid_job_ads = self.validator.validate(job_ads)
        self.stats['invalid'] = len(invalid_job_ads)

        self.stats['processed_count'] = len(valid_job_ads)

        self.logger.info(f"✅ Aufbereitung abgeschlossen:")
        self.logger.info(f"   Input: {self.stats['input_count']}")
        self.logger.info(f"   Bereinigt: {self.stats['cleaned_count']}")
        self.logger.info(f"   Duplikate entfernt: {self.stats['deduplicated']}")
        self.logger.info(f"   Invalide: {self.stats['invalid']}")
        self.logger.info(f"   Output: {self.stats['processed_count']}")

        return valid_job_ads

    def _clean_texts(self, job_ads: List[JobAd]) -> List[JobAd]:
        """Bereinigt Texte aller Job Ads"""
        cleaned_count = 0

        for job in job_ads:
            try:
                # Text bereinigen
                job.cleaned_text = self.text_cleaner.clean(job.raw_text)

                # Textqualität berechnen
                job.text_quality = self.text_cleaner.calculate_text_quality(
                    job.cleaned_text
                )

                cleaned_count += 1

            except Exception as e:
                self.logger.error(f"Fehler bei {job.file_name}: {e}")
                job.cleaned_text = job.raw_text
                job.text_quality = 0.0
                self.stats['error_count'] += 1

        self.stats['cleaned_count'] = cleaned_count

        return job_ads

    def get_preparation_stats(self) -> Dict:
        """Gibt Aufbereitungs-Statistiken zurück"""
        return self.stats
