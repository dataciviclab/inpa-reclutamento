import streamlit as st
from sources import load_mart, fmt_num

st.title("📅 Scadenze prossime")

# Filters
col1, col2 = st.columns(2)
with col1:
    giorni = st.slider("Prossimi giorni", 7, 90, 30)
with col2:
    regione = st.selectbox("Regione", ["Tutte"] + [
        "Lombardia", "Veneto", "Emilia Romagna", "Toscana", "Campania",
        "Piemonte", "Lazio", "Sicilia", "Puglia", "Marche", "Sardegna",
        "Abruzzo", "Calabria", "Liguria", "Umbria", "Molise", "Basilicata"
    ])

st.divider()

# Load data
df = load_mart("mart_scadenze_calendario")

if df is not None and len(df) > 0:
    # Filter by days
    import pandas as pd
    today = pd.Timestamp.now().normalize()
    cutoff = today + pd.Timedelta(days=giorni)
    df = df[(df["data_scadenza"] >= today) & (df["data_scadenza"] <= cutoff)]
    
    if len(df) > 0:
        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Bandi in scadenza", fmt_num(df["num_bandi"].sum()))
        with col2:
            st.metric("Posti totali", fmt_num(df["posti_totali"].sum()))
        with col3:
            st.metric("Giorni coperti", len(df))
        
        # Chart
        st.bar_chart(df.set_index("data_scadenza")[["num_bandi", "posti_totali"]], use_container_width=True)
        
        # Table
        st.dataframe(
            df[["data_scadenza", "num_bandi", "posti_totali", "enti_diversi", "categorie"]].rename(columns={
                "data_scadenza": "Data",
                "num_bandi": "Bandi",
                "posti_totali": "Posti",
                "enti_diversi": "Enti",
                "categorie": "Categorie",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Nessuna scadenza nei prossimi giorni selezionati.")
else:
    st.warning("Dati non disponibili.")
