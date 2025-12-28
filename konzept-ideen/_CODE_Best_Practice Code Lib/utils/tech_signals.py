from __future__ import annotations
import re
from typing import List, Set
from ...domain import JobPosting
from ...registry import registry
TOOLS=['python','java','kotlin','docker','kubernetes','sql','pandas','matplotlib','git','aws']
METHODS=['scrum','tdd','ci/cd','agile','microservices']
R_TOKEN=re.compile(r'(?<![A-Za-z])R(?![A-Za-z])')
def _norm_tokens(text:str)->Set[str]:
    low=re.sub(r"[^a-z0-9#+\./\-\s]"," ",text.lower()); return set(low.split())
@registry.register('enrich.tech_signals')
def enrich_tech(items: List[JobPosting], app_cfg, params):
    for jp in items:
        toks=_norm_tokens(jp.description)
        jp.tags.tools=sorted({t for t in TOOLS if t in toks or (t=='r' and R_TOKEN.search(jp.description))})
        jp.tags.methods=sorted({m for m in METHODS if m in toks})
    return items
