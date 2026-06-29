# בתוך קובץ ה-utils שלך או בקובץ app.py הראשי
import streamlit as st


def enforce_authentication():
    """securing any page that is not the main authentication page"""
    if not st.session_state.get("password_correct", False):

        st.set_page_config(initial_sidebar_state="collapsed")

        st.warning("🔒 הגישה לדף זה חסומה. אנא עבר לדף הבית והזן סיסמה.")
        st.info("💡 לחץ על דף הבית (הדף הראשי) בסיידבר כדי להתחבר.")

        st.stop()