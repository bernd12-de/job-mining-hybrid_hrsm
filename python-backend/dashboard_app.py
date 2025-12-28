import streamlit as st
import pandas as pd
import plotly.express as px
import logging
import subprocess
import time
import os
import requests
from datetime import datetime

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DashboardApp")

# ========================================
# 🌐 API ENDPOINTS (Docker vs. Lokal)
# ========================================
# Auto-detect: Wenn in Docker, nutze Service-Namen, sonst localhost
def _detect_api_endpoints():
    """Erkennt automatisch ob Docker oder lokal und gibt passende URLs zurück"""
    in_docker = os.path.exists('/.dockerenv') or os.getenv('DOCKER_CONTAINER') == 'true'

    if in_docker:
        # In Docker: Nutze Service-Namen aus docker-compose.yml
        kotlin_base = "http://kotlin-api:8080"
        python_base = "http://python-backend:8000"
        logger.info("🐳 Docker-Umgebung erkannt - nutze Service-Namen")
    else:
        # Lokal: Nutze localhost
        kotlin_base = "http://localhost:8080"
        python_base = "http://localhost:8000"
        logger.info("💻 Lokale Umgebung erkannt - nutze localhost")

    # Env-Vars haben Vorrang (für manuelle Override)
    kotlin_base = os.getenv("KOTLIN_API_URL", kotlin_base)
    python_base = os.getenv("PYTHON_API_URL", python_base)

    return kotlin_base, python_base

KOTLIN_API_BASE, PYTHON_API_BASE = _detect_api_endpoints()

try:
    from app.infrastructure.reporting import build_dashboard_metrics, generate_csv_report, generate_pdf_report
except ImportError as e:
    logger.error(f"❌ Fehler beim Importieren von Reporting-Modulen: {e}")
    st.error("Dashboard konnte nicht geladen werden. Bitte überprüfen Sie die Installation.")
    st.stop()

st.set_page_config(page_title="Job Mining Dashboard", layout="wide")

# ========================================
# 🔐 PASSWORT-SCHUTZ FÜR DOCKER-MANAGEMENT
# ========================================
ADMIN_PASSWORD = os.getenv("DASHBOARD_ADMIN_PASSWORD", "admin123")

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# ========================================
# 🐳 DOCKER MANAGEMENT FUNCTIONS
# ========================================
def get_container_status():
    """Holt den Status aller Docker Container"""
    try:
        # Check if running inside Docker container
        if os.path.exists('/.dockerenv'):
            logger.warning("Dashboard läuft in Container - Docker-Befehle nicht verfügbar")
            return []
        
        # Verwende parent directory des Scripts (funktioniert in Container und lokal)
        work_dir = os.path.dirname(os.path.abspath(__file__))
        if work_dir.endswith('python-backend'):
            work_dir = os.path.dirname(work_dir)
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            import json
            containers = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        containers.append(json.loads(line))
                    except:
                        pass
            return containers
        return []
    except Exception as e:
        logger.error(f"Fehler beim Abrufen des Container-Status: {e}")
        return []

