import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils.components import status_badge, show_simple_bar_chart
from utils.data_source import sheet
from variables.static import InternalGoogleSheetVars
import logging


logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
# right alignment to all the text in the page
st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    /* יישור כל האפליקציה לימין */
    .main .block-container {
        direction: rtl;
        text-align: right;
    }

    /* */
    h1, h2, h3, p, span, label {
        text-align: right !important;
        direction: rtl !important;
    }

    /*  */
    [data-testid="stSidebar"] {
        direction: rtl;
        text-align: right;
    }
    </style>
    """,
    unsafe_allow_html=True
)

_all= 'הכל'
st.title(InternalGoogleSheetVars.mbt_spreadsheet_name)

with st.form(key="general_view"):
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'main'

    col1, col2 , col3, col4 = st.columns(4)
    st.session_state.current_page = "main"
    st.session_state.bar_chart_data_frame = {"ישוב":[],"מדד כולל":[]}

    st.session_state.divisions = ['הכל','צפונית','דרומית']
    st.session_state.councils = ['הכל','שדרות','שער הנגב','שדות נגב','אשכול','חוף אשקלון']
    st.session_state.types = ['הכל','סמוך','ליבה','ליבה קדמי']
    st.session_state.distances = ['הכל','7+','4-7','0-4']

    st.session_state.amount = 0
    st.session_state.middle = 0
    st.session_state.filters = {"division":st.session_state.divisions,
                                "council":st.session_state.councils,
                                "type":st.session_state.types,
                                "distance":st.session_state.distances}


    with col1:
        st.session_state.filters['division'] = st.multiselect("חטיבה", st.session_state.divisions)
        st.session_state.filters['council'] = st.multiselect("מועצה", st.session_state.councils)
        st.session_state.filters['type'] = st.multiselect("סיווג", st.session_state.types)
        st.session_state.filters['distance'] = st.multiselect("מרחק מהגדר", st.session_state.distances)

    with col2:
        st.subheader("מדד כולל")

        values = []
        for line in sheet:
            tab_line = line
            if ((tab_line['חטיבה'] in st.session_state.filters['division'] or _all in st.session_state.filters['division']) and
                    (tab_line['מועצה']  in st.session_state.filters['council'] or _all in st.session_state.filters['council']) and
                    (tab_line['סיווג'] in st.session_state.filters['type'] or _all in st.session_state.filters['type']) and
                    (tab_line['מרחק מהגדר'] in st.session_state.filters['distance'] or _all in st.session_state.filters['distance'])):


                if '#' in tab_line['מדד כולל']:
                    values.append(0)
                    st.session_state.bar_chart_data_frame['מדד כולל'].append(0)
                    st.session_state.bar_chart_data_frame['ישוב'].append(tab_line['ישוב'])
                else:
                    values.append(float(line['מדד כולל'][:-1]))
                    st.session_state.bar_chart_data_frame['ישוב'].append(tab_line['ישוב'])
                    st.session_state.bar_chart_data_frame['מדד כולל'].append(float(line['מדד כולל'][:-1]))

        st.session_state.all_avg = np.mean(values)
        st.session_state.amount = len(values)
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=st.session_state.all_avg,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "מדד בטחון כולל"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "red" if st.session_state.all_avg < 50 else ("yellow" if  50 < st.session_state.all_avg < 90 else "green" )},
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
        st.plotly_chart(fig, width='content')
        text = "לא תקין" if st.session_state.all_avg < 50 else ("חלקי" if 50 < st.session_state.all_avg < 90 else "תקין")
        color = "error" if st.session_state.all_avg < 50 else ("part" if 50 < st.session_state.all_avg < 90 else "success")
        status_badge(text, color)

    with col3:
        st.subheader('כמותי')
        st.metric(label="כמות ישובים", value=st.session_state.amount)
        st.metric(label="חציון חלקי", value=st.session_state.amount)
        st.metric(label="חציון תקין", value=st.session_state.amount)

    with col4:
        st.subheader('התפלגות')
        st.session_state.data_pi = {"סטטוס כולל": ["תקין", "חלקי", "לא תקין\\חלקי"], "כמות": [0, 0, 0]}
        for line in sheet:
            if ((line['חטיבה'] in st.session_state.filters['division'] or _all in st.session_state.filters[
                'division']) and (line['מועצה'] in st.session_state.filters['council'] or _all in st.session_state.filters[
                'council']) and (
                    line['סיווג'] in st.session_state.filters['type'] or _all in st.session_state.filters['type']) and (
                    line['מרחק מהגדר'] in st.session_state.filters['distance'] or _all in st.session_state.filters[
                'distance'])):
                st.session_state.data_pi["כמות"][st.session_state.data_pi["סטטוס כולל"].index(line["סטטוס כולל"])] += 1

        fig = px.pie(
            st.session_state.data_pi,
            values='כמות',
            names='סטטוס כולל',
            title='',
            color='סטטוס כולל',
            color_discrete_map={'תקין': '#C6EFCE', 'חלקי': '#FFEB9C', 'לא תקין\\חלקי': '#FFC7CE'})

        fig.update_traces(textinfo='percent+label', hole=0.1)
        st.plotly_chart(fig, width='stretch')
    show_simple_bar_chart(st.session_state.bar_chart_data_frame, "ישוב")
    st.form_submit_button("טען")

# ####################################### Sidebar - pages select ##############################################


settelments_nameing = {"beeri":"בארי",
               "gvaram":"גברעם",
               "zikim":"זיקים",
               "yad mordechai":"יד מרדכי",
               "carmia":"כרמיה",
               "mavkim":"מבקיעים",
               "nativ ha asara":"נתיב העשרה",
               "beit ha gedi":"בית הגדי",
               "givolim":"גבעולים",
               "zimrat":"זמרת",
               "zroaa":"זרועה",
               "yoshivia":"יושיביה",
               "kfar maimon":"כפר מימון",
               "meloilot":"מלילות",
               "magalim":"מעגלים",
               "saad":"סעד",
               "alimim":"עלומים",
               "shuva":"שובה",
               "shokeda":"שוקדה",
               "":"שיבולים",
               "":"שרשרת",
               "":"תושיה",
               "":"תקומה",
               "":"שדרות",
               "":"אור הנר",
               "":"איבים",
               "":"ארז",
               "":"ברור חיל",
               "":"גבים",
               "":"דורות",
               "":"יכיני",
               "":"כפר עזה",
               "":"מפלסים",
               "":"נחל עוז",
               "":"ניר עם",
               "":"רוחמה",
               "":"אבשלום",
               "":"אוהד",
               "":"אורים",
               "":"בני נצרים",
               "":"גבולות",
               "":"דקל",
               "":"חולית",
               "":"יבול",
               "":"ישע",
               "":"יתד",
               "":"כסופים",
               "":"כרם שלום",
               "":"מבטחים",
               "":"מגן",
               "":"נווה",
               "":"ניר יצחק",
               "":"ניר עוז",
               "":"נירים",
               "":"סופה",
               "":"עין הבשור",
               "":"עין השלושה",
               "":"עמי עוז",
               "":"פרי גן",
               "":"צאלים",
               "":"צוחר",
               "":"רעים",
               "":"שדה ניצן",
               "":"שדי אברהם",
               "":"שלומית",
               "":"תלמי אליהו",
               "":"תלמי יוסף"}

#selected_page = st.sidebar.selectbox("", options=settelments_pages.keys())

