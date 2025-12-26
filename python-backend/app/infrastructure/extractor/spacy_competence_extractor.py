import spacy
from spacy.matcher import PhraseMatcher
from typing import List, Optional
from spacy.util import is_package
from app.domain.models import CompetenceDTO
# NEU: Importiere die Factory statt den Manager
from app.application.factories.analysis_result_factory import AnalysisResultFactory
from app.interfaces.interfaces import ICompetenceExtractor

class SpaCyCompetenceExtractor(ICompetenceExtractor):

    def __init__(self, repository=None, manager=None, esco_service=None, domain_rule_service=None, nlp_model=None):
        """Kompatibler Konstruktor: Akzeptiert `repository` (neu), oder die alten Parameter
        `manager`, `esco_service` und `domain_rule_service` (Legacy)."""
        MODEL_NAME = "de_core_news_md"

        # Speichere optionale Services für spätere Nutzung
        self.esco_service = esco_service
        self.domain_rule_service = domain_rule_service
        self.manager = manager

        # Legacy-Adapter: Wenn kein Repository gegeben, versuche aus manager oder esco_service
        if repository is None:
            if manager is not None and hasattr(manager, 'get_all_identifiable_labels'):
                repository = manager
            elif esco_service is not None:
                # Erzeuge einen kleinen Adapter, der die benötigten Methoden bereitstellt
                class _EscoAdapter:
                    def __init__(self, esco):
                        self.esco = esco

                    def get_all_identifiable_labels(self):
                        return list(self.esco.get_esco_target_labels() or [])

                    def get_level(self, term: str):
                        return 3

                    def is_digital_skill(self, term: str):
                        return False

                    # Optional: Methoden zum direkten Zugriff, werden in Extraktor genutzt
                    def get_esco_uri_and_id(self, label: str):
                        return getattr(self.esco, 'get_esco_uri_and_id', lambda x: (None, None, None))(label)

                    def get_esco_mapping(self):
                        return getattr(self.esco, 'get_esco_mapping', lambda: {})()

                repository = _EscoAdapter(esco_service)
            else:
                raise ValueError("SpaCyCompetenceExtractor benötigt ein 'repository' oder 'esco_service' bzw. 'manager'.")

        if nlp_model:
            self.nlp = nlp_model
        else:
            if not is_package(MODEL_NAME):
                spacy.cli.download(MODEL_NAME)
            self.nlp = spacy.load(MODEL_NAME)

        self.repository = repository
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # Patterns aus dem Repository laden (SSoT)
        labels = self.repository.get_all_identifiable_labels()
        if labels:
            # Erzeuge zusätzliche einfache Varianten (z.B. ohne Leerzeichen, ohne Bindestriche)
            ext_labels = set()
            for l in labels:
                ext_labels.add(l)
                ext_labels.add(l.replace(' ', ''))
                ext_labels.add(l.replace('-', ' '))
            # Erzeuge Docs mit make_doc (stabiler als tokenizer.pipe in manchen Env)
            patterns = [self.nlp.make_doc(l) for l in list(ext_labels)]
            self.matcher.add("KNOWLEDGE_BASE", patterns)
            print(f"✅ spaCy Extractor geladen mit {len(ext_labels)} Begriffen (inkl. Varianten).")
        else:
            print("⚠️ spaCy Extractor Warnung: Repository ist leer!")

    def extract_competences(self, text: str, role: str = None) -> List[CompetenceDTO]:
        if not text: return []

        doc = self.nlp(text[:100000]) # Limit protection
        matches = self.matcher(doc)
        results = []
        seen = set()

        # Blacklist (Domain-Rule-Service) - optional
        blacklist = set()
        if self.domain_rule_service is not None:
            try:
                blacklist = set(self.domain_rule_service.get_active_blacklist_keys() or [])
            except Exception:
                blacklist = set()

        # Kandidaten aus Repository cachen (für exakte Abgleiche)
        candidates = []
        try:
            candidates = self.repository.get_all_identifiable_labels() if hasattr(self.repository, 'get_all_identifiable_labels') else []
        except Exception:
            candidates = []

        for _, start, end in matches:
            term = doc[start:end].text
            term_lower = term.lower().strip()

            # Einfache Filter: zu kurze Tokens oder keine Buchstaben ignorieren
            if len(term_lower) < 3 or not any(c.isalpha() for c in term_lower):
                continue

            # Prüfe auf exakten Kandidaten (oder kompakte Variante ohne Leerzeichen)
            term_compact = term_lower.replace(' ', '')
            exact_match = None
            for cand in candidates:
                cand_lower = cand.lower()
                if cand_lower == term_lower or cand_lower.replace(' ', '') == term_compact:
                    exact_match = cand
                    break

            # Wenn kein exakter Kandidat gefunden wurde, überspringe (vermeidet "und Kunden beraten"-Fälle)
            if exact_match is None:
                continue

            if term_lower in seen:
                continue

            # Blacklist prüfen
            if term_lower in blacklist:
                continue

            seen.add(term_lower)

            # Versuche ESCO Informationen zu holen, falls vorhanden
            esco_label = term
            esco_uri = f"custom/{term_lower}"
            esco_group_code = None

            try:
                # Mapping (z.B. 'jira' -> 'Projektmanagement durchführen')
                mapped = None
                if self.esco_service is not None:
                    mapping = getattr(self.esco_service, 'get_esco_mapping', lambda: {})() or {}
                    mapped = mapping.get(term_lower)
                    if mapped:
                        esco_label = mapped

                # Versuche zuerst mit dem (möglicherweise) gemappten Label die URI zu holen
                label_to_lookup = esco_label

                if hasattr(self.repository, 'get_esco_uri_and_id'):
                    uri, _id, group = self.repository.get_esco_uri_and_id(label_to_lookup)
                    if uri:
                        esco_uri = uri
                    if group:
                        esco_group_code = group
                elif self.esco_service is not None:
                    uri, _id, group = getattr(self.esco_service, 'get_esco_uri_and_id', lambda x: (None, None, None))(label_to_lookup)
                    if uri:
                        esco_uri = uri
                    if group:
                        esco_group_code = group

                # Falls der gemappte Label-Lookup nicht erfolgreich war, versuche die Kandidaten aus dem Repository zu finden
                if esco_uri.startswith('custom/'):
                    # Suche nach Labels, die Teil des gefundenen Terms sind (robust gegen Prefix/Suffix)
                    candidates = self.repository.get_all_identifiable_labels() if hasattr(self.repository, 'get_all_identifiable_labels') else []
                    found = None
                    term_norm = term_lower.replace(' ', '')
                    for cand in candidates:
                        cand_norm = cand.lower()
                        if cand_norm in term_lower or cand_norm.replace(' ', '') in term_norm:
                            found = cand
                            break
                    if found:
                        esco_label = found
                        # Hole URI für das gefundene Label
                        try:
                            uri, _id, group = (
                                self.repository.get_esco_uri_and_id(found)
                                if hasattr(self.repository, 'get_esco_uri_and_id')
                                else (None, None, None)
                            )
                            if uri:
                                esco_uri = uri
                            if group:
                                esco_group_code = group
                        except Exception:
                            pass

            except Exception:
                pass

            dto = AnalysisResultFactory.create_competence(
                original_term=term,
                esco_label=esco_label,
                esco_uri=esco_uri,
                level=self.repository.get_level(term),
                is_digital=self.repository.is_digital_skill(term),
                role_context=role,
                confidence=1.0
            )

            # Ergänze optionales Group-Attribut (kompatibel zu alten DTOs)
            if esco_group_code is not None:
                setattr(dto, 'esco_group_code', esco_group_code)

            results.append(dto)

        # Fallback: Verwende einfachen Fuzzy/Substrings-Abgleich über n-grams, falls nichts gefunden wurde
        if not results:
            try:
                from rapidfuzz import fuzz

                labels = self.repository.get_all_identifiable_labels()
                tokens = [t.text for t in self.nlp(text)]
                max_n = min(4, max((len(l.split()) for l in labels), default=1))

                def ngrams(seq, n):
                    return [seq[i:i+n] for i in range(len(seq)-n+1)]

                for label in labels:
                    norm_label = ''.join(label.split()).lower()
                    found = False
                    for n in range(1, max_n+1):
                        for gram in ngrams(tokens, n):
                            joined = ''.join(gram).lower()
                            if norm_label in joined:
                                # Erzeuge DTO ähnlich wie beim Matcher
                                dto = AnalysisResultFactory.create_competence(
                                    original_term=' '.join(gram),
                                    esco_label=label,
                                    esco_uri=f"custom/{label.lower().replace(' ', '_')}",
                                    level=self.repository.get_level(label),
                                    is_digital=self.repository.is_digital_skill(label),
                                    role_context=role
                                )
                                results.append(dto)
                                found = True
                                break
                            # Fuzzy-Check (falls nötig)
                            score = fuzz.partial_ratio(norm_label, joined)
                            if score >= 80:
                                dto = AnalysisResultFactory.create_competence(
                                    original_term=' '.join(gram),
                                    esco_label=label,
                                    esco_uri=f"custom/{label.lower().replace(' ', '_')}",
                                    level=self.repository.get_level(label),
                                    is_digital=self.repository.is_digital_skill(label),
                                    role_context=role
                                )
                                results.append(dto)
                                found = True
                                break
                        if found:
                            break
            except Exception:
                pass

        return results
        return results
