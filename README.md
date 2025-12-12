# job-mining-kotlin-python


Docker 

2. Starten Sie nur den Datenbank-Service
Da Ihr Kotlin- und Python-Backend lokal in IntelliJ/Uvicorn laufen, starten wir nur den Datenbank-Container, der in Ihrer docker-compose.yml definiert ist (wahrscheinlich jobmining-db).

Führen Sie diesen Befehl aus:

Bash

docker compose up -d jobmining-db
docker compose up: Startet die Services, die in der docker-compose.yml definiert sind.

-d: Führt den Service im "Detached Mode" (Hintergrund) aus, damit Ihr Terminal frei bleibt.

jobmining-db: Dies ist der Name des spezifischen Service, den wir starten wollen (der PostgreSQL-Datenbank-Container).

3. Prüfen, ob der Container läuft
Nachdem der Befehl ausgeführt wurde, prüfen Sie den Status:

Bash

docker ps
Sie sollten einen Container in der Liste sehen, dessen Name mit jobmining-db (oder einem ähnlichen Projektnamen) beginnt und dessen Status Up (läuft) ist.


docker compose down

Python-URL
Test-URL im Browser aufrufen
Öffnen Sie Ihren Webbrowser und navigieren Sie zur Dokumentation des FastAPI-Services:

URL: http://127.0.0.1:8000/docs

3. Test-Upload durchführen
Endpunkt finden: Suchen Sie auf der Seite den Endpunkt POST /analyse (Dieser sollte als einziger roter oder grüner Block sichtbar sein).

Klicken Sie auf: "Try it out" (Ausprobieren).

Wählen Sie die Datei: Es öffnet sich ein Feld mit der Beschriftung file. Klicken Sie auf "Choose File" (Datei auswählen).

Wählen Sie Ihr Dokument: Wählen Sie eine Ihrer Test-Stellenanzeigen (PDF oder DOCX) von Ihrer Festplatte.

Führen Sie den Test aus: Klicken Sie auf "Execute" (Ausführen).

💡 Erwartetes Ergebnis
Wenn der Test erfolgreich ist, sollte der Response Code 200 (OK) zurückgegeben werden, und Sie sehen im Response Body (Antwortkörper) die korrekte JSON-Struktur des AnalysisResultDTO


Python-Virtual Environment (venv) verwendet Python 3.9


Uvicorn-Befehl sauber eingeben
Der Prozess ist korrekt. Sie müssen nur den Uvicorn-Befehl sauber und ohne die doppelte (.venv)-Vorbemalung ausführen.

1. Korrekter Start des Python-Microservice
Führen Sie diesen Befehl einzeln aus. Die aktive Shell zeigt das (.venv)-Präfix bereits an; Sie müssen es nicht erneut eingeben:

Bash

uvicorn main:app --reload
uvicorn: Das Programm, das FastAPI startet.

main:app: Zeigt auf die app-Instanz in der Datei main.py.

--reload: Sorgt dafür, dass der Server bei Code-Änderungen automatisch neu startet.

2. Prüfung des Uvicorn-Status
Wenn der Befehl korrekt ausgeführt wird, sollte die Ausgabe wie folgt aussehen:

INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [...]
...
INFO:     Application startup complete.

# Wir gehen davon aus, dass Sie sich jetzt im jobmining-hybrid/python-backend Ordner befinden:
# 1. Alte venv löschen (sollte schon passiert sein, aber zur Sicherheit)
rm -rf .venv

# 2. Neue venv mit Python 3.11 erstellen
/opt/homebrew/opt/python@3.11/bin/python3 -m venv .venv

# 3. Neue venv aktivieren und Pakete installieren (mit gelockerten Pins)
source .venv/bin/activate
pip install -r requirements.txt


Version
(.venv) layher-ad@MacBookPro python-backend % python --version

uvicorn main:app --reload

Schritt 1: Python-Environment reparieren
Wir beheben den Versionskonflikt endgültig durch die Erstellung einer sauberen Python 3.11-Umgebung. Führen Sie diese Befehle im Terminal im Ordner jobmining-hybrid/python-backend aus:

Löschen Sie alle alten venv-Instanzen:

Bash

rm -rf .venv
Erstellen Sie die neue, saubere venv mit Python 3.11:

Bash

/opt/homebrew/opt/python@3.11/bin/python3 -m venv .venv
Aktivieren und installieren Sie die korrigierten Dependencies:

Bash

source .venv/bin/activate
pip install -r requirements.txt


1. Gradle Daemon stoppen (Wichtigster Schritt)
Der Gradle Daemon hält oft fehlerhafte Abhängigkeiten im Speicher. Wir müssen ihn manuell stoppen.

Öffnen Sie das Terminal in IntelliJ (oder das normale Mac-Terminal).

Geben Sie den folgenden Befehl ein:

Bash

./gradlew --stop
(Falls Sie sich nicht im Root-Verzeichnis befinden, geben Sie nur gradle --stop ein, falls Gradle im Pfad ist.)

2. Alle Gradle-Caches löschen
Wir löschen den gesamten lokalen Cache, der die beschädigte oder inkompatible Datei enthält:

Schließen Sie IntelliJ.

Navigieren Sie in Ihrem Home-Verzeichnis zum Gradle-Cache-Ordner:

Bash

cd ~/.gradle/caches/
Löschen Sie den gesamten Inhalt dieses Ordners:

Bash

rm -rf *

2. IntelliJ Projektkonfiguration löschen (KRITISCH)
Der Fehler wird durch die Dateien verursacht, die IntelliJ lokal im Projekt ablegt.

Navigieren Sie in Ihr Hauptprojektverzeichnis (jobmining-hybrid/).

Löschen Sie die IntelliJ-Konfigurationsdateien:

Bash

rm -rf .idea/
(Achtung: Dies löscht alle Ihre lokalen IntelliJ-Einstellungen für dieses Projekt (z.B. Run-Konfigurationen), ist aber notwendig, um den Fehler zu beheben.)

Löschen Sie den Build-Ordner im Kotlin-Modul:

Bash

rm -rf kotlin-api/build/



http://127.0.0.1:8000/docs

(.venv) layher-ad@MacBookPro python-backend % uvicorn main:app --reload
INFO:     Will watch for changes in these directories: ['/Users/layher-ad/IdeaProjects/job-mining-kotlin-python/python-backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [77055] using StatReload
INFO:     Started server process [77057]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     127.0.0.1:51014 - "GET / HTTP/1.1" 404 Not Found
INFO:     127.0.0.1:51015 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:51015 - "GET /openapi.json HTTP/1.1" 200 OK
INFO:     127.0.0.1:51019 - "GET /docs HTTP/1.1" 200 OK
INFO:     127.0.0.1:51019 - "GET /openapi.json HTTP/1.1" 200 OK



Kotlin Spring
http://localhost:8080/swagger-ui/index.html
