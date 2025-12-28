"""
Domain Analyzer: Remote Trends Analyzer
Analysiert Remote-Arbeits-Trends über Zeit
"""

from typing import List, Dict
from collections import Counter, defaultdict
from domain.models.job_posting import JobPosting


class RemoteTrendsAnalyzer:
    """
    Analysiert Remote-Arbeits-Trends
    
    Features:
    - Remote-Anteil über Jahre
    - Remote nach Kategorie
    - Remote nach Standort
    """
    
    def __init__(self, jobs: List[JobPosting]):
        self.jobs = jobs
        
        # Gruppiere nach Jahr
        self.jobs_by_year = defaultdict(list)
        for job in jobs:
            if job.year:
                self.jobs_by_year[job.year].append(job)
    
    def get_remote_percentage_by_year(self) -> Dict[int, float]:
        """
        Remote-Anteil pro Jahr
        
        Returns:
            {year: percentage}
        """
        percentages = {}
        
        for year, year_jobs in self.jobs_by_year.items():
            total = len(year_jobs)
            remote_count = sum(1 for job in year_jobs if job.remote)
            
            if total > 0:
                percentages[year] = (remote_count / total) * 100
        
        return dict(sorted(percentages.items()))
    
    def get_remote_by_category(self) -> Dict[str, Dict[str, int]]:
        """
        Remote-Jobs nach Kategorie
        
        Returns:
            {category: {'remote': count, 'total': count, 'percentage': float}}
        """
        category_stats = defaultdict(lambda: {'remote': 0, 'total': 0})
        
        for job in self.jobs:
            for cat in job.job_categories:
                category_stats[cat.value]['total'] += 1
                if job.remote:
                    category_stats[cat.value]['remote'] += 1
        
        # Berechne Prozent
        for cat, stats in category_stats.items():
            if stats['total'] > 0:
                stats['percentage'] = (stats['remote'] / stats['total']) * 100
        
        return dict(category_stats)
    
    def get_remote_by_location(self, top_n: int = 10) -> Dict[str, Dict[str, int]]:
        """
        Remote-Jobs nach Standort
        
        Returns:
            {location: {'remote': count, 'total': count, 'percentage': float}}
        """
        location_stats = defaultdict(lambda: {'remote': 0, 'total': 0})
        
        for job in self.jobs:
            if job.location:
                location_stats[job.location]['total'] += 1
                if job.remote:
                    location_stats[job.location]['remote'] += 1
        
        # Berechne Prozent
        for loc, stats in location_stats.items():
            if stats['total'] > 0:
                stats['percentage'] = (stats['remote'] / stats['total']) * 100
        
        # Top N Standorte nach total
        sorted_locs = sorted(location_stats.items(), 
                            key=lambda x: x[1]['total'], 
                            reverse=True)[:top_n]
        
        return dict(sorted_locs)
    
    def get_salary_remote_comparison(self) -> Dict[str, Dict]:
        """
        Vergleiche Gehälter: Remote vs. On-Site
        
        Returns:
            {'remote': {...}, 'onsite': {...}}
        """
        remote_salaries = []
        onsite_salaries = []
        
        for job in self.jobs:
            if job.salary_min and job.salary_max:
                avg_salary = (job.salary_min + job.salary_max) / 2
                
                if job.remote:
                    remote_salaries.append(avg_salary)
                else:
                    onsite_salaries.append(avg_salary)
        
        def calc_stats(salaries):
            if not salaries:
                return {'count': 0, 'avg': 0, 'min': 0, 'max': 0}
            
            return {
                'count': len(salaries),
                'avg': sum(salaries) / len(salaries),
                'min': min(salaries),
                'max': max(salaries),
            }
        
        return {
            'remote': calc_stats(remote_salaries),
            'onsite': calc_stats(onsite_salaries),
        }
    
    def get_report(self) -> Dict:
        """Umfassender Remote-Trends Report"""
        return {
            'by_year': self.get_remote_percentage_by_year(),
            'by_category': self.get_remote_by_category(),
            'by_location': self.get_remote_by_location(),
            'salary_comparison': self.get_salary_remote_comparison(),
            'total_jobs': len(self.jobs),
            'total_remote': sum(1 for job in self.jobs if job.remote),
            'remote_percentage_overall': (sum(1 for job in self.jobs if job.remote) / len(self.jobs) * 100) if self.jobs else 0,
        }
