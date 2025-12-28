#!/bin/bash
# ========================================
# 📜 DOCKER LIVE LOGS STREAMER
# ========================================
# Zeigt Live-Logs aller Container mit Farb-Coding
# 
# VERWENDUNG:
#   ./docker-logs-live.sh              # Alle Container
#   ./docker-logs-live.sh python-backend   # Nur Python
#   ./docker-logs-live.sh kotlin-api       # Nur Kotlin
#   ./docker-logs-live.sh jobmining-db     # Nur DB
# ========================================

set -e

cd "$(dirname "$0")"

# Farben für die Ausgabe
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}📜 DOCKER LIVE LOGS STREAMER${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Prüfe ob Docker läuft
if ! docker compose ps >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose ist nicht verfügbar!${NC}"
    exit 1
fi

# Zeige Container Status
echo -e "${BLUE}📊 Container Status:${NC}"
docker compose ps
echo ""
echo -e "${YELLOW}⏳ Starte Live-Log-Streaming (Strg+C zum Beenden)...${NC}"
echo ""

# Wenn Parameter übergeben wurde, nur diesen Service
if [ -n "$1" ]; then
    echo -e "${GREEN}🔍 Logs von: $1${NC}"
    echo "=========================================="
    docker compose logs -f --tail=50 "$1"
else
    echo -e "${GREEN}🔍 Logs von: ALLE SERVICES${NC}"
    echo "=========================================="
    docker compose logs -f --tail=20
fi
