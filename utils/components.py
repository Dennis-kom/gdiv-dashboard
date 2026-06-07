from pathlib import Path
from random import random
import streamlit as st
import plotly.graph_objects as go
import folium
from typing import Dict, List
from streamlit_folium import st_folium
from utils.gsheets_auth import GoogleSheetsAuth
from variables.static import InternalGoogleSheetVars
from app import logging

logs_tag = "|[component]:: "
statuses_values_dict = {"תקין": 1,
                        "לא תקין\חסר": 0,
                        "בהקמה": 0.5,
                        "בטיפול":0.5
                        }
class StatusBadgeValues:
    proper = ["תקין", "success"]
    partial = ["חלקי", "part"]
    abnormal = ["לא תקין\\חסר", "error"]


class LocalDataEntry:
    spreadsheet = GoogleSheetsAuth()
    data_sheet = spreadsheet.get_worksheet(InternalGoogleSheetVars.mbt_spreadsheet_name,
                                      InternalGoogleSheetVars.main_data_worksheet_name)
def log_pref(locations= None, message = None):
    setter = ""
    if locations:
        for key, itm in locations.items():
            setter += f"{key}-{itm}, "

    return f"{Path(__file__).name} {setter} LOG::{message}"

def log(message:str):
    print(f"{logs_tag} {message}")

def status_badge(text, color_type="success"):

    if color_type == "success":
        bg_color = "#C6EFCE"
        text_color = "#006100"
    elif color_type == "error":
        bg_color = "#FFC7CE"
        text_color = "#9C0006"
    elif color_type == "part":
        bg_color = "#FFEB9C"
        text_color = "#9C6500"
    elif color_type == "irelevant":
        bg_color = "#D3D3D3"
        text_color = "#A9A9A9"
    else:
        bg_color = "#FFEB9C"
        text_color = "#9C6500"


    badge_html = f"""
    <div style="
        text-align: center; 
        width: 100%; 
        margin-top: -60px; 
        position: relative;
        z-index: 10;
    ">
    <div style="
        display: inline-block;
        padding: 4px 16px;
        background-color: {bg_color};
        color: {text_color};
        border-radius: 20px;
        font-weight: bold;
        font-family: sans-serif;
        font-size: 18px;
        text-align: center;
        direction: rtl;
        border: 1px solid rgba(0,0,0,0.05);
    ">
        {text}
    </div>
    """
    st.markdown(badge_html, unsafe_allow_html=True)

