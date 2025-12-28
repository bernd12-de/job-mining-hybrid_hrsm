"""
test_pipeline.py
Testet die REFACTORED Architektur Schritt für Schritt
"""

import sys
from pathlib import Path
from datetime import datetime


def print_header(title):
    """Gibt formatierten Header aus"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)


def test_step(step_name):
    """Decorator für Test-Schritte"""
    def decorator(func):
        def wrapper():
            print(f"\n🔍 {step_name}...")
            try:
                result = func()
                print(f"✅ {step_name} - OK")
                return result
            except Exception as e:
                print(f"❌ {step_name} - FEHLER: {e}")
                import traceback
                traceback.print_exc()
                sys.exit(1)
        return wrapper
    return decorator


print_header("TESTE REFACTORED ARCHITEKTUR")


# ============================================================================
# SCHRITT 1: DOMAIN MODELS
# ============================================================================

@test_step("Domain Models importieren")
def test_models():
    from models.competence import Competence
    from models.enums import CompetenceType, JobCategory
    
    # Test Competence Erstellung
    comp = Competence(
        name="Figma",
        category="UX Tools",
        competence_type=CompetenceType.TOOL,
        alternative_labels=["Figma Design"]
    )
    
    assert comp.name == "Figma"
    assert comp.competence_type == CompetenceType.TOOL
    print(f"   ✓ Competence erstellt: {comp.name}")
    
    return comp

test_models()


# ============================================================================
# SCHRITT 2: REPOSITORY LAYER
# ============================================================================

@test_step("Repository Layer importieren")
def test_repository_imports():
    from repositories.base_repository import BaseRepository
    from repositories.competence_repository import CompetenceRepository
    from repositories.adapters.json_adapter import JsonAdapter
    from repositories.adapters.csv_adapter import CsvAdapter
    from repositories.adapters.api_adapter import ApiAdapter
    
    print("   ✓ BaseRepository")
    print("   ✓ CompetenceRepository")
    print("   ✓ JsonAdapter")
    print("   ✓ CsvAdapter")
    print("   ✓ ApiAdapter")
    
    return CompetenceRepository

test_repository_imports()


@test_step("Repository Konfiguration laden")
def test_repository_config():
    from repositories.competence_repository import CompetenceRepository
    
    config_path = "data/competences/config/data_sources.yaml"
    
    if not Path(config_path).exists():
        raise FileNotFoundError(f"Config nicht gefunden: {config_path}")
    
    repo = CompetenceRepository(config_path=config_path)
    print(f"   ✓ Config geladen: {config_path}")
    print(f"   ✓ Adapter initialisiert: {len(repo.adapters)}")
    
    return repo

repo = test_repository_config()


@test_step("Kompetenzen aus Repository laden")
def test_repository_load():
    competences = repo.get_all_competences()
    
    print(f"   ✓ {len(competences)} Kompetenzen geladen")
    
    # Zeige erste 3
    for comp in competences[:3]:
        print(f"      - {comp.name} ({comp.category})")
    
    assert len(competences) > 0, "Keine Kompetenzen geladen!"
    
    return competences

library = test_repository_load()


@test_step("Repository Statistiken")
def test_repository_stats():
    stats = repo.get_statistics()
    
    print(f"   ✓ Total: {stats['total']}")
    print(f"   ✓ Domains: {len(stats['by_domain'])}")
    print(f"   ✓ Kategorien: {len(stats['by_category'])}")
    print(f"   ✓ Mit Alternativen: {stats['with_alternatives']}")
    
    print("\n   Domains:")
    for domain, count in stats['by_domain'].items():
        print(f"      - {domain}: {count}")
    
    return stats

test_repository_stats()


# ============================================================================
# SCHRITT 3: SERVICE LAYER - MATCHER
# ============================================================================

@test_step("Competence Matcher importieren")
def test_matcher_import():
    from services.competence_matcher import CompetenceMatcher
    
    matcher = CompetenceMatcher(
        use_word_boundaries=True,
        case_sensitive=False,
        minimum_confidence=0.7
    )
    
    print("   ✓ Matcher initialisiert")
    print(f"      - Word Boundaries: {matcher.use_word_boundaries}")
    print(f"      - Case Sensitive: {matcher.case_sensitive}")
    print(f"      - Min Confidence: {matcher.minimum_confidence}")
    
    return matcher

matcher = test_matcher_import()


@test_step("Matching-Test durchführen")
def test_matching():
    test_text = """
    Wir suchen einen UX Designer mit Erfahrung in Figma, Sketch und 
    User Research. Kenntnisse in Scrum und Product Backlog sind von Vorteil.
    """
    
    found = matcher.find_matches(test_text, library)
    
    print(f"   ✓ {len(found)} Kompetenzen gefunden:")
    for comp in found:
        print(f"      - {comp.name} ({comp.category})")
    
    assert len(found) > 0, "Keine Kompetenzen gefunden!"
    
    return found

test_matching()


# ============================================================================
# SCHRITT 4: SERVICE LAYER - EXTRACTION SERVICE
# ============================================================================

@test_step("Extraction Service importieren")
def test_extraction_service_import():
    from services.competence_extraction import CompetenceExtractionService
    
    # Test Config
    class TestConfig:
        competence_config = "data/competences/config/data_sources.yaml"
        matching_config = {
            'use_word_boundaries': True,
            'case_sensitive': False,
            'minimum_confidence': 0.7
        }
    
    service = CompetenceExtractionService(TestConfig())
    
    print("   ✓ Service initialisiert")
    print(f"      - Repository: {len(service.competence_library)} Kompetenzen")
    print(f"      - Matcher: Konfiguriert")
    
    return service

extraction_service = test_extraction_service_import()


@test_step("JobAd Extraktion testen")
def test_job_ad_extraction():
    # Erstelle Test JobAd
    from models.job_ad import JobAd
    
    test_job = JobAd(
        id="test_001",
        file_name="test.pdf",
        source="test",
        job_title="Senior UX Designer (m/w/d)",
        raw_text="""
        Senior UX Designer (m/w/d)
        
        Wir suchen einen erfahrenen UX Designer für unser Team.
        
        Anforderungen:
        - Sehr gute Kenntnisse in Figma und Sketch
        - Erfahrung mit User Research und Usability Testing
        - Agile Arbeitsweise (Scrum, Kanban)
        - Product Owner Erfahrung von Vorteil
        - Kommunikationsstärke und Teamfähigkeit
        
        Nice to have:
        - Frontend Development (HTML, CSS, JavaScript)
        - Adobe XD, InVision
        """,
        char_count=450,
        word_count=75
    )
    
    # Extrahiere
    processed = extraction_service.extract_single(test_job)
    
    print(f"   ✓ {len(processed.competences)} Kompetenzen extrahiert:")
    
    # Gruppiere nach Kategorie
    from collections import defaultdict
    by_category = defaultdict(list)
    for comp in processed.competences:
        by_category[comp.category].append(comp.name)
    
    for category, comps in sorted(by_category.items()):
        print(f"\n      {category}:")
        for comp_name in comps:
            print(f"         - {comp_name}")
    
    assert len(processed.competences) > 0, "Keine Kompetenzen extrahiert!"
    
    return processed

test_job_ad_extraction()


# ============================================================================
# SCHRITT 5: BATCH PROCESSING
# ============================================================================

@test_step("Batch Extraktion testen")
def test_batch_extraction():
    from models.job_ad import JobAd
    
    # Erstelle mehrere Test Jobs
    test_jobs = [
        JobAd(
            id=f"test_{i:03d}",
            file_name=f"test_{i}.pdf",
            source="test",
            job_title=f"Test Job {i}",
            raw_text=f"Figma Scrum Product Owner Test {i}",
            char_count=50,
            word_count=10
        )
        for i in range(5)
    ]
    
    # Batch Extraktion
    processed = extraction_service.extract_all(test_jobs)
    
    total_comps = sum(len(job.competences) for job in processed)
    avg_comps = total_comps / len(processed)
    
    print(f"   ✓ {len(processed)} Jobs verarbeitet")
    print(f"   ✓ {total_comps} Kompetenzen gefunden")
    print(f"   ✓ Ø {avg_comps:.1f} Kompetenzen/Job")
    
    return processed

test_batch_extraction()


# ============================================================================
# SCHRITT 6: PERFORMANCE TEST
# ============================================================================

@test_step("Performance Test")
def test_performance():
    import time
    from models.job_ad import JobAd
    
    # Erstelle 50 Jobs
    jobs = [
        JobAd(
            id=f"perf_{i:03d}",
            file_name=f"perf_{i}.pdf",
            source="test",
            job_title=f"Performance Test {i}",
            raw_text="Figma Sketch Scrum Kanban Product Owner User Research " * 5,
            char_count=300,
            word_count=50
        )
        for i in range(50)
    ]
    
    start = time.time()
    processed = extraction_service.extract_all(jobs)
    duration = time.time() - start
    
    jobs_per_sec = len(jobs) / duration
    
    print(f"   ✓ {len(jobs)} Jobs in {duration:.2f}s")
    print(f"   ✓ {jobs_per_sec:.1f} Jobs/Sekunde")
    print(f"   ✓ Ø {duration/len(jobs)*1000:.1f}ms pro Job")
    
    return processed

test_performance()


# ============================================================================
# SCHRITT 7: STATISTIKEN
# ============================================================================

@test_step("Service Statistiken")
def test_service_stats():
    stats = extraction_service.get_extraction_stats()
    
    print("   Library Stats:")
    print(f"      - Total: {stats['library_stats']['total']}")
    print(f"      - Domains: {len(stats['library_stats']['by_domain'])}")
    print(f"      - Kategorien: {len(stats['library_stats']['by_category'])}")
    
    print("\n   Matcher Config:")
    print(f"      - Word Boundaries: {stats['matcher_config']['use_word_boundaries']}")
    print(f"      - Case Sensitive: {stats['matcher_config']['case_sensitive']}")
    print(f"      - Min Confidence: {stats['matcher_config']['minimum_confidence']}")
    
    return stats

test_service_stats()


# ============================================================================
# ABSCHLUSS
# ============================================================================

print_header("✅ ALLE TESTS ERFOLGREICH!")

print("""
📊 ZUSAMMENFASSUNG:

✅ Domain Models - OK
✅ Repository Layer - OK  
✅ Data Adapters - OK
✅ Service Layer - OK
✅ Competence Matcher - OK
✅ Extraction Service - OK
✅ Batch Processing - OK
✅ Performance - OK

🎯 SYSTEM BEREIT FÜR PRODUKTION!

Nächste Schritte:
1. Stellenanzeigen in data/raw/job_ads/ ablegen
2. main.py ausführen für komplette Pipeline

Oder teste einzelne Komponenten:
- Repository: python -c "from repositories.competence_repository import CompetenceRepository; print('OK')"
- Service: python -c "from services.competence_extraction import CompetenceExtractionService; print('OK')"
""")

print("="*80)
