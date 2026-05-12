import streamlit as st
from streamlit_folium import st_folium
import folium
import branca
import plotly.graph_objects as go
from utils.gsheets_auth import GoogleSheetsAuth
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.components import status_badge, make_gauge_graph, make_grid, LocalDataEntry, place_vertical_spacer, \
    show_spider_chart, show_heat_map, show_status_heat_map
from variables.static import InternalGoogleSheetVars
from app import sheet
import logging
# settlements_data
st.set_page_config(layout="wide")
st.set_page_config(page_title="מבט כולל כל הישובים")
st.title("")


_all= 'הכל'
# st.session_state.divisions = ['הכל', 'צפונית', 'דרומית']
# st.session_state.councils = ['הכל', 'שדרות', 'שער הנגב', 'שדות נגב', 'אשכול', 'חוף אשקלון']
# st.session_state.types = ['הכל', 'סמוך', 'ליבה', 'ליבה קדמי']
# st.session_state.distances = ['הכל', '7+', '4-7', '0-4']
#
# st.session_state.amount = 0
# st.session_state.middle = 0
# st.session_state.filters = {"division":st.session_state.divisions,
#                             "council":st.session_state.councils,
#                             "type":st.session_state.types,
#                             "distance":st.session_state.distances}
#
# st.session_state.filters['division'] = st.multiselect("חטיבה", st.session_state.divisions)
# st.session_state.filters['council'] = st.multiselect("מועצה", st.session_state.councils)
# st.session_state.filters['type'] = st.multiselect("סיווג", st.session_state.types)
# st.session_state.filters['distance'] = st.multiselect("מרחק מהגדר", st.session_state.distances)
data_load_measure_state = {"max_load":4, "load_stack":0}
st.session_state.divisions = ['הכל', 'צפונית', 'דרומית']
st.session_state.councils = ['הכל', 'שדרות', 'שער הנגב', 'שדות נגב', 'אשכול', 'חוף אשקלון']
st.session_state.types = ['הכל', 'סמוך', 'ליבה', 'ליבה קדמי']
st.session_state.distances = ['הכל', '7+', '4-7', '0-4']
st.session_state.settlements = ['הכל'] + list(InternalGoogleSheetVars.settlements_data.keys())
st.session_state.val_selections =  ['הכל'] + ["0-30", "30-50", "50-90", "90-100"]
st.session_state.data_view_selector = "raw"
st.session_state.models_list = [mod  for mod in InternalGoogleSheetVars.options['model'] if "מדד" in mod] + ["מדד נץ"]


