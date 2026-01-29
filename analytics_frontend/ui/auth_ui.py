import streamlit as st
import requests

from ui import api


def _handle_login(email: str, password: str) -> None:
    try:
        data = api.login(email, password)
        st.session_state["auth"] = data
        st.session_state["user_role"] = data.get("user", {}).get("role", "viewer")
        st.success("Logged in")
    except requests.RequestException as exc:
        st.error(f"Login failed: {exc}")


def _handle_register(email: str, password: str, tenant_id: str, tenant_name: str) -> None:
    try:
        api.register({
            "email": email,
            "password": password,
            "tenant_id": tenant_id or "default",
            "tenant_name": tenant_name or "Default Tenant",
            "role": "viewer",
        })
        st.success("Registration successful. Please log in.")
    except requests.RequestException as exc:
        st.error(f"Registration failed: {exc}")


def render_auth_ui() -> None:
    if st.session_state.get("auth"):
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success("Authenticated")
        with col2:
            if st.button("Logout"):
                api.logout()
                st.session_state.pop("auth", None)
                st.rerun()
        return

    st.subheader("Sign in")
    with st.form("login-form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login")
        if submit:
            _handle_login(email, password)
            st.rerun()

    st.markdown("---")
    st.subheader("Register")
    with st.form("register-form"):
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        tenant_id = st.text_input("Tenant ID", value="default")
        tenant_name = st.text_input("Tenant Name", value="Default Tenant")
        submit = st.form_submit_button("Create account")
        if submit:
            _handle_register(reg_email, reg_password, tenant_id, tenant_name)
