# job-mining/test_db_connection.py

from infrastructure.storage.db_service import get_engine, setup_db
import os

# Definiere den Pfad zur lokalen DB-Datei
DB_FILE = "../../job_mining_local.db"

def test_connection_and_setup():
    """Prüft, ob die Datenbank-Engine erstellt und die Tabellen initialisiert werden können."""

    print("\n--- Start: Expliziter DB-Verbindungstest ---")

    # 1. Sicherstellen, dass keine alte DB existiert
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"Datenbankdatei {DB_FILE} für Testzwecke gelöscht.")

    try:
        # 2. Engine erstellen (Verbindungsparameter prüfen)
        engine = get_engine()
        print("✅ DB-Engine erfolgreich erstellt.")

        # 3. Tabellen erstellen (Schema prüfen)
        setup_db(engine)
        print("✅ DB-Tabellen (jobs, competences) erfolgreich erstellt.")

        # 4. Prüfen, ob die Datei tatsächlich existiert
        if os.path.exists(DB_FILE):
            print("✅ DB-Datei erfolgreich auf der Festplatte gefunden.")
            print("SUCCESS: Datenbank-Verbindung und Setup sind stabil.")
        else:
            print("❌ FAILURE: DB-Datei wurde nicht erstellt.")

    except Exception as e:
        print(f"❌ FAILURE: Verbindung oder Setup fehlgeschlagen. Fehler: {e}")

    finally:
        # 5. Aufräumen: Datenbankdatei für weitere Tests löschen
        if os.path.exists(DB_FILE):
            os.remove(DB_FILE)

if __name__ == "__main__":
    test_connection_and_setup()