def filtering(filter_type: str,key="default"):

    match filter_type:
        case "main":
            all_shortcut = st.checkbox('הצג הכל',key=key)
            default_val = ['הכל'] if all_shortcut else None
            data_load_measure_state["load_stack"] += 1 if all_shortcut else 0
            st.session_state.amount = 0
            st.session_state.middle = 0
            st.session_state.filters = {"division": st.multiselect("חטיבה", st.session_state.divisions, default=default_val),
                                        "council": st.multiselect("מועצה", st.session_state.councils, default=default_val),
                                        "type": st.multiselect("סיווג", st.session_state.types, default=default_val),
                                        "distance": st.multiselect("מרחק מהגדר", st.session_state.distances, default=default_val)}
        case "settlements":
            all_shortcut = st.checkbox('הצג הכל',key=key)
            default_val = ['הכל'] if all_shortcut else None
            data_load_measure_state["load_stack"] += 1 if all_shortcut else 0
            st.session_state.settlements_selections = st.multiselect("ישובים", st.session_state.settlements, default=default_val)
        case "selections":
            st.session_state.data_view_selector = "raw"
            all_shortcut = st.checkbox('הצג הכל',key=key)
            default_val = ['הכל'] if all_shortcut else None
            data_load_measure_state["load_stack"] += 1 if all_shortcut else 0
            st.session_state.amount = 0
            st.session_state.middle = 0
            st.session_state.selections = {
                'status': st.multiselect("סטטוס", InternalGoogleSheetVars.options['status'], default=default_val),
                'action': st.multiselect("הפעלה", InternalGoogleSheetVars.options['action'], default=default_val),
                'types': st.multiselect("סיווג", InternalGoogleSheetVars.options['types'], default=default_val),
                'frame': st.multiselect("מסגרת", InternalGoogleSheetVars.options['frame'], default=default_val),
                'domain': st.multiselect("תחום", InternalGoogleSheetVars.options['domain'], default=default_val),
                'model': st.multiselect("מודל", InternalGoogleSheetVars.options['model'], default=default_val),
                'economy': st.multiselect("משק", InternalGoogleSheetVars.options['economy'], default=default_val),
                'family': st.multiselect("משפחה", InternalGoogleSheetVars.options['family'], default=default_val)}
        case "model":
            st.session_state.data_view_selector = "model"
            st.session_state.model_selection = st.multiselect("מודל", st.session_state.models_list)
        case "values":
            all_shortcut = st.checkbox('הצג הכל',key=key)
            default_val = ['הכל'] if all_shortcut else None
            data_load_measure_state["load_stack"] += 1 if all_shortcut else 0
            st.session_state.values_selections = st.multiselect("ערכים",st.session_state.val_selections,default=default_val)

        case _:
            pass

 # st.session_state.filters_local_memory = InternalGoogleSheetVars.settlements_data
# with st.expander("פילטר ראשי"):


tab1, tab2, tab3, tab4 = st.tabs(["מטריצת מדדים", "מפה", "ניתוח רוחבי", "חקר ביצועים"])

with tab1:
    with st.form(key="main details", width="stretch"):
        with st.expander("פילטר ראשי"):
            with st.container():
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    filtering("main","main_filter")
                with col_b:
                    st.write("\n יש לבחור אפשרות אחת לפחות ")
                with col_c:
                    st.form_submit_button("טען", key="main_1")

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
    with st.form(key="set_map_details", width="stretch"):
        with st.expander("פילטר ראשי"):
            with st.container():
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    filtering("main", "map_main_filter_1")
                with col_b:
                    st.write("\n יש לבחור אפשרות אחת לפחות ")
                with col_c:
                    st.form_submit_button("טען", key="map_1")
        @st.cache_data
        def fig_to_html(fig):
            fig.update_layout(autosize=True, width=None, height=None)
            return fig.to_html(include_plotlyjs='cdn', full_html=False)


        # @st.cache_data
        # def expose_int_map():
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
                width=700,
                key="int_map")
        # expose_int_map()
    # st.form_submit_button("טען")

