import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_env_var(key, default=None):
    try:
        # Try to get from Streamlit secrets first
        if hasattr(st, 'secrets') and key in st.secrets:
            value = st.secrets[key]
            if value:  # Ensure it's not an empty string
                return value
    except Exception:
        # If accessing secrets fails, continue to try environment variables
        pass
    
    # If secrets don't have it or is empty, get from environment variables
    return os.getenv(key, default)


# Admin credentials
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

# Email configuration
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
SENDER_PASSWORD = os.getenv('SENDER_PASSWORD') 

# MongoDB configuration
MONGO_URI = os.getenv('MONGO_URI')
MONGO_DB_NAME = os.getenv('MONGO_DB_NAME')