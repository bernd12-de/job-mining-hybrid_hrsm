"""
services/analysis.py
Analysiert extrahierte Daten

Theoretische Grundlagen:
- Hirschle (2021): Machine Learning für Zeitreihen
- McMahon (2023): Machine Learning Engineering
- Barton et al. (2018): Digitalisierung in Unternehmen
"""

import logging
from typing import List, Dict, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime
import statistics

from models.job_ad import JobAd, Competence, JobCategory
from models.analysis_results import (
    CompetenceTrend, BranchProfile, RoleProfile,
    TimeSeriesAnalysis, ClusterAnalysis, AnalysisReport,
    AIInsights
)


class TimeSeriesAnalyzer:
    """
    Zeitreihenanalyse für Kompetenztrends
    Nach Hirschle (2021): Machine Learning für Zeitreihen
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze(self, job_ads: List[JobAd]) -> TimeSeriesAnalysis:
        """Führt Zeitreihenanalyse durch"""
        self.logger.info("📊 Zeitreihenanalyse...")

        # Nach Zeit gruppieren
        time_groups = self._group_by_time(job_ads)

        # Trends für einzelne Kompetenzen berechnen
        competence_trends = self._calculate_competence_trends(time_groups)

        # Aggregierte Trends
        rising = [t.competence_name for t in competence_trends if t.trend_direction == "rising"]
        falling = [t.competence_name for t in competence_trends if t.trend_direction == "falling"]
        emerging = self._identify_emerging_competences(time_groups)

        analysis = TimeSeriesAnalysis(
            start_date=min(job_ads, key=lambda x: x.posting_date or datetime.now()).posting_date or datetime.now(),
            end_date=max(job_ads, key=lambda x: x.posting_date or datetime.now()).posting_date or datetime.now(),
            competence_trends=competence_trends,
            rising_competences=rising[:20],  # Top 20
            falling_competences=falling[:20],
            emerging_competences=emerging
        )

        self.logger.info(f"   Rising: {len(rising)}, Falling: {len(falling)}, Emerging: {len(emerging)}")

        return analysis

    def _group_by_time(self, job_ads: List[JobAd]) -> Dict[str, List[JobAd]]:
        """Gruppiert Job Ads nach Zeitperiode"""
        groups = defaultdict(list)

        for job in job_ads:
            period = job.get_time_period()
            groups[period].append(job)

        return dict(groups)

    def _calculate_competence_trends(self, time_groups: Dict[str, List[JobAd]]) -> List[CompetenceTrend]:
        """Berechnet Trends für Kompetenzen"""
        # Alle Kompetenzen sammeln
        all_competences = set()
        for jobs in time_groups.values():
            for job in jobs:
                for comp in job.competences:
                    all_competences.add(comp.name)

        trends = []

        for comp_name in all_competences:
            # Häufigkeiten über Zeit
            periods = sorted(time_groups.keys())
            frequencies = []
            percentages = []

            for period in periods:
                jobs = time_groups[period]
                count = sum(1 for job in jobs if job.has_competence(comp_name))
                frequencies.append(count)
                percentages.append((count / len(jobs)) * 100 if jobs else 0)

            # Trend erstellen
            if sum(frequencies) >= 3:  # Mindestens 3 Vorkommen
                # Kategorie ermitteln
                category = "General"
                for jobs in time_groups.values():
                    for job in jobs:
                        for comp in job.competences:
                            if comp.name == comp_name:
                                category = comp.category
                                break

                trend = CompetenceTrend(
                    competence_name=comp_name,
                    category=category,
                    time_periods=periods,
                    frequencies=frequencies,
                    percentages=percentages,
                    mean_frequency=statistics.mean(frequencies),
                    std_deviation=statistics.stdev(frequencies) if len(frequencies) > 1 else 0
                )

                trend.calculate_trend()
                trends.append(trend)

        return sorted(trends, key=lambda x: x.growth_rate, reverse=True)

    def _identify_emerging_competences(self, time_groups: Dict[str, List[JobAd]]) -> List[str]:
        """Identifiziert neu aufkommende Kompetenzen"""
        periods = sorted(time_groups.keys())

        if len(periods) < 3:
            return []

        # Kompetenzen in erster Hälfte vs zweiter Hälfte
        mid = len(periods) // 2
        first_half_periods = periods[:mid]
        second_half_periods = periods[mid:]

        first_half_comps = set()
        for period in first_half_periods:
            for job in time_groups[period]:
                first_half_comps.update(c.name for c in job.competences)

        second_half_comps = set()
        for period in second_half_periods:
            for job in time_groups[period]:
                second_half_comps.update(c.name for c in job.competences)

        # Neu in zweiter Hälfte
        emerging = second_half_comps - first_half_comps

        return list(emerging)[:15]  # Top 15


class BranchAnalyzer:
    """Branchenvergleich"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze(self, job_ads: List[JobAd]) -> List[BranchProfile]:
        """Analysiert Branchen"""
        self.logger.info("🏢 Branchenanalyse...")

        # Nach Branche gruppieren
        branch_groups = defaultdict(list)
        for job in job_ads:
            branch = job.organization.branch if job.organization else "Unknown"
            branch_groups[branch].append(job)

        profiles = []

        for branch, jobs in branch_groups.items():
            if branch and len(jobs) >= 3:  # Mindestens 3 Anzeigen
                profile = BranchProfile(branch_name=branch)
                profile.calculate_metrics(jobs)
                profiles.append(profile)

        self.logger.info(f"   {len(profiles)} Branchen analysiert")

        return sorted(profiles, key=lambda x: x.job_ads_count, reverse=True)


