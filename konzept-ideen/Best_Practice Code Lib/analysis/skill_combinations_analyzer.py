"""
Domain Analyzer: Skill Combinations Analyzer
Analysiert welche Skills zusammen vorkommen
"""

from typing import List, Dict, Tuple
from collections import Counter, defaultdict
from domain.models.job_posting import JobPosting


class SkillCombinationsAnalyzer:
    """
    Analysiert Skill-Kombinationen
    
    Features:
    - Häufigste Skill-Paare
    - Skill-Cluster (was kommt zusammen vor?)
    - "Wenn X, dann oft auch Y"
    """
    
    def __init__(self, jobs: List[JobPosting]):
        self.jobs = jobs
    
    def get_top_pairs(self, n: int = 20) -> List[Tuple[str, str, int]]:
        """
        Finde häufigste Skill-Paare
        
        Returns:
            List[(skill1, skill2, count)]
        """
        pairs = Counter()
        
        for job in self.jobs:
            skills = [c.name for c in job.competences]
            
            # Alle Paare bilden
            for i, skill1 in enumerate(skills):
                for skill2 in skills[i+1:]:
                    # Sortiere alphabetisch für Konsistenz
                    pair = tuple(sorted([skill1, skill2]))
                    pairs[pair] += 1
        
        # Top N Paare
        top_pairs = []
        for (skill1, skill2), count in pairs.most_common(n):
            top_pairs.append((skill1, skill2, count))
        
        return top_pairs
    
    def get_skill_associations(self, skill_name: str, min_support: int = 3) -> List[Tuple[str, int, float]]:
        """
        Finde Skills die oft mit einem bestimmten Skill vorkommen
        
        Args:
            skill_name: Skill nach dem gesucht wird
            min_support: Minimum Anzahl Vorkommen
            
        Returns:
            List[(other_skill, count, confidence)]
            confidence = P(other_skill | skill_name)
        """
        # Zähle wie oft skill_name vorkommt
        skill_count = sum(1 for job in self.jobs 
                         if any(c.name == skill_name for c in job.competences))
        
        if skill_count == 0:
            return []
        
        # Zähle Co-Occurrences
        co_occurrences = Counter()
        
        for job in self.jobs:
            skill_names = [c.name for c in job.competences]
            
            if skill_name in skill_names:
                for other_skill in skill_names:
                    if other_skill != skill_name:
                        co_occurrences[other_skill] += 1
        
        # Berechne Confidence und filtere
        results = []
        for other_skill, count in co_occurrences.items():
            if count >= min_support:
                confidence = count / skill_count
                results.append((other_skill, count, confidence))
        
        # Sortiere nach Confidence
        results.sort(key=lambda x: x[2], reverse=True)
        
        return results
    
    def get_skill_clusters(self, min_cluster_size: int = 3) -> Dict[str, List[str]]:
        """
        Finde Skill-Cluster basierend auf Co-Occurrence
        
        Returns:
            Dict[cluster_name, List[skills]]
        """
        # Vereinfachtes Clustering: Finde Skills die oft zusammen vorkommen
        clusters = defaultdict(set)
        
        # Für jeden Skill, finde top Assoziationen
        all_skills = set()
        for job in self.jobs:
            for comp in job.competences:
                all_skills.add(comp.name)
        
        for skill in all_skills:
            associations = self.get_skill_associations(skill, min_support=2)
            
            if len(associations) >= min_cluster_size - 1:
                # Erstelle Cluster-Name aus Top Skill
                cluster_key = skill
                clusters[cluster_key].add(skill)
                
                for other_skill, _, confidence in associations[:min_cluster_size]:
                    if confidence > 0.3:  # Mind. 30% Co-Occurrence
                        clusters[cluster_key].add(other_skill)
        
        # Nur Cluster mit mind. min_cluster_size Skills
        filtered_clusters = {
            k: list(v) for k, v in clusters.items() 
            if len(v) >= min_cluster_size
        }
        
        return filtered_clusters
    
    def get_report(self) -> Dict:
        """
        Umfassender Report über Skill-Kombinationen
        """
        top_pairs = self.get_top_pairs(10)
        
        # Top 5 Skills und ihre Assoziationen
        top_skills_overall = Counter()
        for job in self.jobs:
            for comp in job.competences:
                top_skills_overall[comp.name] += 1
        
        associations_report = {}
        for skill_name, _ in top_skills_overall.most_common(5):
            assocs = self.get_skill_associations(skill_name, min_support=2)
            associations_report[skill_name] = assocs[:5]
        
        # Cluster
        clusters = self.get_skill_clusters()
        
        return {
            'top_pairs': top_pairs,
            'skill_associations': associations_report,
            'clusters': clusters,
        }
