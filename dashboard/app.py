import streamlit as st
from lab_connectors.branding import apply_branding

st.set_page_config(
    page_title="inPA Reclutamento",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_branding(
    repo_name="inpa-reclutamento",
    repo_url="https://github.com/dataciviclab/inpa-reclutamento",
)

pages = {
    "Panoramica": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
    ],
    "Mercato Lavoro PA": [
        st.Page("pages/02_Profili.py", title="Profili", icon="👤"),
        st.Page("pages/03_Geografia.py", title="Geografia", icon="🗺️"),
        st.Page("pages/04_Scadenze.py", title="Scadenze", icon="📅"),
        st.Page("pages/09_Bandi.py", title="Bandi", icon="📋"),
    ],
    "Analisi": [
        st.Page("pages/05_Tempi.py", title="Tempi", icon="⏱️"),
        st.Page("pages/06_Trasparenza.py", title="Trasparenza", icon="🔍"),
        st.Page("pages/07_Enti.py", title="Enti", icon="🏛️"),
    ],
    "Strumenti": [
        st.Page("pages/08_SQL.py", title="SQL", icon="💻"),
    ],
}

pg = st.navigation(pages, position="sidebar")
pg.run()
