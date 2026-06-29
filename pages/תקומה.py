import streamlit as st
from pathlib import Path
from Setllements.settelmet_page_base import PageBase
from visual_components.page_layout import page_layout_rtl
from utils.secure import enforce_authentication

enforce_authentication()

page_layout_rtl()
p = PageBase(f"{Path(__file__).name.split('.')[0].strip()}")