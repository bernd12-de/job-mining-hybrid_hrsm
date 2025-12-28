from __future__ import annotations
import re, logging
from typing import List
from models.job_ad import JobAd

class TextCleaner:
    def clean(self, text: str) -> str:
        if not text: return ""
        text = re.sub(r"http[s]?://\S+", "", text)
        text = re.sub(r"\S+@\S+", "", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def calculate_text_quality(self, text: str) -> float:
        if not text: return 0.0
        score = 0.0
        max_score = 5.0
        if 500 <= len(text) <= 10000: score += 1.0
        elif 200 <= len(text) <= 20000: score += 0.5
        if any(w in text.lower() for w in ['und','der','die','das','in','mit','für','and','the','of','to']): score += 1.0
        if any(p in text for p in ['.',',',';' ,':']): score += 1.0
        upper_count = sum(1 for c in text if c.isupper())
        if 0.01 < upper_count/len(text) < 0.5: score += 1.0
        special = sum(1 for c in text if not c.isalnum() and not c.isspace())
        if special/len(text) < 0.2: score += 1.0
        return score / max_score

class DataPreparationService:
    def __init__(self, config=None):
        self.logger = logging.getLogger(__name__)
        self.text_cleaner = TextCleaner()

    def prepare(self, jobs: List[JobAd]) -> List[JobAd]:
        out = []
        for j in jobs:
            j.cleaned_text = self.text_cleaner.clean(j.raw_text)
            j.text_quality = self.text_cleaner.calculate_text_quality(j.cleaned_text)
            out.append(j)
        return out
