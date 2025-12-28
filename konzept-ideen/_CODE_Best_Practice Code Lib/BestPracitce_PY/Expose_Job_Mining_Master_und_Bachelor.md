# Exposé: Job-Mining – Automatisierte Analyse von Stellenanzeigen zu Kompetenzanforderungen in digitalen Berufsbildern

**Autor:** Michael Layher  
**Studiengang:** Human-Computer Interaction (HCI)  
**Betreuung (angefragt):** Prof. Schott  
**Projektstatus:** Exposé / Konzept (nicht die Arbeit selbst)

---

## Variante A: Masterprojekt (empfohlen)

### 1. Hintergrund & Motivation
Die digitale Transformation verändert berufliche Rollen kontinuierlich – insbesondere in UX, Produktmanagement und IT-Consulting. Unternehmen spiegeln diese Veränderungen in **Stellenanzeigen**, die als frei verfügbare Datenquelle wertvolle Hinweise auf **Kompetenzen, Methoden und Tools** liefern. Gleichzeitig sind diese Informationen **unstrukturiert** (PDF, DOCX, HTML) und terminologisch **uneinheitlich** (z. B. „Ihr Profil“, „Anforderungen“, „Skills“). Das Projekt *Job‑Mining* soll diese Signale **systematisch erschließen** und **trendorientiert** auswerten.

**Fokus:** Kundenzentrierung (User/Customer Centricity) als Leitprinzip digitaler Wertschöpfung und deren **Operationalisierung** in realen Anforderungsprofilen (Schnittstellen UX – Produkt – Entwicklung).

### 2. Forschungsfragen
- **Hauptfrage:** Welche **Kompetenzen, Tools und Methoden** werden in aktuellen Stellenanzeigen digitaler Rollen gefordert – und wie unterscheiden sie sich **nach Branche, Rolle, Erfahrungsniveau, Land und Zeit**?
- **Teilfragen:**  
  1) Wie haben sich die Kompetenzanforderungen **2018–2025** entwickelt (Trend)?  
  2) Welche **Rollenprofile** (z. B. UX Designer, UX Researcher, Product Owner) zeigen Überschneidungen oder klare Spezialisierungen?  
  3) Welche **Bildungsabschlüsse** und **Erfahrungslevels** werden verlangt?  
  4) Wie manifestiert sich **Kundenzentrierung** in den Anzeigen (Begriffe, Praktiken, Schnittstellen zu Dev/IT)?

### 3. Zielsetzung
- **Methodisch:** Aufbau einer **wiederverwendbaren Pipeline** zur Extraktion strukturierter Daten aus unstrukturierten Anzeigen (Tools, Methoden, Soft Skills, Jahr, Branche, Seniorität, Sprache, Land/Ort).  
- **Analytisch:** Erstellung einer **Bestandsaufnahme** (Katalog) und einer **quantitativen/semantischen Analyse** über Zeit, Rollen und Branchen; Ableitung von **Handlungsempfehlungen** für Ausbildung/Portfolio.

### 4. Theoretischer Rahmen (Auszug)
- **Text Mining / NLP:** Regex, Abschnittserkennung, Keyword‑Lexika, semantische Ähnlichkeit (Embeddings).  
- **Labour Market Intelligence (LMI):** Auswertung arbeitsmarktrelevanter Texte zur Skill‑Identifikation.  
- **Inhaltsanalyse:** Kategoriensysteme für Kompetenzen & Rollen.  
- **CRISP‑DM / KDD:** Vorgehensmodell von Business Understanding bis Deployment.

### 5. Methodik & Daten
**Datenbasis:** Eigener Korpus mit >600 Stellenanzeigen (PDF/DOCX/Export), Zeitraum **2018–2025**, überwiegend DE, ergänzt um FR/US; Rollen u. a. **UX/UI Designer, UX Researcher, Product Owner/Manager, Service Designer, Digital Consultant**.  
**Vorarbeiten:** Funktionsfähiges Extraktions‑Skript (`job_mining_catalog.py`) für Metadaten (Jahr, Rolle, Level, Stadt/Land, Branche, Abschluss, Sprache) + Rohtext (optional).

**Pipeline (vereinfacht):**  
1) **Datenerhebung**: Konsolidierung aller Anzeigen.  
2) **Vorverarbeitung**: Textextraktion (PDF/DOCX), Bereinigung, **Abschnittserkennung** („Anforderungen“, „Aufgaben“, „Benefits“).  
3) **Feature‑Extraktion**: Skills/Tools/Methoden (Lexikon + Embeddings), Seniorität, Abschluss, Ort, Jahr, Sprache.  
4) **Analyse**: Häufigkeiten, **Zeitreihen**, Rollen‑Cluster, Länder‑/Branchenvergleich.  
5) **Validierung**: Stichprobenprüfung; Plausibilitätschecks.  
6) **Bericht**: Tabellen, Diagramme, **Trendbericht** + Empfehlungen.

