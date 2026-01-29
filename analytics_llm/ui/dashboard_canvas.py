import streamlit as st
import pandas as pd


def _render_component(component, datasets):
    data_source = component.get("data_source")
    df = datasets.get(data_source)
    title = component.get("title", component.get("id", "Component"))

    st.subheader(title)

    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        st.info("No data available for this component.")
        return

    ctype = component.get("type")
    x = component.get("x")
    y = component.get("y")

    if ctype == "line" and x in df.columns and y in df.columns:
        st.line_chart(df.set_index(x)[y])
    elif ctype == "bar" and x in df.columns and y in df.columns:
        st.bar_chart(df.set_index(x)[y])
    elif ctype == "table":
        st.dataframe(df.head(200))
    else:
        st.dataframe(df.head(200))


def render_dashboard_canvas() -> None:
    st.markdown("---")
    st.header("Live Dashboard Canvas")

    mcp = st.session_state.get("active_mcp", {"version": "v3", "components": [], "annotations": []})
    datasets = st.session_state.get("datasets", {})

    components = mcp.get("components", [])
    if not components:
        st.info("No dashboard components yet. Use Copilot to generate MCP updates.")
        return

    for component in components:
        _render_component(component, datasets)

    annotations = mcp.get("annotations", [])
    if annotations:
        st.markdown("### Annotations")
        for note in annotations:
            st.markdown(f"- {note}")
