from asyncio import sleep
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st
# from streamlit.runtime.context import get_script_run_ctx
from streamlit.runtime.scriptrunner.script_runner import add_script_run_ctx, get_script_run_ctx
from data.entities.defence_class_fighter import Ravshatz
from data.external.defence_class_data_frame import DefenceClass
from visual_components.page_layout import page_layout_rtl
from data.internal.run_time_instances import get_database_instance, get_google_sheets_instance
from data.static import InternalGoogleSheetVars
from utils.logger import tracer, tracer_status

page_layout_rtl()

# import logging

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
ctx = get_script_run_ctx()

def worker_with_context(func, *args, **kwargs):
    if ctx:
        add_script_run_ctx(ctx)

    return func(*args, **kwargs)

@st.cache_data
def data_sheet():
    data = get_google_sheets_instance().get_worksheet(InternalGoogleSheetVars.mbt_spreadsheet_name,
                                                        InternalGoogleSheetVars.main_data_worksheet_name)
    return data

@st.cache_data
def dc():
 return DefenceClass()

def database_connection():
    with st.spinner("מתחבר למסד נתונים"):
        db = get_database_instance()
        if db.get_connection_status():
            st.success("התחברות למסד הנתונים בוצעה בהצלחה!")
            return True
        else:
            st.error("התחברות למסד נתונים נכשלה")
            return False



def setup_ravshtz_run_time_data_elements(key):
        ret = {}
        for line in data_sheet():
            if line["ישוב"].strip() == key:
                ravshatz_name = line['רבש"צ'].strip()
                Ravshatz(ravshatz_name, key)
                ret[key] = {}
                ret[key]["name"] = ravshatz_name
                break
        return ret

def setup_defence_class_fighters(key):
    res = {}
    data = dc().get_defence_class_fighters_data_frame(key)

    res[key] = {"names": [], "qualifications": []}
    res[key]["names"] = [tup[0] for tup in data if tup[0] != "nan"]
    res[key]["qualifications"] = [tup[1] for tup in data if tup[0] != "nan"]

    return res


def check_password()-> bool:
    tracer("app.py - check_password")
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title(" מערכת ניהול - כניסה מאובטחת")
    st.write("אנא הזן סיסמה כדי לגשת לדשבורד:")

    with st.form("login_form"):

        password = st.text_input("סיסמה:", type="password")
        submit_button = st.form_submit_button("התחבר")

        if submit_button:

            correct_password = st.secrets.get("auth_password", "admin123")

            if password == correct_password:
                st.session_state["password_correct"] = True

                st.rerun()
            else:
                st.error("❌ הסיסמה שגויה. אנא נסה שנית.")
                st.session_state["password_correct"] = False

    return False


if check_password():
    st.success("ברוך הבא למערכת!")
    if "ravshats_table" not in st.session_state:
        st.session_state["ravshats_table"] = {}
    if "settlements_stack" not in st.session_state:
        st.session_state["settlements_stack"] = []
    if "active_screen_index" not in st.session_state:
        st.session_state["active_screen_index"] = "general"
    if "settlement_details_frame" not in st.session_state:
        st.session_state["settlement_details_frame"] = "s_tab1"
    if "session_run_time_data" not in st.session_state:
        st.session_state["session_run_time_data"] = {}
    for key in InternalGoogleSheetVars.settlements_data.keys():
        st.session_state["session_run_time_data"][key] = {}
        st.session_state["session_run_time_data"][key]["main_score"] = 0
        st.session_state["session_run_time_data"][key]["ravhatz"] = {"name": "", "qualification": ""}
        st.session_state["session_run_time_data"][key]["defence_class"] = {"names": [], "qualifications": []}

    stage_1_func = []
    stage_1_res = []

    stage_2_func = []
    stage_2_res = []

    stage_3_func = []
    stage_3_res = []

    switch_flag = True

    with ThreadPoolExecutor(max_workers=10) as executor:

        stage_2_func = [executor.submit(worker_with_context, setup_ravshtz_run_time_data_elements,key) for key in InternalGoogleSheetVars.settlements_data.keys()]

        stage_3_func = [executor.submit(worker_with_context,setup_defence_class_fighters,key) for key in InternalGoogleSheetVars.settlements_data.keys()]


        for task in as_completed(stage_2_func):

            try:
                if task:
                    stage_2_res.append(task.result())
            except Exception as e:
                print(f"Exception in appending stage_2_res.append(task.result()) : {e}")


        for task in as_completed(stage_3_func):

            try:
                # {settelment_name: {names: [], qulifications: []}
                stage_3_res.append(task.result())
            except Exception as e:
                print(f"Exception in appending stage_3_res.append(task.result()) : {e}")


    with st.spinner("טוען מבנה זיכרון פנימי"):
        for key in InternalGoogleSheetVars.settlements_data.keys():
            for set_name in stage_2_res:
                if set_name:
                    if list(set_name.keys())[0] == key:
                        st.session_state["session_run_time_data"][key]["ravhatz"]["name"] = set_name[key]["name"]
        st.success("מבנה זיכרון פנימי בוצע!")

    with st.spinner("מבצע חישובי ביניים"):
        for key in InternalGoogleSheetVars.settlements_data.keys():
            for set_name in stage_3_res:
                if set_name:
                    if list(set_name.keys())[0] == key:
                        st.session_state["session_run_time_data"][key]["defence_class"] = set_name[key]
        st.success("ניתובים חישוביים עודכנו בהצלחה!")

    with st.spinner("מתחבר למסד נתונים מרוחק"):
        for key in InternalGoogleSheetVars.settlements_data.keys():
            ravshatz = Ravshatz(st.session_state["session_run_time_data"][key]["ravhatz"]["name"], key)
            qualification = ravshatz.get_ravshatz_qualification_status()['data'][0]['qualifications']
            st.session_state["session_run_time_data"][key]["ravhatz"]["qualification"] = qualification
        st.success("התחברות למסד הנתונים בוצעה בהצלחה!")

        # print("___________________________  Testing ___________________________________")
        # for att in (("ravhatz","name"), ("ravhatz","qualification"),("defence_class", "names"),("defence_class","qualifications") ):
        #     for key in InternalGoogleSheetVars.settlements_data.keys():
        #         print(f"{st.session_state['session_run_time_data'][key][att[0]][att[1]]}=")

        if switch_flag:
            st.switch_page("pages/01_כולל.py")
        else:
            st.write("שגיאה בטעינת נתונים או בעיית התחברות")

            #                  All Project Tasks List:
            # ============================================================

            # fixme: run time session state pushing empty stack
            # fixme: in detailes settlement view the main gauges still remaining
            # fixme: hide the secrets and tokens
            # todo: add the tech project module
            # todo: make the run time date updates all over its relevant
            # todo: code cleaning
            # todo: make all the loading and manifast cucurent
            # todo: make all the application work with multi treads
            # fixme: the first loading still takes to much time

