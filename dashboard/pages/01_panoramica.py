import streamlit as st
from sources import load_mart, fmt_num, fmt_pct

st.title("📊 inPA Reclutamento")

# KPI from mart tables (lightweight)
col1, col2, col3, col4 = st.columns(4)

df_trend = load_mart("mart_trend_anno")
df_cal = load_mart("mart_scadenze_calendario")

if df_trend is not None and len(df_trend) > 0:
    latest = df_trend[df_trend['anno'] == 2026].iloc[0] if 2026 in df_trend['anno'].values else None
    if latest is not None:
        with col1:
            st.metric("Bandi 2026", fmt_num(int(latest['num_bandi'])))
        with col2:
            st.metric("Posti 2026", fmt_num(int(latest['posti_totali'])))
    else:
        with col1: st.metric("Bandi 2026", "—")
        with col2: st.metric("Posti 2026", "—")
else:
    with col1: st.metric("Bandi 2026", "—")
    with col2: st.metric("Posti 2026", "—")

import datetime
if df_cal is not None and len(df_cal) > 0:
    today = datetime.date.today()
    upcoming = df_cal[df_cal['data_scadenza'] >= str(today)]
    with col3:
        scadenze_30 = df_cal[(df_cal['data_scadenza'] >= str(today)) & (df_cal['data_scadenza'] <= str(today + datetime.timedelta(days=30)))]
        st.metric("Scadenze 30gg", fmt_num(int(scadenze_30['num_bandi'].sum())))
    with col4:
        st.metric("Giorni con scadenze", len(upcoming))
else:
    with col3: st.metric("Scadenze 30gg", "—")
    with col4: st.metric("Giorni con scadenze", "—")

st.divider()

# Trend
if df_trend is not None and len(df_trend) > 0:
    st.subheader("📈 Trend bandi e posti (2022-2026)")
    df_plot = df_trend[(df_trend['anno'] >= 2022) & (df_trend['anno'] <= 2026)].set_index('anno')
    c1, c2 = st.columns(2)
    with c1:
        st.bar_chart(df_plot[['num_bandi']], height=250)
    with c2:
        st.bar_chart(df_plot[['posti_totali']], height=250)

# Scadenze prossime
if df_cal is not None and len(df_cal) > 0:
    st.divider()
    st.subheader("📅 Prossime scadenze")
    today = datetime.date.today()
    upcoming = df_cal[df_cal['data_scadenza'] >= str(today)].head(14)
    if len(upcoming) > 0:
        st.bar_chart(upcoming.set_index('data_scadenza')[['num_bandi', 'posti_totali']], height=250)
