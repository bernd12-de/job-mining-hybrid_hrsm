from __future__ import annotations
import statistics
from typing import List, Dict
from models.job_ad import JobAd

class QualityEvaluator:
    def evaluate(self, jobs: List[JobAd]) -> Dict:
        if not jobs:
            return {"data_quality":0.0,"extraction_accuracy":0.0,"esco_coverage":0.0}
        data_quality = statistics.mean([j.extraction_quality for j in jobs]) if jobs else 0.0
        complete = 0
        total_comp = 0
        with_esco = 0
        for j in jobs:
            total_comp += len(j.competences)
            with_esco += sum(1 for c in j.competences if c.esco_uri)
            if (len(j.competences)>0 and j.organization and j.organization.name!="Unbekannt" and j.location and j.location!="Nicht angegeben"):
                complete += 1
        return {
            "data_quality": data_quality,
            "extraction_accuracy": complete/len(jobs),
            "esco_coverage": (with_esco/total_comp) if total_comp>0 else 0.0
        }
