from __future__ import annotations
import re
from typing import List, Optional
from datetime import datetime
from ...domain import JobPosting, Precision
from ...registry import registry
YEAR_RE=re.compile(r"\b(20\d{2})\b")
@registry.register('enrich.meta_heuristics')
def enrich_meta(items: List[JobPosting], app_cfg, params):
    for jp in items:
        m=YEAR_RE.search(jp.description)
        if m:
            jp.posting_date_precision=Precision.year
            jp.posting_date=datetime(int(m.group(1)),1,1)
        jp.language='de' if any(ch in jp.description for ch in 'äöüÄÖÜß') else 'en'
    return items
