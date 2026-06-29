from pathlib import Path

from data.external.gdrive_auth import GoogleDriveAuth, normalize_none_value
from utils.logger import color_logger, log_pref

log = color_logger()
_locations = {"file_name" : Path(__file__).name}

class DefenceClass:
    """
    Defence Class data handler that uses GoogleDriveAuth for file operations.
    Uses composition instead of inheritance to avoid issues with @st.cache_resource decorator.
    """
    def __init__(self):
        self.google_drive = GoogleDriveAuth()
        self._locations = _locations.copy()
        self._locations["class"] = "DefenceClass"

    def get_defence_class_fighters_status_list(self, settlement_name: str):
        self._locations["method"] = "get_defence_class_fighters_list"
        df = self.google_drive.get_last_file_content_as_data_frame(settlement_name)

        if df is not None:
            # Extract the values from the DataFrame
            extracted_values = []
            for row in range(df.shape[0]):
                for col in range(df.shape[1]):
                    value = normalize_none_value(df.at[row, col])
                    if value is not None:
                        extracted_values.append(value)

            return extracted_values
        else:
            log.warning(log_pref(locations=self._locations, message=f"DataFrame is None for settlement: {settlement_name}"))
            return []

    def get_defence_class_fighters_data_frame(self, settlement_name: str):
        self._locations["method"] = "grab_defence_class_fighters_data_frame"

        df = self.google_drive.get_last_file_content_as_data_frame(settlement_name)

        extracted_value = None
        if df is not None:
            self._locations["stage"] = "data frame scan"
            row_idx = None
            col_idx = None

            row_10 = any([normalize_none_value(df.at[9, c]) for c in range(df.columns.size - 1)])

            row_11 = any([normalize_none_value(df.at[10, c]) for c in range(df.columns.size - 1)])

            start_row = 10 if row_10 else 11 if row_11 else 0
            run_flag = True
            names_col_found = False
            vals_col_found = False
            grads_col_found = False
            row_offset = 7
            names_col_idx = 0
            names_row_idx = 0

            val_col_idx = 0
            val_row_idx = 0

            grade_col_idx = 0
            grade_row_idx = 0

            names_list = []
            grades_list = []
            vals_list = []

            for r_idx in range(start_row, df.shape[0]):
                if not names_col_found or not vals_col_found:

                    for c_idx in range(df.columns.size - 1):
                        try:
                            cell_value = str(df.at[r_idx, c_idx]).strip()
                        except (KeyError, IndexError):
                            # Skip if cell doesn't exist
                            continue

                        if not names_col_found:
                            if cell_value == "שם היורה":
                                names_col_idx = c_idx
                                names_row_idx = r_idx + 1
                                print(f"{cell_value=} {names_col_idx=} {names_row_idx=}")
                                names_col_found = True
                        if not vals_col_found:
                            if cell_value == "עבר/ לא עבר" or cell_value == "בכשירות/לא בכשירות":
                                val_row_idx = r_idx + 1
                                val_col_idx = c_idx
                                print(f"{cell_value=} {val_row_idx=} {val_col_idx=}")
                                vals_col_found = True



            data_consistency = True
            row_idx = names_row_idx
            col_idx = names_col_idx

            while data_consistency:
                try:
                    name_value = str(df.at[row_idx, col_idx]).strip()

                    val_value = str(df.at[row_idx, val_col_idx]).strip()

                except (KeyError, IndexError):
                    # Skip if cell doesn't exist
                    data_consistency = False
                    continue

                names_list.append(name_value)
                vals_list.append(val_value)
                row_idx += 1

            extracted_value = list(zip(names_list, vals_list))

        return extracted_value



# dc = DefenceClass()
# settlement_name = "כפר עזה"
# print(dc.get_defence_class_fighters_data_frame(settlement_name))

