import spacy
from spacy.matcher import PhraseMatcher # NEU: Der Kern der Lösung
from rapidfuzz import process, fuzz # Wird jetzt weniger genutzt
from typing import List, Optional, Tuple
from core.entities.job_posting import Competence # (Annahme: Korrekter Importpfad)
from core.competence_extraction_interface import CompetenceExtractorInterface
from infrastructure.data.esco_skills import get_esco_mapping, get_esco_target_labels # Datenquelle

# --- Lade das deutsche spaCy Modell einmalig ---
try:
    # Laden des größeren, präziseren Modells, falls verfügbar, sonst small
    NLP = spacy.load("de_core_news_md")
except OSError:
    try:
        NLP = spacy.load("de_core_news_sm")
    except OSError:
        NLP = None
        print("❌ FEHLER: SpaCy Modell 'de_core_news_sm' oder 'md' nicht gefunden. Bitte installieren Sie es.")


# --------------------------------------------------------------------
# A. Hilfsfunktionen (Optimiert)
# --------------------------------------------------------------------

# Der Lexikalische Matcher ist jetzt nur noch für die Nachbearbeitung von Aliassen zuständig
CONFIDENCE_THRESHOLD_P1 = 95  # Erhöhte Schwelle für Lexikalisches Matching

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

# Semantisches Matching wird entfernt, da es teuer ist und die lexikalische Lösung das Problem behebt
# _semantic_esco_match(..) ENTFÄLLT HIER

# --------------------------------------------------------------------
# B. Haupt-Extractor-Klasse (Korrekt implementierter Matcher)
# --------------------------------------------------------------------

class SpaCyCompetenceExtractor(CompetenceExtractorInterface):

    def __init__(self):
        self.nlp = NLP
        self.esco_map = get_esco_mapping()
        self.esco_target_labels = get_esco_target_labels()

        # KERN-FIX: Initialisierung des PhraseMatchers
        self.matcher = None
        if self.nlp:
            self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

            # WICHTIG: Erstellen Sie spaCy Doc-Muster aus den ESCO-Labels (14.569 Phrasen)
            patterns = [self.nlp.make_doc(text) for text in self.esco_target_labels if text]
            self.matcher.add("ESCO_SKILLS", patterns)
            print(f"*** ✅ PhraseMatcher initialisiert mit {len(patterns)} ESCO-Patterns. ***")


    def map_to_esco(self, skill: str) -> str:
        """
        Führt das ESCO-Mapping aus. Wird jetzt primär für Mappings von
        Custom-Keywords und Fallbacks genutzt.
        """

        # 1. Direkter Match (Fast Lane: z.B. SQL -> Datenbanken verwalten)
        normalized_skill = skill.lower().strip()
        if normalized_skill in self.esco_map:
            return self.esco_map[normalized_skill]

        # 2. Lexikalisches Matching (Fall-back für Synonyme/Ähnliches)
        esco_match_p1, score_p1 = _lexical_esco_match(skill, self.esco_target_labels)
        if esco_match_p1:
            return esco_match_p1

        # 3. Kein Match: Gibt den Originalterm als Platzhalter zurück
        return skill


    def extract_competences(self, raw_text: str) -> List[Competence]:
        """ KERN-LOGIK: Analysiert den Rohtext und extrahiert Kompetenzen mit PhraseMatcher. """
        if not self.nlp or not raw_text or len(raw_text) < 50:
            return []
        if not self.matcher:
            print("⚠️ Matcher nicht initialisiert. Rückgabe leer.")
            return []

        doc = self.nlp(raw_text)
        competences: List[Competence] = []
        found_skills = set()

        # --- KERN-FIX: Wenden Sie den PhraseMatcher auf das gesamte Dokument an ---
        matches = self.matcher(doc)

        for match_id, start, end in matches:
            span = doc[start:end]
            original_skill = span.text.strip()

            # Verhindert Duplikate
            if original_skill in found_skills:
                continue

            # Da die Matcher-Patterns aus ESCO-Labels erstellt wurden, ist der Match selbst das Label
            esco_label = original_skill

            competences.append(
                Competence(
                    original_term=original_skill,
                    esco_label=esco_label,
                    # Die URI muss hier aus dem Repositorium geholt werden (Wird im nächsten Schritt oft hinzugefügt)
                    # Für den Test nutzen wir das ESCO-Label als URI-Marker, bis die Logik angepasst ist
                    esco_uri=f"esco/skill/MATCHED_{esco_label.replace(' ', '_')}",
                    confidence_score=1.0,
                    esco_group_code=None
                )
            )
            found_skills.add(original_skill)

        # HINWEIS: Die alte generische Regellogik (UX/Data) wurde entfernt,
        # da der Matcher diese Ergebnisse präziser liefert.

        return competences
