#!/usr/bin/env bash
set -e
cd /workspaces/GreedyAnalytics/analytics-llm
set -a
. ./.env
set +a
streamlit run ui/streamlit_app.py --server.port "${STREAMLIT_SERVER_PORT:-8501}" --server.address "${STREAMLIT_SERVER_ADDRESS:-0.0.0.0}"
