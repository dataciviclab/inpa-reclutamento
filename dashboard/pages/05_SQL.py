"""Query SQL — Interroga direttamente i dati inPA Reclutamento."""

from lab_connectors.duckdb.sql_page import render_sql_query
from sources import PREFIX, SLUG_BANDI, get_registry

render_sql_query(
    registry=get_registry(),
    prefix=PREFIX,
    default_slug=SLUG_BANDI,
    title="💻 Query SQL",
    description=(
        "Interroga direttamente i dati del Portale inPA. "
        "Usa ``clean_input`` come nome della tabella virtuale."
    ),
)
