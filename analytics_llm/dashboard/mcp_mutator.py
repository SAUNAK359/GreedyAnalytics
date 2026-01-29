from typing import Dict, Any
import uuid
import streamlit as st


def mutate_dashboard(plan: Dict[str, Any], verified: Dict[str, Any]) -> Dict[str, Any]:
    mcp = st.session_state.get("active_mcp", {"version": "v3", "components": [], "annotations": []})

    if not verified.get("valid"):
        mcp["annotations"].append(f"Verification failed: {verified.get('reason')}")
        return mcp

    component = {
        "id": f"chart_{uuid.uuid4().hex[:6]}",
        "type": plan.get("chart_type", "table"),
        "data_source": st.session_state.get("active_dataset"),
        "x": plan.get("x"),
        "y": plan.get("y"),
        "title": plan.get("question"),
        "filters": {},
    }

    mcp["components"].append(component)
    mcp["annotations"].append("Dashboard updated via Copilot plan.")

    versions = st.session_state.get("mcp_versions", [])
    version_label = f"v{len(versions) + 1}"
    versions.append({"version_label": version_label, "mcp": mcp})
    st.session_state["mcp_versions"] = versions
    st.session_state["active_version_label"] = version_label

    return mcp
