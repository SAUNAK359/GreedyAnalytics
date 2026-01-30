import streamlit as st

from analytics_llm.frontend.ui.layout import render_layout
from analytics_llm.frontend.ui.auth_ui import render_auth_ui
from analytics_llm.frontend.ui.copilot_panel import render_copilot_panel
from analytics_llm.frontend.ui.dashboard_canvas import render_dashboard_canvas
from analytics_llm.frontend.ui.ingestion_ui import render_ingestion_ui
from analytics_llm.frontend.ui.governance_ui import render_governance_ui
from analytics_llm.frontend.ui.versioning_ui import render_versioning_ui
from analytics_llm.frontend.storage.state_store import init_state


def main() -> None:
    init_state()

    render_layout()

    render_auth_ui()

    if st.session_state.get("auth"):
        render_ingestion_ui()
        render_dashboard_canvas()
        render_governance_ui()
        render_versioning_ui()
        render_copilot_panel()
    else:
        st.info("Authenticate to access analytics features.")


if __name__ == "__main__":
    main()
