#!/usr/bin/env bash
set -e
cd /workspaces/GreedyAnalytics
set -a
. ./.env
set +a
PYTHONPATH="/workspaces/GreedyAnalytics" streamlit run analytics_llm/frontend/app.py --server.port "${STREAMLIT_SERVER_PORT:-8501}" --server.address "${STREAMLIT_SERVER_ADDRESS:-0.0.0.0}"
