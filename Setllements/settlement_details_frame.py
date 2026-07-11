import random
import time
from pathlib import Path
import streamlit as st
from data.internal.run_time_instances import get_google_drive_instance
from utils.components import make_grid, make_gauge_graph, LocalDataEntry, show_spider_chart, \
    present_model_components_table
from utils.logger import color_logger, log_pref, tracer, tracer_status

# logging instance
log = color_logger()
file_name = Path(__file__).name.split('.')[0].strip()


st.session_state["settlement_details_frame"] = "s_tab1"

class StaticData:
    spreadsheet_name = "מרכיבי בטחון "
    worksheet_name = "נתונים"

class VisualConfiguration:
    class Button:
        type = "secondary"
        size = "stretch"
        # class Size:
        #     stretch = "stretch"
        #     small = "small"
        #     medium = "medium"
        #     large = "large"
        #
        # class Type:
        #     primary = "primary"
        #     secondary = "secondary"
        #     tertiary = "tertiary"


@st.cache_data
def get_qualification_data(settlement_name):
    _locations = {"file_name: " : file_name, "function: ": "get_qualification_data", "arg": settlement_name}
    log.debug(log_pref(locations=_locations, message=f"google drive authentication"))
    gs = get_google_drive_instance()

    ret_val = gs.get_qualification_variable(settlement_name)
    log.debug(log_pref(locations=_locations, message=f"returned ret_val = {ret_val}"))


    if ret_val:
        dt = float(gs.get_qualification_variable(settlement_name))
        if dt:
            return dt * 100

    log.critical(log_pref(locations=_locations, message=f"get_qualification_data ret_val got None returning default regenerate"))
    return random.uniform(0.6, 1.0)*100

