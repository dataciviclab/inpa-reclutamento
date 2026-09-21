import streamlit as st
import pandas as pd
import re
from sources import load_clean_bandi, load_clean_comunicazioni, fmt_num

st.set_page_config(page_title="Scheda Bando", page_icon="📋", layout="wide")

# Get bando ID from query params
params = st.query_params
bando_id = params.get("id", None)

if not bando_id:
    st.warning("Nessun bando selezionato.")
    st.page_link("pages/09_Bandi.py", label="← Torna ai bandi", icon="📋")
    st.stop()

# Load data
bandi = load_clean_bandi()
com = load_clean_comunicazioni()

# Find the bando
bando = bandi[bandi['id'] == bando_id]

if len(bando) == 0:
    st.error(f"Bando con ID `{bando_id}` non trovato.")
    st.page_link("pages/09_Bandi.py", label="← Torna ai bandi", icon="📋")
    st.stop()

b = bando.iloc[0]

# Back button
st.page_link("pages/09_Bandi.py", label="← Tutti i bandi", icon="📋")

# Header
col_title, col_status = st.columns([4, 1])
with col_title:
    st.title(b['titolo'] if pd.notna(b['titolo']) else "Senza titolo")
with col_status:
    if b['status'] == 'OPEN':
        st.success("🟢 APERTO")
    else:
        st.error("🔴 CHIUSO")

# Subtitle
subtitle_parts = []
if pd.notna(b['figura_ricercata']):
    subtitle_parts.append(f"**Figura:** {b['figura_ricercata']}")
if pd.notna(b['ente']):
    subtitle_parts.append(f"**Ente:** {b['ente']}")
if pd.notna(b['regione']):
    subtitle_parts.append(f"**Regione:** {b['regione']}")
if subtitle_parts:
    st.markdown(" | ".join(subtitle_parts))

# Key metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    posti = int(b['num_posti']) if pd.notna(b['num_posti']) else "—"
    st.metric("📍 Posti", posti)
with col2:
    scad = b['data_scadenza'].strftime('%d/%m/%Y') if pd.notna(b['data_scadenza']) else "—"
    st.metric("📅 Scadenza", scad)
with col3:
    st.metric("📋 Tipo", b['tipo_procedura'] if pd.notna(b['tipo_procedura']) else "—")
with col4:
    st.metric("🏷️ Categoria", b['categoria'] if pd.notna(b['categoria']) else "—")

st.divider()

# Description
if pd.notna(b['descrizione']):
    st.subheader("📝 Descrizione")
    desc = re.sub(r'<[^>]+>', '', str(b['descrizione']))
    desc = desc.strip()
    if desc:
        st.markdown(desc)

st.divider()

# Details in columns
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📋 Dettagli")
    details = {}
    if pd.notna(b['codice']):
        details['Codice'] = b['codice']
    if pd.notna(b['settore']):
        details['Settore'] = b['settore']
    if pd.notna(b['provincia']):
        details['Provincia'] = b['provincia']
    if pd.notna(b['data_pubblicazione']):
        if hasattr(b['data_pubblicazione'], 'strftime'):
            details['Pubblicato'] = b['data_pubblicazione'].strftime('%d/%m/%Y')
        else:
            details['Pubblicato'] = str(b['data_pubblicazione'])
    for k, v in details.items():
        st.markdown(f"**{k}:** {v}")

with col_right:
    st.subheader("💰 Retribuzione")
    if pd.notna(b['salary_min']) and pd.notna(b['salary_max']) and b['salary_max'] > 100:
        st.markdown(f"**Min:** €{b['salary_min']:,.0f}")
        st.markdown(f"**Max:** €{b['salary_max']:,.0f}")
    elif pd.notna(b['salary_max']) and b['salary_max'] > 100:
        st.markdown(f"**Max:** €{b['salary_max']:,.0f}")
    else:
        st.info("Retribuzione non dichiarata nel bando")

    st.subheader("🔧 Requisiti")
    requisiti = []
    if b.get('pec_obbligatoria', False):
        requisiti.append("✅ PEC obbligatoria")
    if b.get('richiede_pagamento', False):
        requisiti.append("💰 Richiede pagamento")
    if b.get('is_remote', False):
        requisiti.append("🏠 Possibilità di lavoro remoto")
    if not requisiti:
        requisiti.append("Nessun requisito speciale dichiarato")
    for r in requisiti:
        st.markdown(f"- {r}")

st.divider()

# Links
col_links, col_allegati = st.columns(2)
with col_links:
    link_pa = b.get('link_sito_pa')
    if pd.notna(link_pa) and link_pa:
        st.subheader("🔗 Link")
        st.link_button("Vai al sito dell'Ente", link_pa, icon="🌐")
with col_allegati:
    n_all = int(b.get('n_allegati', 0)) if pd.notna(b.get('n_allegati')) else 0
    if n_all > 0:
        st.subheader("📎 Allegati")
        st.info(f"Questo bando ha **{n_all}** allegati. Consulta il sito dell'ente per scaricarli.")

# Multi-sede
sedi_val = b.get('sedi')
if pd.notna(sedi_val) and '|' in str(sedi_val):
    st.divider()
    st.subheader("📍 Sedi")
    sedi = str(sedi_val).split('|')
    st.markdown(", ".join(sedi[:10]))
    if len(sedi) > 10:
        st.caption(f"... e altre {len(sedi) - 10} sedi")

# Comunicazioni correlate
st.divider()
st.subheader("💬 Comunicazioni")
com_bando = com[com['concorso_id'] == bando_id]

if len(com_bando) > 0:
    for _, c in com_bando.sort_values('data_pubblicazione', ascending=False).iterrows():
        data_com = c['data_pubblicazione']
        if hasattr(data_com, 'strftime'):
            data_str = data_com.strftime('%d/%m/%Y')
        else:
            data_str = str(data_com)
        cat = c.get('categoria', 'N/A')
        with st.expander(f"📅 {data_str} — {cat}"):
            st.markdown(f"**{c.get('subject', '')}**")
            if pd.notna(c.get('body')):
                body = re.sub(r'<[^>]+>', '', str(c['body']))
                st.markdown(body[:500])
else:
    st.info("Nessuna comunicazione pubblicata per questo bando.")

# Altri bandi dello stesso ente
st.divider()
st.subheader("🏛️ Altri bandi dello stesso ente")
if pd.notna(b['ente']):
    altri = bandi[
        (bandi['ente'] == b['ente']) &
        (bandi['id'] != bando_id) &
        (bandi['status'] == 'OPEN')
    ].head(5)

    if len(altri) > 0:
        for _, altro in altri.iterrows():
            titolo = altro['titolo'][:80] if pd.notna(altro['titolo']) else "Senza titolo"
            scad_val = altro['data_scadenza']
            scad_str = scad_val.strftime('%d/%m') if pd.notna(scad_val) and hasattr(scad_val, 'strftime') else "?"
            posti_val = altro['num_posti']
            posti_str = int(posti_val) if pd.notna(posti_val) else "?"
            st.markdown(f"- **{titolo}** — Scadenza: {scad_str} | Posti: {posti_str}")
    else:
        st.info("Nessun altro bando aperto per questo ente.")
