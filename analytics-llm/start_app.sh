#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== GreedyAnalytics Enterprise Launcher ===${NC}"

# Ensure we are in the right directory
cd /workspaces/GreedyAnalytics/analytics-llm

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

# 1. Kill any existing processes on ports 8000 (API) and 8501 (Streamlit)
echo -e "${BLUE}[1/4] Cleaning up ports...${NC}"
lsof -ti:8000 | xargs -r kill -9
lsof -ti:8501 | xargs -r kill -9
sleep 2

# 2. Start Backend
echo -e "${BLUE}[2/4] Starting Backend API...${NC}"
# Run in background, redirect logs
nohup uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}Backend started (PID: $BACKEND_PID). Logs at backend.log${NC}"

# 3. Wait for Backend to be healthy
echo -e "${BLUE}[3/4] Waiting for API to be ready...${NC}"
MAX_RETRIES=30
count=0
while ! curl -s http://localhost:8000/api/v1/auth/register > /dev/null; do
    # Note: Using a lightweight check or just verifying port is open. 
    # Actually, /docs or a specific health endpoint is better.
    # But /docs might be disabled in prod settings.
    # Let's check /health (which we saw is at /health or /api/v1/meta/health)
    # The code has @app.get("/health")
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        break
    fi
    
    sleep 1
    count=$((count+1))
    if [ $count -ge $MAX_RETRIES ]; then
        echo -e "${RED}Backend failed to start. Check backend.log${NC}"
        tail -n 20 backend.log
        kill $BACKEND_PID
        exit 1
    fi
    echo -n "."
done
echo -e "\n${GREEN}API is Online!${NC}"

# 4. Start Frontend
echo -e "${BLUE}[4/4] Starting Streamlit Dashboard...${NC}"
nohup streamlit run /workspaces/GreedyAnalytics/analytics_llm/app.py --server.port 8501 --server.address 0.0.0.0 > ui.log 2>&1 &
UI_PID=$!
echo -e "${GREEN}Frontend started (PID: $UI_PID). Logs at ui.log${NC}"
echo -e "${GREEN}Application is running!${NC}"
echo -e "Backend: http://localhost:8000"
echo -e "Frontend: http://localhost:8501"
