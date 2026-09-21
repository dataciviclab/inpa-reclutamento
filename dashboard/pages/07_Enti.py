import streamlit as st
from sources import load_mart, fmt_num

st.title("🏛️ Enti")

st.markdown("""
Classifica degli enti per volume di bandi e posti.
""")

df = load_mart("mart_efficienza_ente")

if df is not None and len(df) > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Enti nel dataset", fmt_num(len(df)))
    with col2:
        st.metric("Media bandi/ente", fmt_num(df["totale_bandi"].mean()))
    with col3:
        st.metric("Media posti/ente", fmt_num(df["totale_posti"].mean()))

    st.divider()

    sort_by = st.selectbox("Ordina per", ["Totale posti", "Totale bandi", "Media posti/bando"])
    min_bandi = st.slider("Minimo bandi", 1, 50, 3)

    filtered = df[df["totale_bandi"] >= min_bandi]
    sort_map = {
        "Totale posti": "totale_posti",
        "Totale bandi": "totale_bandi",
        "Media posti/bando": "media_posti_per_bando",
    }
    filtered = filtered.sort_values(sort_map[sort_by], ascending=False)

    st.subheader(f"Top 20 per {sort_by.lower()}")
    st.bar_chart(filtered.head(20).set_index("ente")[["totale_bandi", "totale_posti"]], use_container_width=True, height=400)

    st.divider()

    st.dataframe(
        filtered[["ente", "totale_bandi", "totale_posti", "media_posti_per_bando"]].rename(columns={
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
