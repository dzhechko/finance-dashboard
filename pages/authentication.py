import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from utils.helpers import logger, load_config, get_debug_status
import bcrypt
from typing import Dict, Optional

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
        
        /* Form inputs */
        .stTextInput input, .stTextInput div {
            background-color: #262730 !important;
            color: #FFFFFF !important;
        }
        
        /* Buttons */
        .stButton button {
            background-color: #3498db !important;
            color: #FFFFFF !important;
            border: none !important;
        }
    </style>
""", unsafe_allow_html=True)

class AuthenticationManager:
    def __init__(self):
        self.debug_mode = get_debug_status()
        self.config = load_config()
        self.authenticator = self._initialize_authenticator()

    def _initialize_authenticator(self) -> stauth.Authenticate:
        """Initialize the authenticator with current configuration"""
        try:
            return stauth.Authenticate(
                self.config['credentials'],
                self.config['cookie']['key'],
                self.config['cookie']['name'],
                self.config['cookie']['expiry_days'],
                ["admin", "user"]  # Possible preauthorized roles
            )
        except Exception as e:
            logger.error(f"Error initializing authenticator: {e}")
            raise

    def _save_config(self) -> None:
        """Save updated configuration to config file"""
        try:
            with open('config/config.yaml', 'w', encoding='utf-8') as file:
                yaml.dump(self.config, file, default_flow_style=False, allow_unicode=True)
            if self.debug_mode:
                logger.debug("Configuration saved successfully")
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise

    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def register_user(self, username: str, name: str, email: str, password: str) -> bool:
        """Register a new user"""
        try:
            if username in self.config['credentials']['usernames']:
                st.error("Пользователь с таким именем уже существует")
                return False

            hashed_password = self._hash_password(password)
            
            self.config['credentials']['usernames'][username] = {
                'email': email,
                'name': name,
                'password': hashed_password
            }
            
            self._save_config()
            if self.debug_mode:
                logger.debug(f"User registered successfully: {username}")
            return True
            
        except Exception as e:
            logger.error(f"Error during user registration: {e}")
            st.error("Ошибка при регистрации пользователя")
            return False

    def login(self) -> Optional[Dict]:
        """Handle user login"""
        try:
            name, authentication_status, username = self.authenticator.login(
                "Вход в систему", "main"
            )
            
            if authentication_status:
                if self.debug_mode:
                    logger.debug(f"User logged in successfully: {username}")
                return {"name": name, "username": username}
            elif authentication_status is False:
                st.error("Неверное имя пользователя или пароль")
            elif authentication_status is None:
                st.warning("Пожалуйста, введите имя пользователя и пароль")
                
            return None
            
        except Exception as e:
            logger.error(f"Error during login: {e}")
            st.error("Ошибка при входе в систему")
            return None

    def logout(self) -> None:
        """Handle user logout"""
        try:
            self.authenticator.logout("Выйти", "main")
            if self.debug_mode:
                logger.debug("User logged out successfully")
        except Exception as e:
            logger.error(f"Error during logout: {e}")
            st.error("Ошибка при выходе из системы")

def main():
    st.title("Аутентификация")
    
    auth_manager = AuthenticationManager()
    
    # Create tabs for login and registration
    tab1, tab2 = st.tabs(["Вход", "Регистрация"])
    
    with tab1:
        st.subheader("Вход в систему")
        user_data = auth_manager.login()
        if user_data:
            st.session_state.authenticated = True
            st.success(f"Добро пожаловать, {user_data['name']}!")
            auth_manager.logout()

    with tab2:
        st.subheader("Регистрация нового пользователя")
        with st.form("registration_form"):
            username = st.text_input("Имя пользователя")
            name = st.text_input("Полное имя")
            email = st.text_input("Email")
            password = st.text_input("Пароль", type="password")
            password_repeat = st.text_input("Подтвердите пароль", type="password")
            
            submit_button = st.form_submit_button("Зарегистрироваться")
            
            if submit_button:
                if password != password_repeat:
                    st.error("Пароли не совпадают")
                elif not all([username, name, email, password]):
                    st.error("Пожалуйста, заполните все поля")
                else:
                    if auth_manager.register_user(username, name, email, password):
                        st.success("Регистрация успешна! Теперь вы можете войти в систему.")

if __name__ == "__main__":
    main() 