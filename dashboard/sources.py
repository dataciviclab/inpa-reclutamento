"""Data loaders — solo mart tables, zero load_clean."""

from pathlib import Path

import streamlit as st
from lab_connectors.duckdb.queries import _resolve_url, load_mart_table
from lab_connectors.formatters import fmt_num, fmt_pct  # noqa: F401 — re-exported for pages
from lab_connectors.registry import load_registry

_REPO = Path(__file__).parent.parent
PREFIX = "inpa/"
SLUG_BANDI = "inpa_bandi"
SLUG_INSIGHT = "inpa_insight"

_registry = load_registry(_REPO / "registry" / "registry.json")


def get_registry():
    return _registry


@st.cache_data(ttl=3600, show_spinner=False)
def load_mart(table: str, slug: str = SLUG_BANDI):
    return load_mart_table(slug, table, 2026, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_regioni():
    """Carica le regioni distinte dai dati clean (esclude multi-sede e NULL)."""
    import duckdb

    url = _resolve_url("clean", "clean_parquet", prefix=PREFIX, slug=SLUG_BANDI, year=2026)
    con = duckdb.connect()
    df = con.sql(f"""
        SELECT DISTINCT regione
        FROM read_parquet('{url}')
        WHERE status = 'OPEN' AND NOT is_graduatoria
          AND regione IS NOT NULL AND regione NOT LIKE '%|%'
        ORDER BY regione
    """).df()
    return sorted(df["regione"].tolist())
