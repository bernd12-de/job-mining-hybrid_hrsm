
import os, json
from .ingest import read_any
def _flatten_records(obj):
    if isinstance(obj, dict) and obj.get("_batch"):
        for r in obj["records"]:
            yield from _flatten_records(r)
    else:
        yield obj
def process_documents(inputs, render_js=False):
    recs=[]
    for x in inputs:
        rec=read_any(x, render_js=render_js)
        for r in _flatten_records(rec): recs.append(r)
    return recs
def to_jsonl(records, out_path, mode="w"):
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, mode, encoding="utf-8") as f:
        for r in records: f.write(json.dumps(r, ensure_ascii=False)+"\n")
def load_esco_alias(path="data/esco_alias.json"):
    try: return json.load(open(path,"r",encoding="utf-8"))
    except Exception: return {}
def enrich_with_esco(records, esco_map):
    keys=list(esco_map.keys())
    lowered=[(k.lower(),esco_map[k]) for k in keys]
    for r in records:
        text=(r.get("text") or "").lower(); hits=set()
        for lk,val in lowered[:1000]:
            if lk in text: hits.add(val)
        r.setdefault("fields",{}).setdefault("skills_esco",[])
        r["fields"]["skills_esco"]=sorted(hits)
    return records
