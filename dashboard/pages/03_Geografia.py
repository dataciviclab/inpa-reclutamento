import streamlit as st
from sources import load_mart, fmt_num

st.title("🗺️ Geografia del reclutamento PA")

st.markdown("""
Dove si cerca più personale nella PA italiana? Visualizzazione per regione.
""")

df = load_mart("mart_geografia_bandi")

if df is not None and len(df) > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Regioni attive", fmt_num(len(df)))
    with col2:
        st.metric("Bandi totali", fmt_num(df["n_bandi"].sum()))
    with col3:
        st.metric("Posti totali", fmt_num(df["posti_totali"].sum()))

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Bandi per regione")
        st.bar_chart(df.set_index("regione")[["n_bandi"]], use_container_width=True, height=500)
    with col_b:
        st.subheader("Posti per regione")
        st.bar_chart(df.set_index("regione")[["posti_totali"]], use_container_width=True, height=500)

    st.divider()

    st.subheader("Dettaglio per regione")
    st.dataframe(
        df[["regione", "n_bandi", "posti_totali", "enti_diversi", "media_posti_per_bando"]].rename(columns={
            "regione": "Regione",
            "n_bandi": "Bandi",
            "posti_totali": "Posti",
            "enti_diversi": "Enti",
            "media_posti_per_bando": "Media posti/bando",
        }),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("Dati non disponibili.")
