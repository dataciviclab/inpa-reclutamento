import re

import pandas as pd
import streamlit as st
from sources import fmt_num, load_bando, load_comunicazioni_bando, load_regioni, search_bandi

st.title("🔍 Cerca Bandi")

params = st.query_params
detail_id = params.get("id", None)

if detail_id:
    bando = load_bando(detail_id)

    if len(bando) == 0:
        st.error("Bando non trovato.")
        st.page_link("pages/03_Cerca.py", label="← Cerca", icon="🔍")
        st.stop()

    b = bando.iloc[0]

    st.page_link("pages/03_Cerca.py", label="← Cerca", icon="🔍")

    titolo = b["titolo"] if pd.notna(b.get("titolo")) else "Senza titolo"
    st.title(str(titolo)[:120])

    status = b.get("status", "?")
    if status == "OPEN":
        st.success("🟢 APERTO")
    else:
        st.error("🔴 CHIUSO")

    link_inpa = b.get("link_inpa")
    if pd.notna(link_inpa) and str(link_inpa).startswith("http"):
        st.link_button("🔗 Vai al bando su inPA", str(link_inpa), type="primary")

    parts = []
    for key, prefix in [
        ("figura_ricercata", "👤"),
        ("ente", "🏛️"),
        ("regione", "📍"),
        ("provincia", "📌"),
    ]:
        v = b.get(key)
        if pd.notna(v):
            parts.append(f"{prefix} {v}")
    if parts:
        st.markdown(" | ".join(parts))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        posti = b.get("num_posti")
        st.metric("Posti", int(posti) if pd.notna(posti) else "—")
    with c2:
        scad = b.get("data_scadenza")
        st.metric("Scadenza", pd.to_datetime(scad).strftime("%d/%m/%Y") if pd.notna(scad) else "—")
    with c3:
        tipo = b.get("tipo_procedura")
        st.metric("Tipo", str(tipo) if pd.notna(tipo) else "—")
    with c4:
        cat = b.get("categoria")
        st.metric("Categoria", str(cat) if pd.notna(cat) else "—")

    st.divider()

    desc = b.get("descrizione")
    if pd.notna(desc):
        st.subheader("📝 Descrizione")
        desc_clean = re.sub(r"<[^>]+>", "", str(desc)).strip()
        if desc_clean:
            st.markdown(desc_clean)

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📋 Dettagli")
        details = {}
        for k, label in [
            ("codice", "Codice bando"),
            ("settore", "Settore"),
            ("provincia", "Provincia"),
            ("ente", "Ente"),
            ("enti_riferimento", "Enti di riferimento"),
        ]:
            v = b.get(k)
            if pd.notna(v):
                details[label] = v
        pub = b.get("data_pubblicazione")
        if pd.notna(pub):
            details["Pubblicato"] = pd.to_datetime(pub).strftime("%d/%m/%Y")
        for k, v in details.items():
            st.markdown(f"**{k}:** {v}")

    with c2:
        st.subheader("💰 Retribuzione")
        sal_max = b.get("salary_max")
        sal_min = b.get("salary_min")
        if pd.notna(sal_max) and float(sal_max) > 100:
            sal_min_v = float(sal_min) if pd.notna(sal_min) else 0
            min_fmt = f"{sal_min_v:,.0f}".replace(",", ".")
            max_fmt = f"{float(sal_max):,.0f}".replace(",", ".")
            st.metric("Stipendio annuo", f"€{min_fmt} – €{max_fmt}")
        else:
            st.info("Retribuzione non dichiarata nel bando")

        st.subheader("📎 Link")
        if pd.notna(link_inpa) and str(link_inpa).startswith("http"):
            st.markdown(f"[Apri su inPA]({link_inpa})")
        else:
            st.info("Nessun link disponibile")

    com = load_comunicazioni_bando(detail_id)
    if len(com) > 0:
        st.divider()
        st.subheader(f"💬 Comunicazioni ({len(com)})")
        for _, c in com.iterrows():
            data = c.get("data_pubblicazione")
            data_str = pd.to_datetime(data).strftime("%d/%m/%Y") if pd.notna(data) else "?"
            cat_c = c.get("categoria", "?")
            with st.expander(f"📅 {data_str} — {cat_c}"):
                subj = c.get("subject", "")
                if pd.notna(subj):
                    st.markdown(f"**{subj}**")
                body = c.get("body", "")
                if pd.notna(body):
                    body_clean = re.sub(r"<[^>]+>", "", str(body)).strip()
                    if body_clean:
                        st.markdown(body_clean[:500])

else:
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        search = st.text_input("🔍 Ricerca", placeholder="titolo, ente, figura...")
    with col2:
        regioni = ["Tutte"] + load_regioni()
        regione = st.selectbox("Regione", regioni)
    with col3:
        tipo = st.selectbox(
            "Tipo",
            ["Tutti", "ESAMI", "TITOLI_ESAMI", "TITOLI_COLLOQUIO", "COLLOQUIO", "TITOLI"],
        )
    with col4:
        giorni = st.slider("Scadenza entro gg", 7, 180, 60)

    results = search_bandi(search, regione, tipo, giorni)

    st.metric("Risultati", fmt_num(len(results)))

    if len(results) == 0:
        st.info("Nessun bando trovato.")
    else:
        for _, row in results.head(50).iterrows():
            titolo = str(row["titolo"])[:70] if pd.notna(row.get("titolo")) else "?"
            ente = str(row["ente"])[:30] if pd.notna(row.get("ente")) else "?"
            fig = (
                str(row["figura_ricercata"])[:30] if pd.notna(row.get("figura_ricercata")) else "?"
            )
            scad = (
                pd.to_datetime(row["data_scadenza"]).strftime("%d/%m")
                if pd.notna(row.get("data_scadenza"))
                else "?"
            )
            posti = int(row["posti"]) if pd.notna(row.get("posti")) else 0

            st.page_link(
                "pages/03_Cerca.py",
                label=f"**{titolo}**",
                query_params={"id": row["id"]},
            )
            st.caption(f"🏛️ {ente} | 👤 {fig} | 📅 {scad} | 📍 {posti} posti")
            st.divider()
