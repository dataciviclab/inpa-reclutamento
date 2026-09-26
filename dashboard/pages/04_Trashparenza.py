import streamlit as st
from sources import load_mart

st.title("📈 Trasparenza PA")

st.caption(
    "La PA pubblica bandi ma dice chi ha assunto? "
    "Dati sui bandi chiusi e le loro comunicazioni (graduatorie, esiti, calendari)."
)

df_trasp = load_mart("mart_trasparenza_ente", slug="inpa_insight")
df_tempi = load_mart("mart_tempi_per_ente", slug="inpa_insight")
df_proc = load_mart("mart_tempi_per_procedura", slug="inpa_insight")

tab_trasp, tab_tempi, tab_proc = st.tabs(["🏛️ Enti", "⏱️ Tempi", "📋 Procedure"])

with tab_trasp:
    if len(df_trasp) > 0:
        # KPI
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Enti analizzati", len(df_trasp))
        with c2:
            zero = len(df_trasp[df_trasp["pct_trasparenza"] == 0])
            st.metric("Mai trasparenti", f"{zero}", f"{100*zero//len(df_trasp)}%")
        with c3:
            cento = len(df_trasp[df_trasp["pct_trasparenza"] == 100])
            st.metric("Sempre trasparenti", f"{cento}")

        st.divider()

        # Worst
        st.subheader("🏛️ Peggiori — mai pubblicano esiti")
        worst = df_trasp[df_trasp["pct_trasparenza"] == 0].nlargest(10, "totale_bandi_chiusi")
        st.dataframe(
            worst[["ente", "totale_bandi_chiusi"]].rename(columns={
                "ente": "Ente",
                "totale_bandi_chiusi": "Bandi chiusi (mai pubblicato)",
            }),
            use_container_width=True,
            hide_index=True,
        )

        # Best
        st.subheader("🏆 Migliori — sempre trasparenti")
        best = df_trasp[df_trasp["pct_trasparenza"] == 100].nlargest(10, "totale_bandi_chiusi")
        if len(best) > 0:
            st.dataframe(
                best[["ente", "totale_bandi_chiusi", "bandi_con_comunicazioni"]].rename(columns={
                    "ente": "Ente",
                    "totale_bandi_chiusi": "Bandi chiusi",
                    "bandi_con_comunicazioni": "Con comunicazioni",
                }),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("Nessun ente pubblica il100% delle comunicazioni")
    else:
        st.info("Dati non disponibili — serve il compose con closed")

with tab_tempi:
    if len(df_tempi) > 0:
        st.subheader("Quanto tempo impiegano gli enti a pubblicare aggiornamenti?")

        c1, c2 = st.columns(2)
        with c1:
            st.metric("Mediana giorni", f"{int(df_tempi['mediana_giorni'].median())}")
        with c2:
            st.metric("Enti analizzati", len(df_tempi))

        st.dataframe(
            df_tempi.nlargest(20, "mediana_giorni")[["ente", "n_bandi_con_comunicazioni", "mediana_giorni"]].rename(columns={
                "ente": "Ente",
                "n_bandi_con_comunicazioni": "Bandi con com.",
                "mediana_giorni": "Mediana giorni",
            }),
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.info("Dati non disponibili")

with tab_proc:
    if len(df_proc) > 0:
        st.subheader("Comunicazioni per tipo di procedura")

        df_display = df_proc.copy()
        df_display["tipo_procedura"] = df_display["tipo_procedura"].str.replace("_", " ").str.title()

        st.dataframe(
            df_display[["tipo_procedura", "n_bandi_totali", "n_con_comunicazioni", "pct_con_comunicazioni", "mediana_gg"]].rename(columns={
                "tipo_procedura": "Procedura",
                "n_bandi_totali": "Bandi totali",
                "n_con_comunicazioni": "Con comunicazioni",
                "pct_con_comunicazioni": "% con com.",
                "mediana_gg": "Mediana giorni",
            }),
            use_container_width=True,
            hide_index=True,
        )

        st.caption(
            "Solo il2-3% delle procedure riceve comunicazioni. "
            "La PA pubblica il bando ma non dice mai chi è stato assunto."
        )
    else:
        st.info("Dati non disponibili")
