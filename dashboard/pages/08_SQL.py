import streamlit as st
from lab_connectors.duckdb.sql_page import render_sql_query

st.title("💻 SQL")

st.markdown("""
Esegui query SQL sui dati inPA.

**Tabelle disponibili**:
- `clean_input` — bandi (default)
- `inpa_comunicazioni` — comunicazioni di procedura
- `inpa_insight` — analisi cross-dataset
""")

render_sql_query(
    title="Query SQL",
    slugs=["inpa_bandi", "inpa_comunicazioni", "inpa_insight"],
    prefix="inpa/",
    years=[2026],
)
