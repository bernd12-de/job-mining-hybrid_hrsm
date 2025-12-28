from __future__ import annotations
import yaml, pathlib, logging
from typing import List
from ...domain import JobPosting, SkillRef
from ...registry import registry

log = logging.getLogger("plugin.enrich.skills_rulebased")

@registry.register("enrich.skills_rulebased")
def enrich_skills(items: List[JobPosting], app_cfg, params):
    resources_dir = pathlib.Path(app_cfg.resources_dir)
    aliases = yaml.safe_load((resources_dir / "aliases.yaml").read_text())
    out = []
    for jp in items:
        found = []
        lower = jp.description.lower()
        for canonical, patterns in aliases.items():
            for pat in patterns:
                if pat.lower() in lower:
                    found.append(SkillRef(name=canonical, confidence=0.6))
                    break
        # merge unique by name
        names = set()
        merged = []
        for s in jp.skills + found:
            if s.name not in names:
                names.add(s.name)
                merged.append(s)
        jp.skills = merged
        out.append(jp)
    log.info(f"enrich.skills_rulebased skills_added=ok items={len(out)}")
    return out
