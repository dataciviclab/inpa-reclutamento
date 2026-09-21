import streamlit as st
import pandas as pd
from sources import fmt_num

st.title("🔍 Cerca Bandi")

# DuckDB query-based search (no full load)
@st.cache_data(ttl=3600, show_spinner=False)
def search_bandi(search="", regione=None, tipo=None, max_giorni=180):
    from lab_connectors.duckdb.queries import _resolve_url
    import duckdb

    url = _resolve_url("clean", "clean_parquet", prefix="inpa/", slug="inpa_bandi", year=2026)
    con = duckdb.connect()

    where = ["status = 'OPEN'", "NOT is_graduatoria"]

    if search:
        search_esc = search.replace("'", "''")
        where.append(f"(titolo ILIKE '%{search_esc}%' OR ente ILIKE '%{search_esc}%' OR figura_ricercata ILIKE '%{search_esc}%')")
    if regione and regione != "Tutte":
        where_esc = regione.replace("'", "''")
        where.append(f"regione = '{where_esc}'")
    if tipo and tipo != "Tutti":
        tipo_esc = tipo.replace("'", "''")
        where.append(f"tipo_procedura = '{tipo_esc}'")

    where.append("data_scadenza IS NOT NULL")
    where.append(f"data_scadenza <= CURRENT_DATE + INTERVAL '{max_giorni} days'")

    where_sql = " AND ".join(where)

    sql = f"""
        SELECT id, titolo, figura_ricercata, ente, regione,
               data_scadenza, CAST(num_posti AS INT) as posti, tipo_procedura
        FROM read_parquet('{url}')
        WHERE {where_sql}
        ORDER BY data_scadenza
        LIMIT 200
    """
    return con.sql(sql).df()


@st.cache_data(ttl=3600, show_spinner=False)
def get_bando_detail(bando_id):
    from lab_connectors.duckdb.queries import _resolve_url
    import duckdb

    url = _resolve_url("clean", "clean_parquet", prefix="inpa/", slug="inpa_bandi", year=2026)
    con = duckdb.connect()
    id_esc = bando_id.replace("'", "''")
    sql = f"SELECT * FROM read_parquet('{url}') WHERE id = '{id_esc}'"
    return con.sql(sql).df()


@st.cache_data(ttl=3600, show_spinner=False)
def get_comunicazioni(bando_id):
    from lab_connectors.duckdb.queries import _resolve_url
    import duckdb

    url = _resolve_url("clean", "clean_parquet", prefix="inpa/", slug="inpa_comunicazioni", year=2026)
    con = duckdb.connect()
    id_esc = bando_id.replace("'", "''")
    sql = f"SELECT * FROM read_parquet('{url}') WHERE concorso_id = '{id_esc}' ORDER BY data_pubblicazione DESC"
    return con.sql(sql).df()


# Check if showing detail
params = st.query_params
detail_id = params.get("id", None)