# todo: refactor all function to more robastic maner - now it hard coded - when the data base will be ready
def present_single_settlement_details(settlement_name: str):
    _locations = {"file_name: ": file_name, "function: ": "present_single_settlement_details", "arg": settlement_name}
    tracer(f"settlement_details_frame.py - present_single_settlement_details invoked - for settlement {st.session_state.settlement_name} ")

    tracer_status(
        f"app.py - {st.session_state['ravshats_table']=}, {st.session_state['settlements_stack']=}, {st.session_state['active_screen_index']=} {st.session_state["settlement_details_frame"]=}")
    # load parameters
    # pivot_parameters_names = list(LocalDataEntry.data_sheet[0].keys())
    spider_chart_df = {}
    heat_map_data = []

    statuses_values_dict = {"תקין":1,
                            "לא תקין\חסר":0,
                            "בהקמה":0.5,
                    }
    pivot_parameters_names = {"מדד מב\"ט בסיסי":["מדד מב\"ט בסיסי"],
                "מדד מב\"ט מתקדם":["מדד מב\"ט מתקדם"],
                "רפואה":["רפואה - אמבולנס","רפואה - ציוד"] ,
                "מחלקת הגנה":["מחלקות הגנה - כח אדם",
                              "מחלקות הגנה - כשירות",
                              "מחלקת הגנה - ציוד - צל\"מ",
                              "מחלקת הגנה - ציוד - אמסל\"ח",
                              "מחלקת הגנה - ציוד - תקשוב",
                              "מחלקת הגנה - ציוד - לוגיסטי"],
                "נץ":["נץ הטמעה סטטוס"],
                "צחי":["צח\"י כשירות סטטוס", "צח\"י - כח אדם"],
                "חמ\"ל ישובי" :["חמ\"ל ישובי כח אדם", "חמ\"ל ישובי - ציוד"]}



    def go_back():
        tracer(f"settlement_details_frame.py - go_back button callback - for settlement {st.session_state.settlement_name} ")
        st.session_state["settlement_details_frame"] = "s_tab1"
        st.rerun()

    def s_tab2():
        tracer(
            f"settlement_details_frame.py - s_tab2  invoked - for settlement {st.session_state.settlement_name} ")
        if st.session_state["settlement_details_frame"] == "s_tab2":
            table_keys = ["מדד מב\"ט בסיסי"]
            tracer(
                f"settlement_details_frame.py - s_tab2 with {table_keys[0]} invoked and approved - for settlement {st.session_state.settlement_name} ")
            log.debug(log_pref(locations=_locations, message=f" \n**** input from tab 2 -settlement_name = {settlement_name} table_keys = {table_keys}"))
            present_model_components_table(settlement_name, table_keys)
            st.button(on_click=go_back, label="חזור", type="secondary", key=f"back_button_{random.random()}")
    def s_tab3():
        if st.session_state["settlement_details_frame"] == "s_tab3":
            table_keys = ["מדד מב\"ט מתקדם"]
            tracer(
                f"settlement_details_frame.py - s_tab3 with {table_keys[0]} invoked and approved - for settlement {st.session_state.settlement_name} ")
            log.debug(log_pref(locations=_locations, message=f" \n**** input from tab 3 -settlement_name = {settlement_name} table_keys = {table_keys}"))
            present_model_components_table(settlement_name, table_keys)
            st.button(on_click=go_back, label="חזור", type="secondary", key=f"back_button_{random.random()}")
    def s_tab4():
        if st.session_state["settlement_details_frame"] == "s_tab4":
            table_keys = ["רפואה - אמבולנס","רפואה - ציוד"]
            r_ranges = ["A276:B277" ,"X29:AB33" ]
            tracer(
                f"settlement_details_frame.py - s_tab4 with {table_keys[0]} invoked and approved - for settlement {st.session_state.settlement_name} ")
            log.debug(log_pref(locations=_locations, message=f" \n**** input from tab 4 -settlement_name = {settlement_name} table_keys = {table_keys}"))
            present_model_components_table(settlement_name, table_keys, r_ranges)
            st.button(on_click=go_back, label="חזור", type="secondary", key=f"back_button_{random.random()}")

    def s_tab5():
        if st.session_state["settlement_details_frame"] == "s_tab5":
            table_keys = ["מדד איוש מ\"ה","מחלקות הגנה - כשירות"]
            tracer(
                f"settlement_details_frame.py - s_tab5 with {table_keys[0]} invoked and approved - for settlement {st.session_state.settlement_name} ")
            r_ranges = ["K21:P24", "R4:V19"]
            log.debug(log_pref(locations=_locations, message=f" \n**** input from tab 4 -settlement_name = {settlement_name} table_keys = {table_keys}"))
            present_model_components_table(settlement_name, table_keys,r_ranges,get_qualification_data(settlement_name))
            st.button(on_click=go_back, label="חזור", type="secondary", key=f"back_button_{random.random()}")

    def s_tab6():
        if st.session_state["settlement_details_frame"] == "s_tab6":
            st.write("בפיתוח")
            st.button(on_click=go_back, label="חזור", type="secondary", key=f"back_button_{random.random()}")

    def s_tab7():
        if st.session_state["settlement_details_frame"] == "s_tab7":
            st.write("בפיתוח")
            st.button(on_click=go_back, label="חזור", type="secondary", key=f"back_button_{random.random()}")

    def s_tab8():
        if st.session_state["settlement_details_frame"] == "s_tab8":
            st.write("בפיתוח")
            st.button(on_click=go_back, label="חזור", type="secondary", key=f"back_button_{random.random()}")


    callbacks_references = {"מדד מב\"ט בסיסי":s_tab2, "מדד מב\"ט מתקדם":s_tab3, "רפואה":s_tab4, "מחלקת הגנה":s_tab5, "נץ":s_tab6, "צחי":s_tab7, "חמ\"ל ישובי":s_tab8}
    def switch_view(func):
        _locations["function"] = "switch_view"
        tracer(
            f"settlement_details_frame.py - switch_view button callback - for settlement {st.session_state.settlement_name} ")
        tracer_status(
            f"app.py - {st.session_state['ravshats_table']=}, {st.session_state['settlements_stack']=}, {st.session_state['active_screen_index']=}")
        log.debug(log_pref(locations=_locations,
                           message=f" \nsettlement_name = {settlement_name}  {func.__name__}"))
        st.session_state["settlement_details_frame"] = func.__name__
        func()

    def s_tab1():
        if st.session_state["settlement_details_frame"] == "s_tab1":
            with st.container():

                tracer_status(
                    f"app.py - {st.session_state['ravshats_table']=}, {st.session_state['settlements_stack']=}, {st.session_state['active_screen_index']=}")
                st.markdown(f"""
                             <div style='text-align: right;'>
                                 <h1>{settlement_name} </h1>
                             </div>
                             """, unsafe_allow_html=True)
                max_parameters = len(pivot_parameters_names)
                min_parameters = 0
                settlement_details = {}

                # find the settlement
                for line in LocalDataEntry.data_sheet:
                    if line["ישוב"] == settlement_name:
                        settlement_details = line
                        break

                # initializing grid creation
                if settlement_details:
                    rows = 0
                    cols = 0

                    grid = make_grid(3, max_parameters)
                    for key, comps in pivot_parameters_names.items():
                        with grid[rows][cols]:

                            for comp in comps:
                                val_range = []
                                if ("סטטוס" in comp or "אמבולנס" in comp) and 'נץ' not in comp:
                                    val_range.append(statuses_values_dict[settlement_details[comp]])
                                else:

                                    if  "מחלקות הגנה - כשירות" not in comp and "מחלקת הגנה - ציוד - לוגיסטי" not in comp and  'נץ' not in comp:
                                        val_range.append(float(settlement_details[comp][:-1]))
                                    elif "מחלקות הגנה - כשירות" in comp:
                                        val_range.append(get_qualification_data(settlement_name) if get_qualification_data(settlement_name) else 74)
                                        time.sleep(1)
                                    elif 'נץ' in comp:
                                        val_range.append(statuses_values_dict[settlement_details[comp]]*100)
                                    else:
                                        val_range.append(float(settlement_details[comp][:-1])*20)
                            log.debug(log_pref(locations=_locations, message=f"key = {key} comp = {comp} val_range = {sum(val_range)} avg = {sum(val_range)/len(val_range)}"))
                            spider_chart_df[key] = sum(val_range)/len(val_range)
                            make_gauge_graph(key, sum(val_range)/len(val_range))
                            st.button(label=f"  פרטים ",
                                      on_click=switch_view,
                                      args=(callbacks_references[key],),
                                      width="stretch",
                                      type="tertiary",
                                      key=f"{key}_callback_{random.random()}")


                        if cols == 2:
                            cols = 0
                            rows += 1
                        else:
                            cols += 1

                show_spider_chart(spider_chart_df, "מדד כולל")

    if st.session_state["settlement_details_frame"] == "s_tab1":
        s_tab1()


