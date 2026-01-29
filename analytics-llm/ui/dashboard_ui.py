import os
import sys
import streamlit as st
import requests
from auth.rbac import authorize

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from backend.app import dashboard_current as _backend_dashboard_current

API_URL = os.getenv("API_URL", "http://analytics-api:8000")
MOCK_MODE = os.getenv("MOCK_BACKEND", "true").lower() == "true"

def _mock_dashboard(tenant_id="demo"):
    return _backend_dashboard_current(
        authorization="Bearer mock",
        x_tenant_id=tenant_id
    )

def render_dashboard():
    if "auth" not in st.session_state:
        st.warning("Please login")
        return

    auth = st.session_state["auth"]

    st.title("📊 Analytics@LLM Dashboard")

    headers = {
        "Authorization": f"Bearer {auth['access_token']}",
        "X-Tenant-ID": auth["tenant_id"]
    }

    dashboard = None

    if not MOCK_MODE:
        try:
            resp = requests.get(
                f"{API_URL}/dashboard/current",
                headers=headers,
                timeout=2
            )
        except requests.RequestException:
            resp = None
    else:
        resp = None

    if resp is None or resp.status_code != 200:
        st.info("Using mock dashboard data.")
        dashboard = _mock_dashboard(auth.get("tenant_id", "demo"))
    else:
        try:
            dashboard = resp.json()
            if not isinstance(dashboard, dict) or "components" not in dashboard:
                raise ValueError("Invalid dashboard payload")
        except (ValueError, TypeError):
            st.info("Using mock dashboard data.")
            dashboard = _mock_dashboard(auth.get("tenant_id", "demo"))

    for component in dashboard["components"]:
        if component["type"] == "line":
            st.line_chart(component["data"])

        elif component["type"] == "bar":
            st.bar_chart(component["data"])

        elif component["type"] == "table":
            st.dataframe(component["data"])

    if authorize(auth["role"], "edit"):
        st.subheader("🛠 Modify Dashboard")
        feedback = st.text_input("Describe changes")

        if st.button("Apply"):
            if MOCK_MODE:
                st.success("Mock update recorded.")
                return
            try:
                requests.post(
                    f"{API_URL}/dashboard/feedback",
                    headers=headers,
                    json={"feedback": feedback},
                    timeout=2
                )
            except requests.RequestException:
                st.warning("Backend unavailable for updates.")
            else:
                st.success("Dashboard update requested")