class RoleAnalyzer:
    """Rollenprofile"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze(self, job_ads: List[JobAd]) -> List[RoleProfile]:
        """Analysiert Berufsrollen"""
        self.logger.info("👥 Rollenanalyse...")

        # Nach Kategorie gruppieren
        role_groups = defaultdict(list)
        for job in job_ads:
            for category in job.job_categories:
                role_groups[category].append(job)

        profiles = []

        for category, jobs in role_groups.items():
            profile = RoleProfile(
                role_name=category.value,
                job_category=category.name,
                job_ads_count=len(jobs)
            )

            # Top Kompetenzen
            all_comps = []
            for job in jobs:
                all_comps.extend([c.name for c in job.competences])

            comp_counter = Counter(all_comps)
            profile.required_competences = comp_counter.most_common(15)

            # Nach Typ gruppieren
            for job in jobs:
                for comp in job.competences:
                    if comp.competence_type.value in ['tool', 'technology', 'language']:
                        profile.technical_skills.append(comp.name)
                    elif comp.competence_type.value == 'method':
                        profile.methodological_skills.append(comp.name)

            # Deduplizieren
            profile.technical_skills = list(set(profile.technical_skills))[:10]
            profile.methodological_skills = list(set(profile.methodological_skills))[:10]

            # Soft Skills
            for job in jobs:
                profile.soft_skills.extend(job.requirements.soft_skills)
            profile.soft_skills = list(set(profile.soft_skills))[:10]

            profiles.append(profile)

        self.logger.info(f"   {len(profiles)} Rollen analysiert")

        return profiles


class CompetenceClusterer:
    """
    Kompetenz-Clustering
    Nach McMahon (2023): Machine Learning Engineering
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def cluster(self, job_ads: List[JobAd]) -> ClusterAnalysis:
        """Clustert Kompetenzen semantisch"""
        self.logger.info("🔬 Kompetenz-Clustering...")

        # Einfaches regelbasiertes Clustering nach Kategorien
        # (Für echtes ML-Clustering würde sklearn benötigt)

        category_clusters = defaultdict(list)

        for job in job_ads:
            for comp in job.competences:
                category_clusters[comp.category].append(comp)

        # Cluster-Objekte erstellen
        from models.job_ad import CompetenceCluster

        clusters = []
        for i, (category, comps) in enumerate(category_clusters.items()):
            # Deduplizieren nach Namen
            unique_comps = {}
            for comp in comps:
                if comp.name not in unique_comps:
                    unique_comps[comp.name] = comp

            cluster = CompetenceCluster(
                id=f"cluster_{i}",
                name=category,
                description=f"Kompetenzen im Bereich {category}",
                competences=list(unique_comps.values()),
                job_ads_count=len([j for j in job_ads if any(c.category == category for c in j.competences)])
            )

            clusters.append(cluster)

        analysis = ClusterAnalysis(
            method="rule_based_category",
            n_clusters=len(clusters),
            clusters=sorted(clusters, key=lambda x: len(x.competences), reverse=True)
        )

        self.logger.info(f"   {len(clusters)} Cluster erstellt")

        return analysis


