"""Query SQL — Interroga direttamente i dati inPA Reclutamento."""

from lab_connectors.duckdb.sql_page import render_sql_query
from sources import PREFIX, get_registry

render_sql_query(
    registry=get_registry(),
    prefix=PREFIX,
    default_slug="inpa_bandi",
    title="💻 Query SQL",
    description=(
        "Interroga direttamente i dati del Portale inPA. "
        "Usa ``clean_input`` come nome della tabella virtuale."
    ),
)
