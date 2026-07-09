from data.external.gsheets_auth import GoogleSheetsAuth
import streamlit as st


def get_session_parameter(keys: list):
    if "session_run_time_data" not in st.session_state:
        return None
    else:
        data = st.session_state["session_run_time_data"]
        for key in keys:
            data = data[key]

        return data



def set_session_parameter(keys: list, value):
    if "session_run_time_data" not in st.session_state:
        st.session_state["session_run_time_data"] = {}

    data = st.session_state["session_run_time_data"]
    for key in keys[:-1]:
        if key not in data:
            data[key] = {}
        data = data[key]

    data[keys[-1]] = value



