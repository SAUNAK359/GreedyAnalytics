#!/usr/bin/env bash
set -e
cd /workspaces/GreedyAnalytics/analytics-llm
set -a
. ./.env
set +a
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000
