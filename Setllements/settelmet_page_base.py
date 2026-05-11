import streamlit as st
from utils.components import show_settlement_map, show_settlement_data_table, make_gauge_graph, \
    self_search_make_gauge_graph, show_detailed_calculeted_table, show_detailed_badged_table
from variables.static import InternalGoogleSheetVars
from Setllements.settlement_details_frame import present_single_settlement_details



class PageBase:
    def __init__(self, settlement_name):
        self.settlement_name = settlement_name
        self.tab1, self.tab2 = st.tabs([f"{st.session_state.settlement_name} מבט כללי", "מרכיבי בטחון מחושבים"])

        self.page_present()

    def page_present(self):

        # the main SO
        with self.tab1:
            col1, col2, col3 = st.columns(3)
            # primary settlment representation
            with col1:
                show_settlement_map(InternalGoogleSheetVars.coordinates[self.settlement_name][0],
                                    InternalGoogleSheetVars.coordinates[self.settlement_name][1],
                                    self.settlement_name)

            # simple data table of the settlment
            with col2:
                show_settlement_data_table(self.settlement_name)

            #
            with col3:
                # st.write(st.session_state.settlement_name)
                st.markdown(f"<h2 style='text-align: right;'><strong>{self.settlement_name}</strong></h2>",
                            unsafe_allow_html=True)
                self_search_make_gauge_graph(self.settlement_name)
        # calculated security components
        with self.tab2:
            sub_tab1, sub_tab2 = st.tabs(["כללי", "מפורט"])
            # כללי
            with sub_tab1:
                present_single_settlement_details(self.settlement_name)

            #   מפורט
            with sub_tab2:
                show_detailed_calculeted_table(self.settlement_name)

