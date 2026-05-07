import streamlit as st
from pathlib import Path
from Setllements.settelmet_page_base import PageBase

st.session_state.settlement_name = f"{Path(__file__).name.split('.')[0].strip()}"

p = PageBase(st.session_state.settlement_name)