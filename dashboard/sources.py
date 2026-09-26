"""Data access layer — delega a lab-connectors."""

from pathlib import Path

import streamlit as st
from lab_connectors.duckdb.queries import load_mart_table, query_clean
from lab_connectors.formatters import fmt_num, fmt_pct  # noqa: F401 — re-exported
from lab_connectors.registry import load_registry

_REPO = Path(__file__).parent.parent
PREFIX = "inpa-reclutamento/"
YEAR = 2026
SLUG_BANDI = "inpa_bandi_open"
SLUG_COMUNICAZIONI = "inpa_comunicazioni"
SLUG_INSIGHT = "inpa_insight"

_registry = load_registry(_REPO / "registry" / "registry.json")


def get_registry():
    return _registry


@st.cache_data(ttl=300, show_spinner=False)
def load_mart(table: str, slug: str = SLUG_BANDI):
    return load_mart_table(slug, table, YEAR, prefix=PREFIX)


@st.cache_data(ttl=300, show_spinner=False)
def load_regioni():
    return sorted(
        query_clean(
            SLUG_BANDI,
            "SELECT DISTINCT regione FROM clean_input "
            "WHERE status = 'OPEN' AND NOT is_graduatoria "
            "AND regione IS NOT NULL AND regione NOT LIKE '%|%' "
            "ORDER BY regione",
            years=[YEAR],
            prefix=PREFIX,
        )["regione"].tolist()
    )


@st.cache_data(ttl=300, show_spinner=False)
def search_bandi(search="", regione=None, tipo=None, max_giorni=180):
    where = ["status = 'OPEN'", "NOT is_graduatoria"]
    if search:
        s = search.replace("'", "''")
        where.append(f"(titolo ILIKE '%{s}%' OR ente ILIKE '%{s}%' OR figura_ricercata ILIKE '%{s}%')")
    if regione and regione != "Tutte":
        where.append(f"regione = '{regione.replace(chr(39), chr(39)*2)}'")
    if tipo and tipo != "Tutti":
        where.append(f"tipo_procedura = '{tipo.replace(chr(39), chr(39)*2)}'")
    where.append("data_scadenza IS NOT NULL")
    where.append(f"data_scadenza <= CURRENT_DATE + INTERVAL '{max_giorni} days'")
    sql = f"SELECT id, titolo, figura_ricercata, ente, regione, data_scadenza, CAST(num_posti AS INT) as posti, tipo_procedura FROM clean_input WHERE {' AND '.join(where)} ORDER BY data_scadenza LIMIT 200"
    return query_clean(SLUG_BANDI, sql, years=[YEAR], prefix=PREFIX)


@st.cache_data(ttl=300, show_spinner=False)
def load_bando(bando_id: str):
    return query_clean(SLUG_BANDI, f"SELECT * FROM clean_input WHERE id = '{bando_id.replace(chr(39), chr(39)*2)}'", years=[YEAR], prefix=PREFIX)


@st.cache_data(ttl=300, show_spinner=False)
def load_comunicazioni_bando(bando_id: str):
    return query_clean(SLUG_COMUNICAZIONI, f"SELECT * FROM clean_input WHERE concorso_id = '{bando_id.replace(chr(39), chr(39)*2)}' ORDER BY data_pubblicazione DESC", years=[YEAR], prefix=PREFIX)
