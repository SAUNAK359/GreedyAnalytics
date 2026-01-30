#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=== GreedyAnalytics Enterprise Launcher ===${NC}"

# Ensure we are in the right directory
REPO_ROOT="/workspaces/GreedyAnalytics"
APP_DIR="$REPO_ROOT/analytics_llm"
cd "$REPO_ROOT"

# Load environment variables
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

PID_DIR="$APP_DIR/.pids"
mkdir -p "$PID_DIR"

stop_process() {
    local pid_file="$1"
    local name="$2"
    if [ ! -f "$pid_file" ]; then
        return
    fi

    local pid
    pid=$(cat "$pid_file")
    if ! kill -0 "$pid" 2>/dev/null; then
        rm -f "$pid_file"
        return
    fi

    echo -e "${BLUE}Stopping ${name} (PID: ${pid})...${NC}"
    kill "$pid"

    local retries=10
    while kill -0 "$pid" 2>/dev/null && [ $retries -gt 0 ]; do
        sleep 1
        retries=$((retries-1))
    done

    if kill -0 "$pid" 2>/dev/null; then
        echo -e "${RED}${name} did not stop gracefully. Force killing...${NC}"
        kill -9 "$pid"
    fi
    rm -f "$pid_file"
}

# 1. Optional cleanup (dev-only)
echo -e "${BLUE}[1/4] Checking for existing processes...${NC}"
if [ "${DEV_MODE:-0}" = "1" ]; then
    stop_process "$PID_DIR/backend.pid" "Backend API"
    stop_process "$PID_DIR/ui.pid" "Streamlit UI"
else
    echo -e "${BLUE}Skipping process cleanup (set DEV_MODE=1 to enable).${NC}"
fi

# 2. Start Backend
echo -e "${BLUE}[2/4] Starting Backend API...${NC}"
# Run in background, redirect logs
RELOAD_FLAG=""
if [ "${DEV_MODE:-0}" = "1" ]; then
    RELOAD_FLAG="--reload"
fi
nohup env PYTHONPATH="$REPO_ROOT" python -m uvicorn analytics_llm.backend.app:app --host 0.0.0.0 --port 8000 $RELOAD_FLAG > "$APP_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo "$BACKEND_PID" > "$PID_DIR/backend.pid"
echo -e "${GREEN}Backend started (PID: $BACKEND_PID). Logs at backend.log${NC}"

# 3. Wait for Backend to be healthy
echo -e "${BLUE}[3/4] Waiting for API to be ready...${NC}"
API_URL="${API_URL:-http://api:8000}"
MAX_RETRIES=30
count=0
while ! curl -s "${API_URL}/health" > /dev/null; do
    # Note: Using a lightweight check or just verifying port is open. 
    # Actually, /docs or a specific health endpoint is better.
    # But /docs might be disabled in prod settings.
    # Let's check /health (which we saw is at /health or /api/v1/meta/health)
    # The code has @app.get("/health")
    if curl -s "${API_URL}/health" | grep -q "healthy"; then
        break
    fi
    
    sleep 1
    count=$((count+1))
    if [ $count -ge $MAX_RETRIES ]; then
        echo -e "${RED}Backend failed to start. Check backend.log${NC}"
        tail -n 20 "$APP_DIR/backend.log"
        kill $BACKEND_PID
        exit 1
    fi
    echo -n "."
done
echo -e "\n${GREEN}API is Online!${NC}"

# 4. Start Frontend
echo -e "${BLUE}[4/4] Starting Streamlit Dashboard...${NC}"
nohup env PYTHONPATH="$REPO_ROOT" streamlit run analytics_llm/frontend/app.py --server.port 8501 --server.address 0.0.0.0 > "$APP_DIR/ui.log" 2>&1 &
UI_PID=$!
echo "$UI_PID" > "$PID_DIR/ui.pid"
echo -e "${GREEN}Frontend started (PID: $UI_PID). Logs at ui.log${NC}"
echo -e "${GREEN}Application is running!${NC}"
echo -e "Backend: ${API_URL}"
echo -e "Frontend: http://localhost:8501"
