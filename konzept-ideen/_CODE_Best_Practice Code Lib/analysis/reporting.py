"""
services/reporting.py
Minimaler Reporting Service für CSV/JSON Export
"""

import logging
import csv
import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime

from models.job_ad import JobAd


class ReportingService:
    """
    Minimaler Service für Datenexport
    CSV und JSON - kein Excel (optional später)
    """

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

    def export_csv(self, job_ads: List[JobAd], output_file: Path):
        """Exportiert Job Ads als CSV"""
        if not job_ads:
            self.logger.warning("Keine Daten zum Exportieren")
            return

        try:
            self.logger.info(f"📊 Exportiere CSV: {output_file}")

            # Daten konvertieren
            data = [job.to_dict() for job in job_ads]

            # Alle Keys sammeln
            all_keys = set()
            for row in data:
                all_keys.update(row.keys())

            # Keys sortieren
            priority_keys = [
                'id', 'file_name', 'source', 'date_processed',
                'posting_date', 'year', 'month', 'quarter',
                'job_title', 'company_name', 'company_branch', 'location',
                'job_categories', 'competences_count', 'competences',
                'char_count', 'word_count', 'extraction_quality'
            ]

            ordered_keys = []
            for key in priority_keys:
                if key in all_keys:
                    ordered_keys.append(key)
                    all_keys.remove(key)

            # Rest alphabetisch
            ordered_keys.extend(sorted(all_keys))

            # CSV schreiben
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=ordered_keys, delimiter=';')
                writer.writeheader()

                for row in data:
                    # Konvertiere komplexe Felder zu Strings
                    clean_row = {}
                    for key in ordered_keys:
                        value = row.get(key, '')

                        if isinstance(value, list):
                            if value and isinstance(value[0], dict):
                                # Liste von Dicts -> JSON String
                                clean_row[key] = json.dumps(value, ensure_ascii=False)
                            else:
                                # Einfache Liste -> Komma-getrennt
                                clean_row[key] = ', '.join(str(v) for v in value)
                        elif isinstance(value, dict):
                            clean_row[key] = json.dumps(value, ensure_ascii=False)
                        else:
                            clean_row[key] = value

                    writer.writerow(clean_row)

            self.logger.info(f"   ✓ {len(data)} Zeilen exportiert")

        except Exception as e:
            self.logger.error(f"CSV-Export fehlgeschlagen: {e}", exc_info=True)

    def export_json(self, job_ads: List[JobAd], analysis_results: Dict, output_file: Path):
        """Exportiert vollständige Daten als JSON"""
        if not job_ads:
            self.logger.warning("Keine Daten zum Exportieren")
            return

        try:
            self.logger.info(f"📊 Exportiere JSON: {output_file}")

            output_file.parent.mkdir(parents=True, exist_ok=True)

            export_data = {
                'meta': {
                    'generated_at': datetime.now().isoformat(),
                    'total_job_ads': len(job_ads),
                    'project': 'Job Mining - Kompetenzen im Wandel',
                },
                'job_ads': [job.to_dict() for job in job_ads],
                'analysis': analysis_results if analysis_results else {}
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

            self.logger.info(f"   ✓ JSON exportiert")

        except Exception as e:
            self.logger.error(f"JSON-Export fehlgeschlagen: {e}", exc_info=True)

    def generate_statistics_summary(self, job_ads: List[JobAd],
                                    analysis_results: Dict, output_file: Path):
        """Generiert Text-Statistik-Zusammenfassung"""
        if not job_ads:
            return

        try:
            self.logger.info(f"📊 Erstelle Statistik-Zusammenfassung")

            output_file.parent.mkdir(parents=True, exist_ok=True)

            from collections import Counter

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write("JOB MINING PROJEKT - STATISTIK-ZUSAMMENFASSUNG\n")
                f.write("="*80 + "\n\n")

                f.write(f"Generiert: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

                # Basis-Statistiken
                f.write("=" * 80 + "\n")
                f.write("ÜBERSICHT\n")
                f.write("=" * 80 + "\n\n")

                f.write(f"Gesamt Stellenanzeigen: {len(job_ads)}\n")

                total_comps = sum(len(job.competences) for job in job_ads)
                f.write(f"Gesamt Kompetenzen: {total_comps}\n")
                f.write(f"Ø Kompetenzen pro Anzeige: {total_comps/len(job_ads):.1f}\n\n")

                # Zeitliche Verteilung
                years = [job.year for job in job_ads if job.year]
                if years:
                    f.write("=" * 80 + "\n")
                    f.write("ZEITLICHE VERTEILUNG\n")
                    f.write("=" * 80 + "\n\n")

                    year_counts = Counter(years)
                    for year in sorted(year_counts.keys()):
                        f.write(f"  {year}: {year_counts[year]} Anzeigen\n")
                    f.write("\n")

                # Top Unternehmen
                f.write("=" * 80 + "\n")
                f.write("TOP 10 UNTERNEHMEN\n")
                f.write("=" * 80 + "\n\n")

                companies = [job.organization.name for job in job_ads if job.organization]
                for company, count in Counter(companies).most_common(10):
                    f.write(f"  {company}: {count}x\n")
                f.write("\n")

                # Top Standorte
                f.write("=" * 80 + "\n")
                f.write("TOP 10 STANDORTE\n")
                f.write("=" * 80 + "\n\n")

                locations = [job.location for job in job_ads]
                for loc, count in Counter(locations).most_common(10):
                    f.write(f"  {loc}: {count}x\n")
                f.write("\n")

                # Job-Kategorien
                f.write("=" * 80 + "\n")
                f.write("JOB-KATEGORIEN\n")
                f.write("=" * 80 + "\n\n")

                all_cats = []
                for job in job_ads:
                    all_cats.extend([cat.value for cat in job.job_categories])

                for cat, count in Counter(all_cats).most_common():
                    f.write(f"  {cat}: {count}x\n")
                f.write("\n")

                # Top Kompetenzen
                f.write("=" * 80 + "\n")
                f.write("TOP 30 KOMPETENZEN\n")
                f.write("=" * 80 + "\n\n")

                all_comps = []
                for job in job_ads:
                    all_comps.extend([c.name for c in job.competences])

                for comp, count in Counter(all_comps).most_common(30):
                    if comp:
                        f.write(f"  {comp}: {count}x\n")
                f.write("\n")

                # Kompetenzen nach Kategorie
                f.write("=" * 80 + "\n")
                f.write("KOMPETENZEN NACH KATEGORIE\n")
                f.write("=" * 80 + "\n\n")

                comp_by_cat = {}
                for job in job_ads:
                    for comp in job.competences:
                        if comp.category not in comp_by_cat:
                            comp_by_cat[comp.category] = []
                        comp_by_cat[comp.category].append(comp.name)

                for category in sorted(comp_by_cat.keys()):
                    comps = comp_by_cat[category]
                    f.write(f"\n{category} ({len(comps)} Nennungen):\n")
                    f.write("-" * 80 + "\n")

                    comp_counts = Counter(comps)
                    for comp, count in comp_counts.most_common(10):
                        f.write(f"  {comp}: {count}x\n")

                f.write("\n" + "="*80 + "\n")

            self.logger.info(f"   ✓ Statistik-Datei erstellt")

        except Exception as e:
            self.logger.error(f"Statistik-Erstellung fehlgeschlagen: {e}", exc_info=True)
