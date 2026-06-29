from asyncio import sleep

import streamlit as st
from visual_components.page_layout import page_layout_rtl
from data.internal.run_time_instances import get_database_instance

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




def check_password()-> bool:

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
    with st.spinner("מתחבר למסד נתונים"):
        db = get_database_instance()
        if db.get_connection_status():
            st.success("התחברות למסד הנתונים בוצעה בהצלחה!")
            st.switch_page("pages/01_כולל.py")
        else:
            st.error("התחברות למסד נתונים נכשלה")
    #with st.spinner("מבצע התחברות לטבלאות"):
    #     pass
    with st.spinner("מבצע עדכון טבלאות"):
        if "ravshats_table" not in st.session_state:
            st.session_state["ravshats_table"] = {}
        # todo: make a list of a local data table for session maneging
        # todo: add hear more seesion tables for track data
        sleep(1)
    # with st.spinner("בונה יחידת נתונים מקומית"):
    #     sleep(2)

    # st.switch_page("pages/01_כולל.py")