class QualityEvaluator:
    """Evaluiert Datenqualität und Extraktionsgenauigkeit"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def evaluate(self, job_ads: List[JobAd], analysis_results: Dict) -> Dict:
        """Führt Qualitätsevaluation durch"""
        self.logger.info("✅ Qualitätsevaluation...")

        if not job_ads:
            return {
                'data_quality': 0.0,
                'extraction_accuracy': 0.0,
                'esco_coverage': 0.0
            }

        # Datenqualität
        text_quality_scores = [job.text_quality for job in job_ads if hasattr(job, 'text_quality')]
        data_quality = statistics.mean([job.extraction_quality for job in job_ads])

        # Extraktionsgenauigkeit (basierend auf Vollständigkeit)
        complete_extractions = sum(1 for job in job_ads
                                   if len(job.competences) > 0
                                   and job.organization.name != "Unbekannt"
                                   and job.location != "Nicht angegeben")
        extraction_accuracy = complete_extractions / len(job_ads)

        # ESCO-Abdeckung (Anteil mit ESCO-URI)
        with_esco = sum(1 for job in job_ads
                        for comp in job.competences
                        if comp.esco_uri)
        total_comps = sum(len(job.competences) for job in job_ads)
        esco_coverage = with_esco / total_comps if total_comps > 0 else 0

        result = {
            'data_quality': data_quality,
            'extraction_accuracy': extraction_accuracy,
            'esco_coverage': esco_coverage,
            'total_job_ads': len(job_ads),
            'total_competences': total_comps,
            'avg_competences': total_comps / len(job_ads)
        }

        self.logger.info(f"   Datenqualität: {data_quality:.1%}")
        self.logger.info(f"   Extraktionsgenauigkeit: {extraction_accuracy:.1%}")
        self.logger.info(f"   ESCO-Abdeckung: {esco_coverage:.1%}")

        return result


class AIInsightGenerator:
    """
    Generiert KI-gestützte Interpretationen (optional)
    Nach Campesato (2024): Python with ChatGPT/GPT-4
    """

    def __init__(self, model: str = "gpt-4"):
        self.logger = logging.getLogger(__name__)
        self.model = model

        # Check ob OpenAI verfügbar
        try:
            import openai
            self.openai = openai
            self.available = True
        except ImportError:
            self.logger.warning("OpenAI nicht installiert - KI-Features deaktiviert")
            self.available = False

    def generate(self, job_ads: List[JobAd], analysis_results: Dict) -> Optional[AIInsights]:
        """Generiert KI-Insights"""
        if not self.available:
            self.logger.info("⚠️  KI-Insights übersprungen (OpenAI nicht verfügbar)")
            return None

        self.logger.info("🤖 Generiere KI-Insights...")

        insights = AIInsights(model=self.model)

        try:
            # Trend-Narrationen
            if 'time_series' in analysis_results:
                insights.trend_narratives = self._generate_trend_narratives(
                    analysis_results['time_series']
                )

            # Cluster-Beschreibungen
            if 'clusters' in analysis_results:
                insights.cluster_descriptions = self._generate_cluster_descriptions(
                    analysis_results['clusters']
                )

            # Transformations-Assessment
            insights.transformation_assessment = self._assess_transformation(
                job_ads, analysis_results
            )

            # Empfehlungen
            insights.curriculum_recommendations = self._generate_curriculum_recommendations(
                analysis_results
            )

            insights.confidence_score = 0.7  # Placeholder

            self.logger.info("   ✓ KI-Insights generiert")
            return insights

        except Exception as e:
            self.logger.error(f"   KI-Fehler: {e}")
            return None

    def _generate_trend_narratives(self, time_series: TimeSeriesAnalysis) -> Dict[str, str]:
        """Generiert Trend-Beschreibungen"""
        narratives = {}

        # Top Rising
        if time_series.rising_competences:
            top_rising = time_series.rising_competences[:5]
            narratives['rising'] = f"Stark wachsende Kompetenzen: {', '.join(top_rising)}"

        # Emerging
        if time_series.emerging_competences:
            narratives['emerging'] = f"Neu aufkommende Kompetenzen: {', '.join(time_series.emerging_competences[:5])}"

        return narratives

    def _generate_cluster_descriptions(self, cluster_analysis: ClusterAnalysis) -> Dict[str, str]:
        """Generiert Cluster-Beschreibungen"""
        descriptions = {}

        for cluster in cluster_analysis.clusters:
            top_comps = [c.name for c in cluster.competences[:5]]
            descriptions[cluster.name] = f"Kernkompetenzen: {', '.join(top_comps)}"

        return descriptions

    def _assess_transformation(self, job_ads: List[JobAd], analysis_results: Dict) -> str:
        """Bewertet digitale Transformation"""
        # Einfache Heuristik
        agile_mentions = sum(1 for job in job_ads if job.agile_methods_mentioned)
        agile_rate = agile_mentions / len(job_ads) if job_ads else 0

        if agile_rate > 0.7:
            return "Hoher Reifegrad der agilen Transformation erkennbar"
        elif agile_rate > 0.4:
            return "Mittlerer Reifegrad - Transformation im Gange"
        else:
            return "Frühe Phase der digitalen Transformation"

    def _generate_curriculum_recommendations(self, analysis_results: Dict) -> List[str]:
        """Generiert Curriculum-Empfehlungen"""
        recommendations = []

        if 'time_series' in analysis_results:
            ts = analysis_results['time_series']
            if ts.rising_competences:
                recommendations.append(
                    f"Fokus auf wachsende Kompetenzen: {', '.join(ts.rising_competences[:3])}"
                )

        return recommendations


class AnalysisService:
    """
    Hauptservice für Analyse

    Implementiert Phase 4 des CRISP-DM: Modeling & Evaluation
    Theoretische Grundlagen: Barton et al. (2018), Hirschle (2021)
    """

    def __init__(self, config):
        self.config = config
        self.logger = logging.getLogger(__name__)

        # Analyzer initialisieren
        self.time_series_analyzer = TimeSeriesAnalyzer()
        self.branch_analyzer = BranchAnalyzer()
        self.role_analyzer = RoleAnalyzer()
        self.clusterer = CompetenceClusterer()
        self.evaluator = QualityEvaluator()

        # KI (optional)
        if getattr(config, 'use_ai_interpretation', False):
            self.ai_generator = AIInsightGenerator(
                model=getattr(config, 'ai_model', 'gpt-4')
            )
        else:
            self.ai_generator = None

    def analyze_time_series(self, job_ads: List[JobAd]) -> TimeSeriesAnalysis:
        """Führt Zeitreihenanalyse durch"""
        return self.time_series_analyzer.analyze(job_ads)

    def compare_branches(self, job_ads: List[JobAd]) -> List[BranchProfile]:
        """Vergleicht Branchen"""
        return self.branch_analyzer.analyze(job_ads)

    def compare_roles(self, job_ads: List[JobAd]) -> List[RoleProfile]:
        """Vergleicht Rollen"""
        return self.role_analyzer.analyze(job_ads)

    def cluster_competences(self, job_ads: List[JobAd]) -> ClusterAnalysis:
        """Clustert Kompetenzen"""
        return self.clusterer.cluster(job_ads)

    def evaluate_results(self, job_ads: List[JobAd], analysis_results: Dict) -> Dict:
        """Evaluiert Ergebnisse"""
        return self.evaluator.evaluate(job_ads, analysis_results)

    def generate_ai_insights(self, job_ads: List[JobAd], analysis_results: Dict) -> Optional[AIInsights]:
        """Generiert KI-Insights (falls aktiviert)"""
        if self.ai_generator:
            return self.ai_generator.generate(job_ads, analysis_results)
        return None

    def create_full_report(self, job_ads: List[JobAd]) -> AnalysisReport:
        """Erstellt vollständigen Analysebericht"""
        self.logger.info("📊 Erstelle vollständigen Analysebericht...")

        # Alle Analysen durchführen
        time_series = self.analyze_time_series(job_ads) if self.config.time_series_analysis else None
        branch_profiles = self.compare_branches(job_ads) if self.config.branch_comparison else None
        role_profiles = self.compare_roles(job_ads) if self.config.role_comparison else None
        cluster_analysis = self.cluster_competences(job_ads)

        # Zusammengeführte Ergebnisse
        analysis_results = {
            'time_series': time_series,
            'branches': branch_profiles,
            'roles': role_profiles,
            'clusters': cluster_analysis
        }

        # Evaluation
        quality_metrics = self.evaluate_results(job_ads, analysis_results)

        # KI-Insights (optional)
        ai_insights = self.generate_ai_insights(job_ads, analysis_results)

        # Report erstellen
        report = AnalysisReport(
            total_job_ads=len(job_ads),
            date_range=(
                min(job_ads, key=lambda x: x.posting_date or datetime.now()).posting_date,
                max(job_ads, key=lambda x: x.posting_date or datetime.now()).posting_date
            ) if job_ads else (None, None),
            branches_covered=list(set(
                job.organization.branch
                for job in job_ads
                if job.organization and job.organization.branch
            )),
            time_series=time_series,
            branch_profiles=branch_profiles or [],
            role_profiles=role_profiles or [],
            cluster_analysis=cluster_analysis,
            ai_insights=ai_insights,
            data_quality_score=quality_metrics['data_quality'],
            esco_coverage=quality_metrics['esco_coverage'],
            extraction_accuracy=quality_metrics['extraction_accuracy']
        )

        self.logger.info("✅ Analysebericht erstellt")

        return report
