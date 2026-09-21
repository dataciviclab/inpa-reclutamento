import streamlit as st
from lab_connectors.duckdb.sql_page import render_sql_query

st.title("💻 SQL")

st.markdown("""
Esegui query SQL sui dati inPA. Usa gli slug `inpa_bandi`, `inpa_comunicazioni`, `inpa_insight` come tabelle.
""")

render_sql_query(
    title="Query SQL",
    slugs=["inpa_bandi", "inpa_comunicazioni", "inpa_insight"],
    prefix="inpa/",
    years=[2026],
)
