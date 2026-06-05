import streamlit as st
from streamlit_folium import st_folium
import folium
import branca
import plotly.graph_objects as go
import pandas as pd
import traceback
from pathlib import Path
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.components import status_badge, make_gauge_graph, make_grid, LocalDataEntry, place_vertical_spacer, \
    show_spider_chart, show_status_heat_map
from variables.static import InternalGoogleSheetVars
from utils.data_source import sheet
from utils.calculations import modeling_elements_names, StochasticModeling
from app import st, logging
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
st.session_state.precents = ["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%", "110%", "120%", "130%", "140%", "150%"]
st.session_state.probability = ["0%", "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"]
st.session_state.data_view_selector = "raw"
st.session_state.models_list = [mod  for mod in InternalGoogleSheetVars.options['model'] if "מדד" in mod] + ["מדד נץ"]

def log_pref(locations= None, message = None):
    setter = ""
    if locations:
        for key, itm in locations.items():
            setter += f"{key} - {itm}, "

    return f"{Path(__file__).name} {setter}  LOG:: {message}"

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


def filtering(filter_type: str,key="default", iterator = None):

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
            if iterator:
                st.session_state.precents_selections =  { key: st.selectbox(key, st.session_state.precents) for key in iterator}
            else:
                st.session_state.precents_selections  = st.selectbox("אחוזים", st.session_state.precents)
        case "probability":
            if iterator:
                st.session_state.probability_selections = {key: st.selectbox("הסתברות"+" "+key, st.session_state.probability) for key in iterator }
            else:
                st.session_state.probability_selections = st.selectbox("הסתברות", st.session_state.probability)
        case _:
            pass

def is_passing_basic_filter():
    return all([len({tab_line['חטיבה'], _all}.intersection(st.session_state.filters['division'])) > 0, len({tab_line['מועצה'], _all}.intersection(st.session_state.filters['council'])) > 0, len({tab_line['סיווג'], _all}.intersection(st.session_state.filters['type'])) > 0, len({tab_line['מרחק מהגדר'], _all}.intersection(st.session_state.filters['distance'])) > 0])
 # st.session_state.filters_local_memory = InternalGoogleSheetVars.settlements_data
# with st.expander("פילטר ראשי"):


tab1, tab2, tab3, tab4 = st.tabs(["מטריצת מדדים", "מפה", "ניתוח רוחבי", "חקר ביצועים"])

