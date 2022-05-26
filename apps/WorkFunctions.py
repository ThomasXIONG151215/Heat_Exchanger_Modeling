import streamlit as st
import sys
sys.path.append('.')
sys.path.append('.Modules')
from .Modules import HED, HES, OT 

def app():
    OPTIONS = {
        "Heat Exchange Design": HED,
        "Heat Exchange Surface": HES,
        "Outlet Temperature": OT
    }

    selection = st.selectbox("Choose option", list(OPTIONS.keys()))

    option = OPTIONS[selection]
    option.app()