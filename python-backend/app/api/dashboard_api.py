"""
Dashboard API - DEPRECATED ⚠️

Diese Datei ist VERALTET und wird NICHT mehr verwendet!

Die aktuelle Anwendung besteht aus:

1. FastAPI Backend (Port 8000)
   - Datei: python-backend/main_v2.py oder main.py
   - Endpoints: /analyse/*, /batch-process, /system/status, etc.
   
2. Streamlit Dashboard (Port 8501)
   - Datei: python-backend/dashboard_app.py
   - Interaktive Visualisierung mit Echtzeit-Updates
   
3. Kotlin API Gateway (Port 8080)
   - Spring Boot mit OpenAPI/Swagger
   - Centralized API Management
   
4. PostgreSQL Database (Port 5432)
   - Persistierung von Jobs und Kompetenzen

Diese Datei wird nur zu Archivzwecken beibehalten und sollte NICHT genutzt werden.

Nutzen Sie stattdessen:
- FastAPI: http://localhost:8000/docs
- Streamlit: http://localhost:8501
- Swagger: http://localhost:8080/swagger-ui.html
"""


# DUMMY IMPLEMENTATION - Diese Datei ist nicht funktional
class DummyFlaskApp:
    """
    Placeholder Flask App für Backward-Compatibility.
    Diese Klasse verhindert ImportError, aber die Funktionalität
    ist komplett in FastAPI/Streamlit umgezogen.
    """
    
    def __init__(self):
        self.name = "DummyDashboardAPI_DEPRECATED"
        self.debug = False
    
    def route(self, path, **kwargs):
        """Dummy decorator"""
        def decorator(func):
            return func
        return decorator
    
    def run(self, *args, **kwargs):
        """Dummy run method"""
        raise RuntimeError(
            "dashboard_api.py ist veraltet! "
            "Nutze stattdessen: streamlit run dashboard_app.py"
        )


# Erstelle eine Dummy-App für Kompatibilität
app = DummyFlaskApp()


# Dummy Functions für Backward-Compatibility (werden nicht aufgerufen)
def get_competence_trends():
    raise NotImplementedError("Nutze FastAPI Backend oder Streamlit Dashboard")


def get_skill_distribution():
    raise NotImplementedError("Nutze FastAPI Backend oder Streamlit Dashboard")


def get_competence_progression():
    raise NotImplementedError("Nutze FastAPI Backend oder Streamlit Dashboard")


def get_role_mapping():
    raise NotImplementedError("Nutze FastAPI Backend oder Streamlit Dashboard")


def get_skill_analysis():
    raise NotImplementedError("Nutze FastAPI Backend oder Streamlit Dashboard")


def get_metrics():
    raise NotImplementedError("Nutze FastAPI Backend oder Streamlit Dashboard")


def get_regional_competence_analysis():
    raise NotImplementedError("Nutze FastAPI Backend oder Streamlit Dashboard")


def export_competence_data():
    raise NotImplementedError("Nutze FastAPI Backend oder Streamlit Dashboard")


# ============================================================================
# VERFÜGBARE ALTERNATIVE ENDPOINTS
# ============================================================================

print("""
╔════════════════════════════════════════════════════════════════════════════════╗
║                   ⚠️  DASHBOARD_API.PY IST VERALTET                           ║
╚════════════════════════════════════════════════════════════════════════════════╝

Diese Datei wird nicht mehr verwendet. Nutze stattdessen:

1. 📊 STREAMLIT DASHBOARD (interaktiv, Echtzeit):
   
   Terminal:
   $ streamlit run python-backend/dashboard_app.py
   
   Browser:
   http://localhost:8501

2. 📡 FASTAPI BACKEND (REST API):
   
   API-Docs:
   http://localhost:8000/docs
   
   Endpoints:
   POST   /batch-process
   POST   /analyse/file
   POST   /analyse/scrape-url
   GET    /system/status
   GET    /reports/dashboard-metrics

3. 🔌 KOTLIN API GATEWAY (Centralized):
   
   Swagger UI:
   http://localhost:8080/swagger-ui.html
   
   OpenAPI Schema:
   http://localhost:8080/v3/api-docs

════════════════════════════════════════════════════════════════════════════════
""")

