from variables.static import InternalGoogleSheetVars
from utils.gsheets_auth import GoogleSheetsAuth

class SessionData:
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SessionData, cls).__new__(cls)
        return cls._instance


    def __new__(self, worksheet_name, spreadsheet_name):
        self.spreadsheet = GoogleSheetsAuth()
        self.sheet = self.spreadsheet.get_worksheet(worksheet_name, spreadsheet_name)