import altair as alt
import pandas as pd
import streamlit as st
from sources import fmt_num, load_mart

st.set_page_config(page_title="Trend — inPA", page_icon="📈", layout="wide")

st.title("📈 Quanti concorsi la PA bandisce")
st.caption(
    "Bandi pubblicati per anno (archivio chiuso + aperti). "
    "Esclusi aggiornamenti di procedura."
)

df_closed = load_mart("mart_trend_anno", slug="inpa_bandi_closed")
df_open = load_mart("mart_trend_anno", slug="inpa_bandi_open")

if len(df_closed) == 0 and len(df_open) == 0:
    st.info("Dati trend non disponibili.")
    st.stop()

frames = []
if len(df_closed) > 0:
    frames.append(df_closed.assign(source="chiusi"))
if len(df_open) > 0:
    frames.append(df_open.assign(source="aperti"))

df = pd.concat(frames, ignore_index=True)
agg = (
    df.groupby("anno", as_index=False)
    .agg(num_bandi=("num_bandi", "sum"), posti_totali=("posti_totali", "sum"))
    .sort_values("anno")
)
agg["anno_int"] = agg["anno"].astype(int)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Anni coperti", len(agg))
with c2:
    peak = agg.loc[agg["num_bandi"].idxmax()]
    st.metric(
        "Anno più attivo",
        str(int(peak["anno"])),
        f"{fmt_num(int(peak['num_bandi']))} bandi",
    )
with c3:
    st.metric(
        "Bandi totali (archivio)",
        fmt_num(int(agg["num_bandi"].sum())),
    )

chart = (
    alt.Chart(agg)
    .mark_bar()
    .encode(
        x=alt.X("anno:O", title=None, sort=None),
        y=alt.Y("num_bandi:Q", title="Bandi pubblicati"),
        tooltip=[
            alt.Tooltip("anno:O", title="Anno"),
            alt.Tooltip("num_bandi:Q", title="Bandi", format=","),
            alt.Tooltip("posti_totali:Q", title="Posti", format=","),
        ],
    )
    .properties(height=360)
)
st.altair_chart(chart, width="stretch")

st.caption(
    "Il 2026 è l'anno in corso: il conteggio crescerà fino a dicembre. "
    "Un bando può restare pubblicato su inPA anche dopo la scadenza. "
    "I «posti» sommano anche i concors scolastici nazionali da decine di "
    "migliaia di posti — il conteggio bandi è più leggibile della somma."
)

st.divider()
st.subheader("Dettaglio per anno")
show = agg[["anno", "num_bandi", "posti_totali"]].copy()
show["num_bandi"] = show["num_bandi"].astype(int)
show["posti_totali"] = show["posti_totali"].fillna(0).astype(int)
show.columns = ["Anno", "Bandi", "Posti"]
st.dataframe(show, width="stretch", hide_index=True)
