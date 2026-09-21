import streamlit as st
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
    titolo = b['titolo'] if hasattr(b, 'titolo') and str(b['titolo']) != 'nan' else "Senza titolo"
    st.title(str(titolo)[:80])

    status = b.get('status', '?')
    if status == 'OPEN':
        st.success("🟢 APERTO")
    else:
        st.error("🔴 CHIUSO")

    # Info row
    parts = []
    fig = b.get('figura_ricercata')
    if fig and str(fig) != 'nan': parts.append(f"👤 {fig}")
    ente = b.get('ente')
    if ente and str(ente) != 'nan': parts.append(f"🏛️ {ente}")
    reg = b.get('regione')
    if reg and str(reg) != 'nan': parts.append(f"📍 {reg}")
    if parts:
        st.markdown(" | ".join(parts))

    # Metrics
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        posti = b.get('num_posti')
        st.metric("Posti", int(posti) if posti and str(posti) != 'nan' else "—")
    with c2:
        scad = b.get('data_scadenza')
        if scad and str(scad) != 'nan':
            import pandas as pd
            scad_dt = pd.to_datetime(scad)
            st.metric("Scadenza", scad_dt.strftime('%d/%m/%Y'))
        else:
            st.metric("Scadenza", "—")
    with c3:
        tipo = b.get('tipo_procedura')
        st.metric("Tipo", str(tipo) if tipo and str(tipo) != 'nan' else "—")
    with c4:
        cat = b.get('categoria')
        st.metric("Categoria", str(cat) if cat and str(cat) != 'nan' else "—")

    st.divider()

    # Description
    import re
    desc = b.get('descrizione')
    if desc and str(desc) != 'nan':
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
            if v and str(v) != 'nan': details[label] = v
        pub = b.get('data_pubblicazione')
        if pub and str(pub) != 'nan':
            import pandas as pd
            details['Pubblicato'] = pd.to_datetime(pub).strftime('%d/%m/%Y')
        for k, v in details.items():
            st.markdown(f"**{k}:** {v}")

    with c2:
        st.subheader("💰 Retribuzione")
        sal_max = b.get('salary_max')
        sal_min = b.get('salary_min')
        if sal_max and str(sal_max) != 'nan' and float(sal_max) > 100:
            sal_min_v = float(sal_min) if sal_min and str(sal_min) != 'nan' else 0
            st.metric("Stipendio", f"€{sal_min_v:,.0f} – €{float(sal_max):,.0f}")
        else:
            st.info("Non dichiarata")

        st.subheader("🔧 Requisiti")
        for k, label in [('pec_obbligatoria', 'PEC obbligatoria'), ('richiede_pagamento', 'Pagamento'), ('is_remote', 'Remote')]:
            v = b.get(k)
            if v and str(v) != 'nan' and v:
                st.markdown(f"✅ {label}")

    # Comunicazioni
    com = get_comunicazioni(detail_id)
    if len(com) > 0:
        st.divider()
        st.subheader(f"💬 Comunicazioni ({len(com)})")
        for _, c in com.iterrows():
            data = c.get('data_pubblicazione')
            data_str = pd.to_datetime(data).strftime('%d/%m/%Y') if data and str(data) != 'nan' else "?"
            cat = c.get('categoria', '?')
            with st.expander(f"📅 {data_str} — {cat}"):
                subj = c.get('subject', '')
                if subj and str(subj) != 'nan': st.markdown(f"**{subj}**")
                body = c.get('body', '')
                if body and str(body) != 'nan':
                    body_clean = re.sub(r'<[^>]+>', '', str(body)).strip()
                    if body_clean: st.markdown(body_clean[:500])

else:
    # === BROWSE ===
    st.sidebar.header("Filtri")
    search = st.sidebar.text_input("🔍 Ricerca", placeholder="titolo, ente, figura...")

    regioni = ["Tutte", "Lombardia", "Veneto", "Emilia Romagna", "Toscana", "Campania",
               "Piemonte", "Lazio", "Sicilia", "Puglia", "Marche", "Sardegna",
               "Abruzzo", "Calabria", "Liguria", "Umbria", "Molise", "Basilicata"]
    regione = st.sidebar.selectbox("Regione", regioni)

    tipi = ["Tutti", "ESAMI", "TITOLI_ESAMI", "TITOLI_COLLOQUIO", "COLLOQUIO", "TITOLI"]
    tipo = st.sidebar.selectbox("Tipo", tipi)

    giorni = st.sidebar.slider("Scadenza entro gg", 7, 180, 60)

    results = search_bandi(search, regione, tipo, giorni)

    st.metric("Risultati", fmt_num(len(results)))

    if len(results) == 0:
        st.info("Nessun bando trovato.")
    else:
        # Build clickable list
        for _, row in results.head(50).iterrows():
            titolo = str(row['titolo'])[:70] if row['titolo'] and str(row['titolo']) != 'nan' else "?"
            ente = str(row['ente'])[:30] if row['ente'] and str(row['ente']) != 'nan' else "?"
            fig = str(row['figura_ricercata'])[:30] if row['figura_ricercata'] and str(row['figura_ricercata']) != 'nan' else "?"
            scad = pd.to_datetime(row['data_scadenza']).strftime('%d/%m') if row['data_scadenza'] and str(row['data_scadenza']) != 'nan' else "?"
            posti = int(row['posti']) if row['posti'] and str(row['posti']) != 'nan' else 0

            st.page_link(
                "pages/03_cerca.py",
                label=f"**{titolo}**",
                query_params={"id": row['id']},
            )
            st.caption(f"🏛️ {ente} | 👤 {fig} | 📅 {scad} | 📍 {posti} posti")
            st.divider()
