import streamlit as st
from sources import load_mart, fmt_pct

st.title("🔍 Trasparenza")

st.markdown("""
Questa pagina mostra la **trasparenza** degli enti nella pubblicazione di comunicazioni di procedura.
Un ente è trasparente se pubblica aggiornamenti sui propri concorsi.
""")

# Filters
col1, col2 = st.columns(2)
with col1:
    view = st.selectbox("Visualizza", ["Meno trasparenti", "Più trasparenti"])
with col2:
    min_bandi = st.slider("Minimo bandi chiusi", 5, 50, 10)

st.divider()

# Load data
df = load_mart("mart_trasparenza_ente", slug="inpa_insight")

if df is not None and len(df) > 0:
    # Filter
    df = df[df["totale_bandi_chiusi"] >= min_bandi]
    
    # Sort
    ascending = view == "Meno trasparenti"
    df = df.sort_values("pct_trasparenza", ascending=ascending)
    
    # Summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Enti analizzati", len(df))
    with col2:
        st.metric("Media trasparenza", fmt_pct(df["pct_trasparenza"].mean()))
    with col3:
        st.metric("Enti al 100%", len(df[df["pct_trasparenza"] == 100]))
    
    # Chart
    st.bar_chart(
        df.head(20).set_index("ente")[["pct_trasparenza"]],
        use_container_width=True,
    )
    
    # Table
    st.dataframe(
        df[["ente", "totale_bandi_chiusi", "bandi_con_comunicazioni", "pct_trasparenza"]].rename(columns={
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
