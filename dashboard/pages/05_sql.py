import streamlit as st
from lab_connectors.duckdb.sql_page import render_sql_query

st.title("💻 SQL")

render_sql_query(
    title="Query SQL",
    slugs=["inpa_bandi", "inpa_comunicazioni"],
    prefix="inpa/",
    years=[2026],
)
