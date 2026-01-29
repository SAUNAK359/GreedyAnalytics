import os
import streamlit as st
import requests


def _api_url() -> str:
    return os.getenv("API_URL", "http://localhost:8000").rstrip("/")


def login_ui():
    st.sidebar.title("🔐 Access")

    if "auth" in st.session_state:
        user = st.session_state["auth"].get("user", {})
        st.sidebar.success(f"Logged in as {user.get('email', 'user')}")

        if st.sidebar.button("Logout"):
            _logout()
            st.rerun()
        return

    login_tab, register_tab = st.sidebar.tabs(["Login", "Register"])

    with login_tab:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login", type="primary"):
            if not email or not password:
                st.error("Email and password are required")
                return

            try:
                resp = requests.post(
                    f"{_api_url()}/api/v1/auth/login",
                    data={"username": email, "password": password},
                    timeout=10
                )

                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state["auth"] = {
                        "access_token": data.get("access_token"),
                        "refresh_token": data.get("refresh_token"),
                        "role": data.get("user", {}).get("role", "viewer"),
                        "tenant_id": data.get("user", {}).get("tenant_id", "default"),
                        "user": data.get("user", {})
                    }
                    st.success("Login successful")
                    st.rerun()
                elif resp.status_code == 429:
                    st.error("Too many attempts. Please wait and retry.")
                else:
                    st.error("Invalid credentials")
            except requests.RequestException:
                st.error("Unable to reach API. Check API_URL.")

    with register_tab:
        st.caption("Create a new account")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
        reg_tenant = st.text_input("Tenant ID", value="default", key="reg_tenant")
        reg_role = st.selectbox("Role", ["viewer", "analyst", "admin"], index=0, key="reg_role")

        if st.button("Register"):
            if not reg_email or not reg_password or not reg_confirm:
                st.error("All fields are required")
                return
            if reg_password != reg_confirm:
                st.error("Passwords do not match")
                return

            try:
                resp = requests.post(
                    f"{_api_url()}/api/v1/auth/register",
                    json={
                        "email": reg_email,
                        "password": reg_password,
                        "tenant_id": reg_tenant or "default",
                        "role": reg_role
                    },
                    timeout=10
                )

                if resp.status_code == 200:
                    st.success("Registration successful. Please log in.")
                else:
                    detail = resp.json().get("detail", "Registration failed") if resp.headers.get("content-type", "").startswith("application/json") else "Registration failed"
                    st.error(detail)
            except requests.RequestException:
                st.error("Unable to reach API. Check API_URL.")


def _logout():
    auth = st.session_state.get("auth", {})
    token = auth.get("access_token")
    if token:
        try:
            requests.post(
                f"{_api_url()}/api/v1/auth/logout",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5
            )
        except requests.RequestException:
            pass
    st.session_state.pop("auth", None)