if detail_id:
    # === SCHEDA BANDO ===
    bando = get_bando_detail(detail_id)

    if len(bando) == 0:
        st.error("Bando non trovato.")
        st.page_link("pages/03_cerca.py", label="← Cerca", icon="🔍")
        st.stop()

    b = bando.iloc[0]

    st.page_link("pages/03_cerca.py", label="← Cerca", icon="🔍")

    # Header
    titolo = b['titolo'] if pd.notna(b.get('titolo')) else "Senza titolo"
    st.title(str(titolo)[:80])

    status = b.get('status', '?')
    if status == 'OPEN':
        st.success("🟢 APERTO")
    else:
        st.error("🔴 CHIUSO")

    # Info row
    parts = []
    for key, prefix in [('figura_ricercata', '👤'), ('ente', '🏛️'), ('regione', '📍')]:
        v = b.get(key)
        if pd.notna(v): parts.append(f"{prefix} {v}")
    if parts:
        st.markdown(" | ".join(parts))

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        posti = b.get('num_posti')
        st.metric("Posti", int(posti) if pd.notna(posti) else "—")
    with c2:
        scad = b.get('data_scadenza')
        st.metric("Scadenza", pd.to_datetime(scad).strftime('%d/%m/%Y') if pd.notna(scad) else "—")
    with c3:
        tipo = b.get('tipo_procedura')
        st.metric("Tipo", str(tipo) if pd.notna(tipo) else "—")
    with c4:
        cat = b.get('categoria')
        st.metric("Categoria", str(cat) if pd.notna(cat) else "—")

    st.divider()

    # Description
    import re
    desc = b.get('descrizione')
    if pd.notna(desc):
        st.subheader("📝 Descrizione")
        desc_clean = re.sub(r'<[^>]+>', '', str(desc)).strip()
        if desc_clean:
            st.markdown(desc_clean[:2000])

    st.divider()

    # Details
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📋 Dettagli")
        details = {}
        for k, label in [('codice', 'Codice'), ('settore', 'Settore'), ('provincia', 'Provincia')]:
            v = b.get(k)
            if pd.notna(v): details[label] = v
        pub = b.get('data_pubblicazione')
        if pd.notna(pub):
            details['Pubblicato'] = pd.to_datetime(pub).strftime('%d/%m/%Y')
        for k, v in details.items():
            st.markdown(f"**{k}:** {v}")

    with c2:
        st.subheader("💰 Retribuzione")
        sal_max = b.get('salary_max')
        sal_min = b.get('salary_min')
        if pd.notna(sal_max) and float(sal_max) > 100:
            sal_min_v = float(sal_min) if pd.notna(sal_min) else 0
            st.metric("Stipendio", f"€{sal_min_v:,.0f} – €{float(sal_max):,.0f}")
        else:
            st.info("Non dichiarata")

        st.subheader("🔧 Requisiti")
        for key, label in [('pec_obbligatoria', 'PEC obbligatoria'), ('richiede_pagamento', 'Pagamento'), ('is_remote', 'Remote')]:
            v = b.get(key)
            if pd.notna(v) and v:
                st.markdown(f"✅ {label}")

    # Comunicazioni
    com = get_comunicazioni(detail_id)
    if len(com) > 0:
        st.divider()
        st.subheader(f"💬 Comunicazioni ({len(com)})")
        for _, c in com.iterrows():
            data = c.get('data_pubblicazione')
            data_str = pd.to_datetime(data).strftime('%d/%m/%Y') if pd.notna(data) else "?"
            cat_c = c.get('categoria', '?')
            with st.expander(f"📅 {data_str} — {cat_c}"):
                subj = c.get('subject', '')
                if pd.notna(subj): st.markdown(f"**{subj}**")
                body = c.get('body', '')
                if pd.notna(body):
                    body_clean = re.sub(r'<[^>]+>', '', str(body)).strip()
                    if body_clean: st.markdown(body_clean[:500])

else:
    # === BROWSE with filters on top ===
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search = st.text_input("🔍 Ricerca", placeholder="titolo, ente, figura...", label_visibility="visible")
    with col2:
        regione = st.selectbox("Regione", ["Tutte", "Lombardia", "Veneto", "Emilia Romagna", "Toscana", "Campania",
               "Piemonte", "Lazio", "Sicilia", "Puglia", "Marche", "Sardegna",
               "Abruzzo", "Calabria", "Liguria", "Umbria", "Molise", "Basilicata"])
    with col3:
        tipo = st.selectbox("Tipo", ["Tutti", "ESAMI", "TITOLI_ESAMI", "TITOLI_COLLOQUIO", "COLLOQUIO", "TITOLI"])
    with col4:
        giorni = st.slider("Scadenza entro gg", 7, 180, 60)

    results = search_bandi(search, regione, tipo, giorni)

    st.metric("Risultati", fmt_num(len(results)))

    if len(results) == 0:
        st.info("Nessun bando trovato.")
    else:
        for _, row in results.head(50).iterrows():
            titolo = str(row['titolo'])[:70] if pd.notna(row.get('titolo')) else "?"
            ente = str(row['ente'])[:30] if pd.notna(row.get('ente')) else "?"
            fig = str(row['figura_ricercata'])[:30] if pd.notna(row.get('figura_ricercata')) else "?"
            scad = pd.to_datetime(row['data_scadenza']).strftime('%d/%m') if pd.notna(row.get('data_scadenza')) else "?"
            posti = int(row['posti']) if pd.notna(row.get('posti')) else 0

            st.page_link(
                "pages/03_cerca.py",
                label=f"**{titolo}**",
                query_params={"id": row['id']},
            )
            st.caption(f"🏛️ {ente} | 👤 {fig} | 📅 {scad} | 📍 {posti} posti")
            st.divider()
