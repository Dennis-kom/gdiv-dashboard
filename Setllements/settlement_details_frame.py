import random
import time
import streamlit as st
from utils.gdrive_auth import GoogleDriveAuth
from utils.components import make_grid, make_gauge_graph, status_badge, LocalDataEntry, show_spider_chart, \
    show_heat_map, present_model_components_table, log


class StaticData:
    spreadsheet_name = "מרכיבי בטחון "
    worksheet_name = "נתונים"


@st.cache_data
def get_qualification_data(settlement_name):
    gs = GoogleDriveAuth()
    ret_val = gs.get_qualification_variable(settlement_name)
    print(f"   >> >> get_qualification_data ret_val = {ret_val}")
    if ret_val:
        dt = float(gs.get_qualification_variable(settlement_name))
        if dt:
            return dt * 100

    print(f"   >> >> >> ALERT: get_qualification_data ret_val got None returning default regenerate ... ")
    return random.uniform(0.6, 1.0)*100

def present_single_settlement_details(settlement_name: str):

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

    s_tab1, s_tab2, s_tab3, s_tab4, s_tab5, s_tab6, s_tab7, s_tab8 = st.tabs(["מסכם","מדד מב\"ט בסיסי", "מדד מב\"ט מתקדם", "רפואה", "מחלקת הגנה", "נץ", "צחי", "חמ\"ל ישובי"])
    with s_tab1:
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
                                time.sleep(1.5)
                            elif 'נץ' in comp:
                                val_range.append(statuses_values_dict[settlement_details[comp]]*100)
                            else:
                                val_range.append(float(settlement_details[comp][:-1])*20)
                    print(f"key = {key} comp = {comp} val_range = {sum(val_range)} avg = {sum(val_range)/len(val_range)}")
                    spider_chart_df[key] = sum(val_range)/len(val_range)
                    make_gauge_graph(key, sum(val_range)/len(val_range))


                if cols == 2:
                    cols = 0
                    rows += 1
                else:
                    cols += 1

        show_spider_chart(spider_chart_df, "מדד כולל")
    with s_tab2:
        table_keys = ["מדד מב\"ט בסיסי"]
        log(f" \n**** input from tab 2 -settlement_name = {settlement_name} table_keys = {table_keys}")
        present_model_components_table(settlement_name, table_keys)
    with s_tab3:
        table_keys = ["מדד מב\"ט מתקדם"]
        log(f" \n**** input from tab 3 -settlement_name = {settlement_name} table_keys = {table_keys}")
        present_model_components_table(settlement_name, table_keys)
    with s_tab4:
        table_keys = ["רפואה - אמבולנס","רפואה - ציוד"]
        r_ranges = ["A276:B277" ,"X29:AB33" ]
        log(f" \n**** input from tab 4 -settlement_name = {settlement_name} table_keys = {table_keys}")
        present_model_components_table(settlement_name, table_keys, r_ranges)
    with s_tab5:
        table_keys = ["מדד איוש מ\"ה","מחלקות הגנה - כשירות"]
        r_ranges = ["K21:P24", "R4:V19"]
        log(f" \n**** input from tab 4 -settlement_name = {settlement_name} table_keys = {table_keys}")
        present_model_components_table(settlement_name, table_keys,r_ranges,get_qualification_data(settlement_name) )
    with s_tab6:
        st.write("tab 6")
    with s_tab7:
        st.write("tab 7")
    with s_tab8:
        st.write("tab 8")



