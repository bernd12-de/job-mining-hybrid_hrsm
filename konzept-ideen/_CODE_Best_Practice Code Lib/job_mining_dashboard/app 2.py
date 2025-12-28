import streamlit as st
import pandas as pd
import json
import plotly.express as px
import os

st.set_page_config(page_title="Job Mining Dashboard", layout="wide")

st.title("📊 Job Mining Model Comparison Dashboard")
st.markdown("Visualisierung der Ergebnisse aus RapidFuzz, MiniLM und MultiLM Matching.")

# --- Load data ---
default_csv = "job_mining/outputs/model_comparison.csv"
default_json = "job_mining/outputs/jobs_mapped.json"

@st.cache_data
def load_data(csv_path, json_path):
    df_csv = pd.read_csv(csv_path)
    with open(json_path, "r", encoding="utf-8") as f:
        data_json = json.load(f)
    return df_csv, data_json

if not os.path.exists(default_csv) or not os.path.exists(default_json):
    st.error("⚠️ Ergebnisdateien wurden nicht gefunden. Bitte stelle sicher, dass 'job_mining/outputs/' vorhanden ist.")
    st.stop()

df, data_json = load_data(default_csv, default_json)

# --- Sidebar ---
st.sidebar.header("⚙️ Filter & Optionen")
keywords = sorted(df["keyword"].unique())
selected_kw = st.sidebar.multiselect("Filter nach Keyword(s)", keywords, default=[])

if selected_kw:
    df_filtered = df[df["keyword"].isin(selected_kw)]
else:
    df_filtered = df

# --- KPIs ---
col1, col2, col3 = st.columns(3)
col1.metric("Gesamt Keywords", len(df))
col2.metric("Durchschnitt RapidFuzz", round(df["rapidfuzz"].mean(), 2))
col3.metric("Durchschnitt MiniLM", round(df["miniLM"].mean(), 3))

st.divider()

# --- Modellvergleich ---
st.subheader("🔍 Modellvergleich (RapidFuzz vs MiniLM vs MultiLM)")
fig = px.scatter(df_filtered, x="miniLM", y="multiLM",
                 color="best_model",
                 hover_data=["keyword", "rapidfuzz"],
                 title="Vergleich der Modell-Scores (MiniLM vs MultiLM)")
st.plotly_chart(fig, use_container_width=True)

# --- Score-Verteilung ---
st.subheader("📈 Score-Verteilungen")
col1, col2, col3 = st.columns(3)
col1.plotly_chart(px.histogram(df_filtered, x="rapidfuzz", nbins=20, title="RapidFuzz"), use_container_width=True)
col2.plotly_chart(px.histogram(df_filtered, x="miniLM", nbins=20, title="MiniLM"), use_container_width=True)
col3.plotly_chart(px.histogram(df_filtered, x="multiLM", nbins=20, title="MultiLM"), use_container_width=True)

# --- Häufigste Best-Model Ergebnisse ---
st.subheader("🏆 Modell-Häufigkeit")
model_counts = df_filtered["best_model"].value_counts().reset_index()
model_counts.columns = ["Modell", "Anzahl"]
st.plotly_chart(px.pie(model_counts, values="Anzahl", names="Modell", title="Bestes Modell nach Keywords"))

# --- Export ---
st.download_button(
    label="📥 Gefilterte Daten als CSV herunterladen",
    data=df_filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_model_comparison.csv",
    mime="text/csv",
)
