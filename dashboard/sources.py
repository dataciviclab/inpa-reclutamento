"""Data loaders per la dashboard inPA Reclutamento."""

import streamlit as st
from lab_connectors.duckdb.queries import load_mart_table, query_clean as _query_clean, load_clean
from lab_connectors.formatters import fmt_num, fmt_pct

PREFIX = "inpa/"
SLUG_BANDI = "inpa_bandi"
SLUG_COMUNICAZIONI = "inpa_comunicazioni"
SLUG_INSIGHT = "inpa_insight"


@st.cache_data(ttl=3600, show_spinner=False)
def load_mart(table: str, slug: str = SLUG_BANDI, year: int = 2026):
    return load_mart_table(slug, table, year, prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def query_clean(sql: str, slug: str = SLUG_BANDI):
    return _query_clean(slug, sql, [2026], prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_clean_bandi():
    """Load all bandi from clean layer."""
    return load_clean(SLUG_BANDI, [2026], prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_clean_comunicazioni():
    """Load all comunicazioni from clean layer."""
    return load_clean(SLUG_COMUNICAZIONI, [2026], prefix=PREFIX)


@st.cache_data(ttl=3600, show_spinner=False)
def load_kpi():
    bandi = load_clean_bandi()
    com = load_clean_comunicazioni()

    import duckdb
    con = duckdb.connect()

    con.register("bandi", bandi)
    con.register("com", com)

    bandi_stats = con.execute("""
        SELECT
            COUNT(*) as totale,
            SUM(CASE WHEN status = 'OPEN' THEN 1 ELSE 0 END) as aperti,
            SUM(CASE WHEN status = 'OPEN' AND NOT is_graduatoria THEN num_posti ELSE 0 END) as posti_aperti,
            COUNT(DISTINCT CASE WHEN status = 'OPEN' THEN ente END) as enti_aperti
        FROM bandi
    """).fetchone()

    com_stats = con.execute("SELECT COUNT(*) FROM com").fetchone()

    scadenze = con.execute("""
        SELECT COUNT(*)
        FROM bandi
        WHERE status = 'OPEN'
          AND data_scadenza IS NOT NULL
          AND data_scadenza >= CURRENT_DATE
          AND data_scadenza <= CURRENT_DATE + INTERVAL '30 days'
    """).fetchone()

    return {
        "bandi_totali": bandi_stats[0],
        "bandi_aperti": bandi_stats[1],
        "posti_aperti": bandi_stats[2] or 0,
        "enti_aperti": bandi_stats[3],
        "comunicazioni": com_stats[0],
        "scadenze_30gg": scadenze[0],
    }
