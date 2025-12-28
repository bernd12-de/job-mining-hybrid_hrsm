from __future__ import annotations
import csv, json
from pathlib import Path
from typing import List, Dict
from models.job_ad import JobAd

class ReportingService:
    def export_csv(self, jobs: List[JobAd], path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        keys = [
            'id','file_name','source','date_processed','posting_date','year','month','quarter',
            'job_title','company_name','company_branch','location','job_categories',
            'competences_count','char_count','word_count','extraction_quality'
        ]
        with open(path, "w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys, delimiter=';')
            w.writeheader()
            for j in jobs:
                w.writerow(j.to_dict())

    def export_json(self, jobs: List[JobAd], analysis: Dict, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "meta": {"total_job_ads": len(jobs)},
            "job_ads": [j.to_dict() for j in jobs],
            "analysis": analysis
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
