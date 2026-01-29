import requests
import streamlit as st

from agents.planner import PlannerAgent
from agents.executor import ExecutorAgent
from agents.verifier import VerifierAgent
from dashboard.mcp_mutator import mutate_dashboard
from storage.state_store import append_chat
from ui import api


def _toggle_button() -> None:
    if st.button("🤖 Copilot", help="Open Copilot chat"):
        st.session_state["copilot_open"] = not st.session_state.get("copilot_open", False)


def render_copilot_panel() -> None:
    _toggle_button()

    if not st.session_state.get("copilot_open", False):
        return

    if not st.session_state.get("auth"):
        with st.sidebar:
            st.info("Login to use Copilot.")
        return

    with st.sidebar:
        st.subheader("Copilot")
        st.caption("Plans → Executes → Verifies → Mutates MCP")

        history = st.session_state.get("chat_history", [])
        for entry in history:
            with st.chat_message(entry["role"]):
                st.markdown(entry["content"])

        prompt = st.chat_input("Ask your analytics question")
        if prompt:
            append_chat("user", prompt)

            datasets = st.session_state.get("datasets", {})
            active_dataset = st.session_state.get("active_dataset")
            df = datasets.get(active_dataset) if active_dataset else None
            schema = st.session_state.get("schema", {}).get(active_dataset, {}) if active_dataset else {}

            planner = PlannerAgent()
            executor = ExecutorAgent()
            verifier = VerifierAgent()

            plan = planner.plan(prompt, schema)
            result = executor.execute(plan, df)
            verified = verifier.verify(plan, result)

            try:
                response = api.query({"query": prompt})
                answer = response.get("result", {}).get("answer", "No response")
            except requests.RequestException as exc:
                answer = f"Backend error: {exc}"

            mcp = mutate_dashboard(plan, verified)
            mcp.setdefault("annotations", []).append(answer)
            append_chat("assistant", answer)
            st.session_state["active_mcp"] = mcp
