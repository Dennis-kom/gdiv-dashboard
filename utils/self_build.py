import os.path

from variables.static import InternalGoogleSheetVars

def make_pages():
    pages_path = "C:\\repositories\\gdiv-dashboard\\pages"
    for name in InternalGoogleSheetVars.coordinates.keys():
        if not os.path.exists(os.path.join(pages_path, name)):
            code_file = os.open(os.path.join(pages_path, f"{name}.py"), os.O_CREAT)
            with open(os.path.join(pages_path, f"{name}.py"), "w", encoding="utf-8") as f:
                f.write("""import streamlit as st
from utils.components import show_settlement_map, show_settlement_data_table, make_gauge_graph, self_search_make_gauge_graph, show_detailed_calculeted_table, show_detailed_badged_table
from variables.static import InternalGoogleSheetVars
from Setllements.settlement_details_frame import present_single_settlement_details

st.session_state.settlement_name = ""
tab1, tab2, tab3 = st.tabs([f"{st.session_state.settlement_name} מבט כללי", "מרכיבי בטחון מחושבים", "מפת חום"])

with tab1:
    col1 ,col2 ,col3 = st.columns(3)
    with col1:
        show_settlement_map(InternalGoogleSheetVars.coordinates[st.session_state.settlement_name][0],
                            InternalGoogleSheetVars.coordinates[st.session_state.settlement_name][1],
                            st.session_state.settlement_name)
    with col2:
        show_settlement_data_table(st.session_state.settlement_name)


    with col3:
        # st.write(st.session_state.settlement_name)
        st.markdown(f"<h2 style='text-align: right;'><strong>{st.session_state.settlement_name}</strong></h2>", unsafe_allow_html=True)
        self_search_make_gauge_graph(st.session_state.settlement_name)


with tab2:
    sub_tab1, sub_tab2 = st.tabs(["כללי", "מפורט"])
    with sub_tab1:
        present_single_settlement_details(st.session_state.settlement_name)
    with sub_tab2:
        show_detailed_calculeted_table(st.session_state.settlement_name)

with tab3:
    show_detailed_badged_table(st.session_state.settlement_name)
    """)



