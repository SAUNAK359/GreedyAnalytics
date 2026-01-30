import streamlit as st
from analytics_llm.frontend.governance.pii_detector import detect_pii


def render_governance_ui() -> None:
    st.markdown("---")
    st.header("Governance")

    datasets = st.session_state.get("datasets", {})
    if not datasets:
        st.info("No datasets to scan for PII.")
        return

    for name, df in datasets.items():
        st.subheader(f"PII Scan: {name}")
        findings = detect_pii(df)
        if not findings:
            st.success("No PII detected.")
        else:
            st.warning("PII detected. Redaction policy will apply.")
            st.json(findings)
