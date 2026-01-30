import streamlit as st


def render_versioning_ui() -> None:
    st.markdown("---")
    st.header("Versioning & Rollback")

    versions = st.session_state.get("mcp_versions", [])
    if not versions:
        st.info("No MCP versions yet.")
        return

    labels = [f"{v['version_label']} ({v.get('created_at', 'unknown')})" for v in versions]
    selected = st.selectbox("Select version", options=labels)
    if st.button("Rollback"):
        for v in versions:
            if f"{v['version_label']} ({v.get('created_at', 'unknown')})" == selected:
                st.session_state["active_mcp"] = v["mcp"]
                st.success(f"Rolled back to {selected}")
                break
