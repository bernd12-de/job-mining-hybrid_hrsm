"""
Domain Analyzer: Year Comparison Analyzer
Vergleicht Skills über Jahre hinweg
"""

from typing import List, Dict, Optional
from collections import Counter, defaultdict
from domain.models.job_posting import JobPosting


class YearComparisonAnalyzer:
    """
    Analysiert Skill-Trends über Jahre
    
    Features:
    - Jahresvergleiche
    - Neue/verschwundene Skills
    - Wachstum/Rückgang
    - Top Skills pro Jahr
    """
    
    def __init__(self, jobs: List[JobPosting]):
        self.jobs = jobs
        
        # Gruppiere nach Jahr
        self.jobs_by_year = defaultdict(list)
        for job in jobs:
            if job.year:
                self.jobs_by_year[job.year].append(job)
    
    def get_available_years(self) -> List[int]:
        """Verfügbare Jahre (sortiert)"""
        return sorted(self.jobs_by_year.keys())
    
    def get_skills_for_year(self, year: int) -> Counter:
        """Skills für ein Jahr"""
        skills = Counter()
        
        for job in self.jobs_by_year[year]:
            for comp in job.competences:
                skills[comp.name] += 1
        
        return skills
    
    def compare_years(self, year1: int, year2: int) -> Dict:
        """
        Vergleiche zwei Jahre
        
        Returns:
            {
                'year1': int,
                'year2': int,
                'jobs_change': int,
                'new_skills': List[str],
                'lost_skills': List[str],
                'top_growth': List[Tuple[str, float]],
                'top_decline': List[Tuple[str, float]],
            }
        """
        skills1 = self.get_skills_for_year(year1)
        skills2 = self.get_skills_for_year(year2)
        
        # Neue Skills
        new_skills = list(set(skills2.keys()) - set(skills1.keys()))
        
        # Verschwundene Skills
        lost_skills = list(set(skills1.keys()) - set(skills2.keys()))
        
        # Wachstum berechnen
        growth = []
        for skill in set(skills1.keys()) & set(skills2.keys()):
            count1 = skills1[skill]
            count2 = skills2[skill]
            
            # Prozentuales Wachstum
            if count1 > 0:
                growth_pct = ((count2 - count1) / count1) * 100
                growth.append((skill, growth_pct))
        
        # Sortiere nach Wachstum
        growth.sort(key=lambda x: x[1], reverse=True)
        
        return {
            'year1': year1,
            'year2': year2,
            'jobs_year1': len(self.jobs_by_year[year1]),
            'jobs_year2': len(self.jobs_by_year[year2]),
            'jobs_change': len(self.jobs_by_year[year2]) - len(self.jobs_by_year[year1]),
            'new_skills': sorted(new_skills),
            'lost_skills': sorted(lost_skills),
            'top_growth': growth[:10],
            'top_decline': growth[-10:],
        }
    
    def get_comprehensive_report(self) -> Dict:
        """
        Umfassender Bericht über alle Jahre
        
        Returns:
            {
                'total_jobs': int,
                'available_years': List[int],
                'all_time_top_skills': List[Tuple[str, int]],
                'year_comparisons': List[Dict],
                'category_distribution': Dict[str, int],
            }
        """
        # All-time Top Skills
        all_skills = Counter()
        for job in self.jobs:
            for comp in job.competences:
                all_skills[comp.name] += 1
        
        # Jahresvergleiche (Jahr zu Jahr)
        years = self.get_available_years()
        comparisons = []
        
        for i in range(len(years) - 1):
            comp = self.compare_years(years[i], years[i + 1])
            comparisons.append(comp)
        
        # Kategorien-Verteilung
        categories = Counter()
        for job in self.jobs:
            for cat in job.job_categories:
                categories[cat.value] += 1
        
        return {
            'total_jobs': len(self.jobs),
            'available_years': years,
            'all_time_top_skills': all_skills.most_common(20),
            'year_comparisons': comparisons,
            'category_distribution': dict(categories),
        }
    
    def get_year_stats(self, year: int) -> Dict:
        """
        Statistiken für ein Jahr
        
        Returns:
            {
                'year': int,
                'job_count': int,
                'avg_skills': float,
                'top_skills': List[Tuple[str, int]],
                'categories': Dict[str, int],
            }
        """
        jobs = self.jobs_by_year[year]
        
        if not jobs:
            return {
                'year': year,
                'job_count': 0,
                'avg_skills': 0,
                'top_skills': [],
                'categories': {},
            }
        
        # Skills
        skills = self.get_skills_for_year(year)
        
        # Avg Skills pro Job
        total_skills = sum(len(job.competences) for job in jobs)
        avg_skills = total_skills / len(jobs)
        
        # Kategorien
        categories = Counter()
        for job in jobs:
            for cat in job.job_categories:
                categories[cat.value] += 1
        
        return {
            'year': year,
            'job_count': len(jobs),
            'avg_skills': avg_skills,
            'top_skills': skills.most_common(10),
            'categories': dict(categories),
        }
