import streamlit as st
from sources import load_mart, fmt_num

st.title("👤 Profili più richiesti")

st.markdown("""
Chi cerca lavoro nella PA? Ecco i profili professionali più richiesti nei bandi aperti.
""")

df = load_mart("mart_profili_ricercati")

if df is not None and len(df) > 0:
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Profili unici", fmt_num(len(df)))
    with col2:
        st.metric("Bandi totali", fmt_num(df["n_bandi"].sum()))

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Per numero di bandi")
        st.bar_chart(df.set_index("profilo")[["n_bandi"]], use_container_width=True, height=400)
    with col_b:
        st.subheader("Per posti totali")
        st.bar_chart(df.set_index("profilo")[["posti_totali"]], use_container_width=True, height=400)

    st.divider()

    st.subheader("Dettaglio")
    st.dataframe(
        df[["profilo", "n_bandi", "posti_totali", "enti_diversi"]].rename(columns={
            "profilo": "Profilo",
            "n_bandi": "Bandi",
            "posti_totali": "Posti",
            "enti_diversi": "Enti",
        }),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("Dati non disponibili.")
