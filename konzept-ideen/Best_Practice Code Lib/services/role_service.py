from __future__ import annotations
import re
from typing import List
from models.job_ad import JobAd, JobCategory

_RULES = [
    (r"\bux\b|\buser experience\b|ux\s*designer|ux\s*consultant", JobCategory.UX_DESIGN),
    (r"\bui\b|interface\s*designer|visual\s*designer", JobCategory.UI_DESIGN),
    (r"\bconsultant\b|berater", JobCategory.CONSULTING),
    (r"\bwerkstudent|working student|student", JobCategory.WORKING_STUDENT),
]

class RoleCategorizer:
    def categorize(self, job: JobAd) -> JobAd:
        text = f"{job.job_title or ''}\n{job.cleaned_text or ''}".lower()
        cats: List[JobCategory] = []
        for pat, cat in _RULES:
            if re.search(pat, text):
                cats.append(cat)
        if not cats and (job.job_title or '').lower().strip():
            cats = [JobCategory.OTHER]
        job.job_categories = list(set(cats)) or job.job_categories
        return job
