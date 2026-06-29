import streamlit as st
from Setllements.settlement_details_frame import present_single_settlement_details
from utils.components import show_detailed_calculeted_table


# class DetailedView:
#     def __init__(self, settlement_name, general=None):
#         self.settlement_name = settlement_name
#         self.main_page = general
#         self.present()
#
#
#     def present(self):
#         if st.session_state["active_screen_index"] == "detailed":
#             sub_tab1, sub_tab2 = st.tabs(["כללי", "מפורט"])
#             # כללי
#             with sub_tab1:
#                 present_single_settlement_details(self.settlement_name)
#
#             #   מפורט
#             with sub_tab2:
#                 show_detailed_calculeted_table(self.settlement_name)
# st.session_state["settlement_name"]
if st.session_state["active_screen_index"] == "detailed":
    sub_tab1, sub_tab2 = st.tabs(["כללי", "מפורט"])
    # כללי
    with sub_tab1:
        present_single_settlement_details(st.session_state["settlement_name"])

    #   מפורט
    with sub_tab2:
        show_detailed_calculeted_table(st.session_state["settlement_name"])