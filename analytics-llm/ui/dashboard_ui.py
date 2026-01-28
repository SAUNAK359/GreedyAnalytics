import streamlit as st
import requests
from auth.rbac import authorize

API_URL = "http://api:8000"

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

    resp = requests.get(
        f"{API_URL}/dashboard/current",
        headers=headers
    )

    if resp.status_code != 200:
        st.error("Failed to load dashboard")
        return

    dashboard = resp.json()

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
            requests.post(
                f"{API_URL}/dashboard/feedback",
                headers=headers,
                json={"feedback": feedback}
            )
            st.success("Dashboard update requested")
