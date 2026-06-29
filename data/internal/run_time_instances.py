from data.database.superbase import PostgresDatabase
import streamlit as st
from data.external.gdrive_auth import GoogleDriveAuth
from data.external.gsheets_auth import GoogleSheetsAuth


@st.cache_resource
def get_database_instance():
    db = PostgresDatabase()
    db.connect()
    return db

@st.cache_resource
def get_google_sheets_instance():
    gsheets = GoogleSheetsAuth()
    return gsheets

@st.cache_resource
def get_google_drive_instance():
    gdrive = GoogleDriveAuth()
    return gdrive