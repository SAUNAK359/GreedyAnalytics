import streamlit as st
import requests
from auth.jwt import decode_token

API_URL = "http://api:8000"

def login_ui():
    if "auth" in st.session_state:
        return

    st.sidebar.title("🔐 Login")

    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")

    if st.sidebar.button("Login"):
        resp = requests.post(
            f"{API_URL}/auth/login",
            json={"email": email, "password": password}
        )

        if resp.status_code == 200:
            data = resp.json()
            payload = decode_token(data["access_token"])

            st.session_state["auth"] = {
                "access_token": data["access_token"],
                "refresh_token": data["refresh_token"],
                "user_id": payload["sub"],
                "tenant_id": payload["tenant_id"],
                "role": payload["role"]
            }

            st.sidebar.success(f"Welcome {email}")
            st.rerun()
        else:
            st.sidebar.error("Invalid credentials")
