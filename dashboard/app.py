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
    "": [
        st.Page("pages/01_Panoramica.py", title="Panoramica", icon="📊", default=True),
        st.Page("pages/02_DoveChi.py", title="Dove e Chi", icon="🗺️"),
        st.Page("pages/03_Cerca.py", title="Cerca Bandi", icon="🔍"),
        st.Page("pages/05_SQL.py", title="SQL", icon="💻"),
    ],
}

pg = st.navigation(pages, position="sidebar")
pg.run()