def status_card(label, text, color_type="success"):

    colors = {
        "success": ("#C6EFCE", "#006100"),
        "error": ("#FFC7CE", "#9C0006"),
        "part": ("#FFEB9C", "#9C6500"),
        "irelevant": ("#D3D3D3", "#A9A9A9")
    }
    bg_color, text_color = colors.get(color_type, colors["part"])

    # ה-HTML המאוחד: כרטיס עם מסגרת
    card_html = f"""
    <div style="
        border: 1px solid #444; 
        border-radius: 8px; 
        padding: 10px; 
        margin-bottom: 10px;
        background-color: #1e1e1e;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 100px;
        direction: rtl;
    ">
        <div style="
            color: white; 
            font-weight: bold; 
            font-size: 14px; 
            margin-bottom: 8px;
            text-align: center;
        ">
            {label}
        </div>
        <div style="
            display: inline-block;
            padding: 4px 12px;
            background-color: {bg_color};
            color: {text_color};
            border-radius: 15px;
            font-weight: bold;
            font-size: 14px;
            text-align: center;
            white-space: nowrap;
        ">
            {text}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

def make_grid(cols, rows):
    logging.debug(log_pref(locations={"function":"make_grid"}, message=f"Creating grid args: {cols=} {rows=}"))
    grid = [st.columns(cols) for _ in range(rows)]
    return grid

def make_gauge_graph(in_title, in_value):
    logging.debug(log_pref(locations={"function": "make_gauge_graph"}, message=f"gauge : {in_title=}"))
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=in_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': in_title},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "red" if in_value < 50 else ("yellow" if  50 < in_value < 90 else "green" )},
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

    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=0),
        height=250,
    )
    # st.button(in_title,key=f"{in_title}_jump_btn")
    # todo: the simple title in the graph should be replaced by dynamic link to the settlment page
    st.plotly_chart(fig, width='content',key=f"{in_title}_{in_value}_{random()}")
    
@st.cache_data(ttl=2600)
def self_search_make_gauge_graph(settlement_name):

    settlement_details = {}
    for line in LocalDataEntry.data_sheet:
        if line['ישוב'] == settlement_name:
            settlement_details = line
            break

    make_gauge_graph(settlement_details["סטטוס כולל"], float(settlement_details["מדד כולל"][:-1]))


def show_settlement_map(lat, lon, settlement_name):
    m = folium.Map(location=[lat, lon], zoom_start=15)


    folium.Marker(
        [lat, lon],
        popup=settlement_name,
        tooltip=f"לחץ לפרטים על {settlement_name}",
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)

    st_folium(m, width=300, height=300)

@st.cache_data(ttl=2600)
def show_settlement_data_table(settlment_name):

    settlement_details = {}
    for line in LocalDataEntry.data_sheet:
        if line["ישוב"] == settlment_name:
            settlement_details = line
            break

    data = [
        {"חטיבה": settlement_details['חטיבה'],
        "מדד": settlement_details['מדד כולל'],
        "מועצה": settlement_details['מועצה'],
        "סיווג": settlement_details['סיווג'],
        "מרחק מהגדר": settlement_details['מרחק מהגדר'],
        "סטטוס כולל": settlement_details['סטטוס כולל'],
         "רבש\"צ":settlement_details['רבש"צ']}
    ]

    df_original = pd.DataFrame(data)
    df_t = df_original.T.reset_index()
    df_t.columns = ["פרמטר", "נתון"]
    df_t = df_t[["נתון", "פרמטר"]]
    styled_df = df_t.style.set_properties(**{
        'text-align': 'center',
        'font-family': 'sans-serif'
    }).set_table_styles([{
        'selector': 'th',  # מרכוז גם של הכותרות
        'props': [('text-align', 'center')]
    }])

    # הצגת הטבלה המעוצבת
    st.dataframe(styled_df, width='stretch')


def show_detailed_calculeted_table(settlement_name):
    raw_data = []
    set_sheet = LocalDataEntry.spreadsheet.get_worksheets_range(InternalGoogleSheetVars.mbt_spreadsheet_name,
                                                                settlement_name,
                                                                InternalGoogleSheetVars.calculated_table_ranges["הזזה"])
    titles = set_sheet[0]
    body = set_sheet[1:]
    data_frame = []
    for line in body:
        d = {}
        for i in range(len(line)):
            d[titles[i]] = line[i]
        data_frame.append(d)

   #  data_frame = [dict(zip(set_sheet[0], line)) for line in set_sheet[1:]]


    _all = 'הכל'


    all_shortcut = st.checkbox('הצג הכל')
    default_val = ['הכל'] if all_shortcut else None

    with st.form('מדדים מפורטים'):

        ssub_col1, ssub_col2 = st.columns(2)
        with ssub_col1:
            st.session_state.selections = {
                'status': st.multiselect("סטטוס", InternalGoogleSheetVars.options['status'], default=default_val),
                'action': st.multiselect("הפעלה", InternalGoogleSheetVars.options['action'], default=default_val),
                'types': st.multiselect("סיווג", InternalGoogleSheetVars.options['types'], default=default_val),
                'frame': st.multiselect("מסגרת", InternalGoogleSheetVars.options['frame'], default=default_val),
                'domain': st.multiselect("תחום", InternalGoogleSheetVars.options['domain'], default=default_val),
                'model': st.multiselect("מודל", InternalGoogleSheetVars.options['model'], default=default_val),
                'economy': st.multiselect("משק", InternalGoogleSheetVars.options['economy'], default=default_val),
                'family': st.multiselect("משפחה", InternalGoogleSheetVars.options['family'], default=default_val)
            }
        with ssub_col2:

            data_view = st.radio(
                " סוג ההצגה:",
                ["שעונים", "פנל", "פריסה"],
                index=0
            )
            st.form_submit_button('הצג')

        for line in data_frame:
            # todo: the status line can be allso list of models handle it
            if all([
            (line["סטטוס"] in st.session_state.selections['status'] or _all in st.session_state.selections['status']),
            (line["הפעלה"] in st.session_state.selections['action'] or _all in st.session_state.selections['action']),
            (line["סיווג"] in st.session_state.selections['types'] or _all in st.session_state.selections['types']),
            (line["מסגרת"] in st.session_state.selections['frame'] or _all in st.session_state.selections['frame']),
            (line["תחום"] in st.session_state.selections['domain'] or _all in st.session_state.selections['domain']),

            (line["שיוך למודל"] in st.session_state.selections['model']  or _all in st.session_state.selections['model']) if isinstance(line["שיוך למודל"], str) else True,
            (line["משק"] in st.session_state.selections['economy'] or _all in st.session_state.selections['economy']),
            (line["משפחה"] in st.session_state.selections['family'] or _all in st.session_state.selections['family'])
        ]):

                if 'רבש"צ' not in line['קריטריון']:
                    raw_data.append((line['קריטריון'],int(statuses_values_dict[line['סטטוס']])*100 if line.get('סטטוס') else float(line['מדד'][:-1])))

        with st.container():
            if len(raw_data) > 0:
                if data_view == "פריסה":
                    int_data_frame = {itm[0]:itm[1] for itm in raw_data}
                    show_spider_chart(int_data_frame,'פיזור מדדים')
                else:
                    if data_view == "פנל":
                        st.markdown("<div style='height: 60px;'></div>", unsafe_allow_html=True)
                    cols = st.columns(4)

                    for i, pair in enumerate(raw_data):
                        current_col = cols[i % 4]
                        with current_col:
                            if data_view == "שעונים":

                                make_gauge_graph(pair[0], pair[1])

                            elif data_view == "פנל":
                                if 0 <= pair[1] < 50:
                                    color = "error"
                                elif 50 <= pair[1] < 90:
                                    color = "part"
                                elif pair[1] >= 90:
                                    color = "success"
                                with st.container():
                                    status_badge(pair[0], color)
                                    st.markdown("<div style='height: 45px;'></div>", unsafe_allow_html=True)




@st.cache_data(ttl=3600)
def show_detailed_badged_table(settlement_name):
    raw_data = {}
    spreadsheet = GoogleSheetsAuth()
    for title, table_range in InternalGoogleSheetVars.detailed_badged_table_ranges.items():
        # process the data and cut irelevant
        raw_data[title] = spreadsheet.get_worksheets_range(InternalGoogleSheetVars.main_data_worksheet_name,settlement_name,table_range)[1][0]

    # grid according to data dimentions
    map_grid = make_grid(5,len(raw_data))

    # insert in each grid cell the title and under that the badge of it
    color_dict = {"תקין": "success",
                  "לא תקין\\חסר": "error",
                  "חלקי":"part",
                  "בהקמה":"irelevant" }

    row = 0
    col = 0
    for item, status in raw_data.items():

        with map_grid[row][col]:
            status_card(item, status, color_dict.get(status))

        if col == 4:
            col = 0
            row += 1
        else:
            col += 1

def show_simple_bar_chart(data_frame: Dict,index: str):
    df = pd.DataFrame(data_frame)

    st.bar_chart(df.set_index(index))


def show_spider_chart(data_frame: Dict,index: str):
    categories = list(data_frame.keys())
    values = list(data_frame.values())

    if len(categories):
        categories_closed = categories + [categories[0]]
    if len(values):
        values_closed = values + [values[0]]
    if len(categories) + len(values) >= 2:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            name=index,
            line_color='teal'
        ))

        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            title="ניתוח מדדים - מבט רב ממדי"
        )

        st.plotly_chart(fig, width='stretch')
    else:
        st.write(InternalGoogleSheetVars.messages["no_data"])



def show_heat_map(matrix_data_frame: list, index: str):

    dim = len(matrix_data_frame)
    df = pd.DataFrame(matrix_data_frame, columns=[f"עמודה {i}" for i in range(dim)])

    fig = px.imshow(df,
                    text_auto=True,
                    aspect="auto",
                    color_continuous_scale='Viridis',
                    title=index)
    st.plotly_chart(fig, width='stretch')


import pandas as pd
import plotly.express as px
import streamlit as st


def show_status_heat_map(matrix_data: list, row_names: list, col_names: list, title: str):

    # 1. מיפוי המספרים למילים לצורך התצוגה
    status_map = {0: "לא תקין", 1: "חלקי", 2: "תקין"}

    text_matrix = [[status_map.get(val, "") for val in row] for row in matrix_data]

    df = pd.DataFrame(matrix_data, columns=col_names, index=row_names)

    custom_colors = [
        [0.0, "rgb(215, 48, 39)"],  # אדום עמוק
        [0.5, "rgb(255, 255, 191)"],  # צהוב בהיר
        [1.0, "rgb(26, 152, 80)"]  # ירוק עמוק
    ]

    # 4. יצירת הגרף
    fig = px.imshow(
        df,
        labels=dict(x="מדד", y="מיקום", color="סטטוס"),
        x=col_names,
        y=row_names,
        color_continuous_scale=custom_colors,
        title=title,
        aspect="auto"
    )

    # הלבשת הטקסט על המשבצות במקום המספרים
    fig.update_traces(
        text=text_matrix,
        texttemplate="%{text}",
        hovertemplate="<b>%{y} - %{x}</b><br>סטטוס: %{text}<extra></extra>"
    )

    # הגדרות עיצוב נוספות
    fig.update_layout(
        coloraxis_showscale=False,  # מחביא את סרגל הצבעים (כי המילים כבר מסבירות)
        font=dict(size=14)
    )

    st.plotly_chart(fig, width='stretch')


# --- דוגמה לשימוש ---

# 0=אדום, 1=צהוב, 2=ירוק
# data = [
#     [2, 0, 1],
#     [0, 1, 1],
#     [2, 2, 0]
# ]
#
# rows = ["גליל עליון", "מטה אשר", "מעלה יוסף"]
# cols = ["מוכנות", "לוגיסטיקה", "כוח אדם"]
#
# show_status_heat_map(data, rows, cols, "סטטוס מדדים רוחבי")
def place_vertical_spacer(dim: int):

    for i in range(dim):
        st.write("")


def show_table():
    pass


def show_table_with_battery_(data_frame: list, titles: list, battery_column: str = None, battery_title: str = "מדד"):
    df = pd.DataFrame(data_frame, columns=titles)

    source_col = battery_column if battery_column in df.columns else titles[-1]

    def _to_number(v):
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            return float(v)
        if isinstance(v, str):
            s = v.strip().rstrip('%').replace(',', '').strip()
            try:
                return float(s)
            except ValueError:
                return 0.0
        return 0.0

    df[battery_title] = df[source_col].apply(_to_number)

    st.dataframe(
        df,
        column_config={
            battery_title: st.column_config.ProgressColumn(
                battery_title,
                min_value=0,
                max_value=100,
                format="%.0f%%",
            )
        },
        use_container_width=True,
        hide_index=True,
    )
# Helper function to parse percentages safely
def parse_percentage_string(val):
    if pd.isna(val) or not str(val).strip():
        return 0.0
    val_str = str(val).replace('%', '').strip()
    try:
        num = float(val_str)
        if '%' in str(val):
            return num / 100.0
        return num
    except ValueError:
        return 0.0

def show_table_with_battery(data_rows, headers, target_col_name='מדד משוקלל', display_col_name='מדד משוקלל'):
    """
    Renders a clean Streamlit dataframe using native ProgressColumn
    for visual metric representation.
    """
    # 1. יצירת הדאטה פריים וניקוי רווחים מהכותרות
    cleaned_headers = [str(h).strip() for h in headers]
    df = pd.DataFrame(data_rows, columns=cleaned_headers)

    target_col = str(target_col_name).strip()


    if 'קריטריון' in df.columns:
        df = df[df['קריטריון'].str.strip() != '']
        df = df[df['קריטריון'].str.strip() != 'משוקלל']

    df = df.drop(columns=[''], errors='ignore')

    # 3. המרת העמודה למספר עשרוני (Float בין 0.0 ל-1.0)
    if target_col in df.columns:
        df[target_col] = df[target_col].apply(parse_percentage_string)
    else:
        st.dataframe(df, hide_index=True)
        return

    # 4. הגדרת עמודת הפרוגרס-בר הרשמית של Streamlit
    # המנגנון המובנה הזה מציג פס התקדמות יפה מ-0% עד 100% ישירות בתא
    column_configuration = {
        target_col: st.column_config.ProgressColumn(
            label=target_col,
            help="מדד משוקלל לקריטריון",
            format="%.0f%%",  # מציג את המספר כאחוז (למשל 0.77 יוצג כ-77%)
            min_value=0.0,
            max_value=1.0,
        )
    }

    # 5. הצגת הטבלה היחידה ב-Streamlit
    st.dataframe(
        df,
        column_config=column_configuration,
        hide_index=True
    )
def present_model_components_table(settlement_name: str, keys: List, ranges=None, add_data=None):
    local_dict = {'רפואה - אמבולנס':"אמבולנס ממוגן",
                  'רפואה - ציוד':"מדד ציוד רפואי",}
    first_seperator = ["אמבולנס"]
    second_seperator = []

    if ranges is None:
        ranges = []
    for index, k_range in enumerate(keys):
        model_table = []
        try:
            if k_range in local_dict.keys():
                model_table = LocalDataEntry.spreadsheet.get_worksheets_range(
                    InternalGoogleSheetVars.mbt_spreadsheet_name, settlement_name,
                    ranges[index] if ranges else InternalGoogleSheetVars.settlements_models_ranges[local_dict[k_range]])
            elif k_range == 'מחלקות הגנה - כשירות':

                with st.container():
                    st.write(f"{add_data}  כשירות מחלקת הגנה: ")

            else:

                model_table = LocalDataEntry.spreadsheet.get_worksheets_range(InternalGoogleSheetVars.mbt_spreadsheet_name, settlement_name, ranges[index] if ranges else InternalGoogleSheetVars.settlements_models_ranges[k_range]
            )

        except Exception as e:
            log(f"\nError revoked from key: {k_range} reading table from file - failed!\n")
            st.error(f" {k_range}: {e}")
            log(f"Error says {e}")

        #log(f"checking models table is not null =  {len(model_table)}")
        if model_table:
            log(f" **** **** model_table with len {len(model_table)} accepted with key {k_range}....")
            log(f" **** **** k condition { any([True if "אמבולנס" in k else False for k in k_range])} accepted with key {k_range}")
            if any([True if "אמבולנס" in k else False for k in k_range]) :

                data = model_table[1:]
                log(f"\n >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> \n")
                log(f"data: {data}")
                st.write(data)
                headers = model_table[0]
                df = pd.DataFrame(data, columns=headers)
                st.subheader(k_range)
                st.dataframe(df, hide_index=True)
            else:
                show_table_with_battery(model_table[1:], model_table[0], 'מדד משוקלל', 'מדד משוקלל')




