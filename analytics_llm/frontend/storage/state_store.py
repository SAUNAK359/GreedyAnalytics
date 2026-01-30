import os
import streamlit as st


def init_state() -> None:
    st.session_state.setdefault("datasets", {})
    st.session_state.setdefault("documents", [])
    st.session_state.setdefault("schema", {})
    st.session_state.setdefault("profiles", {})
    st.session_state.setdefault("active_dataset", None)
    st.session_state.setdefault("active_mcp", {"version": "v3", "components": [], "annotations": []})
    st.session_state.setdefault("mcp_versions", [])
    st.session_state.setdefault("chat_history", [])
    st.session_state.setdefault("copilot_open", False)
    st.session_state.setdefault("user_role", "analyst")
    st.session_state.setdefault("auth", None)

    st.session_state.setdefault("gemini_api_key", os.getenv("GEMINI_API_KEY", ""))
    st.session_state.setdefault("openai_api_key", os.getenv("OPENAI_API_KEY", ""))


def append_chat(role: str, content: str) -> None:
    st.session_state.setdefault("chat_history", []).append({"role": role, "content": content})
