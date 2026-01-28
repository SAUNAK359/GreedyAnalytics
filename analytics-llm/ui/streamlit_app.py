import streamlit as st
from auth_ui import login_ui
from dashboard_ui import render_dashboard

st.set_page_config(layout="wide")
login_ui()
render_dashboard()
