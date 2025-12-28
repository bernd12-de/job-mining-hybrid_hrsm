
import os, re, json, zipfile, csv, io
from .normalize import parse_date
from .location_gazetteer import CityIndex, detect_city, normalize_city_entry

ROOT = os.path.dirname(os.path.dirname(__file__))
GAZ = CityIndex(os.path.join(ROOT,"resources_cities_de_at_ch.json"),
                 os.path.join(ROOT,"geonames_cities500.txt") if os.path.exists(os.path.join(ROOT,"geonames_cities500.txt")) else None)

# Seed alias (fallback)
ALIAS = {
  "docker": {"id":"esco:docker","label":"Docker","domain":"ICT"},
  "kubernetes": {"id":"esco:kubernetes","label":"Kubernetes","domain":"ICT"},
  "java": {"id":"esco:java","label":"Java","domain":"ICT"},
  "python": {"id":"esco:python","label":"Python","domain":"ICT"},
  "springboot": {"id":"esco:springboot","label":"Spring Boot","domain":"ICT"},
  "rest": {"id":"esco:rest","label":"REST APIs","domain":"ICT"},
  "ci/cd": {"id":"esco:cicd","label":"CI/CD","domain":"ICT"},
  "customer journey": {"id":"esco:customer_journey","label":"Customer Journey","domain":"Marketing"},
  "a/b": {"id":"esco:ab_testing","label":"A/B Testing","domain":"Marketing"},
  "ab testing": {"id":"esco:ab_testing","label":"A/B Testing","domain":"Marketing"},
  "design thinking": {"id":"esco:design_thinking","label":"Design Thinking","domain":"UX"},
  "google analytics 4": {"id":"esco:ga4","label":"Google Analytics 4","domain":"Marketing"},
  "gtm": {"id":"esco:gtm","label":"Google Tag Manager","domain":"Marketing"},
  "wordpress": {"id":"esco:wordpress","label":"WordPress","domain":"ICT"}
}

def load_esco_from_zip(zip_path: str):
    """Try to read ESCO German CSVs from the provided zip. Build label->id dictionary."""
    mapping = {}
    if not os.path.exists(zip_path):
        return mapping
    try:
        with zipfile.ZipFile(zip_path) as z:
            for name in z.namelist():
                if not name.lower().endswith(".csv"): 
                    continue
                with z.open(name) as f:
                    data = f.read().decode("utf-8", errors="ignore")
                # very defensive CSV parse
                reader = csv.reader(io.StringIO(data), delimiter=';', quotechar='"')
                header = next(reader, None)
                # Heuristic: find columns that look like id/label
                if header:
                    cols = {h.lower():i for i,h in enumerate(header)}
                    # guess: conceptUri ; preferredLabel
                    id_idx = None; label_idx = None
                    for i,h in enumerate(header):
                        hl = h.lower()
                        if id_idx is None and ("uri" in hl or "id" in hl): id_idx = i
                        if label_idx is None and ("label" in hl or "bezeichnung" in hl or "preferredlabel" in hl): label_idx = i
                    if id_idx is None or label_idx is None:
                        continue
                    for row in reader:
                        try:
                            cid = row[id_idx].strip()
                            lab = row[label_idx].strip()
                            if not cid or not lab: 
                                continue
                            norm = re.sub(r"[^a-z0-9 ]+","", lab.lower())
                            norm = re.sub(r"\s+"," ", norm).strip()
                            if norm:
                                mapping.setdefault(norm, set()).add(cid)
                        except Exception:
                            pass
        return {k: sorted(v)[0] for k,v in mapping.items()}
    except Exception:
        return {}

ESCO_AUTO = load_esco_from_zip(os.path.join(ROOT, "ESCO dataset - v1.2.0 - classification - de - csv.zip"))

def tokenize(text):
    return re.findall(r"[A-Za-zÄÖÜäöüß0-9\+#/\.]{2,}", text or "")

def extract_esco_skills(text):
    low = (text or "").lower()
    skills = {}
    # alias hits (section-unaware here; simple demo scoring)
    for key, meta in ALIAS.items():
        if key in low:
            sid = meta["id"]
            skills.setdefault(sid, {"id": sid, "label": meta["label"], "domain": meta["domain"], "confidence": 0.6, "sources":[key], "section":"mixed"})
    # full ESCO label match (exact phrase, normalized)
    # naive approach: match long phrases only (>= 3 tokens) to reduce noise
    tokens = tokenize(low)
    text_norm = " ".join(tokens)
    for phrase, cid in ESCO_AUTO.items():
        if phrase.count(" ") >= 2 and (" "+phrase+" ") in (" "+text_norm+" "):
            sid = f"esco:{cid.split('/')[-1]}"
            skills.setdefault(sid, {"id": sid, "label": phrase, "domain": "ESCO", "confidence": 0.7, "sources":[phrase], "section":"mixed"})
    return list(skills.values())

