
import json, os, re, unicodedata
_WORD = r"[A-Za-zÄÖÜäöüß\.\-()'/]+"
NEARBY_HINT = re.compile(r"\b(in|bei|am|standort|arbeitsort|office|ort)\b", re.I)
PLZ_RE = re.compile(r"\b(\d{5})\b")
def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.replace("ß","ss")
    return re.sub(r"[^a-z0-9]+","", s.lower()).strip()
class CityIndex:
    def __init__(self, builtin_path: str, external_path: str|None=None):
        self.by_key = {}
        data = []
        if builtin_path and os.path.exists(builtin_path):
            data += json.load(open(builtin_path,"r",encoding="utf-8"))
        if external_path and os.path.exists(external_path):
            for ln in open(external_path,"r",encoding="utf-8",errors="ignore"):
                toks = ln.strip().split("\t")
                if len(toks) < 19: continue
                name, ascii_n, country, admin1, lat, lon, pop = toks[1], toks[2], toks[8], toks[10], toks[4], toks[5], toks[14]
                try:
                    data.append({"name":name,"ascii":ascii_n,"alts":[],"country":country,"admin1":admin1,"lat":float(lat),"lon":float(lon),"population":int(pop) if pop.isdigit() else 0,"postal_prefixes":[]})
                except Exception: pass
        for c in data:
            keys = {_norm(c.get("name","")), _norm(c.get("ascii",""))}
            for a in c.get("alts") or []: keys.add(_norm(a))
            for k in keys:
                if not k: continue
                self.by_key.setdefault(k, []).append(c)
    def lookup(self, token: str):
        return self.by_key.get(_norm(token), [])
def best_candidate(cands, plz=None):
    if not cands: return None
    if plz:
        for c in cands:
            for pref in c.get("postal_prefixes") or []:
                if plz.startswith(pref): return c
    return sorted(cands, key=lambda x: int(x.get("population") or 0), reverse=True)[0]
def detect_city(text: str, gaz: 'CityIndex'):
    m = PLZ_RE.search(text or ""); plz = m.group(1) if m else None
    lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
    for ln in lines[:200]:
        near = bool(NEARBY_HINT.search(ln))
        tokens = re.findall(_WORD, ln)
        for t in tokens:
            cands = gaz.lookup(t)
            if not cands: continue
            chosen = best_candidate(cands, plz if near else None)
            if chosen: return chosen
    return None
def normalize_city_entry(c):
    if not c: return {}
    norm = f"{c.get('country','')}: {c.get('name','')}"
    return {
        "location_city": c.get("name"),
        "location_admin1": c.get("admin1"),
        "location_country": c.get("country"),
        "location_norm": norm,
        "location_geo": {"lat": c.get("lat"), "lon": c.get("lon")}
    }
