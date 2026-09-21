"""Data loaders — solo mart tables, zero load_clean."""

import streamlit as st
from lab_connectors.duckdb.queries import load_mart_table
from lab_connectors.formatters import fmt_num, fmt_pct

PREFIX = "inpa/"
SLUG_BANDI = "inpa_bandi"
SLUG_INSIGHT = "inpa_insight"


@st.cache_data(ttl=3600, show_spinner=False)
def load_mart(table: str, slug: str = SLUG_BANDI):
    return load_mart_table(slug, table, 2026, prefix=PREFIX)
