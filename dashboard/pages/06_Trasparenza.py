import streamlit as st
from sources import load_mart, fmt_num, fmt_pct

st.title("🔍 Trasparenza del reclutamento")

st.markdown("""
Quanto sono trasparenti gli enti nella pubblicazione degli aggiornamenti?
Un ente è trasparente se pubblica comunicazioni di procedura (graduatorie, calendari, ammessi).
""")

df = load_mart("mart_trasparenza_ente", slug="inpa_insight")

if df is not None and len(df) > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Enti analizzati", fmt_num(len(df)))
    with col2:
        st.metric("Media trasparenza", fmt_pct(df["pct_trasparenza"].mean()))
    with col3:
        st.metric("Enti al 100%", len(df[df["pct_trasparenza"] == 100]))

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Meno trasparenti (top 20)")
        low = df.nsmallest(20, "pct_trasparenza")
        st.bar_chart(low.set_index("ente")[["pct_trasparenza"]], use_container_width=True, height=400)
    with col_b:
        st.subheader("Più trasparenti (top 20)")
        high = df.nlargest(20, "pct_trasparenza")
        st.bar_chart(high.set_index("ente")[["pct_trasparenza"]], use_container_width=True, height=400)

    st.divider()

    min_bandi = st.slider("Minimo bandi chiusi", 5, 50, 10)
    filtered = df[df["totale_bandi_chiusi"] >= min_bandi].sort_values("pct_trasparenza")

    st.dataframe(
        filtered[["ente", "totale_bandi_chiusi", "bandi_con_comunicazioni", "pct_trasparenza"]].rename(columns={
            "ente": "Ente",
            "totale_bandi_chiusi": "Bandi chiusi",
            "bandi_con_comunicazioni": "Con comunicazioni",
            "pct_trasparenza": "Trasparenza",
        }),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("Dati non disponibili.")
