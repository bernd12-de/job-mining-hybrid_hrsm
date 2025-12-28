import json
import os
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Any
from pathlib import Path
import io
import csv

from app.infrastructure.job_classifier import (
    classify_job_role,
    categorize_competence,
    group_jobs_by_category,
    group_skills_by_category,
)

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
    """
    Aggregiert Domains basierend auf Job-Klassifizierung.
    Gruppiert in: Software Dev, Data Science, Product Management, UX/UI, Consulting, etc.
    """
    counter = Counter()
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            title = data.get('title', '')
            role = data.get('job_role', '')
            industry = data.get('industry', '')
            
            # Nutze die neue Job-Klassifizierung
            classification = classify_job_role(title, role, industry)
            category = classification['category']
            sub_category = classification['sub_category']
            
            # Kombiniere Haupt- und Unterkategorie
            if sub_category and sub_category != 'general':
                domain = f"{category.replace('_', ' ').title()} — {sub_category.replace('_', ' ').title()}"
            else:
                domain = category.replace('_', ' ').title()
            
            counter[domain] += 1
        except Exception:
            continue
    return dict(counter)


def aggregate_collection_breakdown() -> Dict[str, int]:
    """
    Zählt Skills nach Kompetenz-Kategorien (eigenes Modell + ESCO):
    - technical_core: Python, Java, Kotlin, C#, etc.
    - frameworks_tools: Spring, Django, FastAPI, React, etc.
    - data_ml: Pandas, NumPy, TensorFlow, NLP, etc.
    - design_ux: Figma, Adobe, Prototyping, UX Research, etc.
    - product_management: Scrum, Jira, Agile, Strategy, etc.
    - soft_skills: Kommunikation, Teamfähigkeit, Leadership, etc.
    - infrastructure: Docker, Kubernetes, AWS, Azure, etc.
    - database: SQL, PostgreSQL, MongoDB, etc.
    - languages: Deutsch, Englisch, etc.
    """
    counter = Counter()
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                collections = c.get('collections', [])
                
                if not label:
                    continue
                
                # Nutze die neue Kompetenz-Kategorisierung
                categorization = categorize_competence(label, collections)
                category = categorization['category']
                
                # Humanize category names
                category_display = category.replace('_', ' ').title()
                counter[category_display] += 1
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
    
    # Neue Features: Job-Gruppierung nach Rolle
    job_groups = aggregate_jobs_by_role()
    skill_groups = aggregate_skills_by_competence_category()

    return {
        'total_jobs': total_jobs,
        'total_skills': total_skills,
        'top_skills': [{'skill': s, 'count': c} for s, c in top_skills],
        'domain_mix': domain_mix,
        'collection_breakdown': collection_breakdown,
        'time_series': time_series,
        'job_groups': job_groups,  # NEU
        'skill_groups': skill_groups,  # NEU
    }


def aggregate_jobs_by_role() -> Dict[str, Dict[str, Any]]:
    """
    Gruppiert alle Jobs nach ihrer Klassifizierung:
    {
        'software_dev': {
            'total': 15,
            'sub_categories': {'frontend': 5, 'backend': 8, 'devops': 2},
            'top_skills': [...]
        },
        'ux_design': {...},
        ...
    }
    """
    groups = {}
    
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            title = data.get('title', '')
            role = data.get('job_role', '')
            industry = data.get('industry', '')
            
            classification = classify_job_role(title, role, industry)
            category = classification['category']
            sub = classification['sub_category']
            
            if category not in groups:
                groups[category] = {
                    'total': 0,
                    'sub_categories': Counter(),
                    'skills_counter': Counter(),
                }
            
            groups[category]['total'] += 1
            if sub and sub != 'unknown':
                groups[category]['sub_categories'][sub] += 1
            
            # Sammle Skills für diese Rolle
            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                if label:
                    groups[category]['skills_counter'][label] += 1
        except Exception:
            continue
    
    # Formatiere für JSON-Output
    result = {}
    for cat, data in groups.items():
        top_skills = data['skills_counter'].most_common(5)
        result[cat] = {
            'total': data['total'],
            'sub_categories': dict(data['sub_categories']),
            'top_skills': [{'skill': s, 'count': c} for s, c in top_skills],
        }
    
    return result


def aggregate_skills_by_competence_category() -> Dict[str, Dict[str, Any]]:
    """
    Gruppiert alle Skills nach ihrer Kompetenz-Kategorie:
    {
        'technical_core': {
            'total': 500,
            'skills': [{'name': 'Python', 'count': 45}, ...],
            'roles': {'software_dev': 40, 'data_science': 8, ...}
        },
        ...
    }
    """
    categories = {}
    
    for p in _iter_job_files():
        try:
            data = json.load(open(p, 'r', encoding='utf-8'))
            title = data.get('title', '')
            role = data.get('job_role', '')
            industry = data.get('industry', '')
            job_cat = classify_job_role(title, role, industry)['category']
            
            for c in data.get('competences', []):
                label = c.get('esco_label') or c.get('original_term')
                if not label:
                    continue
                
                collections = c.get('collections', [])
                categorization = categorize_competence(label, collections)
                cat = categorization['category']
                
                if cat not in categories:
                    categories[cat] = {
                        'total': 0,
                        'skills': Counter(),
                        'roles': Counter(),
                    }
                
                categories[cat]['total'] += 1
                categories[cat]['skills'][label] += 1
                categories[cat]['roles'][job_cat] += 1
        except Exception:
            continue
    
    # Formatiere für JSON-Output
    result = {}
    for cat, data in categories.items():
        top_skills = data['skills'].most_common(10)
        top_roles = data['roles'].most_common(5)
        result[cat] = {
            'total': data['total'],
            'top_skills': [{'skill': s, 'count': c} for s, c in top_skills],
            'top_roles': [{'role': r, 'count': c} for r, c in top_roles],
        }
    
    return result
