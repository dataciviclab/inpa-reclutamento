import datetime

import altair as alt
import streamlit as st
from sources import fmt_num, load_mart

st.set_page_config(page_title="inPA Reclutamento", page_icon="🏛️", layout="wide")

# ── Load ────────────────────────────────────────────────────────
df_cal = load_mart("mart_scadenze_calendario")
df_geo = load_mart("mart_geografia_bandi")
df_prof = load_mart("mart_profili_ricercati")
df_proc = load_mart("mart_tipo_procedura")
df_enti = load_mart("mart_enti")

today = datetime.date.today()

def ordered_bar(df, x, y, height=300):
    """Bar chart ordinato per valore, non alfabeticamente."""
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(y, sort="-x", title=y),
        y=alt.Y(x, sort="-x", title=None),
    ).properties(height=height)
    st.altair_chart(chart, use_container_width=True)

n_bandi = int(df_cal["num_bandi"].sum()) if len(df_cal) > 0 else 0
n_posti = int(df_cal["posti_totali"].sum()) if len(df_cal) > 0 else 0

# ── Calcola statistiche reali ───────────────────────────────────
if len(df_proc) > 0:
    proc_best = df_proc.sort_values("media_posti_per_bando", ascending=False).iloc[0]
    proc_worst = (
        df_proc[df_proc["n_bandi"] >= 10].sort_values("media_posti_per_bando").iloc[0]
        if len(df_proc[df_proc["n_bandi"] >= 10]) > 0
        else None
    )
else:
    proc_best = proc_worst = None

scad_30 = (
    int(
        df_cal[df_cal["data_scadenza"] <= str(today + datetime.timedelta(days=30))][
            "num_bandi"
        ].sum()
    )
    if len(df_cal) > 0
    else 0
)
pct_30 = f"{100 * scad_30 // n_bandi}" if n_bandi > 0 else "—"

# ── Hero ────────────────────────────────────────────────────────
st.title("🏛️ Bandi aperti nella PA")

st.markdown(
    f"**{fmt_num(n_bandi)} bandi** attivi per **{fmt_num(n_posti)} posti** "
    f"in **{len(df_geo)} regioni**"
)

# ── Insight principale ─────────────────────────────────────────

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Scadono entro 30gg", f"{pct_30}%", f"{fmt_num(scad_30)} bandi")
with c2:
    if proc_best is not None:
        label = proc_best["tipo_procedura"].replace("_", " ").title()
        st.metric(f"Più posti: {label}", f"media {int(proc_best['media_posti_per_bando'])} posti")
with c3:
    if proc_worst is not None:
        label = proc_worst["tipo_procedura"].replace("_", " ").title()
        st.metric(f"Meno posti: {label}", f"media {int(proc_worst['media_posti_per_bando'])} posti")

# ── Dove + Chi ──────────────────────────────────────────────────
col_geo, col_prof = st.columns(2)

with col_geo:
    st.subheader("📍 Dove si assume")
    if len(df_geo) > 0:
        geo_df = df_geo.head(10)[["regione", "n_bandi"]].rename(columns={"regione": "Regione", "n_bandi": "Bandi"})
        ordered_bar(geo_df, "Regione", "Bandi", height=300)

with col_prof:
    st.subheader("👤 Chi cercano")
    if len(df_prof) > 0:
        prof_df = df_prof[df_prof["profilo"] != "Altro"].head(10)[["profilo", "n_bandi"]].rename(columns={"profilo": "Profilo", "n_bandi": "Bandi"})
        ordered_bar(prof_df, "Profilo", "Bandi", height=300)

# ── Procedura ───────────────────────────────────────────────────
st.divider()
st.subheader("📋 Procedure")

if len(df_proc) > 0:
    proc_df = df_proc[["tipo_procedura", "n_bandi", "posti_totali", "media_posti_per_bando"]].copy()
    proc_df["tipo_procedura"] = proc_df["tipo_procedura"].str.replace("_", " ").str.title()
    proc_df = proc_df.sort_values("posti_totali", ascending=False)

    c1, c2 = st.columns([3, 2])
    with c1:
        chart_df = proc_df[["tipo_procedura", "posti_totali"]].rename(columns={"tipo_procedura": "Procedura", "posti_totali": "Posti"})
        ordered_bar(chart_df, "Procedura", "Posti", height=250)
    with c2:
        st.dataframe(
            proc_df.rename(
                columns={
                    "tipo_procedura": "Procedura",
                    "n_bandi": "Bandi",
                    "posti_totali": "Posti",
                    "media_posti_per_bando": "Media",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )

# ── Scadenze ────────────────────────────────────────────────────
st.divider()
st.subheader("⏰ Scadenze prossime")

if len(df_cal) > 0:
    scadenze = df_cal[
        (df_cal["data_scadenza"] >= str(today))
        & (df_cal["data_scadenza"] <= str(today + datetime.timedelta(days=14)))
    ]
    if len(scadenze) > 0:
        n_scad = int(scadenze["num_bandi"].sum())
        posti_scad = int(scadenze["posti_totali"].sum())
        st.warning(f"**{n_scad}** bandi scadono entro 14 giorni → **{fmt_num(posti_scad)}** posti")
        cal_df = scadenze[["data_scadenza", "num_bandi"]].rename(columns={"data_scadenza": "Data", "num_bandi": "Bandi"})
        cal_df = cal_df.sort_values("Data")
        chart = alt.Chart(cal_df).mark_bar().encode(
            x=alt.X("Data", title=None),
            y=alt.Y("Bandi", title="Bandi"),
        ).properties(height=150)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.info("Nessuna scadenza entro 14 giorni")
