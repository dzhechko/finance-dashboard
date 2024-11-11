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

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def health_check():
    """Health check endpoint for Railway.app"""
    if st.session_state.get('health_check'):
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }

def main():
    # Update deprecated experimental_get_query_params to query_params
    query_params = st.query_params
    
    if 'health_check' in query_params:
        st.json(health_check())
        return

    try:
        # Load configuration
        config = load_config()
        debug_mode = get_debug_status()
        auth_required = get_auth_required()
        
        if debug_mode:
            logger.debug("Application started in debug mode")
        
        # Display header
        st.title("Личный Финансовый Дашборд")
        
        if not auth_required or st.session_state.authenticated:
            st.write("Добро пожаловать в ваш финансовый дашборд!")
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Загрузите ваш файл Excel с финансовыми данными",
                type=["xlsx"]
            )
            
            if uploaded_file is not None:
                if debug_mode:
                    logger.debug(f"File uploaded: {uploaded_file.name}")
                # File processing logic will be implemented here
                pass
                
        else:
            st.warning("Пожалуйста, выполните вход в систему")
            
    except Exception as e:
        logger.error(f"Error in main application: {e}")
        st.error("Произошла ошибка при загрузке приложения")

if __name__ == "__main__":
    main() 