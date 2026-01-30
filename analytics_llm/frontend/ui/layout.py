import os
import streamlit as st


def _init_page() -> None:
    st.set_page_config(
        page_title="Analytics@LLM",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="collapsed",
    )


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        .copilot-fab {
            position: fixed;
            bottom: 24px;
            left: 24px;
            z-index: 1000;
        }
        .top-bar {
            padding: 8px 12px;
            border: 1px solid #E6E6E6;
            border-radius: 12px;
            margin-bottom: 12px;
            background: #FFFFFF;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _api_key_inputs() -> None:
    secrets = st.secrets if hasattr(st, "secrets") else {}
    gemini_default = secrets.get("GEMINI_API_KEY", "") if secrets else os.getenv("GEMINI_API_KEY", "")
    openai_default = secrets.get("OPENAI_API_KEY", "") if secrets else os.getenv("OPENAI_API_KEY", "")

    col1, col2 = st.columns(2)
    with col1:
        st.text_input(
            "Gemini API Key",
            type="password",
            key="gemini_api_key",
            value=st.session_state.get("gemini_api_key", gemini_default),
            help="Used for Google AI Studio / Gemini calls. Stored only in session.",
        )
    with col2:
        st.text_input(
            "OpenAI API Key",
            type="password",
            key="openai_api_key",
            value=st.session_state.get("openai_api_key", openai_default),
            help="Optional fallback LLM. Stored only in session.",
        )


def render_layout() -> None:
    _init_page()
    _inject_css()

    st.title("ANALYTICS@LLM")
    st.caption("Enterprise-Grade Intelligent Agentic Analytics Platform")

    with st.container():
        st.markdown('<div class="top-bar">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            datasets = list(st.session_state.get("datasets", {}).keys())
            active = st.session_state.get("active_dataset")
            label = ", ".join(datasets) if datasets else "No datasets loaded"
            st.markdown(f"**Dataset Context:** {label}")
            if datasets:
                st.session_state["active_dataset"] = st.selectbox(
                    "Active Dataset",
                    options=datasets,
                    index=datasets.index(active) if active in datasets else 0,
                    label_visibility="collapsed",
                )
        with col2:
            versions = st.session_state.get("mcp_versions", [])
            if versions:
                labels = [v["version_label"] for v in versions]
                st.selectbox("MCP Version", options=labels, key="active_version_label")
            else:
                st.markdown("**Version:** v3 (initial)")
        with col3:
            role = st.session_state.get("user_role", "analyst")
            st.selectbox("Role", ["viewer", "analyst", "admin"], index=["viewer", "analyst", "admin"].index(role), key="user_role")
        st.markdown("</div>", unsafe_allow_html=True)

    _api_key_inputs()

    gemini_key = st.session_state.get("gemini_api_key") or os.getenv("GEMINI_API_KEY", "")
    openai_key = st.session_state.get("openai_api_key") or os.getenv("OPENAI_API_KEY", "")
    if not gemini_key and not openai_key:
        st.warning("Mock mode enabled: no LLM API keys configured.")

    st.markdown(
        "<div class='copilot-fab'>" +
        "</div>",
        unsafe_allow_html=True,
    )
