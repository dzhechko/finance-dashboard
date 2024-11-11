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
    initial_sidebar_state="expanded"
)

def main():
    # Automatically redirect to Dashboard page
    st.switch_page("pages/1_📊_Dashboard.py")

if __name__ == "__main__":
    main() 