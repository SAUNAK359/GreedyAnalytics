import streamlit as st
import requests

from analytics_llm.frontend.ui import api


def _handle_login(email: str, password: str) -> None:
    try:
        data = api.login(email, password)
        st.session_state["auth"] = data
        # Safely set user_role, checking if the session state key is writable
        try:
             st.session_state["user_role"] = data.get("user", {}).get("role", "viewer")
        except Exception:
            # If user_role is somehow reserved or immutable (unlikely), default to variable
            pass
        st.success("Logged in")
    except requests.RequestException as exc:
        msg = str(exc)
        error_details = ""
        if exc.response is not None:
            try:
                detail = exc.response.json().get("detail")
                if detail:
                    error_details = f": {detail}"
            except Exception:
                pass

        if "Name or service not known" in msg or "Failed to resolve" in msg:
            st.error(
                "Connection failed: Cannot resolve backend hostname. "
                "If running locally, ensure the backend is running. "
                "If deployed, set 'API_URL' in secrets to your backend URL."
            )
        else:
            st.error(f"Login failed{error_details}")


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
        msg = str(exc)
        error_details = ""
        if exc.response is not None:
            try:
                # Try to get the detailed error message from the JSON response
                detail = exc.response.json().get("detail")
                if detail:
                    error_details = f": {detail}"
            except Exception:
                pass

        if "Name or service not known" in msg or "Failed to resolve" in msg:
            st.error(
                "Connection failed: Cannot resolve backend hostname. "
                "If running locally, ensure the backend is running. "
                "If deployed, set 'API_URL' in secrets to your backend URL."
            )
        else:
            st.error(f"Registration failed{error_details}")


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
