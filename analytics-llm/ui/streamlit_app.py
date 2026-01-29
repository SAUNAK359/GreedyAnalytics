import os
import sys
import streamlit as st

CURRENT_DIR = os.path.dirname(__file__)
if CURRENT_DIR not in sys.path:
	sys.path.append(CURRENT_DIR)

from auth_ui import login_ui
from dashboard_ui import render_dashboard
from chat_ui import chat

st.set_page_config(
	page_title="Analytics LLM Platform",
	page_icon="📊",
	layout="wide",
	initial_sidebar_state="expanded"
)

st.title("📊 Analytics LLM Platform")
st.caption("Enterprise analytics with secure AI-driven insights")

with st.sidebar:
	st.markdown("---")
	st.subheader("🔑 LLM Access")
	st.caption("Provide your Google AI Studio API key (stored only in this session)")
	st.text_input("Google AI Studio API Key", type="password", key="gemini_api_key")

	st.markdown("---")
	st.markdown("**Author's Name:** Saunak Das Chaudhuri")
	st.markdown("**Support:** saunakdaschaudhuri4@gmail.com")

login_ui()

tab_dashboard, tab_chat = st.tabs(["Dashboard", "Chat"])

with tab_dashboard:
	render_dashboard()

with tab_chat:
	chat()
