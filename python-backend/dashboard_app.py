import streamlit as st
import pandas as pd
import plotly.express as px
import logging

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("DashboardApp")

try:
    from app.infrastructure.reporting import build_dashboard_metrics, generate_csv_report, generate_pdf_report
except ImportError as e:
    logger.error(f"❌ Fehler beim Importieren von Reporting-Modulen: {e}")
    st.error("Dashboard konnte nicht geladen werden. Bitte überprüfen Sie die Installation.")
    st.stop()

st.set_page_config(page_title="Job Mining Dashboard", layout="wide")
st.title("Job Mining — Dashboard")

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
st.caption("Minimaler Dashboard-Prototyp basierend auf dem RTFD-Spezifikationsbeispiel. Für Produktion: Authentifizierung, Pagination und Hintergrund-Jobs hinzufügen.")
