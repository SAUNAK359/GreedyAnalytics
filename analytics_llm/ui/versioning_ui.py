import streamlit as st


def render_versioning_ui() -> None:
    st.markdown("---")
    st.header("Versioning & Rollback")

    versions = st.session_state.get("mcp_versions", [])
    if not versions:
        st.info("No MCP versions yet.")
        return

    labels = [v["version_label"] for v in versions]
    selected = st.selectbox("Select version", options=labels)
    if st.button("Rollback"):
        for v in versions:
            if v["version_label"] == selected:
                st.session_state["active_mcp"] = v["mcp"]
                st.success(f"Rolled back to {selected}")
                break
