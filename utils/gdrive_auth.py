import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import io
import pandas as pd
import openpyxl


@st.cache_resource
class GoogleDriveAuth:

    def __init__(self, credentials_json: str = None):
        self.dev_credentials = r"C:\Users\denni\Downloads\cellular-way-492513-p8-2d96ef76e975.json"
        self.credentials_json = self.dev_credentials if not credentials_json else credentials_json

        self.scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]

        self._dirs_ids = {
            'main': '1rS1Oc0yEk20bI9WOYo0sAF9vLsFExPLY',
            'מחלקתיים': '1f6xHUZkskUNCWGGXNtq6MqGbKsvwz4s-'

        }

        self.settlements_dirs_id_sets = {
            'אבשלום': ('1f3tT27-ZdhH3AZjodwfUYLfDn9w2MKa6', '12rDmWQ6Fq6pWEBOgEyU6y9bgKmmGBrAY'),
            'אוהד': ('1nDE6KGbvnr7WYEtAb2a5NrT6-hhQbnu7', '1OVSwoKR3lMqCKGgtgL7k0bAGuB8vg-Zz'),
            'אור הנר': ('1nE3xdGk6jFulv8Qu2Guji1_ulh_qJqGc', '1PR_ooLr7ifrGTI899FoHqpVEyB23Cqg_'),
            'אורים': ('1qNwi0E82B12o8bjRrvV0rqRPbJ0TuWk-', '1xdkgwH8d0NSejpIvxozwLcR1O4Z2qFoX'),
            'איבים': ('1jb3aD2vuWE3Bv-EBYhoh6vAuRsVa4k7J', '1imYwPrGxFQQyM783D-vREPPY-QWoGVSv'),
            'ארז': ('1xVSAAxfkCff1-VtFe0j_B0hrj7bQvRou', '1174_19RN39Gj72-MHV6i9yWEMZR-PsHn'),
            'בארי': ('1lLhV8R-P7sWxLUdahLhtyQxObH5bI0qj', '1Hk_Vwru0D7osxu7_JA8SyCBs5XoNi0Xx'),
            'בית הגדי': ('1yx5yz-P2bUxdz1nlPFGAW41wbAA_pagD', '1Y-vYxlGcY9ILHcWSxNILA-fYmsurnwIq'),
            'בני נצרים': ('14zML6YoOJzcUqAF7IPcgvy-a5KxnHQpZ', '1B-mAWB4RoIT2pw0jljqi25vTWyzGnhHb'),
            'ברור חיל': ('1UKm099fUnVCh6fU4vuhsvbzvRpr30tIe', '1GQS-80UTckcyKloUT-Vh3kB5zqDpokZ0'),
            'גבולות': ('1KDsVp7DBcwFjTE3-bXXh0nG8E-nwjUjs', '1rQmapaQd7jf0_1s4Uu2T6evYY22qZdAO'),
            'גבים': ('1yf1Pgf_LoQPIIedT9qHVLRUCU1YX9ceP', '1OAHZA-szaU1c9FbSm4ZUb6mJsG06EVE5'),
            'גבעולים': ('18cUlhiiESnAe2gU97907PcFQhX4tuRx8', '1Tk-xfuLuVbSA7cWBU8ojYi52v2VEQ5yl'),
            'גברעם': ('1peaiXnu_4wd5LpP3aPenBUNLzVkq0r4P', '19MQqCr1JBDsLVsyacBHRQ78Etn8In79g'),
            'דורות': ('13R3nj6jETv5nEC9-OU7ZOxOhLOfP_Z3n', '15nuk9GSDZ95VR66EdHfIA-NceUj1qEsD'),
            'דקל': ('1H365HVghyHU3JK0xlLIjIltHUHPgwPju', '1qRBxbSvc7-Aa6ZZ09pFcEK_5DTICJe5e'),
            'זיקים': ('1Lcv9W1oHE8_qVwpy_yna990KmdeOoYja', '1LJqCGVNVD661762URbelEI7_-Re3uJUk'),
            'זמרת': ('1oDZTycxrryeKoj0oBdI7mVFnZUHmDAKS', '1N0yyConuOBxhEBLDrh3w_fr6njCo7b7J'),
            'זרועה': ('1YVFIEy2lU6OxoVASBj_5uucXNun7GxEo', '1BqvWoDxp2C00DIOzBboErKHKEryE-sRQ'),
            'חולית': ('1DTg_Onmd-vy8iDfOvh7LXkBXQGFS8yvy', '1KY_c72bAwzvb1Lf5WIVqQKjQrqojc_fR'),
            'יבול': ('1WUbIc6gH9URsk_cNVxtkBca-zvt_YaV6', '1IfDvihLroXJl6CCN6cBbc3lzi9WBnUyX'),
            'יד מרדכי': ('1BsFRn5bp9Cgk_5QJ6Qd1THNR5asjhD4p', '1T3alcAqC-j39xn3qqyBr9xZiq0oNcP47'),
            'יושיביה': ('1qYkrSLdzqSjd_5jP5LGGjukktZgt7ZNy', '1vmKPksjU9TRM2QdLsylFS8ZZVUzDdFwO'),
            'יכיני': ('15eJYcXlkNMf4e3qqtj7e6jhsvenWHYvj', '1wtlXFk2rXyEjDc6PAJxTGQxKWiz89vu0'),
            'ישע': ('10bBuK9fdTkaDMMtC9Fw5iAO93zccHALg', '1gawmnZtb0xJ8g2QzEbxVggmbUoKp-QMu'),
            'יתד': ('1Oyw96TEdBaPhLSKfCx1ZL-KM-pSFUjdh', '1IhxtxD5lloCpxYrmWzAQV4g8kW19CAmT'),
            'כיסופים': ('1xNqlS9-of1pFVNt2swfN2hVADTmPe5kf', '1M1R9XJ9IuWudXp1jvaMHlcqIoosTxaCc'),
            'כפר מימון': ('1jVFTB3FPY_X7irhGd8rVkLrx4-TAyEE3', '13n1dszYbmhTZmHN2N_yulLN6uhhZIBH1'),
            'כפר עזה': ('1YejBaspnT1drBnVGWzHbJfu1Nf6meAaO', '1X4FLD6HJSWoujojrghG7X-jy6Ow4Z1jK'),
            'כרם שלום': ('1KQPSAuDssb793x_0sD-QbLGSwStiCGZt', '1sInyIkK8Ecty91G-JwOJ6AdGdSMB1F3j'),
            'כרמיה': ('1_d_HsFoj4ZRR2mLSZW4bji7XiR-30qnF', '130AXnS_-MIsON7cmrWNDwSC7p4aQtzbZ'),
            'מבטחים': ('1foOBSDjecNLAd7rWs2qDox_GzAtSChry', '1TMrcrEivugRJxxGOhYAGWvhOuvXgXiQG'),
            'מבקיעים': ('1V4G97CnqWze6KIpxkxY_Pq4l9R7lotGr', '15WGNsL5ohbjB4osJPGQwWdixhlrX90Pp'),
            'מגן': ('18H9vZr8fTd7ZQA_svGzrSDuoMo1MEywk', '1gAbtPCl9Sg1cyP7pBH4FBHl78qRPM4NJ'),
            'מלילות': ('15-hKws0hsEFMdi_IlFyupHC6MsbZfAbS', '1Jio093inIvQvS6mxyGiwA2rxXm1Xj_5c'),
            'מעגלים': ('1efoGhsLdokzT3QysdLoWSHO58_w7e13g', '1sirNkZQa5sZs9Ff37RFvQIcWvZWVNGXY'),
            'מפלסים': ('1ZQAaJnKWeYybnm9ItenQEHla2jNDDb2Z', '16v4s4AVSK2WrkbjztqdOiL0Pwsco43xQ'),
            'נווה': ('1C29HHwbbrq_xP5DFqEnCzf5h3LYzGAcO', '1AQsY2gEQpR8OMqGuR_Tocu_nwJbqOTfy'),
            'נחל עוז': ('1vYWH-jq6grA-Ln6ZdUSgG_hcYg8nTeLq', '1qoD14vP5m5a2wQsCluSFHPObBakpJcsm'),
            'ניר יצחק': ('1Y6kDkuvWM6XyT8UoGPqvurbtBWhKdKyO', '1i7mHpFgEiEfq9nWenCATAqK4vttjQRMm'),
            'ניר עוז': ('1iRtwHStL-Ykj3mCyZWa4TV9hz5A5px9g', '11qOtrkB0GLPFAO77-yKEIZ3ewP4vSnuy'),
            'ניר עם': ('1bj-k1LjwgEze8RGou8dpIL6PWv5PUfz_', '12Y5PgDOH6w5CiuNJMJib-MdZKjQUCVp7'),
            'נירים': ('1YjphQINtNuYF9fwqZW2oqvsLepGlnMI0', '1xisAgfjg3dyKQDGzI8N6cQMGbb4CDAS9'),
            'נתיב העשרה': ('1q-ggLrBgbDjvm1tw8Unyo0MpxSb9-6ls', '1nxQyVVDFMIliXk81TfopT9u_lDolMJW7'),
            'סופה': ('1vJ4L9m88hWBb9IscRNvPF65Kc68BaBN-', '1wAtfnsfZK2pzAjtbn_GmY02Epkf76RgA'),
            'סעד': ('1V885r58hdnTYvuBmkUAoYS460dQpLDEt', '1yQ9184YNX2oohlrb5__N8hpdUA6f_GKu'),
            'עין הבשור': ('1t3hVC6s8DznTukc_C6qsXCBqfUUWXdZy', '1ulkydAWA0JZ9iogaJbjveHH_6unRoX2c'),
            'עין השלושה': ('18z6TEC6dlN3myWVAo8KjOMQosNP_APvA', '1Qy3JkVWURn9idPlgoLR35kWLHr0THzDc'),
            'עלומים': ('1vbhfZcZv-p3X8x0H66gcno5J6faF2Ubg', '1toajTYH-cmGw8Zzqb2ICMr3mou3cuwlq'),
            'עמי עוז': ('19EDmbvzTQpjj1omuHpdM-Mrqe1ww95wI', '1Sv3UAKFh43dXZQoDjsx4Zsur1nbFGzjI'),
            'פרי גן': ('1VeY_v_sAX7HUkah8hcJXfUeIp-QB3h73', '1W8kwEeQWfaKw69i7lVKOmqs2CN-ehQqg'),
            'צאלים': ('1p1zZREAT0bx-O_hubbptMwKL-fNNDurn', '1RD-L1xOYhb4DcWbU2XQbmFZbu8W5R29Y'),
            'צוחר': ('1pyu_wGms6cZmLiPSPoz-xQDA5m_E18af', '1049iBo4NdOdOMgk6WL6uD9huQSsamjGy'),
            'רוחמה': ('1suHN8GsGDOCtMOiH03Fo3N7xBrcqePb7', '1m-FryQ0NlzvWslOQJU_M1OOHAfKGwLUq'),
            'רעים': ('1PRVuFiTuUf4XJJVm3r0xy-LccA3pgybc', '13pD7ly8zAI6gVchKUMI5pr_MT71bPN3r'),
            'שדה ניצן': ('1Z6v2pYzklMk3aCj3xguVXPD0NHQtj-Jp', '1iYeKrK-BLQf7_9sbkeQXkBnUJi6N4wnM'),
            'שדי אברהם': ('1jLIisGByC8AfHGi-Gr9EAVkUaObTR9MF', '1KxWN-x4_Plaw315OSmukAdwXn4bhMJVC'),
            'שדרות': ('1dbfnxq53QR9ZV1RX5byrgyBu0eatQRKD', '1Y8SiCzTdCni3sY0jTCyEwNeGZ48AYyoQ'),
            'שובה': ('1Dv-2NKrOXsUzf9UtVjLk8V4tweKAvrQm', '1NzoA1D7rf1XxMVy3Br0XwvueVPTfy4au'),
            'שוקדה': ('11ASf72JfcmMbZdX7NLKz955kngwG9nIC', '1iR2_uY7hJ53Djft77gIw-foBZgN1RXsl'),
            'שיבולים': ('1XW6pkyO3TiMej2h0E3mR71g9l9mkivef', '13Cvkjbwf-B-CHqbll7VnuuKmqUeHuA2I'),
            'שלומית': ('1bTvg384AW_IT1ms3WncbR_8scaXp9vQ5', '1c5oRACDJzVAjg5FtrlDgE3mKSA38TgBt'),
            'שרשרת': ('1JuC0BSOadb3eQZ7vdj4bQpUKTpgG3Oiz', '1es0tFSb77_kZe8BDApnjthiUDJIkXw8T'),
            'תושיה': ('1wRBpeNch3cnb53yauY_hNVsFnupSs8Tf', '1bWsH3s-RlBFa45ZFhDgQ0AxJn0Zj1qle'),
            'תלמי אליהו': ('1m1bIQNKWbaqtikZ-an09o4XLh2-jyi-R', '1Wemnz-Fj47gGZ2X9N2WkCxeyimRAFyzu'),
            'תלמי יוסף': ('1cLe2ycoPSR9WA-RTlJDJz-Z0FQJmO562', '1vkr-9od2Ez_FkKKku2CbRLGIr9UdFAOb'),
            'תקומה': ('1op9G1YIk8XWXLH3K5V3yFaxf80LO3uAs', '1CGtNw2uDIvZTtJNFTU-yyAbfh9iWwPhc')

        }

        # Initialize credentials
        self.creds = Credentials.from_service_account_file(self.credentials_json, scopes=self.scopes)

        # Build Drive API Service
        self.service = build('drive', 'v3', credentials=self.creds)

    def get_folder_id_by_name(self, folder_name: str):
        """Finds folder ID by its exact name."""
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            return None
        return items[0]['id']

    def list_files_in_folder(self, folder_name: str):
        """Scans a folder by name and prints all files inside it."""
        folder_id = self.get_folder_id_by_name(folder_name)

        if not folder_id:
            print(f"Folder not found: {folder_name}")
            return []

        query = f"'{folder_id}' in parents and trashed = false"
        results = self.service.files().list(
            q=query,
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()

        items = results.get('files', [])

        if not items:
            print("Folder is empty.")
        else:
            print(f"Found {len(items)} files in folder '{folder_name}':")
            for item in items:
                print(f"- File: {item['name']} | Type: {item['mimeType']} | ID: {item['id']}")

        return items

    def list_files_in_root(self):
        """Queries the root (My Drive) folder directly."""
        query = "'root' in parents and trashed = false"

        results = self.service.files().list(
            q=query,
            fields="files(id, name, mimeType)"
        ).execute()

        items = results.get('files', [])
        return items

    def _find_folder_by_name(self, folder_name: str, parent_id: str = None) -> str:
        """Helper to find folder ID by name, optionally filtered by a parent folder ID."""
        query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        if parent_id:
            query += f" and '{parent_id}' in parents"

        results = self.service.files().list(q=query, fields="files(id, name)").execute()
        items = results.get('files', [])
        return items[0]['id'] if items else None

    def scan_all_department_files(self):
        """Scans the fixed directory structure down to the management subfolders."""

        # Step 1: Locate the Main root folder ID
        main_id = self._dirs_ids['main']

        if not main_id:
            print("Error: Main folder ID is missing or invalid in _dirs_ids.")
            return

        print(f"Main folder verified. ID: {main_id}")

        # Step 2: Locate the nested 'מחלקתיים' folder ID
        nested_folder_name = "מחלקתיים"
        nested_id = self._dirs_ids[nested_folder_name]

        if not nested_id:
            print(f"Error: Nested folder '{nested_folder_name}' ID is missing or invalid.")
            return

        print(f"Nested folder verified. ID: {nested_id}")

        # Step 3: Get all settlement subfolders within the nested 'מחלקתיים' folder
        query_subfolders = f"'{nested_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        subfolders_result = self.service.files().list(q=query_subfolders, fields="files(id, name)").execute()
        settlement_folders = subfolders_result.get('files', [])

        print(f"Found {len(settlement_folders)} settlement folders to process.\n")

        # Step 4: Iterate through each settlement folder to target its specific management subfolder
        for settlement in settlement_folders:
            settlement_id = settlement['id']
            settlement_name = settlement['name']
            print(f"--- Processing settlement: {settlement_name} (ID: {settlement_id}) ---")

            # Construct target management folder name dynamically (e.g., "זיקים - הנהלה")
            target_management_name = f"{settlement_name} - הנהלה"
            query_management = (
                f"name = '{target_management_name}' and "
                f"'{settlement_id}' in parents and "
                f"mimeType = 'application/vnd.google-apps.folder' and "
                f"trashed = false"
            )

            management_result = self.service.files().list(q=query_management, fields="files(id, name)").execute()
            management_folders = management_result.get('files', [])

            if not management_folders:
                print(f"   Warning: Management folder '{target_management_name}' not found.")
                print("\n")
                continue

            management_id = management_folders[0]['id']
            print(f"   Target folder found: {target_management_name} (ID: {management_id})")

            # Step 5: Scan and print files within the specific management folder
            query_files = f"'{management_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
            files_result = self.service.files().list(q=query_files, fields="files(id, name, mimeType)").execute()
            files = files_result.get('files', [])

            if not files:
                print("   (Folder contains no files)")
            else:
                for file in files:
                    print(f"   File: {file['name']} | Type: {file['mimeType']}")
            print("\n")


        def get_settlement_files(settlement_name: str):
            """Scans the fixed directory structure down to the management subfolders."""

            # Step 1: Locate the Main root folder ID
            main_id = self._dirs_ids['main']

            if not main_id:
                print("Error: Main folder ID is missing or invalid in _dirs_ids.")
                return

            print(f"Main folder verified. ID: {main_id}")

            # Step 2: Locate the nested 'מחלקתיים' folder ID
            nested_folder_name = "מחלקתיים"
            nested_id = self._dirs_ids[nested_folder_name]

            if not nested_id:
                print(f"Error: Nested folder '{nested_folder_name}' ID is missing or invalid.")
                return

            print(f"Nested folder verified. ID: {nested_id}")

            # Step 3: Get all settlement subfolders within the nested 'מחלקתיים' folder
            query_subfolders = f"'{nested_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
            subfolders_result = self.service.files().list(q=query_subfolders, fields="files(id, name)").execute()
            settlement_folders = subfolders_result.get('files', [])

            print(f"Found {len(settlement_folders)} settlement folders to process.\n")

            # Step 4: Iterate through each settlement folder to target its specific management subfolder
            for settlement in settlement_folders:
                settlement_id = settlement['id']
                settlement_name = settlement['name']
                print(f"--- Processing settlement: {settlement_name} (ID: {settlement_id}) ---")

                # Construct target management folder name dynamically (e.g., "זיקים - הנהלה")
                target_management_name = f"{settlement_name} - הנהלה"
                query_management = (
                    f"name = '{target_management_name}' and "
                    f"'{settlement_id}' in parents and "
                    f"mimeType = 'application/vnd.google-apps.folder' and "
                    f"trashed = false"
                )

                management_result = self.service.files().list(q=query_management, fields="files(id, name)").execute()
                management_folders = management_result.get('files', [])

                if not management_folders:
                    print(f"   Warning: Management folder '{target_management_name}' not found.")
                    print("\n")
                    continue

                management_id = management_folders[0]['id']
                print(f"   Target folder found: {target_management_name} (ID: {management_id})")

                # Step 5: Scan and print files within the specific management folder
                query_files = f"'{management_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"
                files_result = self.service.files().list(q=query_files, fields="files(id, name, mimeType)").execute()
                files = files_result.get('files', [])

                if not files:
                    print("   (Folder contains no files)")
                else:
                    for file in files:
                        print(f"   File: {file['name']} | Type: {file['mimeType']}")
                print("\n")

    def get_files_by_folder_id(self, settlement_name: str):
        """Fetches and prints file names from a specific settlement folder ID."""

        # Extract the folder ID from the dictionary using the provided structure
        try:
            folder_id = self.settlements_dirs_id_sets[settlement_name][1]
        except (KeyError, IndexError):
            print(f"Error: Settlement '{settlement_name}' or its folder ID at index 1 was not found.")
            return []

        # Construct query to fetch files (excluding subfolders) inside the target folder
        query = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed = false"

        try:
            results = self.service.files().list(
                q=query,
                fields="files(id, name, mimeType)"
            ).execute()

            items = results.get('files', [])
            items_as_list = []
            print(f"--- Scanning folder for settlement: {settlement_name} (ID: {folder_id}) ---")
            if not items:
                print("   (Folder contains no files)")
            else:
                for file in items:
                    print(f"   File: {file['name']} | Type: {file['mimeType']}")
                    items_as_list.append(file['name'])
            print("\n")

            return items_as_list

        except Exception as e:
            print(f"Error querying files for settlement '{settlement_name}': {e}")
            return []

    def find_last_settlement_report(self, settlement_name: str) -> str:
        set_list = self.get_files_by_folder_id(settlement_name)
        if not set_list:
            print(f"No files found for settlement '{settlement_name}'.")
            return None
        else:
            calc_df = { int(f_name.split('_')[0]): f_name for f_name in set_list if 'אימון' in f_name and f_name.split('_')[0].isdigit() }

            max_val = max(calc_df.keys())
            print(f"--- Max number of files: {max_val} ---")
            print(f"final result: {calc_df[max_val]}")
            return calc_df[max_val]



    def read_xlsx_from_drive(self, file_id: str) -> pd.DataFrame:
        """Downloads a raw .xlsx file from Drive and loads it into a Pandas DataFrame."""
        try:
            # Downloading the binary content of the Excel file
            request = self.service.files().get_media(fileId=file_id)
            file_bytes = io.BytesIO(request.execute())

            # Reading the bytes directly into Pandas (no need to save a physical file)
            df = pd.read_excel(file_bytes, header=None)
            return df

        except Exception as e:
            print(f"Error reading Excel file from Drive: {e}")
            return pd.DataFrame()

    def get_file_id_by_name_and_parent(self, file_name: str, parent_id: str) -> str:
        """Finds a specific file ID by its name and its parent folder ID."""
        # Construct query to match both the exact file name and its parent folder ID
        query = f"name = '{file_name}' and '{parent_id}' in parents and trashed = false"

        try:
            results = self.service.files().list(
                q=query,
                fields="files(id, name)"
            ).execute()

            items = results.get('files', [])

            if not items:
                print(f"File '{file_name}' not found in parent folder ID: {parent_id}")
                return None

            # Extract and return the ID of the first matching file
            file_id = items[0]['id']
            print(f"Successfully found file: {file_name} | ID: {file_id}")
            return file_id

        except Exception as e:
            print(f"Error locating file '{file_name}' under parent '{parent_id}': {e}")
            return None

    def get_qualification_variable(self, settlement_name: str):
        """Example method to demonstrate fetching a specific file and reading its content."""
        # Step 1: Get the list of files in the target settlement's management folder
        target_file_name: str = self.find_last_settlement_report(settlement_name)

        if not target_file_name:
            print(f"No files found for settlement '{target_file_name}'.")
            return None

        # Step 2: Identify the specific file of interest (e.g., "qualification_data.xlsx")

        target_file_id = self.get_file_id_by_name_and_parent(target_file_name, self.settlements_dirs_id_sets[settlement_name][1])

        if not target_file_id:
            print(f"File '{target_file_name}' not found for settlement '{settlement_name}'.")
            return None

        # Step 3: Read the Excel file content into a DataFrame
        df = self.read_xlsx_from_drive(target_file_id)
        # print(df)
        # return df

        extracted_value = None

        if not df.empty:
            row_idx = None
            col_idx = None

            for c in range(df.shape[1]):
                # 1. ניקוי כותרת העמודה מרווחים נסתרים ובדיקה
                column_name = str(df.columns[c]).strip()
                if "ציון סופי" in column_name:
                    col_idx = c
                    break

                # 2. ניקוי כל התאים בעמודה מרווחים ובדיקה (בצורה חסינת קריסה)
                # אנחנו הופכים את התאים לטקסט, מנקים רווחים מהקצוות, ובודקים אם "ציון סופי" בפנים
                has_target = df.iloc[:, c].astype(str).str.strip().str.contains("ציון סופי").any()

                if has_target:
                    col_idx = c
                    break

            # בדיקה זמנית כדי לראות אם מצאנו
            if col_idx is not None:
                print(f"Column with 'ציון סופי' found at index: {col_idx}")
            else:

                # הדפסה שתראה לך בדיוק מה הדאטה פריים מכיל בשורות הראשונות שלו
                print(df.head(5))
            print(f"------- found column {col_idx} -------")

            # 2. Find the row index: one row before the last row containing actual data
            # Replace empty strings/spaces with None, then check which rows have any valid data
            has_data = df.replace(r'^\s*$', None, regex=True).notna().any(axis=1)
            valid_positions = [i for i, available in enumerate(has_data) if available]

            if valid_positions:
                last_data_row_pos = valid_positions[-1]
                row_idx = last_data_row_pos - 1  # One row before the last data row
            else:
                row_idx = None

            # 3. If both indices are valid, extract the value from (row, col - 1)
            if row_idx is not None and col_idx is not None:
                if row_idx >= 0 and col_idx > 0:  # Ensure indices are within valid bounds
                    extracted_value = df.iloc[row_idx, col_idx]
                    print("--- Successfully found dynamically (Row before last data row) ---")
                    print(f"Target Row Index: {row_idx} (Last data row was: {last_data_row_pos})")
                    print(f"Matching Col Index (col - 1): {col_idx }")
                    print(f"Extracted Value: {extracted_value}")
                else:
                    print(f"Error: Calculated indices are out of bounds. Row: {row_idx}, Col: {col_idx}")
            else:
                print(
                    f"Error: Could not locate markers. 'ציון סופי' col: {col_idx} | Last data row found: {bool(valid_positions)}")
        # ----------------------------------------

        return extracted_value
# g = GoogleDriveAuth()
# g.get_qualification_variable("אורים")