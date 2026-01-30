import os
from typing import Dict, Any, Optional

import requests
import streamlit as st


def api_url() -> str:
    secrets = st.secrets if hasattr(st, "secrets") else {}
    secret_url = secrets.get("API_URL") if secrets else None
    return (secret_url or os.getenv("API_URL", "http://api:8000")).rstrip("/")


def _auth_headers() -> Dict[str, str]:
    headers: Dict[str, str] = {}
    auth = st.session_state.get("auth")
    if auth and auth.get("access_token"):
        headers["Authorization"] = f"Bearer {auth['access_token']}"
    gemini_key = st.session_state.get("gemini_api_key")
    if gemini_key:
        headers["X-GEMINI-API-KEY"] = gemini_key
    return headers


def login(email: str, password: str) -> Dict[str, Any]:
    resp = requests.post(
        f"{api_url()}/api/v1/auth/login",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={"username": email, "password": password},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def register(payload: Dict[str, Any]) -> Dict[str, Any]:
    resp = requests.post(
        f"{api_url()}/api/v1/auth/register",
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def query(payload: Dict[str, Any]) -> Dict[str, Any]:
    resp = requests.post(
        f"{api_url()}/api/v1/query",
        headers=_auth_headers(),
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()


def add_datasource(payload: Dict[str, Any]) -> Dict[str, Any]:
    resp = requests.post(
        f"{api_url()}/api/v1/datasources",
        headers=_auth_headers(),
        json=payload,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def list_datasources() -> Dict[str, Any]:
    resp = requests.get(
        f"{api_url()}/api/v1/datasources",
        headers=_auth_headers(),
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def logout() -> Optional[Dict[str, Any]]:
    resp = requests.post(
        f"{api_url()}/api/v1/auth/logout",
        headers=_auth_headers(),
        timeout=30,
    )
    if resp.status_code >= 400:
        return None
    return resp.json()
