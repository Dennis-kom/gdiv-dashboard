import os
from pathlib import Path
import streamlit as st
# postgresql://postgres:D@shB07DAGMAR@db.igjtxjyiqvyyadutgmen.supabase.co:5432/postgres
from supabase import create_client, Client
import psycopg2
from attr import dataclass
from pip._internal import locations
from psycopg2 import OperationalError
import logging
from utils.logger import color_logger, log_pref
import toml
from pathlib import Path

log = color_logger()
_locations = {"file_name" : Path(__file__).name}
class Credentials:
    host: str = "db.igjtxjyiqvyyadutgmen.supabase.co"
    user: str = "postgres"
    database: str = "postgres"
    password: str = "D@shB07DAGMAR"
    port: int = 5432

class PostgresDatabase:

    def __init__(self):
        self._locations = _locations
        self._locations["class"] = "PostgresDatabase"
        #todo: should be hidden into the secrets file - now for testing only
        self.database_url = "postgresql://postgres:D@shB07DAGMAR@db.igjtxjyiqvyyadutgmen.supabase.co:5432/postgres"
        self.SUPABASE_URL = "https://igjtxjyiqvyyadutgmen.supabase.co"
        self.SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImlnanR4anlpcXZ5eWFkdXRnbWVuIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc4MTY4NTYxMSwiZXhwIjoyMDk3MjYxNjExfQ.VEBx0g92eoz59S74yXUZZJ67dX5UQJW1Zb0uWq3WNvQ"
        self.connection: Client = None
        self.connection_status: bool = False



    def connect(self):
        """Connect to the PostgreSQL database using the connection string."""
        self._locations["method"] = "connect"
        self._locations["stage"] = "database connection attempt"
        db_info = st.secrets["postgres"]

        try:
            # todo: after hiding the keys in secret file the connection should be established using the following line - now for testing only
            # self.connection: Client = create_client(db_info["SUPABASE_URL"], db_info["SUPABASE_KEY"])
            self.connection: Client = create_client(self.SUPABASE_URL, self.SUPABASE_KEY)

            log.debug(log_pref(locations=self._locations,
                                  message=f"Attempt connect to PostgreSQL database -> connection successful = {True if self.connection else False}"))
            self.connection_status = True
            return True
        except OperationalError as e:
            log.critical(log_pref(locations=self._locations, 
                                  message=f"Failed to connect to PostgreSQL database: {e}"))

            return False
        except Exception as e:
            log.critical(log_pref(locations=self._locations, 
                                  message=f"Unexpected error during database connection: {e}"))


            root_secrets = Path(__file__).parents[2] / ".streamlit" / "secrets.toml"
            if root_secrets.exists():
                config = toml.load(root_secrets)
                db_info = config["postgres"]
            else:
                raise FileNotFoundError("לא נמצא קובץ secrets.toml לא בסביבת Streamlit ולא בדיסק!")


    def get_connection_status(self):
        """Return the current database connection status."""
        return self.connection_status

    def disconnect(self):
        """Safely disconnect from the PostgreSQL database while handling pending transactions."""
        # todo: make the connetion - failsafe to transactions - safe close without losing data
        self._locations["method"] = "disconnect"
        
        if self.connection_status:
            log.debug(log_pref(locations=self._locations, 
                             message="Connection is already None, no need to disconnect"))
            self.connection = None
            self.connection_status = False

    def get_all_from_table(self,table_name: str):
        response = self.connection.table(table_name).select("*").execute()
        return response

    def insert_into_table(self,table_name: str, data: dict):
        pass

    def create_table(self,table_name: str, data: dict):
        pass

    def query_table(self,table_name: str, query: dict ,columns: str = "*"):
        # {"column": " ","operator": " ","value": " "}
        response = self.connection.table(table_name).select(columns).filter(**query).execute()
        return response

# c_string = "postgresql://postgres:D@shB07DAGMAR@db.igjtxjyiqvyyadutgmen.supabase.co:5432/postgres"
# d = PostgresDatabase()
# d.connect()
