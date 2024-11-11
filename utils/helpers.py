import os
from loguru import logger
import yaml
from typing import Dict, Any
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
log_level = os.getenv("LOG_LEVEL", "INFO")
logger.remove()  # Remove default handler
logger.add(
    "logs/finance_app.log",
    rotation="500 MB",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=log_level
)

def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml and environment variables"""
    try:
        # Load base configuration from file
        with open("config/config.yaml", "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            
        if config is None:
            config = {}
        
        # Ensure required sections exist
        if 'settings' not in config:
            config['settings'] = {}
        if 'cookie' not in config:
            config['cookie'] = {}
        if 'credentials' not in config:
            config['credentials'] = {'usernames': {}}
            
        # Override with environment variables
        config['settings']['debug'] = os.getenv('DEBUG', 'false').lower() == 'true'
        config['settings']['auth_required'] = os.getenv('AUTH_REQUIRED', 'true').lower() == 'true'
        
        # Update cookie settings
        config['cookie']['key'] = os.getenv('AUTH_SECRET_KEY', 
                                          config['cookie'].get('key', 'default_secret_key'))
        config['cookie']['name'] = config['cookie'].get('name', 'finance_dashboard_cookie')
        config['cookie']['expiry_days'] = int(config['cookie'].get('expiry_days', 30))
        
        logger.debug("Configuration loaded successfully")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        # Return default configuration if loading fails
        return {
            'settings': {
                'debug': False,
                'auth_required': True
            },
            'cookie': {
                'key': os.getenv('AUTH_SECRET_KEY', 'default_secret_key'),
                'name': 'finance_dashboard_cookie',
                'expiry_days': 30
            },
            'credentials': {
                'usernames': {}
            }
        }

def validate_excel_file(file) -> bool:
    """Validate uploaded Excel file structure"""
    try:
        required_sheets = ["Net Worth Table", "Income Table", "Expenses Table", "Budget Table"]
        excel_data = pd.read_excel(file, sheet_name=None)
        
        # Check if all required sheets exist
        if not all(sheet in excel_data for sheet in required_sheets):
            logger.error("Missing required sheets in Excel file")
            return False
            
        # Validate sheet structures
        validations = {
            "Net Worth Table": ["Date", "Assets", "Liabilities"],
            "Income Table": ["IncomeID", "Date", "Source", "Amount"],
            "Expenses Table": ["ExpenseID", "Date", "Category", "Description", "Amount"],
            "Budget Table": ["Category", "BudgetAmount"]
        }
        
        for sheet, columns in validations.items():
            if not all(col in excel_data[sheet].columns for col in columns):
                logger.error(f"Missing required columns in {sheet}")
                return False
                
        logger.debug("Excel file validation successful")
        return True
        
    except Exception as e:
        logger.error(f"Error validating Excel file: {e}")
        return False

def get_debug_status() -> bool:
    """Get debug status from config"""
    config = load_config()
    return config["settings"]["debug"]

def get_auth_required() -> bool:
    """Get authentication requirement status from config"""
    config = load_config()
    return config["settings"]["auth_required"] 