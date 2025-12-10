#!/bin/bash
# ===========================================
# DEPLOY SCRIPT - AI Vector Search Demo
# ===========================================
# This script deploys the application with auto-restart capabilities
# using start_demo.sh which includes watchdog monitoring

set -e

# Detect if running in CI/CD environment
if [ -n "$GITHUB_WORKSPACE" ]; then
    PROJECT_DIR="$GITHUB_WORKSPACE"
else
    PROJECT_DIR="/srv/poc_elastik"
fi

cd "$PROJECT_DIR"

echo "=============================================="
echo "   AI Vector Search Demo - Deployment Script"
echo "=============================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 1. Check/Start Elasticsearch
echo -e "${YELLOW}[1/4] Checking Elasticsearch...${NC}"
if curl -s http://localhost:9200 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Elasticsearch is running${NC}"
else
    echo "Starting Elasticsearch..."
    docker start es-demo 2>/dev/null || docker run -d --name es-demo \
        -p 9200:9200 -p 9300:9300 \
        -e "discovery.type=single-node" \
        -e "xpack.security.enabled=false" \
        docker.elastic.co/elasticsearch/elasticsearch:8.15.0
    sleep 10
    echo -e "${GREEN}✅ Elasticsearch started${NC}"
fi

# 2. Stop existing services
echo -e "${YELLOW}[2/4] Stopping existing services...${NC}"
if [ -f "stop_demo.sh" ]; then
    chmod +x stop_demo.sh
    ./stop_demo.sh 2>/dev/null || true
else
    # Fallback manual cleanup
    pkill -f "[w]atchdog.sh" 2>/dev/null || true
    pkill -f "[u]vicorn main:app" 2>/dev/null || true
    pkill -f "[s]treamlit run" 2>/dev/null || true
    pkill -f "[n]grok http" 2>/dev/null || true
fi
sleep 2
echo -e "${GREEN}✅ Old services stopped${NC}"

# 2.5. Clear Python cache to ensure fresh code is loaded
echo -e "${YELLOW}[2.5/4] Clearing Python cache...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
echo -e "${GREEN}✅ Python cache cleared${NC}"

# 3. Install/Update dependencies
echo -e "${YELLOW}[3/4] Installing dependencies...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install -q -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"

# 4. Start all services with watchdog auto-restart
echo -e "${YELLOW}[4/4] Starting services with auto-restart...${NC}"
chmod +x start_demo.sh
chmod +x watchdog.sh
./start_demo.sh

# Wait for services to be ready
sleep 5

# Verify services are running
echo ""
echo -e "${BLUE}Verifying services...${NC}"

if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✅ FastAPI is running on port 8000${NC}"
else
    echo -e "${RED}❌ FastAPI not responding. Check logs/fastapi.log${NC}"
fi

if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Streamlit is running on port 8501${NC}"
else
    echo -e "${RED}❌ Streamlit not responding. Check logs/streamlit.log${NC}"
fi

if ps aux | grep -v grep | grep "watchdog.sh" > /dev/null; then
    echo -e "${GREEN}✅ Watchdog is monitoring (auto-restart enabled)${NC}"
else
    echo -e "${YELLOW}⚠️  Watchdog not detected${NC}"
fi

echo ""
echo "=============================================="
echo -e "${GREEN}   ✅ DEPLOYMENT COMPLETED!${NC}"
echo "=============================================="
echo ""
echo -e "${BLUE}📍 SERVICE URLS:${NC}"
echo "   Streamlit UI: http://localhost:8501"
echo "   API Swagger:  http://localhost:8000/docs"
echo "   API Health:   http://localhost:8000/health"
echo ""
echo -e "${BLUE}📊 LOGS:${NC}"
echo "   FastAPI:   logs/fastapi.log"
echo "   Streamlit: logs/streamlit.log"
echo "   Watchdog:  logs/watchdog.log"
echo ""
echo -e "${BLUE}🔍 MONITORING:${NC}"
echo "   Watch logs:      tail -f logs/watchdog.log"
echo "   Check status:    curl http://localhost:8000/health"
echo "   Stop services:   ./stop_demo.sh"
echo ""
echo -e "${GREEN}🎉 Watchdog auto-restart is ACTIVE!${NC}"
echo "   - Monitors every 30 seconds"
echo "   - Auto-restarts on crash/hang"
echo "   - Max 5 restarts per hour"
echo ""
echo "=============================================="
