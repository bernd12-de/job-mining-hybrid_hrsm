import json
import os
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
from pathlib import Path
import io
import csv

BATCH_RESULTS_DIR = Path(os.getenv('BATCH_RESULTS_DIR', 'data/exports/batch_results'))


def _iter_job_files() -> List[Path]:
    if not BATCH_RESULTS_DIR.exists():
        return []
    return [p for p in BATCH_RESULTS_DIR.iterdir() if p.suffix.lower() == '.json' and p.name != 'summary.json']


def load_summary() -> Dict[str, Any]:
    summary_path = BATCH_RESULTS_DIR / 'summary.json'
    if not summary_path.exists():
        return {}
    with open(summary_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def _should_include_in_top_skills(collections: List[str]) -> bool:
    """
    Filtert Skills nach ESCO-Collections:
    - ✅ Digital, Research → Wertvolle, spezifische Skills
    - ❌ Language, Transversal → Generic, zu breit für Top-Skills
    """
    if not collections:
        return True  # Occupation-specific Skills ohne Collection → behalten
    
    # Exclude wenn NUR Language oder Transversal
    if set(collections).issubset({'language', 'transversal'}):
        return False
    
    return True


def aggregate_top_skills(top_n: int = 10) -> List[Tuple[str, int]]:
    """Aggregiert Top Skills, filtert nach ESCO-Collections (keine Sprachen/Generic)."""
    counter = Counter()
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                collections = c.get('collections', [])
                
                if label and _should_include_in_top_skills(collections):
                    counter[label] += 1
        except Exception:
            continue
    return counter.most_common(top_n)


def aggregate_domain_mix() -> Dict[str, int]:
    """Aggregiert Domains basierend auf Rolle + Industrie Kombination"""
    counter = Counter()
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            role = data.get('job_role', '').strip()
            industry = data.get('industry', '').strip()
            
            # Kombiniere Rolle + Industrie für bessere Segmentierung
            if role and industry:
                domain = f"{role} / {industry}"
            elif role:
                domain = role
            elif industry:
                domain = industry
            else:
                domain = 'Unbekannt'
            
            counter[domain] += 1
        except Exception:
            continue
    return dict(counter)


def aggregate_collection_breakdown() -> Dict[str, int]:
    """
    Zählt Skills nach ESCO-Collections:
    - digital: Tech-Skills (Python, Cloud, etc.)
    - research: Forschungs-Skills
    - transversal: Soft Skills (Kommunikation, Teamarbeit)
    - language: Sprachen (Deutsch, Englisch, etc.)
    - occupation: Berufsspezifische Skills (ohne Collection)
    """
    counter = Counter()
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            for c in data.get('competences', []):
                collections = c.get('collections', [])
                
                if not collections:
                    # Kein Collection → Occupation-specific
                    counter['Occupation-Specific'] += 1
                elif 'digital' in collections:
                    counter['Digital'] += 1
                elif 'research' in collections:
                    counter['Research'] += 1
                elif 'language' in collections:
                    counter['Language'] += 1
                elif 'transversal' in collections:
                    counter['Transversal'] += 1
                else:
                    counter['Other'] += 1
        except Exception:
            continue
    return dict(counter)


def aggregate_time_series_for_skills(skills: List[str]) -> Dict[str, Dict[str, int]]:
    # return {skill: {year: count}}
    result = {s: defaultdict(int) for s in skills}
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            date = data.get('posting_date')
            if not date:
                continue
            year = date.split('-')[0]
            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                if label in result:
                    result[label][year] += 1
        except Exception:
            continue
    # convert defaultdicts to dicts
    return {skill: dict(year_counts) for skill, year_counts in result.items()}


def generate_csv_report() -> io.BytesIO:
    # produce a simple CSV with one row per job and flattened competence labels
    rows = []
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            competences = [c.get('esco_label') or c.get('original_term') for c in data.get('competences', [])]
            rows.append({
                'title': data.get('title'),
                'job_role': data.get('job_role'),
                'region': data.get('region'),
                'industry': data.get('industry'),
                'posting_date': data.get('posting_date'),
                'skills_count': len(competences),
                'skills': '|'.join(competences)
            })
        except Exception:
            continue

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=['title', 'job_role', 'region', 'industry', 'posting_date', 'skills_count', 'skills'], delimiter=',')
    writer.writeheader()
    for r in rows:
        writer.writerow(r)

    bio = io.BytesIO()
    bio.write(output.getvalue().encode('utf-8'))
    bio.seek(0)
    return bio


def generate_pdf_report() -> io.BytesIO:
    """Generiert einen einfachen PDF-Report mit den Dashboard-Metriken (minimal, für Prototyp)."""
    metrics = build_dashboard_metrics(top_n=10)

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except Exception as e:
        # Wenn reportlab nicht verfügbar ist, raise klaren Fehler
        raise RuntimeError("reportlab ist nicht installiert. Bitte 'reportlab' in requirements.txt hinzufügen.")

    bio = io.BytesIO()
    c = canvas.Canvas(bio, pagesize=A4)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, 800, "Job Mining — Report")
    c.setFont("Helvetica", 10)
    c.drawString(50, 780, f"Total Jobs: {metrics.get('total_jobs', 0)}")
    c.drawString(50, 765, f"Total Skills: {metrics.get('total_skills', 0)}")

    y = 740
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y, "Top Skills:")
    y -= 18
    c.setFont("Helvetica", 10)
    for s in metrics.get('top_skills', []):
        c.drawString(60, y, f"{s.get('skill')}: {s.get('count')}")
        y -= 14
        if y < 60:
            c.showPage()
            y = 800
    c.showPage()
    c.save()
    bio.seek(0)
    return bio


def build_dashboard_metrics(top_n: int = 10) -> Dict[str, Any]:
    summary = load_summary()
    total_jobs = summary.get('processed') or 0
    total_skills = summary.get('skills_total') or 0
    top_skills = aggregate_top_skills(top_n=top_n)
    domain_mix = aggregate_domain_mix()
    collection_breakdown = aggregate_collection_breakdown()
    time_series = aggregate_time_series_for_skills([s for s, _ in top_skills])

    return {
        'total_jobs': total_jobs,
        'total_skills': total_skills,
        'top_skills': [{'skill': s, 'count': c} for s, c in top_skills],
        'domain_mix': domain_mix,
        'collection_breakdown': collection_breakdown,
        'time_series': time_series
    }
