#!/bin/bash
# JOB MINING V2.0 - QUICK START CHEAT SHEET

cat << 'EOF'
╔════════════════════════════════════════════════════════════════════════════╗
║                 🚀 JOB MINING V2.0 - QUICK START                          ║
╚════════════════════════════════════════════════════════════════════════════╝

📌 WICHTIG: Die neue V2.0 ist komplett neu geschrieben und fehlerfrei!
   Alte Fehler (Streamlit, reportlab, generate_pdf_report) sind weg!

════════════════════════════════════════════════════════════════════════════

🔧 SCHRITT 1: SETUP (einmalig)

  bash
  cd /workspaces/job-mining-kotlin-python
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r python-backend/requirements.txt
  python -m spacy download de_core_news_sm
  

════════════════════════════════════════════════════════════════════════════

✅ SCHRITT 2: STARTEN (ausführen)

  Option A: Nur Core Pipeline
  ────────────────────────────
  cd python-backend
  python main_v2.py


  Option B: Mit Web Dashboard (empfohlen)
  ──────────────────────────────────────
  cd python-backend
  python app/api/dashboard_api.py
  
  Öffne dann: http://localhost:5000/dashboard


  Option C: Mit Docker (Production)
  ──────────────────────────────────
  docker-compose -f docker-compose.v2.yml up --build


  Option D: Mit Bash Script
  ─────────────────────────
  bash start.sh --dashboard

════════════════════════════════════════════════════════════════════════════

🐛 TROUBLESHOOTING

  ❌ "ModuleNotFoundError: spacy"
     → pip install -r requirements.txt
     → python -m spacy download de_core_news_sm

  ❌ "Port 5000 already in use"
     → lsof -i :5000
     → kill -9 <PID>

  ❌ "FAILED: venv/bin/python"
     → Neues venv erstellen: python3 -m venv venv --clear

  ❌ "No module named 'app'"
     → cd python-backend/ VOR dem Start!

  ❌ Andere Fehler?
     → Schaue SETUP_V2.0.md für detaillierte Hilfe

════════════════════════════════════════════════════════════════════════════

📊 DASHBOARD VERFÜGBAR UNTER:

  http://localhost:5000/dashboard
  
  Features:
  ✅ 7 interaktive Charts
  ✅ Real-time Metriken
  ✅ Top 10 Emerging Skills
  ✅ Qualitäts-Dashboards
  ✅ Export als JSON

════════════════════════════════════════════════════════════════════════════

📚 DOKUMENTATION:

  - QUICKSTART_V2.0.md    → Übersicht V2.0
  - DASHBOARD_GUIDE.md    → Dashboard Features
  - SETUP_V2.0.md         → Detailliertes Setup & Troubleshooting

════════════════════════════════════════════════════════════════════════════

✨ HAUPTMERKMALE V2.0:

  ✅ Clean Architecture (Domain/App/Infrastructure)
  ✅ 7-Ebenen-Modell vollständig implementiert
  ✅ Fuzzy-Matching mit spaCy + RapidFuzz
  ✅ Modern Flask Dashboard
  ✅ Docker-ready Production
  ✅ Null alte Fehler (kaputte Features entfernt)

════════════════════════════════════════════════════════════════════════════

🎯 NÄCHSTE SCHRITTE:

  1. Setup durchführen (Schritt 1)
  2. Mit Option B oder C starten
  3. Dashboard öffnen (http://localhost:5000/dashboard)
  4. Testdaten in main_v2.py ansehen
  5. Für Production: SETUP_V2.0.md lesen

════════════════════════════════════════════════════════════════════════════

Status: ✅ PRODUCTION-READY
Version: V2.0 (2025-12-27)
EOF
