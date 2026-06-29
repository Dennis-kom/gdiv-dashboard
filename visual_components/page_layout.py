import streamlit as st

def page_layout_rtl():
    st.markdown(
        """
        <style>
        /* 1. הפיכת המכולה הראשית והסיידבר ל-RTL */
        [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
            direction: rtl;
            text-align: right;
        }

        /* 2. סידור כיוון הטקסט בתוך תיבות הבחירה והאינפוטים */
        .stSelectbox, .stMultiSelect, .stTextInput, .stTextArea, .stRadio, .stCheckbox {
            direction: rtl;
            text-align: right;
        }

        /* 3. יישור כותרות הטאבים (אם יש) */
        button[data-baseweb="tab"] {
            direction: rtl;
        }

        /* 4. תיקון מיקום החצים הקטנים בפינות של התיבות שלא ידרסו את הטקסט העברי */
        [data-testid="stSelectbox"] svg, [data-testid="stMultiSelect"] svg {
            right: auto;
            left: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )