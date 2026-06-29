import streamlit as st


from utils.secure import enforce_authentication

enforce_authentication()

with st.form("insert_tables_to_data_base"):
    data_table = st.text_input(label="שם הטבלת הנתונים")
    dependency_table = st.text_input(label="שם טבלת השדות לקישור")
    submit_button = st.form_submit_button("העלה טבלה")
    # todo need to build system data dependence tree - then all tables that will be added to the database will be taken in account
