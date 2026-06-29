from pathlib import Path
from random import random

import streamlit as st
from Setllements.settelmet_page_general_view import GeneralView
from utils.components import show_settlement_map, show_settlement_data_table, make_gauge_graph, \
    self_search_make_gauge_graph, show_detailed_calculeted_table, show_detailed_badged_table
from data.static import InternalGoogleSheetVars
from Setllements.settlement_details_frame import present_single_settlement_details, get_qualification_data
from visual_components.page_layout import page_layout_rtl
from utils.logger import color_logger, log_pref

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
        if "settlements_stack" not in st.session_state:
            st.session_state["settlements_stack"] = []
        elif len(st.session_state["settlements_stack"]) > 0:
            if st.session_state["settlements_stack"][-1] != self.settlement_name:
                st.session_state["active_screen_index"] = "general"
        st.session_state["settlements_stack"].append(self.settlement_name)
        self.views = None
        page_layout_rtl()
        self.page_present()

    def page_present(self):
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
        st.session_state["active_screen_index"] = "detailed"

    def present_detailed_view(self):
        if st.session_state["active_screen_index"] == "detailed":

            sub_tab1, sub_tab2 = st.tabs(["כללי", "מפורט"])
            # כללי
            with sub_tab1:
                present_single_settlement_details(self.settlement_name)
            #   מפורט
            with sub_tab2:
                show_detailed_calculeted_table(self.settlement_name)

    def present_general_view(self):
        if st.session_state["active_screen_index"] == "general":
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
                     # st.markdown(f"""
                     # <div style='text-align: center;'>
                     #     <h1>{self.settlement_name} </h1>
                     # </div>
                     # """, unsafe_allow_html=True)
                     #st.page_link(f"Setllements/settelment_page_detailed_view.py")
                    with st.container():
                        status = self_search_make_gauge_graph(self.settlement_name)
                        st.button(label=f"{self.settlement_name}-{status}",
                                    on_click=self.switch_to_detailed_view,
                                    width="stretch",
                                    type="primary",
                                    key=f"{self.settlement_name}_{random()}")
                # # # the main SO
                # if st.session_state["active_screen_index"] == "general":
                #     view = GeneralView(self.settlement_name)
                # elif st.session_state["active_screen_index"] == "detailed":
                #     view = DetailedView(self.settlement_name)

                # page_layout_rtl()


                # elif st.session_state["active_screen_index"] == "detailed":
                    # view = DetailedView(self.settlement_name)
        #



        #
        # elif st.session_state["active_screen_index"] == 1:
        #
        #     sub_tab1, sub_tab2 = st.tabs(["כללי", "מפורט"])
        #     # כללי
        #     with sub_tab1:
        #         present_single_settlement_details(self.settlement_name)
        #
        #     #   מפורט
        #     with sub_tab2:
        #         show_detailed_calculeted_table(self.settlement_name)






