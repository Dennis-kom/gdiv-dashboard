import streamlit as st
from streamlit_folium import st_folium
import folium
import branca
import plotly.graph_objects as go
from utils.gsheets_auth import GoogleSheetsAuth
from utils.components import status_badge, make_gauge_graph, make_grid
from variables.static import InternalGoogleSheetVars
from app import sheet

st.set_page_config(layout="wide")
st.set_page_config(page_title="מבט כולל כל הישובים")
st.title("")


_all= 'הכל'
st.session_state.divisions = ['הכל', 'צפונית', 'דרומית']
st.session_state.councils = ['הכל', 'שדרות', 'שער הנגב', 'שדות נגב', 'אשכול', 'חוף אשקלון']
st.session_state.types = ['הכל', 'סמוך', 'ליבה', 'ליבה קדמי']
st.session_state.distances = ['הכל', '7+', '4-7', '0-4']

st.session_state.amount = 0
st.session_state.middle = 0
st.session_state.filters = {"division":st.session_state.divisions,
                            "council":st.session_state.councils,
                            "type":st.session_state.types,
                            "distance":st.session_state.distances}
tab1, tab2 , tab3= st.tabs(["מטריצת מדדים", "מפה", "ניתוח רוחבי"])

with st.form(key="optimal details"):
    with st.container():
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.session_state.filters['division'] = st.multiselect("חטיבה", st.session_state.councils)
            st.session_state.filters['council'] = st.multiselect("מועצה", st.session_state.councils)
            st.session_state.filters['type'] = st.multiselect("סיווג", st.session_state.types)
            st.session_state.filters['distance'] = st.multiselect("מרחק מהגדר", st.session_state.distances)
        with col_b:
            st.write("\n יש לבחור אפשרות אחת לפחות ")
        with col_c:
            st.form_submit_button("טען")


    with tab1:
        max_cols = 4
        max_rows = 17

        rows = 0
        cols = 0

        grid  = make_grid(max_cols,max_rows)

        for line in sheet:
            tab_line = line
            if ((tab_line['חטיבה'] in st.session_state.filters['division'] or _all in st.session_state.filters['division']) and
                    (tab_line['מועצה']  in st.session_state.filters['council'] or _all in st.session_state.filters['council']) and
                    (tab_line['סיווג'] in st.session_state.filters['type'] or _all in st.session_state.filters['type']) and
                    (tab_line['מרחק מהגדר'] in st.session_state.filters['distance'] or _all in st.session_state.filters['distance'])):
                val = float(tab_line["מדד כולל"][:-1])
                # st.session_state.amount += 1
                with grid[rows][cols]:

                    make_gauge_graph(tab_line["ישוב"], val)
                    text = "לא תקין" if val < 50 else ("חלקי" if 50 < val < 90 else "תקין")
                    color = "error" if val < 50 else ("part" if 50 < val < 90 else "success")
                    status_badge(text, color)
                    #st.button("פרטים", on_click=present_single_settlement_details_id, args=(line["ישוב"],), key=f"btn{rows}_{cols}")

                if cols == max_cols - 1 :
                    cols = 0
                    rows += 1
                else:
                    cols += 1

    with tab2:

        def fig_to_html(fig):
            fig.update_layout(autosize=True, width=None, height=None)
            return fig.to_html(include_plotlyjs='cdn', full_html=False)

        m = folium.Map(location=[31.47, 34.52], zoom_start=11)

        for line in sheet:
            tab_line = line
            if ((tab_line['חטיבה'] in st.session_state.filters['division'] or _all in st.session_state.filters['division']) and
                    (tab_line['מועצה']  in st.session_state.filters['council'] or _all in st.session_state.filters['council']) and
                    (tab_line['סיווג'] in st.session_state.filters['type'] or _all in st.session_state.filters['type']) and
                    (tab_line['מרחק מהגדר'] in st.session_state.filters['distance'] or _all in st.session_state.filters['distance'])):
                val = float(tab_line["מדד כולל"][:-1])

                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=val,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': line["ישוב"]},
                    gauge={
                        'axis': {'range': [None, 100]},
                        'bar': {'color': "red" if val < 50 else ("yellow" if 50 < val < 90 else "green")},
                        'steps': [
                            {'range': [0, 50], 'color': "lightgray"},
                            {'range': [50, 90], 'color': "gray"},
                            {'range': [90, 100], 'color': "lightgreen"}
                        ],
                        'threshold': {
                            'line': {'color': "black", 'width': 2},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))


                graph_html = fig_to_html(fig)
                iframe = branca.element.IFrame(html=graph_html,
                                               width=350,
                                               height=250)
                popup = folium.Popup(iframe,
                                     max_width=350)

                color = "green" if val > 90 else "orange" if val > 50 else "red"

                # adding the coordinate to the map
                folium.Marker(
                    InternalGoogleSheetVars.coordinates[tab_line["ישוב"]],
                    popup=popup,
                    icon=folium.Icon(color=color,
                                     icon="info-sign"),
                    tooltip=tab_line["ישוב"]
                ).add_to(m)

        st_folium(m,
                  width=700)

    # st.form_submit_button("טען")