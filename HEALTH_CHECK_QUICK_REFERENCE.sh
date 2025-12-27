#!/bin/bash

# ╔════════════════════════════════════════════════════════════════════════════════╗
# ║  HEALTH-CHECK QUICK REFERENCE                                                ║
# ║  Copy-Paste ready commands for API validation                                ║
# ╚════════════════════════════════════════════════════════════════════════════════╝

cat << 'EOF'

╔════════════════════════════════════════════════════════════════════════════════╗
║                    🔍 HEALTH-CHECK QUICK REFERENCE                            ║
╚════════════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚀 STARTUP COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  Full Startup with Health-Check:
    ./startup-with-health-check.sh

2️⃣  Quick Start (without Health-Check):
    docker-compose up -d

3️⃣  Start with Logs:
    docker-compose up

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔍 HEALTH-CHECK COMMANDS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Einmaliger Health-Check:
    ./api-health-check.sh

Kontinuierliche Überwachung (Check alle 5 Min):
    ./api-health-monitor.sh

Kontinuierliche Überwachung (Check alle 30 Sec):
    ./api-health-monitor.sh 30

Kontinuierliche Überwachung mit Alert nach 1 Fehler:
    ./api-health-monitor.sh 60 1

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 LOGS & REPORTS ANZEIGEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Health-Check Log anzeigen (aktuellste Events):
    tail -50 api-health-check.log

Health-Check Log folgen (live):
    tail -f api-health-check.log

Monitor Log anzeigen:
    cat api-health-monitor.log

Alerts anzeigen:
    cat api-health-alerts.log

Neuester Health-Report:
    cat $(ls -1rt api-health-report-*.txt | tail -1)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 TROUBLESHOOTING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Docker Services Status:
    docker ps

Docker Logs für Kotlin API:
    docker logs kotlin-api | tail -50

Docker Logs für Python Backend:
    docker logs python-backend | tail -50

Alle Docker Logs:
    docker-compose logs

Nur neue Logs (follow):
    docker-compose logs -f

Services neu starten:
    docker-compose restart

Kotlin API neu starten:
    docker-compose restart kotlin-api

Python Backend neu starten:
    docker-compose restart python-backend

Alle Docker Services stoppen:
    docker-compose down

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 ENDPOINT REGISTRY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Alle registrierten Endpoints anzeigen:
    cat .api-endpoints-registry

Nur Kotlin Endpoints:
    grep kotlin .api-endpoints-registry

Nur Python Endpoints:
    grep python .api-endpoints-registry

Endpunktanzahl zählen:
    wc -l .api-endpoints-registry  (sollte 28 sein)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 API ACCESS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Dashboard:           http://localhost:8501
Kotlin API:          http://localhost:8080
Python Backend:      http://localhost:8000
Swagger UI (Kotlin): http://localhost:8080/swagger-ui.html
API Docs (Python):   http://localhost:8000/docs

Quick API Test (Curl):
    curl http://localhost:8000/system/status
    curl http://localhost:8080/actuator/health

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚡ ADVANCED MONITORING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Starte Monitor im Hintergrund (Output zu Datei):
    ./api-health-monitor.sh > monitor.log 2>&1 &

Monitor in Screen/Tmux Session:
    screen -S health-monitor
    ./api-health-monitor.sh
    (Ctrl+A D zum Detach)

Alle laufenden Health-Monitoring Sessions:
    ps aux | grep api-health

Kill alle Monitor Sessions:
    killall api-health-monitor.sh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 WEITERE DOKUMENTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Ausführliche Dokumentation:
    cat HEALTH_CHECK_GUIDE.md

API Endpoints vollständig dokumentiert:
    cat API_ENDPOINTS.md

System Status Übersicht:
    cat V2_STATUS_REPORT.md

Alle Scripts ausführbar machen:
    chmod +x *.sh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💡 TIPP: Speichern Sie diese Referenz und verwenden Sie sie zum schnellen Zugriff
         auf die häufigsten Health-Check und Troubleshooting Befehle!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

EOF
