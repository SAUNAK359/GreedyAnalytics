#!/usr/bin/env bash
set -e
cd /workspaces/GreedyAnalytics
set -a
. ./.env
set +a
python -m uvicorn analytics_llm.backend.app:app --host 0.0.0.0 --port 8000
