
#!/usr/bin/env python3
import json, os, collections
def _iter_jsonl(path):
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if not line: continue
            yield json.loads(line)
def aggregate_from_jsonl(path):
    companies = collections.defaultdict(lambda: {"count":0,"ids":set()})
    industries = collections.defaultdict(int)
    trends = collections.defaultdict(int)
    for rec in _iter_jsonl(path):
        c = rec.get("company") or "Unknown"
        companies[c]["count"] += 1
        companies[c]["ids"].add(rec.get("id"))
        if rec.get("industry_nace_code"): industries[rec["industry_nace_code"]] += 1
        iso = rec.get("posting_date_iso")
        if iso: trends[iso[:4]] += 1
    for k in companies: companies[k]["ids"] = sorted(list(companies[k]["ids"]))
    return companies, industries, trends
def aggregate_locations(path):
    locs = collections.defaultdict(int)
    for rec in _iter_jsonl(path):
        norm = rec.get("location_norm")
        if norm: locs[norm] += 1
    return locs
def save_registry(companies, industries, out_dir, locations=None):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir,"companies.json"),"w",encoding="utf-8") as f:
        json.dump(companies, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir,"industries.json"),"w",encoding="utf-8") as f:
        json.dump(industries, f, ensure_ascii=False, indent=2)
    if locations:
        with open(os.path.join(out_dir,"locations.json"),"w",encoding="utf-8") as f:
            json.dump(locations, f, ensure_ascii=False, indent=2)
    with open(os.path.join(out_dir,"trends.json"),"w",encoding="utf-8") as f:
        json.dump(industries, f, ensure_ascii=False, indent=2)
