import streamlit as st
import pandas as pd
from sources import load_clean_bandi, fmt_num

st.title("📋 Bandi aperti")

st.markdown("""
Cerca e filtra tra i bandi attualmente aperti. Clicca su un bando per vedere la scheda completa.
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
open_df['scadenza'] = pd.to_datetime(open_df['data_scadenza'], errors='coerce')
open_df['posti'] = open_df['num_posti'].fillna(0).astype(int)

# Sidebar filters
st.sidebar.header("Filtri")

# Search
search = st.sidebar.text_input("🔍 Ricerca testuale", placeholder="titolo, ente, figura...")

# Regioni
regioni = sorted([r for r in open_df['regione'].dropna().unique() if '|' not in r])
regione = st.sidebar.selectbox("Regione", ["Tutte"] + regioni)

# Ente
enti = sorted(open_df['ente'].dropna().unique())
ente = st.sidebar.selectbox("Ente", ["Tutti"] + enti[:200])  # limit for perf

# Figura
figure = sorted(open_df['figura_ricercata'].dropna().unique())
figura = st.sidebar.selectbox("Figura ricercata", ["Tutte"] + figure[:200])

# Tipo procedura
tipi = sorted(open_df['tipo_procedura'].dropna().unique())
tipo = st.sidebar.selectbox("Tipo procedura", ["Tutti"] + tipi)

# Range posti
min_posti, max_posti = st.sidebar.slider("Numero posti", 0, 1000, (0, 1000))

# Scadenza
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

if ente != "Tutti":
    filtered = filtered[filtered['ente'] == ente]

if figura != "Tutte":
    filtered = filtered[filtered['figura_ricercata'] == figura]

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
        (filtered['scadenza'].notna()) &
        (filtered['scadenza'].dt.date <= cutoff)
    ]

# Sort
filtered = filtered.sort_values('scadenza', ascending=True)

# Summary
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Bandi trovati", fmt_num(len(filtered)))
with col2:
    st.metric("Posti totali", fmt_num(filtered['posti'].sum()))
with col3:
    st.metric("Enti", fmt_num(filtered['ente'].nunique()))

st.divider()

# Results table
if len(filtered) == 0:
    st.info("Nessun bando trovato con i filtri selezionati.")
else:
    # Prepare display dataframe
    display = filtered[[
        'id', 'titolo', 'figura_ricercata', 'ente', 'regione',
        'scadenza', 'posti', 'tipo_procedura', 'categoria'
    ]].copy()

    display['scadenza'] = display['scadenza'].dt.strftime('%d/%m/%Y')
    display = display.rename(columns={
        'id': '_id',
        'titolo': 'Titolo',
        'figura_ricercata': 'Figura',
        'ente': 'Ente',
        'regione': 'Regione',
        'scadenza': 'Scadenza',
        'posti': 'Posti',
        'tipo_procedura': 'Tipo',
        'categoria': 'Categoria',
    })

    # Show table with selection
    event = st.dataframe(
        display.drop(columns=['_id']),
        use_container_width=True,
        height=600,
        selection_mode="single-row",
        on_select="rerun",
        hide_index=True,
    )

    # Handle row selection
    if event and event.selection and event.selection.rows:
        selected_idx = event.selection.rows[0]
        selected_id = display.iloc[selected_idx]['_id']
        st.query_params["id"] = selected_id
        st.rerun()
