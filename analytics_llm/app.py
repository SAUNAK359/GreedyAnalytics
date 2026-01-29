import os
import sys
import streamlit as st

BASE_DIR = os.path.dirname(__file__)
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from ui.layout import render_layout
from ui.auth_ui import render_auth_ui
from ui.copilot_panel import render_copilot_panel
from ui.dashboard_canvas import render_dashboard_canvas
from ui.ingestion_ui import render_ingestion_ui
from ui.governance_ui import render_governance_ui
from ui.versioning_ui import render_versioning_ui
from storage.state_store import init_state


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
