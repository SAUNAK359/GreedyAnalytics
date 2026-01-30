import streamlit as st
from analytics_llm.frontend.ingestion.loaders.csv_loader import load_csv
from analytics_llm.frontend.ingestion.loaders.excel_loader import load_excel
from analytics_llm.frontend.ingestion.loaders.parquet_loader import load_parquet
from analytics_llm.frontend.ingestion.loaders.pdf_loader import load_pdf
from analytics_llm.frontend.ingestion.loaders.word_loader import load_word
from analytics_llm.frontend.ingestion.loaders.ppt_loader import load_ppt
from analytics_llm.frontend.ingestion.loaders.sap_tally_loader import load_sap_tally
from analytics_llm.frontend.ingestion.schema_infer import infer_schema
from analytics_llm.frontend.ingestion.profiler import profile_dataset
from analytics_llm.frontend.storage.vector_store import VectorStore
from analytics_llm.frontend.ui import api


def _detect_loader(filename: str):
    lowered = filename.lower()
    if lowered.endswith(".csv"):
        return load_csv
    if lowered.endswith((".xls", ".xlsx")):
        return load_excel
    if lowered.endswith(".parquet"):
        return load_parquet
    if lowered.endswith(".pdf"):
        return load_pdf
    if lowered.endswith((".doc", ".docx")):
        return load_word
    if lowered.endswith((".ppt", ".pptx")):
        return load_ppt
    if "sap" in lowered or "tally" in lowered:
        return load_sap_tally
    return None


def render_ingestion_ui() -> None:
    st.markdown("---")
    st.header("Ingestion")
    st.caption("Upload datasets and documents in mixed formats")

    if not st.session_state.get("auth"):
        st.info("Login required to register datasources.")
        return

    uploaded = st.file_uploader(
        "Upload files",
        type=None,
        accept_multiple_files=True,
    )

    if not uploaded:
        try:
            datasources = api.list_datasources().get("datasources", [])
            if datasources:
                st.markdown("**Registered Datasources**")
                st.json(datasources)
        except Exception:
            pass
        return

    vector_store = VectorStore()

    for file in uploaded:
        loader = _detect_loader(file.name)
        if not loader:
            st.warning(f"Unsupported file type: {file.name}")
            continue

        data = loader(file)
        try:
            api.add_datasource({
                "name": file.name,
                "type": data.get("type", "file"),
                "size": getattr(file, "size", None),
            })
        except Exception:
            st.warning(f"Backend datasource registration failed for {file.name}")
        if data.get("type") == "table":
            df = data["data"]
            st.session_state.setdefault("datasets", {})[file.name] = df
            st.session_state["active_dataset"] = file.name

            schema = infer_schema(df)
            st.session_state.setdefault("schema", {})[file.name] = schema

            profile = profile_dataset(df)
            st.session_state.setdefault("profiles", {})[file.name] = profile

        if data.get("type") == "document":
            text = data.get("text", "")
            st.session_state.setdefault("documents", []).append({"name": file.name, "text": text})
            vector_store.add_document(file.name, text)

    st.success("Ingestion complete. Copilot is ready.")
