import streamlit as st
from sources import load_mart, fmt_num, fmt_pct

st.title("⏱️ Tempi procedurali")

st.markdown("""
Quanto tempo ci vuole dal bando alla prima comunicazione? Analisi per tipo di procedura.
""")

df = load_mart("mart_tempi_per_procedura", slug="inpa_insight")

if df is not None and len(df) > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tipi di procedura", fmt_num(len(df)))
    with col2:
        st.metric("Media giorni", fmt_num(df["media_gg"].mean()))
    with col3:
        st.metric("Mediana giorni", fmt_num(df["mediana_gg"].median()))

    st.divider()

    st.subheader("Tempo medio per tipo di procedura")
    chart_df = df.set_index("tipo_procedura")[["media_gg", "mediana_gg"]]
    st.bar_chart(chart_df, use_container_width=True, height=400)

    st.divider()

    st.subheader("Percentuale con comunicazioni")
    st.bar_chart(df.set_index("tipo_procedura")[["pct_con_comunicazioni"]], use_container_width=True, height=300)

    st.divider()

    st.subheader("Dettaglio")
    st.dataframe(
        df[["tipo_procedura", "n_bandi_totali", "n_con_comunicazioni", "pct_con_comunicazioni", "media_gg", "mediana_gg"]].rename(columns={
            "tipo_procedura": "Tipo procedura",
            "n_bandi_totali": "Bandi totali",
            "n_con_comunicazioni": "Con comunicazioni",
            "pct_con_comunicazioni": "% con com.",
            "media_gg": "Media giorni",
            "mediana_gg": "Mediana giorni",
        }),
        use_container_width=True,
        hide_index=True,
    )

    st.divider()
    st.info("""
    **Legenda**:
    - **Solo TITOLI**: selezione basata solo su titoli di studio
    - **SOLO ESAMI**: prova scritta/orale
    - **TITOLI + ESAMI**: combinazione dei due
    - **SOLO COLLOQUIO**: prova orale
    - **TITOLI + COLLOQUIO**: combinazione
    - **CORSO_CONCORSO**: corso formazione + concorso
    """)
else:
    st.warning("Dati non disponibili.")
