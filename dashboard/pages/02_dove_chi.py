import streamlit as st
from sources import load_mart, fmt_num

st.title("🗺️ Dove e Chi")

tab_geo, tab_profi = st.tabs(["📍 Geografia", "👤 Profili"])

with tab_geo:
    df = load_mart("mart_geografia_bandi")
    if df is not None and len(df) > 0:
        c1, c2, c3 = st.columns(3)
        with c1: st.metric("Regioni", len(df))
        with c2: st.metric("Bandi totali", fmt_num(int(df['n_bandi'].sum())))
        with c3: st.metric("Posti totali", fmt_num(int(df['posti_totali'].sum())))

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Bandi per regione")
            st.bar_chart(df.set_index('regione')[['n_bandi']], height=500)
        with c2:
            st.subheader("Posti per regione")
            st.bar_chart(df.set_index('regione')[['posti_totali']], height=500)

        st.dataframe(
            df.rename(columns={'regione': 'Regione', 'n_bandi': 'Bandi', 'posti_totali': 'Posti', 'enti_diversi': 'Enti'}),
            use_container_width=True, hide_index=True
        )

with tab_profi:
    df = load_mart("mart_profili_ricercati")
    if df is not None and len(df) > 0:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Per numero di bandi")
            st.bar_chart(df.set_index('profilo')[['n_bandi']], height=400)
        with c2:
            st.subheader("Per posti totali")
            st.bar_chart(df.set_index('profilo')[['posti_totali']], height=400)

        st.dataframe(
            df.rename(columns={'profilo': 'Profilo', 'n_bandi': 'Bandi', 'posti_totali': 'Posti', 'enti_diversi': 'Enti'}),
            use_container_width=True, hide_index=True
        )
