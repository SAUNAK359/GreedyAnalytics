import os
import streamlit as st
import requests


def _api_url() -> str:
    return os.getenv("API_URL", "http://localhost:8000").rstrip("/")


def _authorize(role: str, action: str) -> bool:
    role_matrix = {
        "admin": {"deploy", "delete", "view", "edit"},
        "analyst": {"view", "edit"},
        "viewer": {"view"}
    }
    return action in role_matrix.get(role, set())


def render_dashboard():
    if "auth" not in st.session_state:
        st.warning("Please login")
        return

    auth = st.session_state["auth"]
    st.title("📊 Analytics@LLM Dashboard")

    headers = {
        "Authorization": f"Bearer {auth['access_token']}"
    }

    try:
        resp = requests.get(
            f"{_api_url()}/api/v1/dashboard",
            headers=headers,
            timeout=15
        )
    except requests.RequestException:
        st.error("Failed to reach API")
        return

    if resp.status_code != 200:
        st.error("Failed to load dashboard")
        return

    payload = resp.json()
    dashboard = payload.get("dashboard", {})

    for component in dashboard.get("components", []):
        if component["type"] == "metrics":
            st.subheader(component.get("title", "Metrics"))
            cols = st.columns(len(component.get("data", [])) or 1)
            for idx, metric in enumerate(component.get("data", [])):
                cols[idx].metric(metric["label"], metric["value"], metric.get("change"))

        elif component["type"] == "line":
            st.subheader(component.get("title", "Line Chart"))
            values = component.get("data", {}).get("values", [])
            st.line_chart(values)

        elif component["type"] == "bar":
            st.subheader(component.get("title", "Bar Chart"))
            values = component.get("data", {}).get("values", [])
            st.bar_chart(values)

        elif component["type"] == "table":
            st.subheader(component.get("title", "Table"))
            st.dataframe(component.get("data", []), use_container_width=True)

    if _authorize(auth.get("role", "viewer"), "edit"):
        st.subheader("🛠 Modify Dashboard")
        feedback = st.text_input("Describe changes")

        if st.button("Apply"):
            try:
                requests.post(
                    f"{_api_url()}/api/v1/dashboard/feedback",
                    headers=headers,
                    json={"feedback": feedback},
                    timeout=10
                )
                st.success("Dashboard update requested")
            except requests.RequestException:
                st.error("Failed to submit feedback")