### 6. Geplante Auswertungen
- **Top‑N Tools & Methoden** (global + je Rolle/Branche/Land).  
- **Trendlinien** (z. B. Figma‑Durchsetzung, Abnahme Legacy‑Tools).  
- **Rollen‑Co‑Occurrence** (welche Skills treten gemeinsam auf?).  
- **Kundenzentrierung**: Präsenz von Research, Testing, Accessibility, Collaboration‑Begriffen.  
- **Abschluss/Level‑Anforderungen** nach Branche und Zeit.

### 7. Ergebnisse (erwartet)
- Vollständige **Bestandsaufnahme** (Jahr, Rolle, Level, Stadt/Land, Branche, Abschluss).  
- **Trendbericht 2018–2025** zu Kompetenzen & Tools; **Cluster** für Rollenprofile.  
- **Empfehlungen** für Curricula, Weiterbildung und Portfolio‑Ausrichtung.

### 8. Vorgehensmodell & Meilensteine (Master, 12–16 Wochen)
1) **Literatur & Frameworks** (W1–2) – Exposé finalisieren, Kategorienschema.  
2) **Korpus & Pipeline** (W3–5) – Parsing, Normalisierung, Abschnittserkennung.  
3) **Feature‑Extraktion** (W6–7) – Skills/Tools (Lexikon + Embeddings), Validierung.  
4) **Analyse & Visualisierung** (W8–10) – Zeit, Rollen, Branchen, Länder.  
5) **Interpretation & Bericht** (W11–13) – Trendbericht, Empfehlungen.  
6) **Review & Finalisierung** (W14–16) – Qualitätssicherung, Abgabe.

### 9. Risiken & Limitation
- Uneinheitliche Terminologie; **Mehrsprachigkeit** (DE/EN/FR).  
- PDF‑Qualität (Scans); Bias durch Quellenkanäle (z. B. Branchenübergewicht).  
- Heuristische Zuordnung (z. B. Stadt/Branche) → Gegenmaßnahme: **Stichproben‑Validierung**.

### 10. Ressourcen & Tools
Python 3.12; **PyMuPDF/pdfminer.six**, **python-docx**; **pandas**, **spaCy/sentence‑transformers**; **matplotlib/Plotly**; optional Power BI; Versionskontrolle (Git).

---

## Variante B: Exposé für eine kleine Bachelorarbeit

**Unterschiede zur Master‑Variante:** geringerer Datenumfang (z. B. 100–200 Anzeigen), Fokus primär auf **Bestandsaufnahme** + **deskriptive Trends**, weniger auf semantische Embeddings/Cluster.

### Ziele (Bachelor kurz)
- Pipeline für **Textextraktion + Katalogisierung** (Jahr, Rolle, Level, Stadt/Land, Branche, Abschluss).  
- **Top‑15 Skills/Tools** und **Zeittrend** 2018–2025.  
- Kurzer **Vergleich** DE vs. ein zweites Land (z. B. FR oder US).

### Zeitplan (8–12 Wochen)
1) Korpus + Extraktion (W1–3), 2) Feature‑Extraktion (W4–5), 3) Auswertung (W6–8), 4) Bericht (W9–10), 5) Review/Abgabe (W11–12).

---

## Geplante Artefakte / Deliverables
- **CSV/Excel‑Katalog** aller Anzeigen (Felder wie oben).  
- **PDF‑Trendbericht** (Diagramme + Zusammenfassung).  
- **Code‑Repository** (Pipeline, Konfigurationsdateien).

## Kurzreferenzen (Rahmen)
- CRISP‑DM (Wirth & Hipp, 2000); Inhaltsanalyse (Kuckartz, 2016); LMI‑Ansätze (Bholat et al., 2015).  
- Kompetenzrahmen: **ESCO, SFIA, O*NET, UXQB** (zur Einordnung, kein Vollabgleich).

---

*Hinweis:* Dieses Exposé basiert auf deinen bisherigen Entwürfen (u. a. Fokus Kundenzentrierung, Zeitraum 2018–2025, Rollenfeld UX/Product/Consulting) und konkretisiert die Umsetzung mit einer lauffähigen Pipeline (inkl. bereitgestelltem Skript).