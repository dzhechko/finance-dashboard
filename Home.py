import streamlit as st
from utils.helpers import load_config, logger, get_debug_status, get_auth_required
import yaml
import os
from datetime import datetime

# Configure page settings
st.set_page_config(
    page_title="Личный Финансовый Дашборд",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Set dark theme
st.markdown("""
    <style>
        /* Main container */
        .stApp {
            background-color: #0E1117;
        }
        
        /* Sidebar */
        [data-testid="stSidebar"] {
            background-color: #262730;
        }
        
        /* Text color */
        .stMarkdown, .stText {
            color: #FFFFFF;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
        }
        
        /* Скрыть пункт меню "app" */
        [data-testid="stSidebarNav"] ul li:first-child {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)

def main():
    # Automatically redirect to Authentication page
    st.switch_page("pages/1_🔐_Вход.py")

if __name__ == "__main__":
    main() 