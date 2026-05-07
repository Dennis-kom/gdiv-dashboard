import streamlit as st
import plotly.graph_objects as go
from utils.gsheets_auth import GoogleSheetsAuth
from utils.components import make_grid, make_gauge_graph, status_badge ,LocalDataEntry, show_spider_chart, show_heat_map

class StaticData:
    spreadsheet_name = "מרכיבי בטחון "
    worksheet_name = "נתונים"


def present_single_settlement_details(settlement_name: str):

    # load parameters
    pivot_parameters_names = list(LocalDataEntry.data_sheet[0].keys())
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
                    if "סטטוס" in comp or "אמבולנס" in comp:
                        val_range.append(statuses_values_dict[settlement_details[comp]])
                    else:
                        print(comp)
                        val_range.append(float(settlement_details[comp][:-1]))
                spider_chart_df[key] = sum(val_range)/len(val_range)
                make_gauge_graph(key, sum(val_range)/len(val_range))


            if cols == 2:
                cols = 0
                rows += 1
            else:
                cols += 1

    show_spider_chart(spider_chart_df, "מדד כולל")




