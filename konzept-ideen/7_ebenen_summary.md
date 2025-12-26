Zusammenfassung: "7 Ebenen" und Beweisstellen

Kurz: Das Repo definiert ein 7‑Ebenen‑Konzept (Ebene 1–5 sind implementiert/konzeptionell; Ebene 6/7 sind erwähnt, zum Teil nur als Kommentare). Es gibt mehrere Fundstellen, die "Beweis" für Integration/Datentransfer liefern (Log‑Ausgaben, Terminal‑Snips).

Wichtige Fundstellen

- konzept-ideen/_Gemini – Reperatur To do Hybrid 25-12-25.html
  - Enthält multiple "Das ist der Beweis!"‑Abschnitte; zeigt Terminal‑Ausgaben/HTTP‑Snippts, z. B.:
    - "GET /health/status ... 200 OK" -> Beweis, dass Kotlin erreichbar ist.
    - "✅ SSoT BEREIT: 29722 Suchbegriffe" -> Beweis, dass SSoT (Kotlin) Daten liefert.
  - Enthält konkrete Reparaturvorschläge (z. B. `load_all_data` fix, `self.esco_data` Indexing).

- app/infrastructure/extractor/discovery_extractor.py
  - Discovery ist Ebene 1: erzeugt DTOs mit `level=1` und `is_discovery=True`.

- app/infrastructure/extractor/metadata_extractor.py
  - `inferred_level = 2` standardmäßig; erkennt `fachbuecher` → Ebene 4, `modulhandbuecher` → Ebene 5.

- generate_domains.py
  - Extrahiert Domänen aus PDFs und kennzeichnet Ebene 4 (Fachbücher) bzw. Ebene 5 (Modulhandbücher).

- app/domain/models.py
  - `CompetenceDTO.level` ist Integer zwischen 1 und 5; `is_discovery` und `is_digital` Felder sind vorhanden.

Status pro Ebene

- Ebene 1 (Discovery): Implementiert (DiscoveryExtractor). Pipeline führt Discovery‑Pass aus.
- Ebene 2 (ESCO/SSoT): Implementiert in Teilen (HybridCompetenceRepository lädt von Kotlin / CSV), aber Levelauflösung fehlt (get_level() ist noch ein Stub).
- Ebene 3 (Digital flag): Feld vorhanden; `is_digital_skill` ist derzeit ein Stub (sollte ESCO‑Metadaten prüfen).
- Ebene 4 (Fachbücher): Domain‑Generierung vorhanden; Repo lädt Domains nicht konsistent in Index (fehlende `_load_local_domains_v2`/Sync‑Logik fehlt oder ist unvollständig).
- Ebene 5 (Academia): Wie Ebene 4 (Domains werden erzeugt, aber Index/Integration fehlt noch).
- Ebene 6 (Segmentierung & Kontext): Konzept/Patterns vorhanden (TASK_PATTERN etc.), nicht als numerischer Level auf DTOs gespeichert.
- Ebene 7 (Zeitreihen / Validierung): Erwähnt (MetadataExtractor Kommentar), jedoch nicht implementiert.

Konkrete Lücken (Kurz)

- `HybridCompetenceRepository.get_level` ist ein Stub; muss Priorität prüfen: Academia (5) → Fachbuch (4) → ESCO (2/3) → default (2).
- `HybridCompetenceRepository` braucht einen `esco_data` Index (label → metadata) und Methoden: `_load_local_domains_v2`, `_sync_legacy_sets`, `_build_esco_index`.
- `is_digital_skill()` ist ein Stub; sollte ESCO‑Metadaten verwenden.
- Tests: fehlende Unit‑Tests, die die Level‑Auflösung und lokale domain‑Ladevorgänge prüfen.

Nächste Schritte (implementiert in Code)

- Implementiere `HybridCompetenceRepository.get_level` (priorisiert academica→fachbuch→esco→heuristik→default).
- Implementiere `_load_local_domains_v2`, `_sync_legacy_sets`, `_build_esco_index` und setze `self.esco_data`, `self.custom_domains`, `_fachbuch_skills`, `_academia_skills`.
- Füge Unit‑Tests: `tests/test_repository_levels.py` (prüft Level‑Prioritäten und is_digital behavior).

Belege (Textausschnitte & Hinweise)

- "Das ist der Beweis! ... Der Log‑Eintrag GET /health/status ... 200 OK beweist, dass dein Kotlin‑Service jetzt erfolgreich mit dem Python‑Service spricht." (konzept‑ideen/_Gemini – Reperatur To do Hybrid 25-12-25.html)
- Discovery: Code in `app/infrastructure/extractor/discovery_extractor.py` erstellt DTOs mit `level=1`.
- `generate_domains.py` markiert Domains (Ebene 4/5) explizit via Kommentar.

Datei erstellt: konzept-ideen/7_ebenen_summary.md

