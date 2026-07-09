from data.internal.run_time_instances import get_database_instance
import streamlit as st


class Fighter:
    def __init__(self, fighter_name, settlement_name):
        self.name: str = fighter_name
        self.settlement_name: str = settlement_name
        self.qualification_status: str = None




class Ravshatz(Fighter):
    def __init__(self, fighter_name, settlement_name):
        super().__init__(fighter_name, settlement_name)
        self.db_instance = get_database_instance()


    def get_ravshatz_qualification_status(self):
        # SELECT qualification FROM ravshatz WHERE name == settlement_name
        table = "ravshatz"
        query = {"column": "name","operator": "eq","criteria": f"{self.settlement_name}"}
        columns = "qualifications"
        response = None
        try:
            response = self.db_instance.query_table(table,query, columns)
        except Exception as e:
            st.error(f"SUPERBASE: keError fetching qualification status: {e}")
            self.qualification_status = response
        if response is not None:
            print(f"data base : {response.dict()=}")
            return response.dict()
        return None

