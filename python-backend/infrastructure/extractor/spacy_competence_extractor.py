from typing import List, Optional, Tuple, Set
import spacy
from rapidfuzz import process, fuzz
from spacy.matcher import PhraseMatcher

from interfaces import ICompetenceExtractor as CompetenceExtractorInterface
from models import CompetenceDTO
from repositories.hybrid_competence_repository import HybridCompetenceRepository

try:
    NLP = spacy.load("de_core_news_md")
except OSError:
    NLP = spacy.load("de_core_news_sm")

def _lexical_esco_match(skill: str, esco_labels: List[str]) -> Tuple[Optional[str], float]:
    best_match = process.extractOne(
        query=skill.lower().strip(),
        choices=esco_labels,
        scorer=fuzz.token_set_ratio
    )
    if best_match and best_match[1] >= 95:
        return best_match[0], best_match[1]
    return None, 0.0

class SpaCyCompetenceExtractor(CompetenceExtractorInterface):
    def __init__(self, repository: HybridCompetenceRepository):
        self.repository = repository
        self.blacklist = self.repository.get_blacklist()
        self.nlp = NLP

        self.esco_map = self.repository.get_esco_mapping()
        self.esco_target_labels = list(self.repository.get_all_skills())

        self.matcher = None
        if self.nlp:
            self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
            patterns = list(self.nlp.pipe(self.esco_target_labels))
            self.matcher.add("ESCO_SKILLS", patterns)
            print(f"*** ✅ Matcher mit {len(patterns)} Patterns bereit. ***")

    def _get_uri_and_id_from_repo(self, label: str) -> Tuple[Optional[str], Optional[str]]:
        match = next((c for c in self.repository.get_all_competences()
                      if c.preferred_label.lower() == label.lower()), None)
        if match:
            uri = match.esco_uri
            esco_id = uri.split('/')[-1] if '/' in uri else "custom"
            return uri, esco_id
        return None, None

    def extract_competences(self, raw_text: str) -> List[CompetenceDTO]:
        if not self.nlp or not raw_text or len(raw_text) < 5:
            return []

        doc = self.nlp(raw_text)
        competences: List[CompetenceDTO] = []
        found_labels: Set[str] = set()
        normalized_text = raw_text.lower()

        # --- PASS 1: PHRASE MATCHER ---
        if self.matcher:
            matches = self.matcher(doc)
            print(f"DEBUG: Matcher hat {len(matches)} Treffer im Text gefunden.")

            for match_id, start, end in matches:
                span = doc[start:end]
                original_skill = span.text.strip()
                norm_skill = original_skill.lower()

                print(f"DEBUG: Prüfe gefundenen Begriff: '{original_skill}'")

                if norm_skill in self.blacklist:
                    print(f"DEBUG: '{original_skill}' wurde durch Blacklist blockiert.")
                    continue

                if norm_skill in found_labels:
                    continue

                uri, esco_id = self._get_uri_and_id_from_repo(original_skill)
                competences.append(CompetenceDTO(
                    id=esco_id or "unknown",
                    original_term=original_skill,
                    esco_label=original_skill,
                    esco_uri=uri or f"esco/skill/fallback_{norm_skill}",
                    confidence_score=1.0
                ))
                found_labels.add(norm_skill)

        # --- PASS 2: CUSTOM MAPPINGS ---
        for term, esco_label in self.esco_map.items():
            norm_term = term.lower()
            if norm_term in normalized_text and norm_term not in found_labels:
                if norm_term in self.blacklist:
                    continue

                print(f"DEBUG: Mapping-Treffer: '{term}' -> '{esco_label}'")
                uri, esco_id = self._get_uri_and_id_from_repo(esco_label)
                competences.append(CompetenceDTO(
                    id=esco_id or "custom",
                    original_term=term,
                    esco_label=esco_label,
                    esco_uri=uri or f"esco/skill/custom_{esco_label.replace(' ', '_')}",
                    confidence_score=1.0
                ))
                found_labels.add(norm_term)
                found_labels.add(esco_label.lower())

        return competences


    def map_to_esco(self, skill: str) -> str:
        """
        Führt das ESCO-Mapping aus (unverändert)
        """
        #normalized_skill = skill.lower().strip()
        #if normalized_skill in self.esco_map:
         #   return self.esco_map[normalized_skill]

        #esco_match_p1, score_p1 = _lexical_esco_match(skill, self.esco_target_labels)
        #if esco_match_p1:
         #   return esco_match_p1
        print("Map to esco in spacy")
        return skill

