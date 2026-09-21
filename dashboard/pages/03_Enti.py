import streamlit as st
from sources import load_mart, fmt_num

st.title("🏛️ Enti")

# Filters
col1, col2 = st.columns(2)
with col1:
    sort_by = st.selectbox("Ordina per", ["Totale bandi", "Totale posti", "Media posti/bando"])
with col2:
    min_bandi = st.slider("Minimo bandi", 1, 50, 3)

st.divider()

# Load data
df = load_mart("mart_efficienza_ente")

if df is not None and len(df) > 0:
    # Filter
    df = df[df["totale_bandi"] >= min_bandi]
    
    # Sort
    sort_map = {
        "Totale bandi": "totale_bandi",
        "Totale posti": "totale_posti",
        "Media posti/bando": "media_posti_per_bando",
    }
    df = df.sort_values(sort_map[sort_by], ascending=False)
    
    # Summary
    st.metric("Enti nel dataset", fmt_num(len(df)))
    
    # Chart
    st.bar_chart(
        df.head(20).set_index("ente")[["totale_bandi", "totale_posti"]],
        use_container_width=True,
    )
    
    # Table
    st.dataframe(
        df[["ente", "totale_bandi", "totale_posti", "media_posti_per_bando"]].rename(columns={
            "ente": "Ente",
            "totale_bandi": "Bandi",
            "totale_posti": "Posti",
            "media_posti_per_bando": "Media posti/bando",
        }),
        use_container_width=True,
        hide_index=True,
    )
else:
    st.warning("Dati non disponibili.")
