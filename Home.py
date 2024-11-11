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
    }
)

# Set dark theme
st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background-color: #0e1117;
            color: #fafafa;
        }
        
        /* Sidebar */
        .css-1d391kg {
            background-color: #262730;
        }
        
        /* Text color */
        .stMarkdown, .stText {
            color: #fafafa;
        }
        
        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #fafafa !important;
        }
        
        /* Metric labels */
        [data-testid="stMetricLabel"] {
            color: #fafafa !important;
        }
        
        /* Metric values */
        [data-testid="stMetricValue"] {
            color: #fafafa !important;
        }
        
        /* Sidebar menu styling */
        .css-1d391kg .stSelectbox label {  /* Sidebar labels */
            color: #fafafa;
        }
        
        /* Sidebar menu items */
        .css-1d391kg [data-testid="stSidebarNav"] {
            background-color: #262730;
            padding-top: 2rem;
        }
        
        /* Sidebar menu item hover */
        .css-1d391kg [data-testid="stSidebarNav"] a:hover {
            background-color: #3498db;
        }
    </style>
""", unsafe_allow_html=True)

def main():
    # Automatically redirect to Authentication page
    st.switch_page("pages/1_🔐_Вход.py")

if __name__ == "__main__":
    main() 