from pathlib import Path
from random import random

import streamlit as st
from Setllements.settelmet_page_general_view import GeneralView
from utils.components import show_settlement_map, show_settlement_data_table, make_gauge_graph, \
    self_search_make_gauge_graph, show_detailed_calculeted_table, show_detailed_badged_table
from data.static import InternalGoogleSheetVars
from Setllements.settlement_details_frame import present_single_settlement_details, get_qualification_data
from visual_components.page_layout import page_layout_rtl
from utils.logger import color_logger, log_pref, tracer, tracer_status

page_layout_rtl()
log = color_logger()
_locations = {"file_name" : Path(__file__).name}

class PageBase:
    def __init__(self, settlement_name):
        self.locations = _locations.copy()
        self.locations["class"] = "PageBase"
        self.locations["method"] = "init"
        self.settlement_name = settlement_name
        self.options = [f"{settlement_name} מבט כללי", "מרכיבי בטחון מחושבים"]
        st.session_state["settlement_name"] = self.settlement_name
        if "active_screen_index" not in st.session_state:
            log.debug(
                log_pref(locations=self.locations, message=f"active state - active_screen_index was not set"))
            st.session_state["active_screen_index"] = "general"

        if len(st.session_state["settlements_stack"]) > 0:
            if st.session_state["settlements_stack"][-1] != self.settlement_name:
                st.session_state["active_screen_index"] = "general"
        if len(st.session_state["settlements_stack"]) > 0:
            if st.session_state["settlements_stack"][-1] == self.settlement_name:
                st.session_state['active_screen_index'] = "general"
                st.session_state["settlement_details_frame"] = 's_tab1'
        if settlement_name not in st.session_state["session_run_time_data"]:
            st.session_state["session_run_time_data"][settlement_name] = {}
        if "ravshatz" not in st.session_state["session_run_time_data"][settlement_name]:
            st.session_state["session_run_time_data"][settlement_name]["ravshatz"] = {"name": "",
                                                                                      "phone": "",
                                                                                      "qualification": ""}

        self.views = None
        page_layout_rtl()
        self.page_present()

    def page_present(self):
        tracer(f"settelment_page_base.py - page_present invoked - for settlement {self.settlement_name} ")
        page_layout_rtl()
        if st.session_state["active_screen_index"] == "general":
            st.markdown(f"""
                         <div style='text-align: right;'>
                             <h1>{self.settlement_name} </h1>
                         </div>
                         """, unsafe_allow_html=True)
            self.present_general_view()
        else:
            self.present_detailed_view()

    def switch_to_detailed_view(self):
        tracer(f"settelment_page_base.py - switch_to_detailed_view callback button  - for settlement {self.settlement_name} ")
        st.session_state["active_screen_index"] = "detailed"
        tracer_status(
            f"app.py - {st.session_state['ravshats_table']=}, {st.session_state['settlements_stack']=}, {st.session_state['active_screen_index']=}")
        #self.present_general_view()
        st.rerun()


    def present_detailed_view(self):
        if st.session_state["active_screen_index"] == "detailed":
            if "settlement_details_frame" not in st.session_state:
                st.session_state["settlement_details_frame"] = "s_tab1"
        page_layout_rtl()
        with st.container(border=True):
            with st.expander(label="צורת תצוגה"):

                st.button(label="כללי", on_click=present_single_settlement_details,args=(self.settlement_name,))
                st.button(label="מפורט", on_click=show_detailed_calculeted_table, args=(self.settlement_name,))

    def present_general_view(self):
        tracer(f"settelment_page_base.py - present_general_view invoked - for settlement {self.settlement_name} ")
        if st.session_state["active_screen_index"] == "general":
            tracer_status(
                f"app.py - {st.session_state['ravshats_table']=}, {st.session_state['settlements_stack']=}, {st.session_state['active_screen_index']=}, {st.session_state['settlement_details_frame']=}")
            col1, col2, col3 = st.columns(3)
            with st.container():
                with col1:
                        show_settlement_map(InternalGoogleSheetVars.coordinates[self.settlement_name][0],
                                    InternalGoogleSheetVars.coordinates[self.settlement_name][1],
                                    self.settlement_name)

                # simple data table of the settlment
                with col2:
                    show_settlement_data_table(self.settlement_name)
            with st.container():
                with col3:

                    with st.container():
                        status = self_search_make_gauge_graph(self.settlement_name)
                        if "תקין" in status and "לא" not in status:
                            btn_label = f"{self.settlement_name}- ✅"
                        elif  "חלקי" in status:
                            btn_label = f"{self.settlement_name}- ⚠️"
                        else:
                            btn_label = f"{self.settlement_name}- ❌"
                        st.button(label=btn_label,
                                    on_click=self.switch_to_detailed_view,
                                    width="stretch",
                                    type="tertiary",
                                    key=f"{self.settlement_name}_{random()}")







