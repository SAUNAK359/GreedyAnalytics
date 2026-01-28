import streamlit as st
import requests

API_URL = "http://analytics-api:8000"

def login_ui():
    if "auth" in st.session_state:
        return

    st.sidebar.title("🔐 Login")

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        resp = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": email,
                "password": password
            }
        )

        if resp.status_code == 200:
            data = resp.json()

            # ✅ Store token as opaque value
            st.session_state["auth"] = {
                "access_token": data["access_token"],
                "role": "unknown"  # role enforced server-side
            }

            st.sidebar.success("Login successful")
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")
import streamlit as st
import requests

API_URL = "http://analytics-api:8000"

def login_ui():
    if "auth" in st.session_state:
        return

    st.sidebar.title("🔐 Login")

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        resp = requests.post(
            f"{API_URL}/auth/login",
            data={
                "username": email,
                "password": password
            }
        )

        if resp.status_code == 200:
            data = resp.json()

            # ✅ Store token as opaque value
            st.session_state["auth"] = {
                "access_token": data["access_token"],
                "role": "unknown"  # role enforced server-side
            }

            st.sidebar.success("Login successful")
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")