# scores matrix
with (tab1):
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
            if is_passing_basic_filter():
                val = float(tab_line["מדד כולל"][:-1])

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
# map
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


        m = folium.Map(location=[31.47, 34.52], zoom_start=11)
        logging.info("running filter")
        for line in sheet:
            tab_line = line
            if all([len({tab_line['חטיבה'], _all}.intersection(st.session_state.filters['division'])) > 0,
                    len({tab_line['מועצה'], _all}.intersection(st.session_state.filters['council'])) > 0,
                    len({tab_line['סיווג'], _all}.intersection(st.session_state.filters['type'])) > 0,
                    len({tab_line['מרחק מהגדר'], _all}.intersection(st.session_state.filters['distance'])) > 0]):
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
                st.toast("שימ/י לב כי כל הנתונים נבחרו להצגה, טעינת הנתונים עלולה לקחת זמן רב! ")


            # create a list of settlements to buffer the search dimension

            target_settlements_list = []
            shrinked_settlements_list = []
            st.session_state.attributes = []
            st.session_state.hm_data_frame_raw_data = []
            st.session_state.hm_data_frame_raw_rows = []
            st.session_state.hm_data_frame_raw_cols = []
            if len({_all}.intersection(st.session_state.settlements_selections)) > 0:
                target_settlements_list = list(InternalGoogleSheetVars.settlements_data.keys())
            else:
                target_settlements_list = st.session_state.settlements_selections

            # tighten search scope with main filters
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
                                logging.info(f" |[raw] insertion of settlement: {settlement}")
                                # the settlement pass all the place filters - creating instance for it data
                                st.session_state.main_raw_data_frame[settlement] = {}

                                #collection anf filtering the criteria list
                                #for crt in st.session_state.criteria_selections:
                else:
                    continue

        with st.spinner("מושך נתונים ..."):
            results = []
            with ThreadPoolExecutor(max_workers=67) as executor:
                future_to_sheet = { executor.submit(LocalDataEntry.spreadsheet.get_worksheets_range, InternalGoogleSheetVars.mbt_spreadsheet_name, s, InternalGoogleSheetVars.calculated_table_ranges['הזזה']): s for s in list(st.session_state.main_raw_data_frame.keys())}

                for future in as_completed(future_to_sheet):
                    settlement_name = future_to_sheet[future]
                    try:
                        # data is a list of lists of the settlement
                        settlement_data = future.result()
                        # make pointing handling
                        pointing_dict = {key.strip(): index for index, key in enumerate(settlement_data[0])}
                        criteria_frame = []
                        ep_data_frame = ['תקן', 'כמות', 'מדד', 'סטטוס']
                        key_transletor = {"status":'סטטוס',"action":'הפעלה',"types":'סיווג',"frame":'מסגרת',"domain":'תחום',"model":'מודל',"economy":'משק',"family":'משפחה'}


                        for line in settlement_data[1:]:
                            flag = False


                            if line[0] in st.session_state.criteria_selections or _all in st.session_state.criteria_selections:
                                logging.info(f" |[raw] criteria: {line[0]} or {_all} recognized as part of criteria_selections: {st.session_state.criteria_selections}")
                                flag = True

                                if flag:
                                    # a check of the other filters
                                    for eng,heb in key_transletor.items():

                                        if line[pointing_dict[heb]]:
                                            if len({_all,line[pointing_dict[heb]]}.intersection(st.session_state.selections[eng])) > 0:
                                                flag = False

                                            break
                                    if flag:

                                        st.session_state.main_raw_data_frame[settlement_name][line[0]] = {}

                                        for key in ep_data_frame:
                                            logging.info(f" |[raw] key: {key}")
                                            logging.info(f" |[raw] pointing_dict[key]: {pointing_dict[key.strip()]}")
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
    st.session_state.model_definition_list = [itm for itm in InternalGoogleSheetVars.options['model'] if 'מדד' in itm and 'מאג' not in itm and 'ציוד לוגיסטי' not in itm ]
    with st.form(key="operations_research_form", width="stretch"):
        with st.expander("הגדרות מודל סטוכסטי"):
            with st.container():
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.write("")
                    filtering("main", "or_main_filter_chbx")
                    filtering("settlements","or_settlements_chbx")
                with col_b:
                    st.write("אחוזי השוואה")
                    filtering("precents", "or_precents_chbx", iterator=st.session_state.model_definition_list)
                    # filtering("criteria", "or_criteria_chbx")
                with col_c:
                    st.write("הסתברות")
                    filtering("probability","or_prob_chbx",iterator=st.session_state.model_definition_list)
                    st.form_submit_button("טען", key="or_btn")


        if data_load_measure_state["load_stack"] == data_load_measure_state["max_load"]:
            st.toast("שימ/י לב כי כל הנתונים נבחרו להצגה הצגת הנתונים עלולה לקחת זמן רב! ")
        st.session_state.stochastic_data_frame = {}
        st.session_state.inverted_data_frame = {}
        st.session_state.settlement_list = []

        def _parse_numeric_percent(value):
            if isinstance(value, (int, float)):
                return float(value)
            if isinstance(value, str):
                cleaned = value.strip().replace("%", "")
                try:
                    return float(cleaned)
                except ValueError:
                    return 0.0
            return 0.0

        with st.container():
            with st.spinner("מבצע חקר ביצועים ..."):
                selected_settlements = (
                    list(InternalGoogleSheetVars.settlements_data.keys())
                    if _all in st.session_state.settlements_selections
                    else st.session_state.settlements_selections
                )

                for settlement in selected_settlements:
                    settlement_meta = InternalGoogleSheetVars.settlements_data.get(settlement) or {}
                    division = settlement_meta.get("division", "")
                    council = settlement_meta.get("council", "")
                    settlement_type = settlement_meta.get("type", settlement_meta.get("classification", ""))
                    distance = settlement_meta.get("distance", "")

                    if (division in st.session_state.filters["division"] or _all in st.session_state.filters["division"]):
                        if (council in st.session_state.filters["council"] or _all in st.session_state.filters["council"]):
                            if (settlement_type in st.session_state.filters["type"] or _all in st.session_state.filters["type"]):
                                if (distance in st.session_state.filters["distance"] or _all in st.session_state.filters["distance"]):
                                    st.session_state.settlement_list.append(settlement)

                settlement_rows = [
                    line for line in LocalDataEntry.data_sheet
                    if line.get("ישוב") in st.session_state.settlement_list
                ]

                if not settlement_rows:
                    st.warning("לא נמצאו ישובים תואמים עבור חישוב המודל")
                else:
                    for key, comps in InternalGoogleSheetVars.pivot_parameters_names.items():
                        per_settlement_averages = []
                        for settlement_details in settlement_rows:
                            comp_values = [
                                converting_raw_data_to_numeric(str(settlement_details.get(comp, "0")))
                                for comp in comps
                            ]
                            if comp_values:
                                per_settlement_averages.append(sum(comp_values) / len(comp_values))

                        average_value = (
                            sum(per_settlement_averages) / len(per_settlement_averages)
                            if per_settlement_averages else 0.0
                        )
                        st.session_state.stochastic_data_frame[key] = [average_value]

                    for key, value in st.session_state.precents_selections.items():
                        if key in st.session_state.stochastic_data_frame:
                            st.session_state.stochastic_data_frame[key].append(_parse_numeric_percent(value))

                    for key, value in st.session_state.probability_selections.items():
                        if key in st.session_state.stochastic_data_frame:
                            st.session_state.stochastic_data_frame[key].append(_parse_numeric_percent(value))



                    # Adapt UI payload to [weight, probability] expected by the stochastic model.
                    model_input = {}
                    for metric_name, raw_values in st.session_state.stochastic_data_frame.items():
                        if metric_name not in modeling_elements_names:
                            print(f" |[model] skipping unsupported modeling key: {metric_name}")
                            continue
                        avg_value = float(raw_values[0]) if len(raw_values) > 0 else 0.0
                        weight_value = float(raw_values[1]) if len(raw_values) > 1 else avg_value
                        probability_value = float(raw_values[2]) if len(raw_values) > 2 else 0.0
                        model_input[metric_name] = [weight_value, probability_value]

                    if not model_input:
                        st.warning("לא נמצאו מפתחות נתמכים עבור מודל סטוכסטי מתוך הקלט שנבחר")
                        st.stop()

                    s = StochasticModeling(model_input, settlements_count=max(1, len(st.session_state.settlement_list)))
                    resolved = s.resolve()

                    def _to_battery_percent(value):
                        if isinstance(value, (int, float)):
                            numeric_value = float(value)
                            if 0 <= numeric_value <= 1:
                                numeric_value *= 100
                            return max(0.0, min(100.0, numeric_value))
                        return 0.0

                    rows = []
                    for key, value in resolved.items():
                        if isinstance(value, dict):
                            for sub_key, sub_val in value.items():
                                rows.append({
                                    "שם": f"{key}.{sub_key}",
                                    "ערך": round(float(sub_val), 4) if isinstance(sub_val, (int, float)) else str(sub_val),
                                    "מדד ביחס ל-100%": _to_battery_percent(sub_val),
                                })
                        else:
                            rows.append({
                                "שם": key,
                                "ערך": round(float(value), 4) if isinstance(value, (int, float)) else str(value),
                                "מדד ביחס ל-100%": _to_battery_percent(value),
                            })

                    result_df = pd.DataFrame(rows, columns=["שם", "ערך", "מדד ביחס ל-100%"])
                    st.dataframe(
                        result_df,
                        width="stretch",
                        hide_index=True,
                        column_config={
                            "מדד ביחס ל-100%": st.column_config.ProgressColumn(
                                "גרף סוללה",
                                min_value=0,
                                max_value=100,
                                format="%.1f%%",
                            )
                        },
                    )

                    overall_score = float(resolved.get("overall_score", 0.0))
                    if overall_score < 50:
                        badge_bg = "#FFC7CE"
                        badge_fg = "#9C0006"
                        result_text = "לא מצליח לעמוד במשימת ההגנה"
                    elif overall_score < 90:
                        badge_bg = "#FFEB9C"
                        badge_fg = "#9C6500"
                        result_text = "בסיכון לעמידה במשימת ההגנה"
                    else:
                        badge_bg = "#C6EFCE"
                        badge_fg = "#006100"
                        result_text = "מצליח לעמוד במשימת ההגנה"

                    chart_keys = list(model_input.keys())
                    actual_coverage = [
                        max(0.0, min(100.0, float(st.session_state.stochastic_data_frame.get(key, [0.0])[0])))
                        for key in chart_keys
                    ]
                    adjusted_coverage = []
                    for key in chart_keys:
                        raw_values = st.session_state.stochastic_data_frame.get(key, [0.0])
                        base_value = float(raw_values[0]) if len(raw_values) > 0 else 0.0
                        percent_value = float(raw_values[1]) if len(raw_values) > 1 else 100.0
                        adjusted_coverage.append(max(0.0, min(100.0, base_value * (percent_value / 100.0))))

                    summary_col_left, summary_col_right = st.columns(2)

                    with summary_col_left:
                        with st.container(border=True):
                            st.markdown("### תוצאת חקר ביצועים")
                            st.markdown(
                                f"""
                                <div style=\"text-align:center; margin-top:10px;\"> 
                                    <div style=\"
                                        display:inline-block;
                                        min-width:260px;
                                        padding:10px 18px;
                                        border-radius:24px;
                                        background:{badge_bg};
                                        color:{badge_fg};
                                        font-weight:bold;
                                        font-size:22px;
                                    \">
                                        {overall_score:.1f}%
                                    </div>
                                    <div style=\"margin-top:10px; font-size:16px;\">{result_text}</div>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                    with summary_col_right:
                        with st.container(border=True):
                            st.markdown("### גרף עכביש - כיסוי מול כיסוי מותאם")
                            if chart_keys:
                                spider_categories = chart_keys + [chart_keys[0]]
                                actual_closed = actual_coverage + [actual_coverage[0]]
                                adjusted_closed = adjusted_coverage + [adjusted_coverage[0]]

                                spider_fig = go.Figure()
                                spider_fig.add_trace(
                                    go.Scatterpolar(
                                        r=actual_closed,
                                        theta=spider_categories,
                                        fill="toself",
                                        name="כיסוי בפועל",
                                            line=dict(color="royalblue"),
                                    )
                                )
                                spider_fig.add_trace(
                                    go.Scatterpolar(
                                        r=adjusted_closed,
                                        theta=spider_categories,
                                        fill="toself",
                                        name="כיסוי לאחר הכפלה באחוזים",
                                            line=dict(color="darkorange"),
                                    )
                                )
                                spider_fig.update_layout(
                                    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                                    showlegend=True,
                                    margin=dict(l=30, r=30, t=30, b=30),
                                )
                                st.plotly_chart(spider_fig, use_container_width=True)
                            else:
                                st.info("אין נתונים להצגת גרף עכביש")

