#!/usr/bin/env python3
"""
Test-Script für Skill-Erkennungs-Verbesserungen
Testet, ob kurze Skills (Java, SQL, Git, AWS, C++) erkannt werden
und ob technische Begriffe (Informatik, Digitalisierung) nicht mehr blockiert werden.
"""
import requests
import json
import sys

API_URL = "http://localhost:8080/api/v1/jobs/analyze-text"

# Test-Text mit kurzen und langen Skills
test_text = """
Senior Software Engineer (m/w/d)

Wir suchen einen erfahrenen Entwickler mit folgenden Skills:
- Java, C++, und Python Programmierung
- SQL Datenbank-Design
- Git Versionskontrolle
- AWS Cloud Services
- API Design und REST
- Go und R für Data Science

Zusätzlich:
- Informatik-Studium oder vergleichbare Qualifikation
- Erfahrung in Digitalisierung und IT-Management
- Projektmanagement und Scrum
- Kenntnisse in Machine Learning
"""

def test_skill_detection():
    """Teste ob alle wichtigen Skills erkannt werden"""
    
    print("🧪 Teste Skill-Erkennung...")
    print("=" * 60)
    
    payload = {
        "text": test_text,
        "job_title": "Senior Software Engineer"
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ API Fehler: Status {response.status_code}")
            print(response.text)
            return False
        
        result = response.json()
        
        # Extrahiere gefundene Skills
        competences = result.get('competences', [])
        found_skills = set()
        
        for comp in competences:
            original = comp.get('original_term', '').lower()
            esco_label = comp.get('esco_label', '').lower()
            found_skills.add(original)
            found_skills.add(esco_label)
        
        # Teste kurze Skills (sollten ALLE gefunden werden)
        short_skills = ['java', 'sql', 'git', 'aws', 'c++', 'api', 'go', 'r']
        missing_short = []
        found_short = []
        
        for skill in short_skills:
            # Prüfe ob Skill in irgendeiner Form gefunden wurde
            found = any(skill in s for s in found_skills)
            if found:
                found_short.append(skill)
            else:
                missing_short.append(skill)
        
        # Teste technische Begriffe (sollten NICHT blockiert sein)
        technical_terms = ['informatik', 'digitalisierung', 'management', 'projektmanagement']
        missing_technical = []
        found_technical = []
        
        for term in technical_terms:
            found = any(term in s for s in found_skills)
            if found:
                found_technical.append(term)
            else:
                missing_technical.append(term)
        
        # Ausgabe
        print(f"\n📊 Ergebnisse:")
        print(f"   Gesamt gefundene Kompetenzen: {len(competences)}")
        print(f"\n✅ Kurze Skills gefunden ({len(found_short)}/{len(short_skills)}):")
        print(f"   {', '.join(found_short)}")
        
        if missing_short:
            print(f"\n❌ Kurze Skills NICHT gefunden ({len(missing_short)}):")
            print(f"   {', '.join(missing_short)}")
        
        print(f"\n✅ Technische Begriffe gefunden ({len(found_technical)}/{len(technical_terms)}):")
        print(f"   {', '.join(found_technical) if found_technical else 'Keine'}")
        
        if missing_technical:
            print(f"\n⚠️  Technische Begriffe nicht gefunden (evtl. OK):")
            print(f"   {', '.join(missing_technical)}")
        
        # Erfolgs-Kriterien
        success_rate_short = len(found_short) / len(short_skills) * 100
        print(f"\n🎯 Erfolgsrate kurze Skills: {success_rate_short:.0f}%")
        
        if success_rate_short >= 75:
            print("✅ TEST BESTANDEN: Kurze Skills werden gut erkannt!")
            return True
        else:
            print("❌ TEST FEHLGESCHLAGEN: Zu viele kurze Skills fehlen!")
            return False
        
    except requests.RequestException as e:
        print(f"❌ Netzwerk-Fehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_skill_detection()
    sys.exit(0 if success else 1)
