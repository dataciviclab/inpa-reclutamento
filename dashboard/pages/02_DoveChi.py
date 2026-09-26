import altair as alt
import streamlit as st
from sources import load_mart

st.set_page_config(page_title="Dove e Chi — inPA", page_icon="🗺️", layout="wide")

df_geo = load_mart("mart_geografia_bandi")
df_prof = load_mart("mart_profili_ricercati")


def ordered_bar(df, x, y, height=300):
    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(y, sort="-x", title=y),
        y=alt.Y(x, sort="-x", title=None),
    ).properties(height=height)
    st.altair_chart(chart, use_container_width=True)


tab_geo, tab_profi, tab_enti = st.tabs(["📍 Dove", "👤 Chi", "🏛️ Enti"])

with tab_geo:
    st.subheader("Bandi per regione")

    if len(df_geo) > 0:
        c1, c2 = st.columns([2, 1])

        with c1:
            geo_df = df_geo[["regione", "n_bandi"]].rename(columns={"regione": "Regione", "n_bandi": "Bandi"})
            ordered_bar(geo_df, "Regione", "Bandi", height=400)

        with c2:
            st.dataframe(
                df_geo[["regione", "n_bandi", "posti_totali", "enti_diversi"]].rename(columns={
                    "regione": "Regione",
                    "n_bandi": "Bandi",
                    "posti_totali": "Posti",
                    "enti_diversi": "Enti",
                }),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("Nessun dato geografico disponibile")

with tab_profi:
    st.subheader("Profili professionali più ricercati")

    if len(df_prof) > 0:
        c1, c2 = st.columns([2, 1])

        with c1:
            prof_df = df_prof[df_prof["profilo"] != "Altro"].head(12)[["profilo", "n_bandi"]].rename(columns={"profilo": "Profilo", "n_bandi": "Bandi"})
            ordered_bar(prof_df, "Profilo", "Bandi", height=400)

        with c2:
            st.dataframe(
                df_prof[["profilo", "n_bandi", "posti_totali", "enti_diversi"]].rename(columns={
                    "profilo": "Profilo",
                    "n_bandi": "Bandi",
                    "posti_totali": "Posti",
                    "enti_diversi": "Enti",
                }),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("Nessun dato profili disponibile")

with tab_enti:
    st.subheader("Enti con più bandi attivi")

    df_enti = load_mart("mart_enti")
    if len(df_enti) > 0:
        min_b = st.slider("Min bandi", 1, 50, 3, key="enti_min")
        filtered = df_enti[df_enti["totale_bandi"] >= min_b].sort_values("totale_bandi", ascending=False)

        c1, c2 = st.columns([2, 1])

        with c1:
            enti_df = filtered.head(15)[["ente", "totale_bandi"]].rename(columns={"ente": "Ente", "totale_bandi": "Bandi"})
            ordered_bar(enti_df, "Ente", "Bandi", height=400)

        with c2:
            st.dataframe(
                filtered.head(30)[["ente", "totale_bandi", "totale_posti", "media_posti_per_bando"]].rename(columns={
                    "ente": "Ente",
                    "totale_bandi": "Bandi",
                    "totale_posti": "Posti",
                    "media_posti_per_bando": "Media",
                }),
                use_container_width=True,
                hide_index=True,
            )
    else:
        st.info("Nessun dato enti disponibile")
