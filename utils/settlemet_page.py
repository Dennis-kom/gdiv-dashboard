from Setllements.settelmet_page_base import PageBase
import streamlit as st

class SettlementPage(PageBase):
    def __init__(self, p_name):
        PageBase.__init__(self, p_name)

    def new_label(self):
        st.write("Settlement Page from page")
