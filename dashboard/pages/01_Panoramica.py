import streamlit as st
from sources import load_kpi, load_mart, fmt_num

st.title("📊 Panoramica")

kpi = load_kpi()

# KPI cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Bandi totali", fmt_num(kpi["bandi_totali"]))
with col2:
    st.metric("Bandi aperti", fmt_num(kpi["bandi_aperti"]))
with col3:
    st.metric("Posti disponibili", fmt_num(kpi["posti_aperti"]))
with col4:
    st.metric("Enti attivi", fmt_num(kpi["enti"]))

col5, col6, col7 = st.columns(3)
with col5:
    st.metric("Comunicazioni", fmt_num(kpi["comunicazioni"]))
with col6:
    st.metric("Scadenze 30gg", fmt_num(kpi["scadenze_30gg"]))
with col7:
    st.metric("Aggiornamento", "Giornaliero")

st.divider()

# Trend
st.subheader("Trend reclutamento PA")

df = load_mart("mart_trend_anno")
if df is not None and len(df) > 0:
    # Filter out anomalous years
    df = df[(df["anno"] >= 2022) & (df["anno"] <= 2026)]
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.line_chart(df.set_index("anno")[["num_bandi"]], use_container_width=True)
    with col_b:
        st.line_chart(df.set_index("anno")[["posti_totali"]], use_container_width=True)
    
    st.dataframe(df, use_container_width=True, hide_index=True)
