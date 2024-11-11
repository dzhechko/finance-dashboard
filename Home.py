import streamlit as st
from utils.helpers import load_config, logger, get_debug_status, get_auth_required
import yaml
import os
from datetime import datetime

# Configure page settings with dark theme
st.set_page_config(
    page_title="Личный Финансовый Дашборд",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    },
    theme={
        "base": "dark",
        "primaryColor": "#3498db",
        "backgroundColor": "#0e1117",
        "secondaryBackgroundColor": "#262730",
        "textColor": "#fafafa",
    }
)

def main():
    # Automatically redirect to Authentication page
    st.switch_page("pages/1_🔐_Вход.py")

if __name__ == "__main__":
    main() 