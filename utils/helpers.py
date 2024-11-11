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
        
        # Try to read the Excel file
        try:
            excel_data = pd.read_excel(file, sheet_name=None)
            if self.debug_mode:
                logger.debug(f"Successfully read Excel file. Found sheets: {list(excel_data.keys())}")
        except Exception as e:
            logger.error(f"Failed to read Excel file: {e}")
            return False
        
        # Check if all required sheets exist
        missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_data]
        if missing_sheets:
            logger.error(f"Missing sheets in Excel file: {missing_sheets}")
            return False
            
        # Validate sheet structures
        validations = {
            "Net Worth Table": ["Date", "Assets", "Liabilities"],
            "Income Table": ["IncomeID", "Date", "Source", "Amount"],
            "Expenses Table": ["ExpenseID", "Date", "Category", "Description", "Amount"],
            "Budget Table": ["Category", "BudgetAmount"]
        }
        
        for sheet, required_columns in validations.items():
            actual_columns = excel_data[sheet].columns.tolist()
            missing_columns = [col for col in required_columns if col not in actual_columns]
            
            if missing_columns:
                logger.error(f"Sheet '{sheet}' is missing columns: {missing_columns}")
                logger.error(f"Available columns: {actual_columns}")
                return False
            
            # Additional validation for date columns
            if "Date" in required_columns:
                try:
                    pd.to_datetime(excel_data[sheet]["Date"])
                except Exception as e:
                    logger.error(f"Invalid date format in {sheet}: {e}")
                    return False
            
            # Additional validation for numeric columns
            numeric_columns = ["Amount", "Assets", "Liabilities", "BudgetAmount"]
            for col in [c for c in required_columns if c in numeric_columns]:
                if not pd.to_numeric(excel_data[sheet][col], errors='coerce').notna().all():
                    logger.error(f"Invalid numeric values in {sheet}.{col}")
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