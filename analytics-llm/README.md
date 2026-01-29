## Analytics LLM Platform

### Streamlit UI (Local)

1) Install UI dependencies:

```
python -m pip install -r requirements.txt
```

2) Start the UI:

```
python -m streamlit run ui/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

### Backend API (Local)

Install backend dependencies:

```
python -m pip install -r backend/requirements.txt
```

Run the API:

```
python backend/app.py
```

### Streamlit Cloud Deployment

- Set the app entry point to: `ui/streamlit_app.py`
- Set the Python requirements file to: `requirements.txt`
- Configure secrets or environment variables:

```
API_URL=https://your-api-url
```

### Environment Variables (Backend)

```
ENV=production
JWT_SECRET=your-secret
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
OPENAI_API_KEY=...
GEMINI_API_KEY=...
```
