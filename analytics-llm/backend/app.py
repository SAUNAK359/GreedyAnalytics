from fastapi import FastAPI, Form, Header, HTTPException
from pydantic import BaseModel

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/login")
def login(username: str = Form(...), password: str = Form(...)):
    if not username.strip() or not password.strip():
        raise HTTPException(status_code=400, detail="Username and password required")
    return {
        "access_token": "mock-token",
        "role": "analyst",
        "tenant_id": "demo"
    }

@app.get("/dashboard/current")
def dashboard_current(
    authorization: str | None = Header(default=None),
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-ID")
):
    if not authorization or not x_tenant_id:
        raise HTTPException(status_code=401, detail="Missing auth headers")
    return {
        "components": [
            {"type": "line", "data": {"sessions": [12, 18, 14, 22, 19, 25]}},
            {"type": "bar", "data": {"queries": [4, 7, 3, 9]}},
            {
                "type": "table",
                "data": [
                    {"metric": "Active Users", "value": 128},
                    {"metric": "Errors", "value": 2},
                    {"metric": "Latency (ms)", "value": 185}
                ]
            }
        ]
    }

class FeedbackPayload(BaseModel):
    feedback: str | None = None

@app.post("/dashboard/feedback")
def dashboard_feedback(payload: FeedbackPayload):
    return {"status": "received", "feedback": payload.feedback}