EMPLOYMENT_TYPES = {"vollzeit":"full_time","teilzeit":"part_time","werkstudent":"working_student","praktikum":"internship","befristet":"fixed_term","unbefristet":"permanent","freelance":"freelance","hybrid":"hybrid","remote":"remote"}
DEG_RE = re.compile(r"\b(bachelor|master|diplom|promotion)\b", re.I)
EDU_FIELD_RE = re.compile(r"(wirtschaftsinformatik|informatik|psychologie|bwl|vwl|mathematik|statistik)", re.I)
EXP_RE = re.compile(r"\b(\d{1,2})\s*[-–]?\s*(jahre|jahr)\b", re.I)
TITLE_HINTS = ["consultant","berater","engineer","entwickler","manager","architect","lead","leiter","product owner","requirements engineer","analyst","designer","data","ml","ai","devops","scrum","projektleiter","ux"]
META_HINTS = ["deutschland","vollzeit","teilzeit","remote","hybrid","vor ort","bewerbungen","standort","https://","http://"]

def _looks_like_date(s):
    import re
    return bool(re.search(r"\b(\d{1,2}[./]\d{1,2}[./]\d{2,4}|\d{4}[./-]\d{1,2}[./-]\d{1,2})\b", s))

def _looks_like_url(s): return s.strip().startswith(("http://","https://"))

def guess_company(lines):
    for ln in lines[:20]:
        l = ln.strip()
        if not l or _looks_like_date(l) or _looks_like_url(l): continue
        if len(l)>=2 and not any(x in l.lower() for x in ["stellenanzeige","job","bewerben"]):
            return l.strip()
    return None

def guess_title(lines):
    for ln in lines[:40]:
        low = ln.lower()
        if any(m in low for m in META_HINTS): continue
        if any(h in low for h in TITLE_HINTS) and len(ln)>=6:
            return ln.strip()
    for ln in lines[:30]:
        low = ln.lower()
        if any(m in low for m in META_HINTS): continue
        if ln.strip() and not _looks_like_date(ln): return ln.strip()
    return None

def extract_employment_type(text):
    low = (text or "").lower()
    for k,v in EMPLOYMENT_TYPES.items():
        if k in low: return v
    return None

def extract_education(text):
    deg = None
    m = DEG_RE.search(text or "")
    if m:
        lv = m.group(1).lower()
        mp = {"bachelor":"bachelor","master":"master","diplom":"diploma","promotion":"phd"}
        deg = {"level": mp.get(lv, lv)}
    fld = None
    mf = EDU_FIELD_RE.search(text or "")
    if mf: fld = mf.group(1).capitalize()
    return deg, fld

def extract_experience_years(text):
    m = EXP_RE.search(text or "")
    return int(m.group(1)) if m else None

def infer_occupation(title, text):
    if not title: return None, None
    t = (title+" "+text[:400]).lower()
    if "requirements" in t and ("engineer" in t or "analyst" in t):
        return "ESCO:requirements_engineer","Requirements engineer"
    if "ux" in t and ("lead" in t or "manager" in t or "leiter" in t):
        return "ESCO:ux_manager","UX manager"
    if "java" in t and ("entwickler" in t or "developer" in t):
        return "ESCO:software_developer","Software developer"
    if "product owner" in t:
        return "ESCO:product_owner","Product owner"
    if "consultant" in t or "berater" in t:
        return "ESCO:management_consultant","Management consultant"
    return None, None

def map_industry(company):
    p = os.path.join(ROOT,"company_to_nace.json")
    if os.path.exists(p):
        seed = json.load(open(p,"r",encoding="utf-8"))
        if company in seed: return seed[company], None
    return None, None

def extract_all(text: str, doc_id: str = None):
    lines = [l.strip() for l in (text or "").splitlines() if l.strip()]
    company = guess_company(lines)
    title = guess_title(lines)
    iso, src, prec = parse_date(text)
    city = detect_city(text, GAZ)
    loc_fields = normalize_city_entry(city) if city else {}
    etype = extract_employment_type(text)
    degree, edu_field = extract_education(text)
    exp_years = extract_experience_years(text)
    esco_skills = extract_esco_skills(text)
    occ_id, occ_label = infer_occupation(title, text)
    nace_code, nace_label = map_industry(company)

    out = {
        "id": doc_id or (title or "job"),
        "title": title,
        "company": company,
        "posting_date_iso": iso,
        "posting_date_source": src,
        "posting_date_precision": prec,
        "employment_type": etype,
        "education_field": edu_field,
        "degree_level": degree["level"] if degree else None,
        "experience_years": exp_years,
        "tools": [],
        "methods": [],
        "fields": {"skills_esco": esco_skills},
        "occupation_esco_id": occ_id,
        "occupation_esco_label": occ_label,
        "industry_nace_code": nace_code,
        "industry_label": nace_label
    }
    out.update(loc_fields)
    return out
