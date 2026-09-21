import streamlit as st
import pandas as pd
from sources import load_mart, fmt_num

st.title("📅 Scadenze prossime")

col1, col2 = st.columns(2)
with col1:
    giorni = st.slider("Prossimi giorni", 7, 90, 30)
with col2:
    st.empty()

st.divider()

df = load_mart("mart_scadenze_calendario")

if df is not None and len(df) > 0:
    today = pd.Timestamp.now().normalize()
    cutoff = today + pd.Timedelta(days=giorni)
    df = df[(df["data_scadenza"] >= today) & (df["data_scadenza"] <= cutoff)]

    if len(df) > 0:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Bandi in scadenza", fmt_num(df["num_bandi"].sum()))
        with col2:
            st.metric("Posti totali", fmt_num(df["posti_totali"].sum()))
        with col3:
            st.metric("Giorni coperti", len(df))

        st.bar_chart(df.set_index("data_scadenza")[["num_bandi", "posti_totali"]], use_container_width=True, height=300)

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
