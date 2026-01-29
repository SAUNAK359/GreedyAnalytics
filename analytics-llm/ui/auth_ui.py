import os
import streamlit as st
import requests

API_URL = os.getenv("API_URL", "http://analytics-api:8000")
MOCK_MODE = os.getenv("MOCK_BACKEND", "true").lower() == "true"

def _fallback_login(email: str) -> None:
    st.session_state["auth"] = {
        "access_token": "mock-token",
        "role": "analyst",
        "tenant_id": "demo"
    }
    st.sidebar.success(f"Logged in as {email} (mock)")
    st.rerun()

def login_ui():
    if "auth" in st.session_state:
        return

    st.sidebar.title("🔐 Login")

    email = st.sidebar.text_input("Email", value="demo@analytics.local")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        try:
            resp = requests.post(
                f"{API_URL}/auth/login",
                data={
                    "username": email,
                    "password": password
                },
                timeout=2
            )
        except requests.RequestException:
            _fallback_login(email)
            return

        if resp.status_code == 200:
            try:
                data = resp.json()
                access_token = data["access_token"]
            except (ValueError, KeyError, TypeError):
                st.sidebar.error("Invalid response from backend")
                if MOCK_MODE:
                    _fallback_login(email)
                return

            st.session_state["auth"] = {
                "access_token": access_token,
                "role": data.get("role", "analyst"),
                "tenant_id": data.get("tenant_id", "demo")
            }

            st.sidebar.success("Login successful")
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")
