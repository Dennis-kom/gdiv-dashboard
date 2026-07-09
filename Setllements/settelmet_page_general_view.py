from pathlib import Path
from random import random
import streamlit as st
from data.static import InternalGoogleSheetVars
from utils.components import show_settlement_map, show_settlement_data_table, self_search_make_gauge_graph
from visual_components.page_layout import page_layout_rtl
from utils.logger import color_logger, log_pref

log = color_logger()
_locations = {"file_name" : Path(__file__).name}


class GeneralView:
    def __init__(self, settlement_name):
        self.locations = _locations.copy()
        self.locations["class"] = "GeneralView"
        self.locations["method"] = "init"
        self.settlement_name = settlement_name
        log.debug(
            log_pref(locations=self.locations, message=f"initializing with{self.settlement_name=}"))

        st.session_state["settlements_stack"].append(self.settlement_name)
        st.session_state["settlement_name"] = self.settlement_name

        log.debug(log_pref(locations=self.locations, message=f"{st.session_state['active_screen_index']=}"))
        self.present()

    def present(self):
        page_layout_rtl()
        self.locations["method"] = "present"

        log.debug(log_pref(locations=self.locations, message=f"{self.settlement_name=} {st.session_state['settlement_name']=}"))
        if st.session_state["active_screen_index"] == "general":
            log.debug(log_pref(locations=self.locations, message=f"{st.session_state['active_screen_index']=}"))
            col1, col2, col3 = st.columns(3)
            with col1:

                show_settlement_map(InternalGoogleSheetVars.coordinates[self.settlement_name][0],
                                    InternalGoogleSheetVars.coordinates[self.settlement_name][1],
                                    self.settlement_name)

            # simple data table of the settlment
            with col2:
                if "ravshats_table" not in st.session_state:
                    st.session_state["ravshats_table"] = {}
                show_settlement_data_table(self.settlement_name)


            with col3:

                st.page_link(f"Setllements/settelment_page_detailed_view.py")
                # st.button(label=f"{self.settlement_name}",
                #         on_click=self.switch_to_detailed_view,
                #         width="stretch",
                #         type="tertiary",
                #         key=f"{self.settlement_name}_{random()}")

                self_search_make_gauge_graph(self.settlement_name)

    # def switch_to_detailed_view(self):
    #     st.session_state["active_screen_index"] = "detailed"
    #     detailed_view = DetailedView(self.settlement_name)
