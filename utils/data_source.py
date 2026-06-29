from __future__ import annotations

import logging
import streamlit as st

from data.external.gsheets_auth import GoogleSheetsAuth
from data.static import InternalGoogleSheetVars

logger = logging.getLogger(__name__)


@st.cache_data(ttl=300)
def load_main_sheet():
    try:
        spreadsheet = GoogleSheetsAuth()
        return spreadsheet.get_worksheet(
            InternalGoogleSheetVars.mbt_spreadsheet_name,
            InternalGoogleSheetVars.main_data_worksheet_name,
        )
    except Exception as exc:
        logger.exception("Failed to load main sheet data, returning empty fallback")
        try:
            st.warning("לא ניתן לטעון נתונים מ-Google Sheets כרגע, מוצג fallback ריק.")
        except Exception:
            pass
        return []


sheet = load_main_sheet()

