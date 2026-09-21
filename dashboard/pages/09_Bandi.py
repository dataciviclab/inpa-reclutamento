import streamlit as st
import pandas as pd
from sources import load_clean_bandi, fmt_num

st.title("📋 Bandi aperti")

st.markdown("""
Cerca e filtra tra i bandi attualmente aperti. Seleziona un bando per vedere la scheda completa.
""")

# Load data
@st.cache_data(ttl=3600, show_spinner=False)
def load_all():
    from sources import SLUG_BANDI, PREFIX
    from lab_connectors.duckdb.queries import load_clean
    return load_clean(SLUG_BANDI, [2026], prefix=PREFIX)

df = load_all()
open_df = df[(df['status'] == 'OPEN') & (~df['is_graduatoria'])].copy()

# Prepare display columns
open_df['scadenza_dt'] = pd.to_datetime(open_df['data_scadenza'], errors='coerce')
open_df['posti'] = open_df['num_posti'].fillna(0).astype(int)

# Sidebar filters
st.sidebar.header("Filtri")

search = st.sidebar.text_input("🔍 Ricerca", placeholder="titolo, ente, figura...")

regioni = sorted([r for r in open_df['regione'].dropna().unique() if '|' not in r])
regione = st.sidebar.selectbox("Regione", ["Tutte"] + regioni)

tipi = sorted(open_df['tipo_procedura'].dropna().unique())
tipo = st.sidebar.selectbox("Tipo procedura", ["Tutti"] + tipi)

min_posti, max_posti = st.sidebar.slider("Numero posti", 0, 1000, (0, 1000))

giorni_scad = st.sidebar.slider("Scadenza entro giorni", 1, 180, 90)

# Apply filters
filtered = open_df.copy()

if search:
    mask = (
        filtered['titolo'].str.contains(search, case=False, na=False) |
        filtered['ente'].str.contains(search, case=False, na=False) |
        filtered['figura_ricercata'].str.contains(search, case=False, na=False)
    )
    filtered = filtered[mask]

if regione != "Tutte":
    filtered = filtered[filtered['regione'] == regione]

if tipo != "Tutti":
    filtered = filtered[filtered['tipo_procedura'] == tipo]

filtered = filtered[
    (filtered['posti'] >= min_posti) &
    (filtered['posti'] <= max_posti)
]

if giorni_scad:
    import datetime
    cutoff = datetime.date.today() + datetime.timedelta(days=giorni_scad)
    filtered = filtered[
        (filtered['scadenza_dt'].notna()) &
        (filtered['scadenza_dt'].dt.date <= cutoff)
    ]

# Sort by scadenza
filtered = filtered.sort_values('scadenza_dt', ascending=True)

# Summary
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Bandi trovati", fmt_num(len(filtered)))
with col2:
    st.metric("Posti totali", fmt_num(filtered['posti'].sum()))
with col3:
    st.metric("Enti", fmt_num(filtered['ente'].nunique()))

st.divider()

if len(filtered) == 0:
    st.info("Nessun bando trovato con i filtri selezionati.")
    st.stop()

# Build options for selectbox
options = []
for _, row in filtered.head(200).iterrows():
    titolo = str(row['titolo'])[:60] if pd.notna(row['titolo']) else "?"
    ente = str(row['ente'])[:30] if pd.notna(row['ente']) else "?"
    fig = str(row['figura_ricercata'])[:30] if pd.notna(row['figura_ricercata']) else "?"
    scad = row['scadenza_dt'].strftime('%d/%m') if pd.notna(row['scadenza_dt']) else "?"
    posti = int(row['posti'])
    label = f"{titolo} | {ente} | {fig} | {scad} | {posti} posti"
    options.append((row['id'], label))

# Select bando
selected = st.selectbox(
    "Seleziona un bando",
    options=[o[0] for o in options],
    format_func=lambda x: next(o[1] for o in options if o[0] == x),
    index=None,
    placeholder="Cerca e seleziona un bando...",
)

# Show preview + button
if selected:
    bando = filtered[filtered['id'] == selected].iloc[0]

    col_a, col_b = st.columns([3, 1])
    with col_a:
        st.markdown(f"**{bando['titolo']}**")
        ente = bando['ente'] if pd.notna(bando['ente']) else "?"
        regione = bando['regione'] if pd.notna(bando['regione']) else "?"
        fig = bando['figura_ricercata'] if pd.notna(bando['figura_ricercata']) else "?"
        scad = bando['scadenza_dt'].strftime('%d/%m/%Y') if pd.notna(bando['scadenza_dt']) else "?"
        st.caption(f"🏛️ {ente} | 📍 {regione} | 👤 {fig} | 📅 {scad} | 📍 {int(bando['posti'])} posti")
    with col_b:
        st.page_link(
            "pages/10_SchedaBando.py",
            label="📋 Apri scheda",
            icon="📋",
            query_params={"id": selected},
        )

# Also show table for reference
st.divider()
with st.expander(f"📊 Tabella completa ({len(filtered)} bandi)", expanded=False):
    display = filtered[[
        'titolo', 'figura_ricercata', 'ente', 'regione',
        'scadenza_dt', 'posti', 'tipo_procedura'
    ]].head(100).copy()
    display['scadenza_dt'] = display['scadenza_dt'].dt.strftime('%d/%m/%Y')
    display = display.rename(columns={
        'titolo': 'Titolo',
        'figura_ricercata': 'Figura',
        'ente': 'Ente',
        'regione': 'Regione',
        'scadenza_dt': 'Scadenza',
        'posti': 'Posti',
        'tipo_procedura': 'Tipo',
    })
    st.dataframe(display, use_container_width=True, hide_index=True, height=400)
