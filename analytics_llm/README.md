## Analytics@LLM

Analytics@LLM is an agentic, LLM-powered analytics platform that replaces static dashboards with conversational, self-evolving analytics artifacts. It combines deterministic execution, multi-modal ingestion, model control protocols, and governance-aware analytics into a production-grade system.

### Why Analytics@LLM Beats Power BI

Power BI is built around static dashboards and manual modeling. Analytics@LLM is an analytics IDE:

- **Agentic analytics engine**: query decomposition, deterministic execution, self-verification, explanation generation.
- **Conversational Copilot**: context-aware, page-specific assistant for anomaly explanation, metric suggestions, and dashboard mutation.
- **MCP (Model Control Protocol)**: dashboards-as-code with versioning, diffing, rollback, and deployment.
- **Memory that matters**: semantic memory of business definitions, assumptions, and prior analytical decisions.
- **Governance & trust**: PII detection, role-based redaction, policy-aware refusal.

### Core Capabilities

- Natural language → analytical plan → execution → visualization
- Planner → Executor → Verifier agents
- Multi-modal ingestion: CSV, Excel, Parquet, PDF, PPT, Word
- Vector-based semantic memory
- MCP-driven dashboard mutation
- Human-in-the-loop control
- Versioned dashboards with rollback
- Governance-aware analytics (PII, RBAC)

### Repository Structure

```
analytics_llm/
├── frontend/          # Streamlit UI (single entrypoint)
├── backend/           # FastAPI service
├── docker/            # Container definitions
├── k8s/               # Kubernetes manifests
└── scripts/           # Local run helpers
```

### Local Development

Install dependencies:

```
python -m pip install -r requirements.txt
```

Start the backend:

```
python -m uvicorn analytics_llm.backend.app:app --host 0.0.0.0 --port 8000
```

Start the UI:

```
streamlit run analytics_llm/frontend/app.py --server.port 8501 --server.address 0.0.0.0
```

Run the command from the repository root so the `analytics_llm` package is importable.

### Docker (API + UI)

```
docker compose -f docker/docker-compose.yml up --build
```

### Streamlit Cloud

- **Entry point**: analytics_llm/frontend/app.py
- **Requirements**: requirements.txt
- **Secrets / environment**:

```
API_URL=https://your-api-url
GEMINI_API_KEY=...
OPENAI_API_KEY=...
```

### Configuration (Environment Variables)

```
ENV=production
DEV_MODE=0
API_URL=http://api:8000
For local development, set:

```
API_URL=http://localhost:8000
```
JWT_SECRET=your-secret
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
OPENAI_API_KEY=...
GEMINI_API_KEY=...
```

### Reliability & Hardening

- Rate limiting
- Token budgets and cost control
- LLM fallback routing
- Retry with backoff
- Deterministic error handling
- Observability hooks

### Principles

- No static dashboards
- No duplicated logic
- No hardcoded URLs
- No fragile imports
- No hallucinated analytics
- No legacy clutter

Copilot reasons. Agents execute. MCP mutates. Humans supervise.
