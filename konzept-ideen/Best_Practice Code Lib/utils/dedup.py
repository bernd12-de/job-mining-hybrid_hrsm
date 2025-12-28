from __future__ import annotations
from typing import List, Set
import hashlib
from ...domain import JobPosting
from ...registry import registry

def _fp(text:str)->str: return hashlib.sha1(text.encode('utf-8')).hexdigest()
@registry.register('enrich.dedup')
def deduplicate(items: List[JobPosting], app_cfg, params):
    seen: Set[str] = getattr(app_cfg, '_dedup_seen', set())
    out=[]
    for jp in items:
        f=_fp(jp.description)
        if f in seen: continue
        seen.add(f); out.append(jp)
    setattr(app_cfg, '_dedup_seen', seen)
    return out
