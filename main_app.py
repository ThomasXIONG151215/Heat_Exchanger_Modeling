import streamlit as st
from apps import WorkFunctions, FluidDatabase, Report

#page = st.selectbox("Choose option", ["Option 1", "Option 2", "Option 3"])


PAGES = {
    "Work Functions": WorkFunctions,
    "Fluid Database": FluidDatabase,
    "Report": Report
}

st.sidebar.title('Navigation')
selection = st.sidebar.radio("Go to", list(PAGES.keys()))
#st.selectbox("Choose option", list(PAGES.keys()))
page = PAGES[selection]
page.app()
