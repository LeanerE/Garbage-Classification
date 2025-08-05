import streamlit as st
from utils.db_utils import init_db_schema_if_needed

init_db_schema_if_needed()

st.set_page_config(
    page_title="Garbage Classification System", 
    page_icon="♻️",
    layout="wide"
)

st.title("Welcome to the Garbage Classification System")
st.markdown("---")

# Main content
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    ### What is this system?
    This is an AI-powered garbage classification system that helps you identify and properly sort different types of waste.
    
    ### How to get started:
    1. **Sign Up** - Create a new account with email verification
    2. **Log In** - Access your account
    3. **Upload Images** - Get instant classification results
    4. **History** - View your past prediction records
    
    ### Features:
    - Email verification for secure registration
    - Image upload and classification
    - Real-time prediction results
    - Secure user authentication
    - View prediction history
    - Admin panel for system management
    """)

with col2:
    st.markdown("### Quick Navigation")
    st.markdown("---")
    st.page_link("pages/signup.py", label="Sign Up — Create new account")
    st.page_link("pages/login.py", label="Login — Access your account")
    st.page_link("pages/upload.py", label="Upload — Classify images")
    st.page_link("pages/history.py", label="History — View your prediction history")
    st.page_link("pages/admin.py", label="Admin Panel — System management")

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit and Eric for a cleaner environment*")
