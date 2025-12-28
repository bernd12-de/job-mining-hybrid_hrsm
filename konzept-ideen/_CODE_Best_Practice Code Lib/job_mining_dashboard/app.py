import streamlit as st
import pandas as pd
import plotly.express as px
import networkx as nx
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Job Mining Dashboard", layout="wide")
st.title("📊 Job Mining Dashboard – Stages 2 & 3")

tab1, tab2 = st.tabs(["Model Comparison", "Skill Evolution"])

with tab1:
    st.subheader("Stage 2: Dual Model Comparison")
    path = "../job_mining/outputs/stage2/model_comparison.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        st.plotly_chart(px.scatter(df, x="miniLM", y="multiLM", color="best_model"), use_container_width=True)
    else:
        st.warning("Keine Stage 2 Ergebnisse gefunden.")

with tab2:
    st.subheader("Stage 3: Skill Evolution & ESCO Mapping")
    path = "../job_mining/outputs/stage3/skill_evolution.csv"
    if os.path.exists(path):
        df = pd.read_csv(path)
        st.plotly_chart(px.bar(df, x="occupation", y="skill_count"), use_container_width=True)
    else:
        st.warning("Keine Stage 3 Ergebnisse gefunden.")