with tab3:
    sub_tab_detailed, sub_tab_model = st.tabs(["גולמי", "מודל"])
    with sub_tab_detailed:
        with st.form(key="data_analysis", width="stretch"):
            with st.expander("פילטר ראשי"):
                with st.container():
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        filtering("main", "data_analysis_filter_chbx")
                        filtering("settlements","settlements_chbx")
                    with col_b:
                        filtering("selections", "selections_chbx")
                    with col_c:
                        filtering("values", "values_chbx")
                        st.form_submit_button("טען", key="width_data")
    with sub_tab_model:
        with st.form(key="data_analysis_model", width="stretch"):
            with st.expander("פילטר ראשי"):
                with st.container():
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        filtering("main", "data_analysis_filter_model_chbx")
                        filtering("settlements","settlements_model_chbx")
                    with col_b:
                        filtering("model", "selections_model")
                    with col_c:
                        filtering("values", "values_model_chbx")
                        st.session_state.data_view_options = st.radio("צורת הצגה", ["שעונים", "פיזור" ,"מפת חום"])
                        place_vertical_spacer(5)
                        st.form_submit_button("טען", key="d_model")


        print("============== Testing sgment ================")
        if data_load_measure_state["load_stack"] == data_load_measure_state["max_load"]:
            st.toast("שימ/י לב כי כל הנתונים נבחרו להצגה הצגת הנתונים עלולה לקחת זמן רב! ")

        # create a list of settlements to buffer the search dimension
        print(" | create a list of settlements to buffer the search dimension")
        target_settlements_list = []
        shrinked_settlements_list = []
        st.session_state.attributes = []
        if _all in st.session_state.settlements_selections:
            target_settlements_list = list(InternalGoogleSheetVars.settlements_data.keys())
        else:
            target_settlements_list = st.session_state.settlements_selections

        # tighten search scope with main filters
        print(" | tighten search scope with main filters")
        print(" | testing sources:")
        print(f" | divisions filter: {st.session_state.filters["division"]}")
        print(f" | councils filter: {st.session_state.filters["council"]}")
        print(f" | types filter: {st.session_state.filters["type"]}")
        print(" | ")
        for settlement in target_settlements_list:
            if (_all in st.session_state.filters["division"] and len(st.session_state.filters["division"]) == 1) or (set(st.session_state.filters["division"]).intersection(set(InternalGoogleSheetVars.settlements_data[settlement]["division"]))):
                if (_all in st.session_state.filters["council"] and len(st.session_state.filters["council"]) == 1) or (set(st.session_state.filters["council"]).intersection(set(InternalGoogleSheetVars.settlements_data[settlement]["council"]))):
                    if (_all in st.session_state.filters["type"] and len(st.session_state.filters["type"]) == 1) or (set(st.session_state.filters["type"]).intersection(set(InternalGoogleSheetVars.settlements_data[settlement]["type"]))):
                        if (_all in st.session_state.filters["distance"] and len(st.session_state.filters["distance"]) == 1) or (set(st.session_state.filters["distance"]).intersection(set(InternalGoogleSheetVars.settlements_data[settlement]["distance"]))):
                            print(f" |_ settlement: {settlement}")
                            shrinked_settlements_list.append(settlement)
            else:
                continue
        # create a list of the attributes that should be taken from the tables
        print(" | create a list of the attributes that should be taken from the tables")
        if st.session_state.data_view_selector =="raw":
            if st.session_state.selections:
                for key in st.session_state.selections:
                    print(f" | key from st.session_state.selection: {key}")
                    if _all not in st.session_state.selections[key]:
                        st.session_state.attributes += st.session_state.selections[key]
                        print(f" | added value to attributes buffer : {st.session_state.selections[key]} buffer length: {len(st.session_state.attributes)}")
                    else:
                        st.session_state.attributes += InternalGoogleSheetVars.options[key]
                        print(
                            f" |_ added value to attributes buffer : {st.session_state.selections[key]} buffer length: {len(st.session_state.attributes)}")
        else:
            st.session_state.attributes = st.session_state.model_selection

        # create data frame according to the selection of the representation

        # buffer related data using external data source (from tables)

        results = []
        print(" | data grabbing segment")
        print(f" | shrinked_settlements_list length: {len(shrinked_settlements_list)}")


        # grabbing data from the googlesheet table
        data_frame = {}
        lines_buffer = []
        for line in sheet:
            if line['ישוב'] in shrinked_settlements_list:
                lines_buffer.append(line)

        # preparing for calculations
        status_translator = {"תקין":100,"בהקמה":50, "לא תקין\חסר": 20}
        local_convertion = {"מדד לוגיסטי אמסל\"ח אישי":"מדד לוגיסטי אמסל\"ח אישי",
                            "מדד לוגיסטי אמסל\"ח מסגרתי":"מדד לוגיסטי אמסל\"ח מסגרתי",
                            "מדד מאג":"מדד מאג",
                            "מדד ציוד רפואי":"מדד ציוד רפואי",
                            "מדד מב\"ט בסיסי":"מדד מב\"ט בסיסי",
                            "מדד מב\"ט מתקדם":"מדד מב\"ט מתקדם",
                            "מדד לוגיסטי צח\"י":"מדד לוגיסטי צח\"י",
                            "מדד לוגיסטי חמ\"ל":"מדד לוגיסטי חמ\"ל",
                            "מדד לוגיסטי מ\"ה":"מחלקת הגנה - ציוד - לוגיסטי",
                            "מדד איוש מ\"ה":"מדד איוש מ\"ה",
                            "מדד ציוד תקשוב מ\"ה": "מחלקת הגנה - ציוד - תקשוב" ,
                            "מדד צח\"י":["צח\"י - ציוד","צח\"י - כח אדם" , "צח\"י כשירות סטטוס"],
                            "נץ הטמעה סטטוס":{"name":"נץ הטמעה סטטוס"},
                            "מדד נץ":{"name":"נץ הטמעה סטטוס"},
                            "מדד ציוד לוגיסטי מ\"ה":""}
        st.session_state.hm_data_frame = []
        for attr in st.session_state.attributes:
            hm_row = []
            if not local_convertion.get(attr):
                hm_row = [float(line[attr][:-1]) for line in lines_buffer]
                data_frame[attr] = sum(hm_row)/len(lines_buffer)
            else:
                if local_convertion.get(attr) and type(local_convertion.get(attr)) == type(str):
                    hm_row = [float(line[local_convertion.get(attr)][:-1]) for line in lines_buffer]
                    data_frame[attr] = sum(hm_row) / len(lines_buffer)
                elif local_convertion.get(attr) and type(local_convertion.get(attr)) == type([]):
                    hm_row = sum([float(line[val][:-1]) if "%" in line[val] else status_translator.get(val) for val in local_convertion.get(attr)])/len(local_convertion.get(attr))
                    data_frame[attr] = sum([sum([float(line[val][:-1]) if "%" in line[val] else status_translator.get(val) for val in local_convertion.get(attr)])/len(local_convertion.get(attr)) for line in lines_buffer])/len(lines_buffer)
                elif local_convertion.get(attr) and type(local_convertion.get(attr)) == type({}):
                    hm_row = [status_translator.get(line[local_convertion.get(attr)["name"]]) for line in lines_buffer]
                    data_frame[attr] = sum(hm_row) / len(lines_buffer)
                else:
                    data_frame[attr] = 0
            st.session_state.hm_data_frame.append(hm_row)

        # data presentation
        if st.session_state.data_view_options == "שעונים":
            max_cols = 4
            rows = 0
            cols = 0
            grid = make_grid(max_cols, max_rows)

            for attr, value in data_frame.items():
                with grid[rows][cols]:
                    make_gauge_graph(attr, value)
                    if st.session_state.data_view_options == "מפת חום":
                        pass
                if cols == max_cols - 1 :
                    cols = 0
                    rows += 1
                else:
                    cols += 1
        if st.session_state.data_view_options == "פיזור":
            show_spider_chart(data_frame, "פריסת נתונים")

        if st.session_state.data_view_options == "מפת חום":
            row_names = shrinked_settlements_list
            col_names = st.session_state.attributes
            show_status_heat_map(st.session_state.hm_data_frame, col_names, row_names, "מפת חום")





        # with st.spinner("מושך נתונים ..."):
        #     with ThreadPoolExecutor(max_workers=67) as executor:
        #
        #         future_to_sheet = { executor.submit(LocalDataEntry.spreadsheet.get_worksheets_range, (InternalGoogleSheetVars.mbt_spreadsheet_name, s)): s for s in shrinked_settlements_list}
        #
        #         for future in as_completed(future_to_sheet):
        #             sheet_name = future_to_sheet[future]
        #             try:
        #                 data = future.result()
        #                 print(sheet_name)
        #                 print(data)
        #                 results.append(data)
        #
        #             except Exception as e:
        #                 print(f"{sheet_name} - exception: {e}")
