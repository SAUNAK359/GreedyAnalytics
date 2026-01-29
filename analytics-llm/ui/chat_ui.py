import os
import streamlit as st
import requests


def _api_url() -> str:
    return os.getenv("API_URL", "http://localhost:8000").rstrip("/")


def chat():
    if "auth" not in st.session_state:
        st.warning("Please login to use chat")
        return

    st.subheader("💬 Ask Analytics")

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    for entry in st.session_state["chat_history"]:
        with st.chat_message("user"):
            st.markdown(entry["question"])
        with st.chat_message("assistant"):
            st.markdown(entry["answer"])

    msg = st.chat_input("Ask analytics question")
    if msg:
        auth = st.session_state["auth"]
        headers = {"Authorization": f"Bearer {auth['access_token']}"}
        gemini_key = st.session_state.get("gemini_api_key")
        if gemini_key:
            headers["X-GEMINI-API-KEY"] = gemini_key
        
        with st.chat_message("user"):
            st.markdown(msg)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            placeholder.markdown("Thinking...")
            try:
                resp = requests.post(
                    f"{_api_url()}/api/v1/query",
                    headers=headers,
                    json={"query": msg},
                    timeout=30
                )
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get("result", {}).get("answer", "No response")
                else:
                    answer = "Failed to process query"
            except requests.RequestException:
                answer = "API request failed"

            placeholder.markdown(answer)

        st.session_state["chat_history"].append({
            "question": msg,
            "answer": answer
        })
