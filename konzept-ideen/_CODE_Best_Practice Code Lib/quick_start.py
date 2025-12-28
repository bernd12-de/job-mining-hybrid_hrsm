"""
quick_start.py
Schnellstart für die REFACTORED Architektur
"""

from pathlib import Path
import sys


def check_structure():
    """Prüft ob Verzeichnisstruktur vorhanden ist"""
    print("🔍 Prüfe Projektstruktur...\n")
    
    required_dirs = {
        'data/competences/domains': 'Domain-Daten (JSON)',
        'data/competences/config': 'Konfiguration',
        'data/raw/job_ads': 'Stellenanzeigen (PDF/DOCX)',
        'models': 'Domain Models',
        'repositories': 'Data Access Layer',
        'repositories/adapters': 'Data Adapters',
        'services': 'Business Logic Layer',
    }
    
    missing = []
    for dir_path, description in required_dirs.items():
        path = Path(dir_path)
        if path.exists():
            print(f"✅ {dir_path:<35} ({description})")
        else:
            print(f"❌ {dir_path:<35} FEHLT!")
            missing.append(dir_path)
    
    return missing


def check_files():
    """Prüft ob wichtige Dateien vorhanden sind"""
    print("\n🔍 Prüfe wichtige Dateien...\n")
    
    required_files = {
        'data/competences/config/data_sources.yaml': 'Config',
        'data/competences/domains/ux_design.json': 'UX Domain',
        'repositories/competence_repository.py': 'Repository',
        'services/competence_extraction.py': 'Extraction Service',
        'services/competence_matcher.py': 'Matcher',
    }
    
    missing = []
    for file_path, description in required_files.items():
        path = Path(file_path)
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {file_path:<50} ({size:>6} bytes)")
        else:
            print(f"❌ {file_path:<50} FEHLT!")
            missing.append(file_path)
    
    return missing


def check_job_ads():
    """Prüft ob Stellenanzeigen vorhanden sind"""
    print("\n🔍 Prüfe Stellenanzeigen...\n")
    
    data_dir = Path("data/raw/job_ads")
    if not data_dir.exists():
        print(f"❌ Verzeichnis fehlt: {data_dir}")
        return False
    
    files = list(data_dir.glob("*.pdf")) + list(data_dir.glob("*.docx"))
    
    if not files:
        print(f"❌ Keine PDF/Word-Dateien in: {data_dir}")
        return False
    
    print(f"✅ Gefunden: {len(files)} Stellenanzeigen")
    for f in files[:5]:  # Zeige erste 5
        print(f"   - {f.name}")
    if len(files) > 5:
        print(f"   ... und {len(files) - 5} weitere")
    
    return True


def test_imports():
    """Testet ob alle Module importierbar sind"""
    print("\n🔍 Teste Imports...\n")
    
    tests = [
        ("Models", "from models.competence import Competence"),
        ("Models", "from models.enums import CompetenceType"),
        ("Repository", "from repositories.competence_repository import CompetenceRepository"),
        ("Adapters", "from repositories.adapters.json_adapter import JsonAdapter"),
        ("Services", "from services.competence_extraction import CompetenceExtractionService"),
        ("Services", "from services.competence_matcher import CompetenceMatcher"),
    ]
    
    failed = []
    for category, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {category:<12} OK")
        except Exception as e:
            print(f"❌ {category:<12} FEHLER: {e}")
            failed.append((category, str(e)))
    
    return failed


def quick_test():
    """Führt Quick-Test der Pipeline durch"""
    print("\n🚀 Starte Quick-Test...\n")
    
    try:
        from repositories.competence_repository import CompetenceRepository
        from services.competence_matcher import CompetenceMatcher
        
        # Test Repository
        print("1. Repository lädt Kompetenzen...")
        repo = CompetenceRepository("data/competences/config/data_sources.yaml")
        library = repo.get_all_competences()
        print(f"   ✅ {len(library)} Kompetenzen geladen")
        
        # Test Matcher
        print("\n2. Matcher findet Kompetenzen...")
        matcher = CompetenceMatcher()
        test_text = "Erfahrung mit Figma, Sketch, Scrum und Product Backlog"
        found = matcher.find_matches(test_text, library)
        print(f"   ✅ {len(found)} Kompetenzen gefunden:")
        for comp in found:
            print(f"      - {comp.name} ({comp.category})")
        
        # Statistiken
        print("\n3. Statistiken:")
        stats = repo.get_statistics()
        print(f"   Total: {stats['total']} Kompetenzen")
        print(f"   Domains: {len(stats['by_domain'])}")
        print(f"   Kategorien: {len(stats['by_category'])}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False


def quick_start():
    """Hauptfunktion für Schnellstart"""
    
    print("="*80)
    print("🚀 JOB MINING - QUICK START (REFACTORED ARCHITECTURE)")
    print("="*80)
    print()
    
    # 1. Struktur prüfen
    missing_dirs = check_structure()
    
    # 2. Dateien prüfen
    missing_files = check_files()
    
    # 3. Job Ads prüfen
    has_job_ads = check_job_ads()
    
    # 4. Imports testen
    failed_imports = test_imports()
    
    # Zusammenfassung
    print("\n" + "="*80)
    print("📋 ZUSAMMENFASSUNG")
    print("="*80)
    
    errors = []
    
    if missing_dirs:
        errors.append(f"❌ {len(missing_dirs)} Verzeichnisse fehlen")
        print(f"\n❌ Fehlende Verzeichnisse:")
        for d in missing_dirs:
            print(f"   mkdir -p {d}")
    
    if missing_files:
        errors.append(f"❌ {len(missing_files)} Dateien fehlen")
        print(f"\n❌ Fehlende Dateien - bitte aus refactored_architecture.tar.gz entpacken!")
    
    if not has_job_ads:
        errors.append("❌ Keine Stellenanzeigen vorhanden")
        print(f"\n❌ Bitte Stellenanzeigen in data/raw/job_ads/ ablegen!")
    
    if failed_imports:
        errors.append(f"❌ {len(failed_imports)} Import-Fehler")
        print(f"\n❌ Import-Fehler:")
        for cat, err in failed_imports:
            print(f"   {cat}: {err}")
    
    if errors:
        print("\n" + "="*80)
        print("❌ SETUP NICHT VOLLSTÄNDIG")
        print("="*80)
        print("\n📝 Nächste Schritte:")
        print("1. Fehlende Verzeichnisse erstellen")
        print("2. Fehlende Dateien aus refactored_architecture.tar.gz entpacken")
        print("3. Stellenanzeigen in data/raw/job_ads/ ablegen")
        print("4. quick_start.py erneut ausführen")
        return False
    
    # Alles OK - Quick Test
    print("\n✅ SETUP VOLLSTÄNDIG!\n")
    
    if quick_test():
        print("\n" + "="*80)
        print("✅ SYSTEM BEREIT!")
        print("="*80)
        print("\n🎯 Starte jetzt die Haupt-Pipeline:")
        print("   python main.py")
        print("\nOder teste einzelne Komponenten:")
        print("   python test_pipeline.py")
        return True
    else:
        print("\n" + "="*80)
        print("⚠️  QUICK TEST FEHLGESCHLAGEN")
        print("="*80)
        print("\nBitte Fehler beheben und erneut versuchen.")
        return False


if __name__ == "__main__":
    success = quick_start()
    sys.exit(0 if success else 1)
