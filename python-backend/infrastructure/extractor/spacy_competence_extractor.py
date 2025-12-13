# spacy_competence_extractor.py - FINALE VERSION

from typing import List, Optional, Tuple

import spacy
from rapidfuzz import process, fuzz
from spacy.matcher import PhraseMatcher

from infrastructure.data.esco_skills import get_esco_mapping, get_esco_target_labels, \
    get_esco_uri_and_id  # NEU: URI-Funktion importiert
from interfaces import ICompetenceExtractor as CompetenceExtractorInterface
from models import CompetenceDTO
from repositories.hybrid_competence_repository import HybridCompetenceRepository  # NEU: Import für DI

# --- KERN-FIX 1: DEFINITION DER BLACKLIST ---
GENERIC_SKILLS_BLACKLIST = {
    "kenntnisse", "fähigkeiten", "kommunikation", "deutsch", "englisch",
    "r", "bau", "ski", "sport", "medien", "wissenschaft", "erfahrung",
    "agil", "strategie", "prozess", "management", "analyse", "projektleitung",
    "kunden", "lösung", "team", "technik", "bereich", "verantwortung übernehmen",
    "beratung", "dienstleistungen", "informatik", "digitalisierung",
    "prägen", "datenschutz", "ethik", "gesundheit", "kommunizieren", "agiles"
}
# ----------------------------------------

# --- Lade das deutsche spaCy Modell einmalig ---
try:
    NLP = spacy.load("de_core_news_md")
except OSError:
    try:
        NLP = spacy.load("de_core_news_sm")
    except OSError:
        NLP = None
        print("❌ FEHLER: SpaCy Modell 'de_core_news_sm' oder 'md' nicht gefunden. Bitte installieren Sie es.")


# --------------------------------------------------------------------
# A. Hilfsfunktionen
# --------------------------------------------------------------------
CONFIDENCE_THRESHOLD_P1 = 95

def _lexical_esco_match(skill: str, esco_labels: List[str]) -> Tuple[Optional[str], float]:
    """ Lexikalisches (Fuzzy) Matching als Fallback für Abkürzungen/Synonyme """
    normalized_skill = skill.lower().strip()
    best_match = process.extractOne(
        query=normalized_skill,
        choices=esco_labels,
        scorer=fuzz.token_set_ratio
    )
    if best_match and best_match[1] >= CONFIDENCE_THRESHOLD_P1:
        return best_match[0], best_match[1]
    return None, 0.0

# --------------------------------------------------------------------
# B. Haupt-Extractor-Klasse
# --------------------------------------------------------------------

class SpaCyCompetenceExtractor(CompetenceExtractorInterface):

    # KORRIGIERT: Nimmt das Repository für den Health Check an
    def __init__(self, repository: HybridCompetenceRepository):
        self.repository = repository  # Nötig für den /health/esco-count Endpunkt
        self.nlp = NLP

        # Datencaches werden geladen, um sie später im Lookup zu nutzen
        self.esco_map = get_esco_mapping()
        self.esco_target_labels = get_esco_target_labels()

        # KERN-FIX 2: Initialisierung des PhraseMatchers
        self.matcher = None
        if self.nlp:
            # Stellt sicher, dass nur die offiziellen Labels gematcht werden
            self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
            patterns = [self.nlp.make_doc(text) for text in self.esco_target_labels if text]
            self.matcher.add("ESCO_SKILLS", patterns)
            print(f"*** ✅ PhraseMatcher initialisiert mit {len(patterns)} ESCO-Patterns. ***")


    def map_to_esco(self, skill: str) -> str:
        """
        Führt das ESCO-Mapping aus (unverändert)
        """
        normalized_skill = skill.lower().strip()
        if normalized_skill in self.esco_map:
            return self.esco_map[normalized_skill]

        esco_match_p1, score_p1 = _lexical_esco_match(skill, self.esco_target_labels)
        if esco_match_p1:
            return esco_match_p1

        return skill

    def extract_competences(self, raw_text: str) -> List[CompetenceDTO]:
        """ KERN-LOGIK: Analysiert den Rohtext und extrahiert Kompetenzen. """

        if not self.nlp or not raw_text or len(raw_text) < 50:
            return []
        if not self.matcher:
            print("⚠️ Matcher nicht initialisiert. Rückgabe leer.")
            return []

        doc = self.nlp(raw_text)
        competences: List[CompetenceDTO] = []
        found_skills = set()
        normalized_text = raw_text.lower()

        # --- PASS 1: PHRASE MATCHER (HIGH PRECISION ESCO PHRASEN) ---
        matches = self.matcher(doc)

        for match_id, start, end in matches:
            span = doc[start:end]
            original_skill = span.text.strip()
            normalized_check = original_skill.lower()

            # Blacklist-Filter (Unverändert und funktioniert)
            if normalized_check in GENERIC_SKILLS_BLACKLIST or \
                    (span.text.split()[0].lower() if span.text else "") in GENERIC_SKILLS_BLACKLIST:
                continue

            if original_skill in found_skills:
                continue

            # Hole die ESCO URI und ID
            esco_label = original_skill
            esco_uri, esco_id = get_esco_uri_and_id(esco_label)

            competences.append(
                CompetenceDTO(
                    id=esco_id,
                    original_term=original_skill,
                    esco_label=esco_label,
                    esco_uri=esco_uri or f"esco/skill/FALLBACK_{esco_label.replace(' ', '_')}",
                    confidence_score=1.0,
                    esco_group_code=None
                )
            )
            found_skills.add(original_skill)

        # --- PASS 2: FALLBACK FÜR CUSTOM KEYWORDS/MAPPINGS (JIRA, SCRUM, etc.) ---

        # Durchsuche die Keys unserer Custom Mappings
        for original_term, esco_label in self.esco_map.items():
            if original_term.lower() in normalized_text:

                # Vermeide Duplikate und Blacklist-Treffer
                if original_term in found_skills or original_term.lower() in GENERIC_SKILLS_BLACKLIST:
                    continue

                # Hole die URI und ID für das Ziel-Label (z.B. "Project-Management-Software benutzen")
                esco_uri, esco_id = get_esco_uri_and_id(esco_label)

                competences.append(
                    CompetenceDTO(
                        id=esco_id,
                        original_term=original_term,  # z.B. "jira"
                        esco_label=esco_label,  # z.B. "Project-Management-Software benutzen"
                        esco_uri=esco_uri or f"esco/skill/CUSTOM_{esco_label.replace(' ', '_')}",
                        confidence_score=1.0,
                        esco_group_code=None
                    )
                )
                found_skills.add(original_term)

        # FINALER RETURN der Methode
        return competences

