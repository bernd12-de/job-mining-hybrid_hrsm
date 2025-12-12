✔️ job-mining-kotlin-python

Hybrid-System zur Analyse von Stellenanzeigen mit Kotlin (Spring Boot), Python (FastAPI) und PostgreSQL.

Dieses Projekt besteht aus drei Komponenten:

Kotlin API Gateway → stellt REST-Endpoints bereit (Upload, Speicherung, Reporting)

Python FastAPI Backend → NLP-Analyse von PDF/DOCX-Stellenanzeigen

PostgreSQL Datenbank → Speicherung aller extrahierten Daten

🚀 1. System starten
Nur die Datenbank starten (empfohlen während der Entwicklung)

Kotlin und Python laufen lokal in IntelliJ bzw. Uvicorn.
Daher starten wir nur die Datenbank aus Docker.

docker compose up -d jobmining-db


Parameter:

up → startet Services

-d → läuft im Hintergrund

jobmining-db → nur die PostgreSQL-Instanz starten

Status prüfen:

docker ps


Container sollte laufen mit:

Up ... job-mining-kotlin-python-jobmining-db-1


Datenbank stoppen:

docker compose down

🧠 2. Python Analyse-Service starten

Wechsle in das Python-Backend:

cd python-backend

✔️ Virtual Environment neu erstellen (Python 3.11)
rm -rf .venv
/opt/homebrew/opt/python@3.11/bin/python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt


Version prüfen:

python --version

✔️ FastAPI starten
uvicorn main:app --reload


Erwartete Ausgabe:

Uvicorn running on http://127.0.0.1:8000
Application startup complete.

✔️ FastAPI Docs öffnen

👉 http://127.0.0.1:8000/docs

Test: /analyse aufrufen

Try it out

PDF oder DOCX wählen

Execute

Erwartetes Ergebnis:
JSON mit erkannten Kompetenzen, Skills, Gruppen & Confidence-Scores.

🧩 3. Kotlin API Gateway starten

Kotlin befindet sich im Ordner:

kotlin-api


Start per IntelliJ ("Run KotlinApiApplication").

Swagger UI öffnen:

👉 http://localhost:8080/swagger-ui/index.html

Wichtige Endpoints:

POST /api/v1/jobs/upload

Lädt eine Stellenanzeige hoch und startet Analyse + Speicherung.

Funktion:

Datei wird an FastAPI geschickt

NLP extrahiert Text, Skills & Gruppen

Ergebnis wird in PostgreSQL gespeichert

Kotlin gibt analysierte JobPosting-Entity zurück

🗂️ 4. Git & Branching Workflow

Aktuelle Branches prüfen:

git branch -a


Einen Remote-Branch lokal auschecken:

git checkout -b feature/batch-process origin/feature/batch-process


Änderungen committen:

git add .
git commit -m "Implement batch processing"
git push


Branch wechseln:

git checkout feature/kotlin-analyse

🔧 5. Gradle bereinigen (bei Spring-Problemen)

Wenn Spring/Gradle Fehler auftreten:

1. Gradle Daemon stoppen
./gradlew --stop

2. Gradle Cache löschen
rm -rf ~/.gradle/caches/*

3. IntelliJ Projektbereinigung
rm -rf .idea/
rm -rf kotlin-api/build/


Dann IntelliJ neu öffnen.

🧪 6. Test-Endpunkte

FastAPI Docs
👉 http://127.0.0.1:8000/docs

Swagger UI (Spring Boot)
👉 http://localhost:8080/swagger-ui/index.html

🎯 7. Zusammenfassung
Komponente	URL	Start
Kotlin API	http://localhost:8080
	IntelliJ
Swagger UI	http://localhost:8080/swagger-ui/index.html
	IntelliJ
Python API	http://127.0.0.1:8000/docs
	uvicorn main:app --reload
Postgres DB	läuft in Docker	docker compose up -d jobmining-db
📌 8. Ziel des Projekts

Die Pipeline extrahiert aus PDF/DOCX-Stellenanzeigen:

Tätigkeiten

Kompetenzen

ESCO-Skills (Label + URI)

Skill-Gruppen

Confidence Scores

Metadaten (Jobtitel, Region, Branche, Posting Date)

Kotlin speichert die Daten & bietet APIs für spätere Reporting- und Trend-Auswertungen.