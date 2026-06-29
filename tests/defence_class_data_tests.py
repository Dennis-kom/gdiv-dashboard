from data.external.defence_class_data_frame import DefenceClass
import pandas as pd


def test_connection():
    dc = DefenceClass()
    settlement_name = "אבשלום"  # Replace with a valid settlement name
    df = dc.get_defence_class_fighters_data_frame(settlement_name)
    print(df.head())
    assert isinstance(df, pd.DataFrame), "Expected a DataFrame"
    assert not df.empty, "DataFrame should not be empty"