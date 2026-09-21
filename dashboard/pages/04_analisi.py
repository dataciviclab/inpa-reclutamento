import streamlit as st
from sources import load_mart, fmt_num, fmt_pct

st.title("📈 Analisi")

tab_tempi, tab_trasp, tab_enti = st.tabs(["⏱️ Tempi", "🔍 Trasparenza", "🏛️ Enti"])

with tab_tempi:
    st.subheader("Tempo medio per tipo di procedura")
    df = load_mart("mart_tempi_per_procedura", slug="inpa_insight")
    if df is not None and len(df) > 0:
        st.bar_chart(df.set_index('tipo_procedura')[['media_gg', 'mediana_gg']], height=350)
        st.dataframe(
            df.rename(columns={
                'tipo_procedura': 'Tipo', 'n_bandi_totali': 'Bandi',
                'n_con_comunicazioni': 'Con com.', 'pct_con_comunicazioni': '% com.',
                'media_gg': 'Media gg', 'mediana_gg': 'Mediana gg'
            }),
            use_container_width=True, hide_index=True
        )

with tab_trasp:
    st.subheader("Trasparenza enti")
    df = load_mart("mart_trasparenza_ente", slug="inpa_insight")
    if df is not None and len(df) > 0:
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Enti", len(df))
        with c2: st.metric("Media", fmt_pct(df['pct_trasparenza'].mean()))
        with c3: st.metric("Al 100%", len(df[df['pct_trasparenza'] == 100]))

        min_b = st.slider("Min bandi chiusi", 5, 50, 10)
        filtered = df[df['totale_bandi_chiusi'] >= min_b].sort_values('pct_trasparenza')

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**meno trasparenti**")
            st.bar_chart(filtered.head(10).set_index('ente')[['pct_trasparenza']], height=300)
        with c2:
            st.markdown("**più trasparenti**")
            st.bar_chart(filtered.tail(10).set_index('ente')[['pct_trasparenza']], height=300)

with tab_enti:
    st.subheader("Classifica enti")
    df = load_mart("mart_efficienza_ente")
    if df is not None and len(df) > 0:
        sort = st.selectbox("Ordina per", ["totale_posti", "totale_bandi"])
        min_b = st.slider("Min bandi", 1, 50, 3, key="enti_min")
        filtered = df[df['totale_bandi'] >= min_b].sort_values(sort, ascending=False)

        st.bar_chart(filtered.head(15).set_index('ente')[['totale_bandi', 'totale_posti']], height=400)

        st.dataframe(
            filtered.head(50).rename(columns={
                'ente': 'Ente', 'totale_bandi': 'Bandi', 'totale_posti': 'Posti',
                'media_posti_per_bando': 'Media'
            }),
            use_container_width=True, hide_index=True
        )
