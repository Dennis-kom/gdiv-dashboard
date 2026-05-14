import streamlit as st
from streamlit_folium import st_folium
import folium
import branca
import plotly.graph_objects as go
import traceback
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

data_load_measure_state = {"max_load":4, "load_stack":0}
st.session_state.divisions = ['הכל', 'צפונית', 'דרומית']
st.session_state.councils = ['הכל', 'שדרות', 'שער הנגב', 'שדות נגב', 'אשכול', 'חוף אשקלון']
st.session_state.types = ['הכל', 'סמוך', 'ליבה', 'ליבה קדמי']
st.session_state.distances = ['הכל', '7+', '4-7', '0-4']
st.session_state.settlements = ['הכל'] + list(InternalGoogleSheetVars.settlements_data.keys())
st.session_state.val_selections =  ['הכל'] + ["0-30", "30-50", "50-90", "90-100"]
st.sessiom_state.precents = ["0", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100", "110", "120", "130", "140", "150"]
st.sessiom_state.probability = ["0", "10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
st.session_state.data_view_selector = "raw"
st.session_state.models_list = [mod  for mod in InternalGoogleSheetVars.options['model'] if "מדד" in mod] + ["מדד נץ"]

def converting_raw_data_to_numeric(data: str):
    if "%" in data:
        return float(data[:-1])
    elif '.' in data and data.split('.')[0].isnumeric():
        return float(data)
    elif data.isnumeric():
        return float(data)
    else:
        status_translator = {"תקין": 100, "בהקמה": 50, "לא תקין\חסר": 20}
        return status_translator.get(data, 0) # default to 0 if status not found


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
                'model': st.multiselect("מודל", InternalGoogleSheetVars.options['model'] + ["הכל"], default=default_val),
                'economy': st.multiselect("משק", InternalGoogleSheetVars.options['economy'], default=default_val),
                'family': st.multiselect("משפחה", InternalGoogleSheetVars.options['family'], default=default_val)}
        case "model":
            st.session_state.data_view_selector = "model"
            st.session_state.model_selection = st.multiselect("מודל", st.session_state.models_list)
        case "values":
            all_shortcut = st.checkbox('הצג הכל',key=key)
            default_val = ['הכל'] if all_shortcut else None
            data_load_measure_state["load_stack"] += 1 if all_shortcut else 0
            st.session_state.values_selections = st.multiselect("פרמטרים",st.session_state.val_selections,default=default_val)
        case "criteria":
            all_shortcut = st.checkbox('הצג הכל', key=key)
            default_val = ['הכל'] if all_shortcut else None
            data_load_measure_state["load_stack"] += 1 if all_shortcut else 0
            st.session_state.criteria_selections = st.multiselect("קריטריונים", InternalGoogleSheetVars.options['criteria'] + ['הכל'], default=default_val)
        case "precents":
            st.session_state.precents_selections  = st.selectbox("אחוזים", st.sessiom_state.precents)
        case "probability":
            st.session_state.probability_selections = st.electbox("הסתברות", st.sessiom_state.probability)
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
                        filtering("criteria", "criteria_chbx")
                        st.session_state.data_view_options_raw = st.radio("צורת הצגה", ["שעונים", "פיזור", "מפת חום"])
                        place_vertical_spacer(10)
                        st.form_submit_button("טען", key="width_data")

            if data_load_measure_state["load_stack"] == data_load_measure_state["max_load"]:
                st.toast("שימ/י לב כי כל הנתונים נבחרו להצגה הצגת הנתונים עלולה לקחת זמן רב! ")

            print(" |[raw] ###############################  Start debugging Segment ###############################")
            # create a list of settlements to buffer the search dimension
            print(" |[raw] create a list of settlements to buffer the search dimension ")
            target_settlements_list = []
            shrinked_settlements_list = []
            st.session_state.attributes = []
            st.session_state.hm_data_frame_raw_data = []
            st.session_state.hm_data_frame_raw_rows = []
            st.session_state.hm_data_frame_raw_cols = []
            if _all in st.session_state.settlements_selections:
                target_settlements_list = list(InternalGoogleSheetVars.settlements_data.keys())
            else:
                target_settlements_list = st.session_state.settlements_selections

            # tighten search scope with main filters
            print(" |[raw] tighten search scope with main filters ")
            print(" |[raw] testing sources :")
            print(f" |[raw] divisions filter : {st.session_state.filters["division"]}")
            print(f" |[raw] councils filter : {st.session_state.filters["council"]}")
            print(f" |[raw] types filter : {st.session_state.filters["type"]}")
            print(" |[raw] ")
            st.session_state.main_raw_data_frame = {}
            for settlement in target_settlements_list:
                if (_all in st.session_state.filters["division"] and len(
                        st.session_state.filters["division"]) == 1) or (
                set(st.session_state.filters["division"]).intersection(
                        set(InternalGoogleSheetVars.settlements_data[settlement]["division"]))):
                    if (_all in st.session_state.filters["council"] and len(
                            st.session_state.filters["council"]) == 1) or (
                    set(st.session_state.filters["council"]).intersection(
                            set(InternalGoogleSheetVars.settlements_data[settlement]["council"]))):
                        if (_all in st.session_state.filters["type"] and len(
                                st.session_state.filters["type"]) == 1) or (
                        set(st.session_state.filters["type"]).intersection(
                                set(InternalGoogleSheetVars.settlements_data[settlement]["type"]))):
                            if (_all in st.session_state.filters["distance"] and len(
                                    st.session_state.filters["distance"]) == 1) or (
                            set(st.session_state.filters["distance"]).intersection(
                                    set(InternalGoogleSheetVars.settlements_data[settlement]["distance"]))):
                                # if (_all is st.session_state.filters["status"] and len(st.session_state.filters["status"]) == 1) or (set(st.session_state.filters["status"].intersection(set(InternalGoogleSheetVars.settlements_data[settlement]["status"])))):
                                print(f" |[raw] insertion of settlement: {settlement}")
                                # the settlement pass all the place filters - creating instance for it data
                                st.session_state.main_raw_data_frame[settlement] = {}

                                #collection anf filtering the criteria list
                                #for crt in st.session_state.criteria_selections:
                else:
                    continue
        print(" |[raw] starting grabbing from sheets")
        with st.spinner("מושך נתונים ..."):
            results = []
            with ThreadPoolExecutor(max_workers=67) as executor:
                print(" |[raw] start grabbing from sheets - ThreadPoolExecutor in context ...")
                print(f" |[raw] static arguments: mbt_spreadsheet_name:{InternalGoogleSheetVars.mbt_spreadsheet_name}  calculated_table_ranges:{InternalGoogleSheetVars.calculated_table_ranges['הזזה']}")
                future_to_sheet = { executor.submit(LocalDataEntry.spreadsheet.get_worksheets_range, InternalGoogleSheetVars.mbt_spreadsheet_name, s, InternalGoogleSheetVars.calculated_table_ranges['הזזה']): s for s in list(st.session_state.main_raw_data_frame.keys())}

                for future in as_completed(future_to_sheet):
                    settlement_name = future_to_sheet[future]
                    try:
                        # data is a list of lists of the settlement
                        settlement_data = future.result()
                        # make pointing handling
                        pointing_dict = {key.strip(): index for index, key in enumerate(settlement_data[0])}
                        print(" |[raw] testing pointing_dict creation ..")
                        print(" ----------------------------------- ")
                        for key, index in pointing_dict.items():
                            print(f"key: {key}")
                            print(f"index: {index}")
                            print("_ _ _ _ _ _")
                        print(" ----------------------------------- ")

                        criteria_frame = []
                        ep_data_frame = ['תקן', 'כמות', 'מדד', 'סטטוס']
                        key_transletor = {"status":'סטטוס',"action":'הפעלה',"types":'סיווג',"frame":'מסגרת',"domain":'תחום',"model":'מודל',"economy":'משק',"family":'משפחה'}
                        print(f" |[raw] sheet_data: {settlement_name}")

                        for line in settlement_data[1:]:
                            flag = False
                            print(f" |[raw] settlement: {settlement_name} criteria: {line[0]}")
                            print(f" |[raw] criteria_selections: {st.session_state.criteria_selections}")
                            if line[0] in st.session_state.criteria_selections or _all in st.session_state.criteria_selections:
                                print(f" |[raw] criteria: {line[0]} or {_all} recognized as part of criteria_selections: {st.session_state.criteria_selections}")
                                flag = True

                                if flag:
                                    # a check of the other filters
                                    for eng,heb in key_transletor.items():
                                        print(f" |[raw] inserting endpoint data ...")
                                        print(" |[raw] line and dict check: ")
                                        print(f" |__[raw]  line: {line}")
                                        print(f" |__[raw]  line[0]: {line[0]}")
                                        print(f" |__[raw]  line[1]: {line[1]}")
                                        print(f" |__[raw]  line[2]: {line[2]}")
                                        print(f" |__[raw]  heb: {heb}")

                                        print(f" |__[raw]  pointing_dict.get(heb): {pointing_dict.get(heb)}")
                                        print(f" |__[raw]  line[pointing_dict.get(heb)]: {line[pointing_dict.get(heb)]}")
                                        print(f" |[raw] data selection data {line[pointing_dict.get(heb)]} in list: {st.session_state.selections.get(eng)} and {_all} in {st.session_state.selections.get(eng)}")
                                        print(f" |___[raw] condition check {line[pointing_dict.get(heb)]} in list: {st.session_state.selections.get(eng)} result: {line[pointing_dict[heb]] in st.session_state.selections[eng]}")
                                        print(f" |___[raw] condition check {_all} in {st.session_state.selections.get(eng)} result: {_all in st.session_state.selections[eng]}")

                                        if line[pointing_dict[heb]]:
                                            if all([_all not in st.session_state.selections[eng], line[pointing_dict[heb]] not in st.session_state.selections[eng]]):
                                                flag = False

                                            break
                                    print(f" |[raw] flag = {flag} result applied")
                                    print(" |[raw] inserting the end point data ...")
                                    if flag:
                                        print(f" |[raw] iteration flag value is {flag}")
                                        print(f" |[raw] testing main_raw_data_frame structure ... ")
                                        print("-----------------------------")
                                        for item, value in st.session_state.main_raw_data_frame.items():
                                            print(f" key: {item} : {value}")
                                        print(" example:")
                                        print(st.session_state.main_raw_data_frame.get('זיקים'))
                                        print(st.session_state.main_raw_data_frame['זיקים'].get('ערד'))
                                        print("-----------------------------")

                                        st.session_state.main_raw_data_frame[settlement_name][line[0]] = {}

                                        for key in ep_data_frame:
                                            print(f" |[raw] key: {key}")
                                            print(f" |[raw] pointing_dict[key]: {pointing_dict[key.strip()]}")
                                            # print(f" |[raw] line[pointing_dict[key]]: {line[pointing_dict[key.strip()]]}")
                                            # print(f" |[raw] inserting data of key: {key} data: {converting_raw_data_to_numeric(line[pointing_dict[key.strip()]])}")
                                            try:
                                                print(" |__[raw] attmptting key adaptation block .... ")
                                                st.session_state.main_raw_data_frame[settlement_name][line[0]][key.strip()] = converting_raw_data_to_numeric(line[pointing_dict[key.strip()]])
                                            except KeyError:
                                                st.session_state.main_raw_data_frame[settlement_name][line[0]][
                                                    key.strip()] = converting_raw_data_to_numeric(
                                                    line[pointing_dict[key + ' ']])

                    except Exception as e:
                        print(f"-frame block exception: {e} ")
                        traceback.print_exc()

        # for item, value in st.session_state.main_raw_data_frame.items():
        #     if not value:
        #         st.session_state.main_raw_data_frame.pop(item)

            _val = 'מדד'
            print(f" |[raw] chosed presentation level: {st.session_state.data_view_options_raw}")
            if True:
                max_cols = 4
                rows = 0
                cols = 0
                grid = make_grid(max_cols, max_rows)
                st.session_state.avarages_data_set = {}
                print(f" |[raw] inserting parameters in clocks function ...")
                round_cnt = 0
                for item, comp in st.session_state.main_raw_data_frame.items():
                    if comp:
                        st.session_state.hm_data_frame_raw_cols.append(item)
                        print(f" |[raw] {item} is not empty, inserting its endpoint data")
                        temp = []
                        for criteria, parameters in comp.items():
                            if round_cnt == 0:
                                st.session_state.hm_data_frame_raw_rows.append(criteria)
                                print(f" |[raw] heat map rows criteria: {criteria} added || actual the last value:  {st.session_state.hm_data_frame_raw_rows[0]}")
                            print(f" |[raw] the data dict of {criteria} is:  {parameters}")
                            print(f" |[raw] criteria: {criteria}: value of {_val} is {parameters.get(_val)}")
                            if  st.session_state.avarages_data_set.get(criteria):
                                st.session_state.avarages_data_set[criteria] += parameters[_val]
                                temp.append(parameters[_val])
                                print(f" |[raw] heat map temp list : {temp}")
                            else:
                                st.session_state.avarages_data_set[criteria] = parameters[_val]
                                temp.append(parameters[_val])
                                print(f" |[raw] heat map temp list : {temp}")

                        st.session_state.hm_data_frame_raw_data.append(temp)
                        print(f" |[raw] heat map data matrix : {st.session_state.hm_data_frame_raw_data}")
                    round_cnt += 1

                for criteria, total_sum in  st.session_state.avarages_data_set.items():
                    st.session_state.avarages_data_set[criteria] = total_sum / len(st.session_state.main_raw_data_frame)

            if st.session_state.data_view_options_raw == "שעונים":
                for title, value in  st.session_state.avarages_data_set.items():
                    with grid[rows][cols]:
                        try:
                            make_gauge_graph(title, value)
                        except KeyError as e:
                            print(f" --- Exceptoion KeyError as {e} of: {criteria}")

                    if cols == max_cols - 1:
                        cols = 0
                        rows += 1
                    else:
                        cols += 1

            elif st.session_state.data_view_options_raw == "פיזור":
                show_spider_chart( st.session_state.avarages_data_set,"פיזור")
            else:
                # heat map
                print(f" |[raw] heat map - data {st.session_state.hm_data_frame_raw_data}")
                print(f" |[raw] heat map - cols {st.session_state.hm_data_frame_raw_cols}")
                print(f" |[raw] heat map - rows {st.session_state.hm_data_frame_raw_rows}")
                print()
                show_status_heat_map(st.session_state.hm_data_frame_raw_data,
                                     st.session_state.hm_data_frame_raw_cols,
                                     st.session_state.hm_data_frame_raw_rows,
                                     "מפת חום")
                pass
    print(" |[raw] ###############################  End debugging Segment ###############################")



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
                        place_vertical_spacer(10)
                        st.form_submit_button("טען", key="d_model")

        if data_load_measure_state["load_stack"] == data_load_measure_state["max_load"]:
            st.toast("שימ/י לב כי כל הנתונים נבחרו להצגה הצגת הנתונים עלולה לקחת זמן רב! ")

        # create a list of settlements to buffer the search dimension
        print(" |[model] create a list of settlements to buffer the search dimension - model section")
        target_settlements_list = []
        shrinked_settlements_list = []
        st.session_state.attributes = []
        if _all in st.session_state.settlements_selections:
            target_settlements_list = list(InternalGoogleSheetVars.settlements_data.keys())
        else:
            target_settlements_list = st.session_state.settlements_selections

        # tighten search scope with main filters
        print(" |[model] tighten search scope with main filters")
        print(" |[model] testing sources:")
        print(f" |[model] divisions filter: {st.session_state.filters["division"]}")
        print(f" |[model] councils filter: {st.session_state.filters["council"]}")
        print(f" |[model] types filter: {st.session_state.filters["type"]}")
        print(" |[model] ")
        for settlement in target_settlements_list:
            if (_all in st.session_state.filters["division"] and len(st.session_state.filters["division"]) == 1) or (set(st.session_state.filters["division"]).intersection(set(InternalGoogleSheetVars.settlements_data[settlement]["division"]))):
                if (_all in st.session_state.filters["council"] and len(st.session_state.filters["council"]) == 1) or (set(st.session_state.filters["council"]).intersection(set(InternalGoogleSheetVars.settlements_data[settlement]["council"]))):
                    if (_all in st.session_state.filters["type"] and len(st.session_state.filters["type"]) == 1) or (set(st.session_state.filters["type"]).intersection(set(InternalGoogleSheetVars.settlements_data[settlement]["type"]))):
                        if (_all in st.session_state.filters["distance"] and len(st.session_state.filters["distance"]) == 1) or (set(st.session_state.filters["distance"]).intersection(set(InternalGoogleSheetVars.settlements_data[settlement]["distance"]))):
                            print(f" |_[model] settlement: {settlement}")
                            shrinked_settlements_list.append(settlement)
            else:
                continue

        ################################# Logic Segment ######################################

        # create a list of the attributes that should be taken from the tables
        print(" |[model] create a list of the attributes that should be taken from the tables")
        if st.session_state.data_view_selector =="raw":
            if st.session_state.selections:
                for key in st.session_state.selections:
                    print(f" |[model] key from st.session_state.selection: {key}")
                    if _all not in st.session_state.selections[key]:
                        st.session_state.attributes += st.session_state.selections[key]
                        print(f" |[model] added value to attributes buffer : {st.session_state.selections[key]} buffer length: {len(st.session_state.attributes)}")
                    else:
                        st.session_state.attributes += InternalGoogleSheetVars.options[key]
                        print(
                            f" |_[model] added value to attributes buffer : {st.session_state.selections[key]} buffer length: {len(st.session_state.attributes)}")
        else:
            st.session_state.attributes = st.session_state.model_selection

        # create data frame according to the selection of the representation
        # buffer related data using external data source (from tables)

        results = []
        print(" |[model] data grabbing segment")
        print(f" |[model] shrinked_settlements_list length: {len(shrinked_settlements_list)}")


        # grabbing data from the googlesheet table
        data_frame = {}
        lines_buffer = []
        for line in sheet:
            if line['ישוב'] in shrinked_settlements_list:
                lines_buffer.append(line)


        # preparing for calculations
        status_translator = {"תקין":100,"בהקמה":50, "לא תקין\חסר": 20}
        local_convertion = {
                            "מדד לוגיסטי צח\"י":"מדד לוגיסטי צח\"י",
                            "מדד לוגיסטי חמ\"ל":"מדד לוגיסטי חמ\"ל",
                            "מדד לוגיסטי מ\"ה":"מחלקת הגנה - ציוד - לוגיסטי",
                            "מדד ציוד תקשוב מ\"ה": "מחלקת הגנה - ציוד - תקשוב" ,
                            "מדד צח\"י":["צח\"י - ציוד","צח\"י - כח אדם" , "צח\"י כשירות סטטוס"],
                            "נץ הטמעה סטטוס":{"name":"נץ הטמעה סטטוס"},
                            "מדד נץ":{"name":"נץ הטמעה סטטוס"},
                            "מדד ציוד לוגיסטי מ\"ה":"מדד לוגיסטי מ\"ה"
                             }
        st.session_state.hm_data_frame = []
        for attr in st.session_state.attributes:
            hm_row = []
            print(f" |[model] current attribute: {attr}")
            if not local_convertion.get(attr):
                hm_row = [float(line[attr][:-1]) for line in lines_buffer]
                data_frame[attr] = sum(hm_row)/len(lines_buffer)
                print(f" |[model] inserted data_frame[attr] : {data_frame[attr]} - {attr}")
            else:
                if local_convertion.get(attr.strip()) and type(local_convertion.get(attr.strip())) == type("str"):
                    hm_row = [float(line[local_convertion.get(attr)][:-1]) for line in lines_buffer]
                    data_frame[attr] = sum(hm_row) / len(lines_buffer)
                    print(f" |[model] inserted data_frame[attr] : {data_frame[attr]} - {attr}")
                elif local_convertion.get(attr) and type(local_convertion.get(attr)) == type([]):
                    hm_row = sum([float(line[val][:-1]) if "%" in line[val] else status_translator.get(val) for val in local_convertion.get(attr)])/len(local_convertion.get(attr))
                    data_frame[attr] = sum([sum([float(line[val][:-1]) if "%" in line[val] else status_translator.get(val) for val in local_convertion.get(attr)])/len(local_convertion.get(attr)) for line in lines_buffer])/len(lines_buffer)
                    print(f" |[model] inserted data_frame[attr] : {data_frame[attr]}")
                elif local_convertion.get(attr) and type(local_convertion.get(attr)) == type({}):
                    hm_row = [status_translator.get(line[local_convertion.get(attr)["name"]]) for line in lines_buffer]
                    data_frame[attr] = sum(hm_row) / len(lines_buffer)
                    print(f" |[model] inserted data_frame[attr] : {data_frame[attr]} - {attr}")
                else:
                    data_frame[attr] = 0
                    print(f" |[model] alert!!! -  inserted data_frame[attr] : is 0 - default value applied - attribute: {attr}")
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

with tab4:
    sub_tab_performence_detailed, sub_tab_performence_model = st.tabs(["לפי קריטריון", "לפי מודל"])
    with sub_tab_performence_detailed:
        with st.form(key="data_analysis_perf", width="stretch"):
            with st.expander("בחירת מדדים"):
                with st.container():
                    col_a, col_b, col_c ,col_d = st.columns(4)
                    with col_a:
                        with st.container():
                            st.title("בחירת טווח")
                            filtering("main", "performence_data_analysis_filter_chbx")
                            filtering("settlements", "performence_settlements_chbx")
                    with col_b:
                        with st.container():
                            st.title("בחירת קרטריונים")
                            filtering("selections", "performence_selections_chbx")
                        with st.container():
                            filtering("criteria", "performence_criteria_chbx")
                    with col_c:
                        with st.container():
                            st.title("מאזן כוח")
                            filtering("values", "performence_values_chbx")
                    with col_d:
                        place_vertical_spacer(15)
                        st.form_submit_button("טען", key="width_data_perf")



               #  ###############  definitions #################
                with st.container():
                    sscol_freind, sscol_enemy = st.columns(2)
                    with sscol_freind:
                        pass
                    with sscol_enemy:
                        pass


                #  ###############  results #################


    with sub_tab_performence_model:
        with st.form(key="data_analysis_model_perf", width="stretch"):
            with st.expander("פילטר ראשי"):
                with st.container():
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        filtering("main", "data_analysis_filter_model_chbx_perf")
                        filtering("settlements","settlements_model_chbx_perf")
                    with col_b:
                        filtering("model", "selections_model_perf")
                    with col_c:
                        filtering("values", "values_model_chbx_perf")
                        place_vertical_spacer(15)
                        st.form_submit_button("טען", key="d_model_perf")




