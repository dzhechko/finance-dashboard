import os
import sys
from loguru import logger
import yaml
from typing import Dict, Any
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logger
def setup_logger():
    """Configure logger for both local and production environments"""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    
    # Remove default handler
    logger.remove()
    
    # Add stdout handler for Railway.app and local environment
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=log_level
    )
    
    # Add file handler only in local environment
    if not os.getenv('RAILWAY_ENVIRONMENT'):
        try:
            os.makedirs('logs', exist_ok=True)
            logger.add(
                "logs/finance_app.log",
                rotation="500 MB",
                retention="10 days",
                format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
                level=log_level
            )
        except Exception as e:
            logger.warning(f"Could not set up file logging: {e}")

# Initialize logger
setup_logger()

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
    """Validate uploaded Excel file structure with enhanced debugging"""
    debug_mode = os.getenv('DEBUG', 'false').lower() == 'true'
    
    try:
        required_sheets = ["Net Worth Table", "Income Table", "Expenses Table", "Budget Table"]
        
        # Try to read the Excel file
        try:
            excel_data = pd.read_excel(file, sheet_name=None)
            logger.debug(f"Found sheets in Excel file: {list(excel_data.keys())}")
        except Exception as e:
            logger.error(f"Failed to read Excel file: {str(e)}")
            return False
        
        # Check if all required sheets exist
        missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_data]
        if missing_sheets:
            logger.error(f"Missing sheets in Excel file: {missing_sheets}")
            return False
            
        # Validate sheet structures with detailed type checking
        validations = {
            "Net Worth Table": {
                "Date": "datetime64",
                "Assets": "float64",
                "Liabilities": "float64"
            },
            "Income Table": {
                "IncomeID": "int64",
                "Date": "datetime64",
                "Source": "object",
                "Amount": "float64"
            },
            "Expenses Table": {
                "ExpenseID": "int64",
                "Date": "datetime64",
                "Category": "object",
                "Description": "object",
                "Amount": "float64"
            },
            "Budget Table": {
                "Category": "object",
                "BudgetAmount": "float64"
            }
        }
        
        for sheet_name, expected_types in validations.items():
            df = excel_data[sheet_name]
            
            # Log actual columns and their types
            actual_columns = df.columns.tolist()
            actual_types = df.dtypes.to_dict()
            logger.debug(f"Sheet '{sheet_name}' columns: {actual_columns}")
            logger.debug(f"Sheet '{sheet_name}' types: {actual_types}")
            
            # Check for missing columns
            missing_columns = [col for col in expected_types.keys() if col not in df.columns]
            if missing_columns:
                logger.error(f"Sheet '{sheet_name}' is missing columns: {missing_columns}")
                return False
            
            # Validate data types and contents
            for column, expected_type in expected_types.items():
                # Get the actual data from the column
                column_data = df[column]
                
                # Log sample of data for debugging
                logger.debug(f"Sample data from {sheet_name}.{column}: {column_data.head()}")
                
                if expected_type == "datetime64":
                    try:
                        # Try to convert to datetime
                        df[column] = pd.to_datetime(df[column])
                        logger.debug(f"Successfully converted {sheet_name}.{column} to datetime")
                    except Exception as e:
                        logger.error(f"Failed to convert {sheet_name}.{column} to datetime: {str(e)}")
                        return False
                
                elif expected_type in ["float64", "int64"]:
                    try:
                        # Check for non-numeric values
                        numeric_data = pd.to_numeric(df[column], errors='coerce')
                        null_mask = numeric_data.isnull()
                        if null_mask.any():
                            invalid_rows = df.loc[null_mask].index.tolist()
                            invalid_values = df.loc[null_mask, column].tolist()
                            logger.error(f"Invalid numeric values in {sheet_name}.{column} at rows {invalid_rows}: {invalid_values}")
                            return False
                        
                        # Convert to proper numeric type
                        df[column] = numeric_data
                        logger.debug(f"Successfully converted {sheet_name}.{column} to {expected_type}")
                    except Exception as e:
                        logger.error(f"Error converting {sheet_name}.{column} to {expected_type}: {str(e)}")
                        return False
                
                elif expected_type == "object":
                    # Validate string data
                    if not all(isinstance(x, (str, type(None))) for x in df[column]):
                        logger.error(f"Invalid string values in {sheet_name}.{column}")
                        return False
            
            # Update the dataframe in excel_data with converted types
            excel_data[sheet_name] = df
        
        logger.info("Excel file validation successful")
        return True
        
    except Exception as e:
        logger.error(f"Error during Excel validation: {str(e)}")
        return False

def get_debug_status() -> bool:
    """Get debug status from config"""
    config = load_config()
    return config["settings"]["debug"]

def get_auth_required() -> bool:
    """Get authentication requirement status from config"""
    config = load_config()
    return config["settings"]["auth_required"] 