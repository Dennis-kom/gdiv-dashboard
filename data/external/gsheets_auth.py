import gspread
from google.oauth2.service_account import Credentials
from concurrent.futures import ThreadPoolExecutor, as_completed
import streamlit as st

@st.cache_resource
class GoogleSheetsAuth:

    def __init__(self, credentials_json:str = None):
        # todo: the credentials must be moved to secrets before pushing to production
        self.dev_credentials = r"C:\Users\denni\Downloads\cellular-way-492513-p8-2d96ef76e975.json"
        self.credentials_json = self.dev_credentials if not credentials_json else credentials_json
        self.credentials = None
        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"]

        self.creds = Credentials.from_service_account_file(self.credentials_json, scopes=self.scopes)
        self.client = gspread.authorize(self.creds)


    def get_spreadsheet(self, spreadsheet_name: str):

        return self.client.open(spreadsheet_name)


    def get_worksheet(self, spreadsheet_name: str, worksheet_name: str):
        data = self.get_spreadsheet(spreadsheet_name).worksheet(worksheet_name).get_all_records()
        return data


    def get_worksheets_range(self, spreadsheet_name: str, worksheet_name: str, ranges:str):
        # d(spreadsheet_name, worksheet_name)
        return self.get_spreadsheet(spreadsheet_name).worksheet(worksheet_name).get(ranges)



