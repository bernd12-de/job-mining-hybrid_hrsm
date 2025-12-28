import os
import time
import logging
import spacy
from spacy.matcher import PhraseMatcher
from typing import List, Optional
from spacy.util import is_package
from app.domain.models import CompetenceDTO
# NEU: Importiere die Factory statt den Manager
from app.application.factories.analysis_result_factory import AnalysisResultFactory
from app.interfaces.interfaces import ICompetenceExtractor

logger = logging.getLogger(__name__)

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
        
        # ✅ BEST PRACTICE: Disable unused pipes for faster processing
        # We only need tokenizer + PhraseMatcher, not tagger/parser/ner
        disabled_pipes = []
        for pipe_name in ['tagger', 'parser', 'ner']:
            if pipe_name in self.nlp.pipe_names:
                disabled_pipes.append(pipe_name)
        
        if disabled_pipes:
            self.nlp.disable_pipes(*disabled_pipes)
            logger.info(f"⚡ spaCy Performance: Disabled pipes {disabled_pipes}")

        # ✅ Modell- und Pipeline-Infos einmalig loggen
        try:
            model_name = getattr(self.nlp, 'meta', {}).get('name', MODEL_NAME)
            model_version = getattr(self.nlp, 'meta', {}).get('version', 'unknown')
            logger.info(f"🧠 spaCy Model: {model_name} v{model_version}")
            logger.info(f"🧩 Active pipes: {list(self.nlp.pipe_names)}")
        except Exception:
            pass

        # Kompatibilitäts-Alias: 'extract' wird in der Pipeline erwartet
        def _extract_alias(doc_or_text):
            if isinstance(doc_or_text, str):
                return self.extract_competences(doc_or_text)
            else:
                return self.extract_competences(doc_or_text.text)

        self.extract = _extract_alias

        self.repository = repository
        self.matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        # Patterns aus dem Repository laden (SSoT)
        labels = self.repository.get_all_identifiable_labels()
        if labels:
            # Nur Labels verwenden, die mindestens 2 Zeichen sind und keine zu generischen Wörter sind
            generic_words = {
                # Deutsche Stopwords
                'und', 'oder', 'der', 'die', 'das', 'den', 'des', 'dem', 'ein', 'eine', 'einen', 
                'einer', 'einem', 'eines', 'von', 'zu', 'im', 'am', 'ist', 'sind', 'war', 'waren',
                # Englische Stopwords (verhindert LinkedIn-UI-Extraktion)
                'the', 'a', 'an', 'of', 'in', 'on', 'at', 'for', 'with', 'is', 'are', 'was', 'were',
                'be', 'been', 'being', 'our', 'your', 'their', 'this', 'that', 'these', 'those',
                'to', 'from', 'by', 'as', 'or', 'and', 'but', 'if', 'so', 'we', 'you', 'they',
                # UI-Fragmente (LinkedIn-Artifact-Prevention)
                'button', 'click', 'menu', 'link', 'page', 'site', 'firm', 'interaction', 'position'
            }
            filtered_labels = [l for l in labels if len(l) >= 2 and l.lower() not in generic_words]  # ✅ Erlaubt R, C, Go
            
            # PhraseMatcher Chunking: Verarbeite alle Skills in Batches
            # spaCy PhraseMatcher hat kein hartes 10k Limit mehr in neueren Versionen,
            # aber wir chunken trotzdem für bessere Performance
            CHUNK_SIZE = 5000
            total_patterns = 0
            num_chunks = 0
            for i in range(0, len(filtered_labels), CHUNK_SIZE):
                chunk = filtered_labels[i:i+CHUNK_SIZE]
                patterns = [self.nlp.make_doc(l) for l in chunk]
                # Verwende eindeutige IDs für chunks
                chunk_id = f"KNOWLEDGE_BASE_{i//CHUNK_SIZE}"
                self.matcher.add(chunk_id, patterns)
                total_patterns += len(patterns)
                num_chunks += 1
            
            # ✅ DETAILLIERTES LOGGING (für objektiven Nachweis des Chunking)
            logger.info(f"✅ spaCy Extractor geladen:")
            logger.info(f"   📊 Labels total: {len(labels)}")
            logger.info(f"   🔍 Nach Filter: {len(filtered_labels)}")
            logger.info(f"   📦 Chunks: {num_chunks}")
            logger.info(f"   ✅ Patterns geladen: {total_patterns}")
            logger.info(f"   💡 Chunk-Größe: {CHUNK_SIZE}")
        else:
            logger.warning("⚠️ spaCy Extractor Warnung: Repository ist leer!")

    def extract_competences(self, text: str, role: str = None) -> List[CompetenceDTO]:
        """
        OPTIMIERTE KOMPETENZEN-EXTRAKTION mit Rollen-Kontextualisierung:
        1. Text-Analyse mit spaCy-NLP
        2. Rollenbasierte Gewichtung (falls Rolle vorhanden)
        3. ESCO-Mapping und Deduplizierung
        """
        if not text: return []
        
        # Role-Context für Gewichtung vorbereiten (Ebene 6: roleContext)
        role_context = role or "Unbekannt"

        # ✅ Konfigurierbares Text-Limit (Default 10k) + Timing
        try:
            default_limit = 10000
            env_limit = os.getenv('SPACY_TEXT_LIMIT')
            text_limit = int(env_limit) if (env_limit and env_limit.isdigit()) else default_limit
        except Exception:
            text_limit = 10000

        # Log Request Start
        logger.info(f"extract_competences: Input {len(text)}->{text_limit} chars, Role={role_context}")
        
        t0 = time.perf_counter()
        doc = self.nlp(text[:text_limit])
        t1 = time.perf_counter()
        matches = self.matcher(doc)
        t2 = time.perf_counter()
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

        # Approved-Mappings aus gemeinsamer Datei laden (Discovery-Review)
        approved_mapping = {}
        try:
            import os, json
            from pathlib import Path
            base = os.environ.get("BASE_DATA_DIR")
            if base:
                p = Path(base) / "discovery" / "approved_skills.json"
            else:
                p = Path(__file__).resolve().parents[4] / "python-backend" / "data" / "discovery" / "approved_skills.json"
            if p.exists():
                approved_mapping = json.loads(p.read_text(encoding="utf-8")) or {}
        except Exception:
            approved_mapping = {}

        for _, start, end in matches:
            term = doc[start:end].text
            term_lower = term.lower().strip()

            # Einfache Filter: zu kurze Tokens oder keine Buchstaben ignorieren
            if len(term_lower) < 2 or not any(c.isalpha() for c in term_lower):  # ✅ Erlaubt R, C
                continue

            # Prüfe auf exakten Kandidaten (oder kompakte Variante ohne Leerzeichen)
            term_compact = term_lower.replace(' ', '')
            exact_match = None
            for cand in candidates:
                cand_lower = cand.lower()
                if cand_lower == term_lower or cand_lower.replace(' ', '') == term_compact:
                    exact_match = cand
                    break

            # Ermittle, ob es ein Custom-Mapping (z.B. 'jira' -> 'Projektmanagement durchführen') gibt
            mapped = None
            if self.esco_service is not None:
                mapping = getattr(self.esco_service, 'get_esco_mapping', lambda: {})() or {}
                # Merge approved mappings (user-reviewed discovery)
                if approved_mapping:
                    try:
                        mapping = {**mapping, **approved_mapping}
                    except Exception:
                        pass
                mapped = mapping.get(term_lower)

            # Debug: Ausgabe der gefundenen Matches (nur beim direkten Testlauf sichtbar)
            # print(f"DEBUG MATCH: term={term!r}, term_lower={term_lower!r}, exact_match={exact_match}, mapped={mapped}")

            # Wenn weder exakter Kandidat noch Mapping gefunden wurde, überspringe (vermeidet falsche Matches)
            if exact_match is None and mapped is None:
                continue

            # Bestimme das kanonische Label (für Deduplizierung): Mapping hat Vorrang
            canonical_label = (mapped if mapped is not None else exact_match)
            canonical_label_lower = canonical_label.lower().strip()

            # Dedupliziere nach kanonischem ESCO-Label
            if canonical_label_lower in seen:
                continue

            # Blacklist prüfen (sowohl gefundener Term als auch das kanonische Label)
            if term_lower in blacklist or canonical_label_lower in blacklist:
                continue

            seen.add(canonical_label_lower)

            # Versuche ESCO Informationen zu holen, falls vorhanden
            esco_label = canonical_label
            esco_uri = f"custom/{canonical_label_lower.replace(' ', '_')}"
            esco_group_code = None

            try:
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
                    # Suche nach Labels, die den gefundenen Term (oder seine kompakte Form) enthalten
                    candidates = self.repository.get_all_identifiable_labels() if hasattr(self.repository, 'get_all_identifiable_labels') else []
                    found = None
                    term_norm = term_lower.replace(' ', '')
                    for cand in candidates:
                        cand_norm = cand.lower().replace(' ', '')
                        if term_lower in cand_norm or term_compact in cand_norm:
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

            # Hole ESCO Collections (digital, research, transversal, language)
            collections = []
            try:
                if hasattr(self.repository, 'get_data_by_label'):
                    esco_data = self.repository.get_data_by_label(esco_label)
                    if esco_data and 'collections' in esco_data:
                        collections = esco_data['collections']
            except Exception:
                pass

            # is_digital Default-Schutz: Fallback zu False wenn None
            try:
                is_digital_value = self.repository.is_digital_skill(term) or False
            except Exception:
                is_digital_value = False
            
            dto = AnalysisResultFactory.create_competence(
                original_term=term,
                esco_label=esco_label,
                esco_uri=esco_uri,
                level=self.repository.get_level(term),
                is_digital=is_digital_value,
                collections=collections,
                role_context=role_context,  # Nutze vorbereitetete role_context (Ebene 6)
                confidence=1.0
            )

            # Ergänze optionales Group-Attribut (kompatibel zu alten DTOs)
            if esco_group_code is not None:
                setattr(dto, 'esco_group_code', esco_group_code)

            results.append(dto)

        # ✅ Fallback: Läuft IMMER (nicht nur bei len=0), um zusätzliche Skills zu finden
        fallback_results = []
        try:
                from rapidfuzz import fuzz

                labels = self.repository.get_all_identifiable_labels()
                # Filtere Tokens: alphabetische oder hyphenierte Tokens, keine Stop-Words
                tokens = [t.text for t in self.nlp(text) if (t.is_alpha or '-' in t.text) and not t.is_stop]
                if not tokens:
                    return results
                max_n = min(4, max((len(l.split()) for l in labels), default=1))

                def ngrams(seq, n):
                    return [seq[i:i+n] for i in range(len(seq)-n+1)]

                # Hole ggf. Custom-Mapping fürs Fallback
                mapping = getattr(self.esco_service, 'get_esco_mapping', lambda: {})() if self.esco_service is not None else {}
                if approved_mapping:
                    try:
                        mapping = {**mapping, **approved_mapping}
                    except Exception:
                        pass

                # 1) Mapping-Pass: suche gezielt nach Mappings in den Tokens (z.B. 'jira', 'nosql')
                for n in range(1, max_n+1):
                    for gram in ngrams(tokens, n):
                        joined = ''.join(gram).lower()
                        gram_joined_space = ' '.join(gram).lower()
                        mapped_label = mapping.get(gram_joined_space) or mapping.get(joined)
                        # Debug
                        # print(f"MAPPING_PASS: gram={gram_joined_space!r}, mapped_label={mapped_label!r}")
                        if mapped_label and mapped_label.lower() not in seen:
                            uri, _id, group = (self.repository.get_esco_uri_and_id(mapped_label) if hasattr(self.repository, 'get_esco_uri_and_id') else (None, None, None))
                            esco_uri_val = uri if uri else f"custom/{mapped_label.lower().replace(' ', '_')}"
                            dto = AnalysisResultFactory.create_competence(
                                original_term=' '.join(gram),
                                esco_label=mapped_label,
                                esco_uri=esco_uri_val,
                                level=self.repository.get_level(mapped_label),
                                is_digital=self.repository.is_digital_skill(mapped_label),
                                role_context=role
                            )
                            results.append(dto)
                            seen.add(mapped_label.lower())

                # 2) Label-Scan: substring / fuzzy matching (nur für Labels, die noch nicht gefunden wurden)
                for label in labels:
                    if label.lower() in seen:
                        continue
                    # Normiertes, alnum-only Label für Vergleiche (z.B. UX-Testing -> uxtesting)
                    norm_label_raw = ''.join(label.split()).lower()
                    norm_label = ''.join(ch for ch in norm_label_raw if ch.isalnum())
                    found = False
                    for n in range(1, max_n+1):
                        for gram in ngrams(tokens, n):
                            joined_raw = ''.join(gram).lower()
                            # Entferne Nicht-Alphanumerische Zeichen für robustere Vergleiche (z.B. UX-Testing -> uxtesting)
                            joined = ''.join(ch for ch in joined_raw if ch.isalnum())

                            # Substring match (hohe Präzision): kurze joined in längeres norm_label
                            if joined and joined in norm_label:
                                # Erzeuge DTO ähnlich wie beim Matcher
                                esco_uri_val = f"custom/{label.lower().replace(' ', '_')}"
                                try:
                                    uri, _id, group = (self.repository.get_esco_uri_and_id(label) if hasattr(self.repository, 'get_esco_uri_and_id') else (None, None, None))
                                    if uri:
                                        esco_uri_val = uri
                                except Exception:
                                    uri, _id, group = (None, None, None)

                                dto = AnalysisResultFactory.create_competence(
                                    original_term=' '.join(gram),
                                    esco_label=label,
                                    esco_uri=esco_uri_val,
                                    level=self.repository.get_level(label),
                                    is_digital=self.repository.is_digital_skill(label),
                                    role_context=role
                                )
                                # Ergänze optional das Gruppen-Attribut falls vorhanden
                                if group is not None:
                                    setattr(dto, 'esco_group_code', group)

                                # Dedupliziere nach ESCO-Label
                                if label.lower() not in seen:
                                    results.append(dto)
                                    seen.add(label.lower())
                                found = True
                                break
                            # Fuzzy-Check (strenger Threshold um False-Positives zu vermeiden)
                            if len(joined) >= 3:
                                score = fuzz.partial_ratio(norm_label, joined)
                                if score >= 90:
                                    dto = AnalysisResultFactory.create_competence(
                                        original_term=' '.join(gram),
                                        esco_label=label,
                                        esco_uri=f"custom/{label.lower().replace(' ', '_')}",
                                        level=self.repository.get_level(label),
                                        is_digital=self.repository.is_digital_skill(label),
                                        role_context=role
                                    )
                                    if label.lower() not in seen:
                                        results.append(dto)
                                        seen.add(label.lower())
                                    found = True
                                    break
                        if found:
                            break
        
                # ✅ Kombiniere Hauptresultate + Fallback
                results.extend(fallback_results)
        
        except Exception:
            pass

        # ✅ DAUERHAFTES PERFORMANCE & RESULT LOGGING
        try:
            t3 = time.perf_counter()
            total_time = t3 - t0

            # IMMER loggen (für Debugging & Performance-Tracking)
            logger.info("=" * 60)
            logger.info("📊 EXTRACTION REPORT:")
            logger.info(f"   📄 Input: {len(text)} chars (limit: {text_limit})")
            logger.info(f"   🎯 Role: {role_context}")
            logger.info(f"   🧩 Tokens: {len(doc)}")
            logger.info(f"   🧷 Matcher Hits: {len(matches)}")
            logger.info(f"   ✅ Results: {len(results)} competences")
            logger.info(f"   🔍 Unique: {len(seen)} (Deduplicated)")
            logger.info(f"   ⏱️  Total Time: {total_time:.3f}s")
            logger.info(f"   ⚡ Breakdown: nlp={t1-t0:.3f}s | match={t2-t1:.3f}s | post={t3-t2:.3f}s")

            # WARNUNG bei zu vielen Kompetenzen (Performance-Problem!)
            if len(results) > 100:
                logger.warning(f"⚠️  PERFORMANCE WARNING: {len(results)} competences extracted (expected: 20-50)")
                logger.warning(f"   → Possible cause: Fuzzy matching too aggressive or duplicates not filtered")

            # WARNUNG bei langsamer Verarbeitung
            if total_time > 5.0:
                logger.warning(f"⚠️  SLOW EXTRACTION: {total_time:.1f}s (expected: <2s)")
                logger.warning(f"   → Check text length ({len(text)} chars) and matcher patterns ({len(matches)} hits)")

        except Exception as e:
            logger.error(f"Error in logging: {e}")

        logger.info("=" * 60)
        return results