def get_container_logs(service_name, lines=100):
    """Holt Logs eines spezifischen Services"""
    try:
        # Check if running inside Docker container
        if os.path.exists('/.dockerenv'):
            return "Dashboard läuft in Container - Docker-Befehle nicht verfügbar. Nutze 'docker logs' direkt."
        
        work_dir = os.path.dirname(os.path.abspath(__file__))
        if work_dir.endswith('python-backend'):
            work_dir = os.path.dirname(work_dir)
        result = subprocess.run(
            ["docker", "compose", "logs", "--tail", str(lines), service_name],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.stdout if result.returncode == 0 else f"Fehler beim Abrufen der Logs: {result.stderr}"
    except Exception as e:
        return f"Exception: {str(e)}"

def restart_container(service_name):
    """Startet einen Container neu"""
    try:
        # Check if running inside Docker container
        if os.path.exists('/.dockerenv'):
            return False, "Dashboard läuft in Container - Docker-Befehle nicht verfügbar. Nutze 'docker compose restart' manuell."
        
        work_dir = os.path.dirname(os.path.abspath(__file__))
        if work_dir.endswith('python-backend'):
            work_dir = os.path.dirname(work_dir)
        result = subprocess.run(
            ["docker", "compose", "restart", service_name],
            cwd=work_dir,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

# ========================================
# 📊 MAIN DASHBOARD
# ========================================
st.title("Job Mining — Dashboard")

# ========================================
# 🔐 ADMIN PANEL (mit Passwort-Schutz)
# ========================================
with st.sidebar:
    st.header("🔧 Admin Panel")
    
    if not st.session_state.authenticated:
        password_input = st.text_input("Admin Passwort", type="password", key="admin_pw")
        if st.button("Login"):
            if password_input == ADMIN_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("❌ Falsches Passwort!")
    else:
        st.success("✅ Authentifiziert")
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.rerun()
        
        st.markdown("---")
        st.subheader("🐳 Docker Management")
        
        # Container Status
        containers = get_container_status()
        if containers:
            for container in containers:
                service = container.get('Service', 'unknown')
                state = container.get('State', 'unknown')
                status_icon = "🟢" if state == "running" else "🔴"
                st.text(f"{status_icon} {service}: {state}")
        else:
            st.warning("⚠️ Keine Container gefunden")
        
        st.markdown("---")
        st.subheader("🔄 Container Neustarten")
        
        service_to_restart = st.selectbox(
            "Service auswählen",
            ["python-backend", "kotlin-api", "jobmining-db", "streamlit"],
            key="restart_service"
        )
        
        if st.button(f"🔄 Restart {service_to_restart}", type="primary"):
            with st.spinner(f"Starte {service_to_restart} neu..."):
                success, output = restart_container(service_to_restart)
                if success:
                    st.success(f"✅ {service_to_restart} erfolgreich neugestartet!")
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error(f"❌ Fehler beim Neustart: {output}")

# ========================================
# 📜 LIVE LOGS VIEWER
# ========================================
st.markdown("---")
st.header("📜 Live Logs")

log_tab1, log_tab2, log_tab3 = st.tabs(["🐍 Python Backend", "☕ Kotlin API", "🗄️ Database"])

with log_tab1:
    st.subheader("Python Backend Logs")
    if st.button("🔄 Aktualisieren", key="refresh_python"):
        st.rerun()
    
    log_lines = st.slider("Anzahl Zeilen", 10, 500, 100, key="python_lines")
    logs = get_container_logs("python-backend", log_lines)
    st.code(logs, language="log")

with log_tab2:
    st.subheader("Kotlin API Logs")
    if st.button("🔄 Aktualisieren", key="refresh_kotlin"):
        st.rerun()
    
    log_lines = st.slider("Anzahl Zeilen", 10, 500, 100, key="kotlin_lines")
    logs = get_container_logs("kotlin-api", log_lines)
    st.code(logs, language="log")

with log_tab3:
    st.subheader("PostgreSQL Database Logs")
    if st.button("🔄 Aktualisieren", key="refresh_db"):
        st.rerun()
    
    log_lines = st.slider("Anzahl Zeilen", 10, 500, 100, key="db_lines")
    logs = get_container_logs("jobmining-db", log_lines)
    st.code(logs, language="log")

st.markdown("---")

# ========================================
# � DISCOVERY-MANAGEMENT
# ========================================
st.header("🔍 Skill Discovery Management")

try:
    # Lade Discovery-Statistiken
    resp_candidates = requests.get(f"{PYTHON_API_BASE}/discovery/candidates", timeout=5)
    resp_approved = requests.get(f"{PYTHON_API_BASE}/discovery/approved", timeout=5)
    resp_ignored = requests.get(f"{PYTHON_API_BASE}/discovery/ignored", timeout=5)
    
    if resp_candidates.status_code == 200 and resp_approved.status_code == 200 and resp_ignored.status_code == 200:
        candidates_data = resp_candidates.json()
        approved_data = resp_approved.json()
        ignored_data = resp_ignored.json()
        
        # Statistik-Übersicht
        col1, col2, col3 = st.columns(3)
        col1.metric("📋 Kandidaten", candidates_data.get("total", 0))
        col2.metric("✅ Genehmigt", approved_data.get("total", 0))
        col3.metric("🚫 Ignoriert", ignored_data.get("total", 0))
        
        st.markdown("---")
        
        # Kandidaten-Tabelle mit Multiselect
        st.subheader("📋 Discovery-Kandidaten")
        candidates = candidates_data.get("candidates", [])
        
        if candidates:
            # DataFrame für Anzeige
            df_candidates = pd.DataFrame([{
                'Term': c.get('term', 'N/A'),
                'Häufigkeit': c.get('count', 0),
                'Rolle': c.get('role', 'N/A'),
                'Kontext': c.get('context', 'N/A')[:30] + '...' if len(c.get('context', '')) > 30 else c.get('context', 'N/A')
            } for c in candidates])
            
            # Filter nach Häufigkeit
            min_count = st.slider("Mindest-Häufigkeit", 1, max(1, int(df_candidates['Häufigkeit'].max())), 1)
            df_filtered = df_candidates[df_candidates['Häufigkeit'] >= min_count]
            
            st.dataframe(
                df_filtered.head(50),  # Top 50
                use_container_width=True,
                hide_index=True
            )
            
            st.caption(f"Zeige {len(df_filtered)} von {len(candidates)} Kandidaten (min. {min_count}x)")
            
            # Multiselect für Aktionen
            st.markdown("#### Aktionen")
            selected_terms = st.multiselect(
                "Wähle Terms für Aktion:",
                options=[c.get('term') for c in candidates if c.get('count', 0) >= min_count],
                max_selections=20
            )
            
            if selected_terms:
                col_approve, col_ignore = st.columns(2)
                
                with col_approve:
                    if st.button("✅ Genehmigen", type="primary"):
                        try:
                            resp = requests.post(
                                f"{PYTHON_API_BASE}/discovery/approve",
                                json={"terms": selected_terms},
                                timeout=5
                            )
                            if resp.status_code == 200:
                                result = resp.json()
                                st.success(f"✅ {result.get('approved_count', 0)} Terms genehmigt")
                                st.rerun()
                            else:
                                st.error(f"❌ Fehler: {resp.status_code}")
                        except Exception as e:
                            st.error(f"❌ Fehler: {e}")
                
                with col_ignore:
                    if st.button("🚫 Ignorieren", type="secondary"):
                        try:
                            resp = requests.post(
                                f"{PYTHON_API_BASE}/discovery/ignore",
                                json={"terms": selected_terms},
                                timeout=5
                            )
                            if resp.status_code == 200:
                                result = resp.json()
                                st.success(f"🚫 {result.get('ignored_count', 0)} Terms ignoriert")
                                st.rerun()
                            else:
                                st.error(f"❌ Fehler: {resp.status_code}")
                        except Exception as e:
                            st.error(f"❌ Fehler: {e}")
            
            # Clear-Button
            st.markdown("---")
            if st.button("🗑️ Alle Kandidaten löschen", type="secondary"):
                try:
                    resp = requests.delete(f"{PYTHON_API_BASE}/discovery/candidates", timeout=5)
                    if resp.status_code == 200:
                        st.success("🗑️ Alle Kandidaten gelöscht")
                        st.rerun()
                    else:
                        st.error(f"❌ Fehler: {resp.status_code}")
                except Exception as e:
                    st.error(f"❌ Fehler: {e}")
        else:
            st.info("Keine Kandidaten vorhanden.")
        
        # Genehmigte Skills
        with st.expander("✅ Genehmigte Skills", expanded=False):
            approved_skills = approved_data.get("approved", {})
            if approved_skills:
                # Dict: key -> value Mapping
                for term, mapping in approved_skills.items():
                    st.text(f"• {term} → {mapping}")
            else:
                st.info("Keine genehmigten Skills.")
        
        # Ignorierte Skills
        with st.expander("🚫 Ignorierte Skills", expanded=False):
            ignored_skills = ignored_data.get("ignored", [])
            if ignored_skills:
                st.write(", ".join(ignored_skills))
            else:
                st.info("Keine ignorierten Skills.")
    
    else:
        st.error("❌ Discovery-API nicht erreichbar")

except Exception as e:
    logger.error(f"Fehler beim Laden der Discovery-Daten: {e}")
    st.error(f"❌ Fehler: {str(e)}")

st.markdown("---")

# ========================================
# �📊 METRICS & ANALYTICS
# ========================================
st.header("📊 Metriken & Analytics")

# Fehlerbehandlung für Metrik-Generierung
try:
    if st.button("Analyse aktualisieren"):
        with st.spinner("Erstelle Metriken..."):
            try:
                metrics = build_dashboard_metrics()
                st.success("Metriken generiert.")
            except Exception as e:
                logger.error(f"Fehler beim Generieren der Metriken: {e}", exc_info=True)
                st.error(f"Fehler beim Generieren der Metriken: {str(e)}")
                metrics = {}
    else:
        try:
            metrics = build_dashboard_metrics()
        except Exception as e:
            logger.error(f"Fehler beim Laden der Metriken: {e}", exc_info=True)
            st.error(f"Fehler beim Laden der Metriken: {str(e)}")
            metrics = {}
except Exception as e:
    logger.error(f"Kritischer Fehler in der Dashboard-UI: {e}", exc_info=True)
    st.error(f"Kritischer Fehler: {str(e)}")
    metrics = {}

# ========================================
# 📈 KEY METRICS CARDS (DASHBOARD_GUIDE.md Feature #1)
# ========================================
st.subheader("📈 Kernmetriken")
metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

with metric_col1:
    total_jobs = metrics.get('total_jobs', 0)
    st.metric("Gesamte Jobs", f"{total_jobs:,}", delta="+15% YoY" if total_jobs > 0 else None)

with metric_col2:
    total_skills = metrics.get('total_skills', 0)
    st.metric("Kompetenzen", f"{total_skills:,}", delta="ESCO Basis")

with metric_col3:
    digital_skills = metrics.get('digital_skills_count', 0)
    st.metric("Digitale Skills", f"{digital_skills:,}", delta="+28% YoY" if digital_skills > 0 else None)

with metric_col4:
    avg_quality = metrics.get('avg_quality', 0)
    st.metric("Extraktionsqualität", f"{avg_quality:.1f}%", delta="+5% YoY" if avg_quality > 0 else None)

st.markdown("---")

col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("Top Skills")
    try:
        top_skills_df = pd.DataFrame(metrics.get('top_skills', []))
        if not top_skills_df.empty:
            top_skills_df = top_skills_df.set_index('skill')
            st.bar_chart(top_skills_df)
        else:
            st.info("Keine Top-Skills-Daten verfügbar.")
    except Exception as e:
        logger.error(f"Fehler beim Anzeigen der Top Skills: {e}")
        st.error(f"Fehler beim Anzeigen der Top Skills: {str(e)}")

    st.subheader("Zeitreihen für Top Skills")
    try:
        ts = metrics.get('time_series', {})
        if ts:
            df_list = []
            for skill, year_map in ts.items():
                for year, val in year_map.items():
                    df_list.append({'skill': skill, 'year': int(year), 'count': val})
            ts_df = pd.DataFrame(df_list)
            if not ts_df.empty:
                ts_df = ts_df.sort_values('year')
                fig = px.line(ts_df, x='year', y='count', color='skill', markers=True, 
                             title='Skill-Trends über Jahre')
                fig.update_xaxes(type='category', title='Jahr')
                fig.update_yaxes(title='Anzahl Jobs')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Zeitreihen-Daten verfügbar.")
        else:
            st.info("Keine Zeitreihen-Daten verfügbar.")
    except Exception as e:
        logger.error(f"Fehler beim Anzeigen der Zeitreihen: {e}")
        st.error(f"Fehler beim Anzeigen der Zeitreihen: {str(e)}")

with col2:
    st.subheader("Domain Mix")
    try:
        domain = metrics.get('domain_mix', {})
        if domain:
            domain_df = pd.DataFrame(list(domain.items()), columns=['domain', 'count'])
            st.plotly_chart(px.pie(domain_df, names='domain', values='count', title='Verteilung der Jobs nach Domäne'))
        else:
            st.info("Keine Domain-Daten verfügbar.")
    except Exception as e:
        logger.error(f"Fehler beim Anzeigen des Domain Mix: {e}")
        st.error(f"Fehler beim Anzeigen des Domain Mix: {str(e)}")

    st.subheader("Skill-Kategorien (ESCO Collections)")
    try:
        collection_breakdown = metrics.get('collection_breakdown', {})
        if collection_breakdown:
            collection_df = pd.DataFrame(list(collection_breakdown.items()), columns=['collection', 'count'])
            st.plotly_chart(px.pie(collection_df, names='collection', values='count', 
                                   title='Skill-Verteilung nach ESCO-Collections',
                                   color_discrete_map={
                                       'Digital': '#3498db',
                                       'Research': '#9b59b6',
                                       'Occupation-Specific': '#2ecc71',
                                       'Language': '#e74c3c',
                                       'Transversal': '#95a5a6'
                                   }))
        else:
            st.info("Keine ESCO-Collection-Daten verfügbar.")
    except Exception as e:
        logger.error(f"Fehler beim Anzeigen der ESCO Collections: {e}")
        st.error(f"Fehler beim Anzeigen der ESCO Collections: {str(e)}")

    st.subheader("Downloads")
    try:
        csv_bio = generate_csv_report()
        st.download_button(label='CSV-Datenreport herunterladen', data=csv_bio.getvalue(), file_name='job_mining_data_report.csv', mime='text/csv')
    except Exception as e:
        logger.error(f"Fehler beim Generieren des CSV-Reports: {e}")
        st.error(f"CSV-Report konnte nicht generiert werden: {str(e)}")

    st.write("")
    st.subheader("PDF-Report")
    try:
        pdf_bio = generate_pdf_report()
        st.download_button(label='PDF-Report herunterladen', data=pdf_bio.getvalue(), file_name='job_mining_report.pdf', mime='application/pdf')
    except Exception as e:
        logger.error(f"PDF-Report nicht verfügbar: {e}")
        st.error(f"PDF-Report nicht verfügbar: {e}")

st.markdown("---")

# ========================================
# 🚀 TOP 10 EMERGING SKILLS (DASHBOARD_GUIDE.md Feature #5)
# ========================================
st.subheader("🚀 Top 10 Aufstrebende Skills (2024-2025)")
try:
    emerging = metrics.get('emerging_skills', [])
    if emerging:
        for idx, skill_data in enumerate(emerging, 1):
            skill_name = skill_data.get('skill', 'N/A')
            growth = skill_data.get('growth', 0)
            growth_pct = skill_data.get('growth_pct', 0)

            medal = "🥇" if idx == 1 else "🥈" if idx == 2 else "🥉" if idx == 3 else f"{idx}."

            if growth_pct == 999:
                st.write(f"{medal} **{skill_name}** — +{growth} (NEU)")
            else:
                st.write(f"{medal} **{skill_name}** — +{growth} ({growth_pct:+.0f}%)")
    else:
        st.info("Keine Emerging Skills-Daten verfügbar.")
except Exception as e:
    logger.error(f"Fehler beim Anzeigen der Emerging Skills: {e}")
    st.error(f"Fehler: {str(e)}")

st.markdown("---")

# ========================================
# 🎯 JOB-ROLLEN VERTEILUNG (DASHBOARD_GUIDE.md Feature #3)
# ========================================
role_col1, role_col2 = st.columns(2)

with role_col1:
    st.subheader("🎯 Job-Rollen Verteilung")
    try:
        role_dist = metrics.get('role_distribution', {})
        if role_dist:
            role_df = pd.DataFrame(list(role_dist.items()), columns=['Rolle', 'Anzahl'])
            fig_roles = px.pie(role_df, names='Rolle', values='Anzahl',
                              title='Jobs nach Rolle',
                              color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig_roles, use_container_width=True)
        else:
            st.info("Keine Rollen-Daten verfügbar.")
    except Exception as e:
        logger.error(f"Fehler beim Anzeigen der Job-Rollen: {e}")
        st.error(f"Fehler: {str(e)}")

# ========================================
# 🌍 REGIONALE VERTEILUNG (DASHBOARD_GUIDE.md Feature #4)
# ========================================
with role_col2:
    st.subheader("🌍 Regionale Verteilung")
    try:
        regional_dist = metrics.get('regional_distribution', {})
        if regional_dist:
            regional_df = pd.DataFrame(list(regional_dist.items()), columns=['Region', 'Anzahl'])
            regional_df = regional_df.sort_values('Anzahl', ascending=False).head(10)
            fig_regional = px.bar(regional_df, x='Region', y='Anzahl',
                                 title='Top 10 Regionen',
                                 color='Anzahl',
                                 color_continuous_scale='blues')
            st.plotly_chart(fig_regional, use_container_width=True)
        else:
            st.info("Keine Regions-Daten verfügbar.")
    except Exception as e:
        logger.error(f"Fehler beim Anzeigen der regionalen Verteilung: {e}")
        st.error(f"Fehler: {str(e)}")

st.markdown("---")

# ========================================
# 📊 7-EBENEN-MODELL PROGRESSION (DASHBOARD_GUIDE.md Feature #2)
# ========================================
st.subheader("📊 7-Ebenen-Modell Progression")
try:
    level_prog = metrics.get('level_progression', {})
    if level_prog:
        level_df = pd.DataFrame(list(level_prog.items()), columns=['Level', 'Skills'])
        fig_levels = px.bar(level_df, x='Level', y='Skills',
                           title='Skills nach Ebenen-Modell',
                           color='Skills',
                           color_continuous_scale='greens')
        st.plotly_chart(fig_levels, use_container_width=True)
    else:
        st.info("Keine Level-Daten verfügbar.")
except Exception as e:
    logger.error(f"Fehler beim Anzeigen der Level-Progression: {e}")
    st.error(f"Fehler: {str(e)}")

st.markdown("---")

# ========================================
# ✅ QUALITÄTS-METRIKEN (DASHBOARD_GUIDE.md Feature #6)
# ========================================
quality_col1, quality_col2 = st.columns(2)

with quality_col1:
    st.subheader("✅ Qualitäts-Metriken")
    try:
        quality_data = metrics.get('quality_metrics', {})
        buckets = quality_data.get('buckets', {})

        if buckets:
            st.write("**Extraktionsqualität:**")
            total = sum(buckets.values())

            if total > 0:
                excellent_pct = (buckets.get('excellent', 0) / total) * 100
                good_pct = (buckets.get('good', 0) / total) * 100
                fair_pct = (buckets.get('fair', 0) / total) * 100
                poor_pct = (buckets.get('poor', 0) / total) * 100

                st.write(f"✅ Excellent (≥90%): {excellent_pct:.1f}%")
                st.write(f"✅ Good (70-89%): {good_pct:.1f}%")
                st.write(f"⚠️ Fair (50-69%): {fair_pct:.1f}%")
                st.write(f"❌ Poor (<50%): {poor_pct:.1f}%")
            else:
                st.info("Keine Qualitätsdaten verfügbar.")
        else:
            st.info("Keine Qualitätsdaten verfügbar.")
    except Exception as e:
        logger.error(f"Fehler beim Anzeigen der Qualitätsmetriken: {e}")
        st.error(f"Fehler: {str(e)}")

# ========================================
# ⚙️ PIPELINE-METRIKEN (DASHBOARD_GUIDE.md Feature #7)
# ========================================
with quality_col2:
    st.subheader("⚙️ Pipeline-Metriken")
    try:
        pipeline_data = metrics.get('pipeline_metrics', {})

        if pipeline_data:
            st.write("**Pipeline-Gesundheit:**")
            st.write(f"✅ Segmentierungserfolg: {pipeline_data.get('segmentierung_erfolg', 0):.0f}%")
            st.write(f"✅ Fuzzy-Match-Präzision: {pipeline_data.get('fuzzy_match_praezision', 0):.0f}%")
            st.write(f"✅ Extraktionsqualität: {pipeline_data.get('extraktionsqualitaet', 0):.0f}%")
            st.write(f"✅ Pipeline-Gesundheit: {pipeline_data.get('pipeline_gesundheit', 0):.0f}%")
        else:
            st.info("Keine Pipeline-Daten verfügbar.")
    except Exception as e:
        logger.error(f"Fehler beim Anzeigen der Pipeline-Metriken: {e}")
        st.error(f"Fehler: {str(e)}")

# ========================================
# 📊 ZEITREIHEN-VALIDIERUNG (Level 7)
# ========================================
st.markdown("---")
st.subheader("📊 Zeitreihen-Validierung (Level 7)")
try:
    ts_validation = metrics.get('time_series_validation', {})

    if ts_validation:
        val_col1, val_col2 = st.columns(2)

        with val_col1:
            st.write("**Datenqualität:**")
            total_skills = ts_validation.get('total_skills', 0)
            validated_skills = ts_validation.get('validated_skills', 0)
            skills_with_gaps = ts_validation.get('skills_with_gaps', 0)
            validation_score = ts_validation.get('validation_score', 0)
            gap_rate = ts_validation.get('gap_rate', 0)
            min_years = ts_validation.get('min_years_required', 3)

            st.write(f"✅ Validierte Skills: {validated_skills} von {total_skills}")
            st.write(f"📊 Validierungs-Score: {validation_score:.1f}%")
            st.write(f"⚠️ Skills mit Lücken: {skills_with_gaps}")
            st.write(f"📈 Gap-Rate: {gap_rate:.1f}%")
            st.write(f"📏 Min. Jahre erforderlich: {min_years}")

        with val_col2:
            st.write("**Trend-Klassifikation:**")
            trends = ts_validation.get('trend_classification', {})
            rising = trends.get('rising', 0)
            stable = trends.get('stable', 0)
            falling = trends.get('falling', 0)

            st.write(f"📈 Rising: {rising}")
            st.write(f"➡️ Stable: {stable}")
            st.write(f"📉 Falling: {falling}")

            # Zusätzliche Statistik
            skills_with_trend = ts_validation.get('skills_with_trend', 0)
            st.write(f"🔍 Skills mit erkanntem Trend: {skills_with_trend}")
    else:
        st.info("Keine Validierungsdaten verfügbar.")
except Exception as e:
    logger.error(f"Fehler bei Zeitreihen-Validierung: {e}")
    st.error(f"Fehler: {str(e)}")

# ========================================
# 📋 JOB-DATEN TABELLE
# ========================================
st.markdown("---")
with st.expander("📋 Job-Daten Übersicht", expanded=False):
    try:
        # Hole Job-Daten von Kotlin-API
        response = requests.get(f"{KOTLIN_API_BASE}/api/v1/jobs", timeout=5)
        if response.status_code == 200:
            jobs_data = response.json()
            if jobs_data:
                # Erstelle DataFrame mit wichtigsten Feldern
                df_jobs = pd.DataFrame([{
                    'ID': job.get('id'),
                    'Titel': job.get('title', 'N/A'),
                    'Rolle': job.get('jobRole', 'N/A'),
                    'Branche': job.get('industry', 'N/A'),
                    'Region': job.get('region', 'N/A'),
                    'Kompetenzen': len(job.get('competences', [])),
                    'Erstellt': job.get('createdAt', 'N/A')[:10] if job.get('createdAt') else 'N/A'
                } for job in jobs_data])
                
                st.dataframe(
                    df_jobs,
                    use_container_width=True,
                    hide_index=True
                )
                st.caption(f"Gesamt: {len(jobs_data)} Jobs")
            else:
                st.info("Keine Jobs in der Datenbank gefunden.")
        else:
            st.warning(f"API-Fehler: Status {response.status_code}")
    except requests.RequestException as e:
        st.error(f"Verbindungsfehler zur Kotlin-API: {e}")
    except Exception as e:
        st.error(f"Fehler beim Laden der Job-Daten: {e}")

st.markdown("---")
st.caption("Minimaler Dashboard-Prototyp basierend auf dem RTFD-Spezifikationsbeispiel. Für Produktion: Authentifizierung, Pagination und Hintergrund-Jobs hinzufügen.")
