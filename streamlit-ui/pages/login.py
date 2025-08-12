import streamlit as st
from utils.db_utils import login_user

st.title("Login")

# Redirect if already logged in
if st.session_state.get('authenticated'):
    user_type = st.session_state.get('user_type', 'user')
    
    if user_type == 'admin':
        st.success(f"Welcome back, Admin!")
        st.markdown("**You are logged in as administrator.**")
        
        # Provide navigation options for admin
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Admin Panel", type="primary"):
                st.switch_page("pages/admin.py")
        with col2:
            if st.button("Logout"):
                # Clear session state for logout
                st.session_state['authenticated'] = False
                st.session_state['user'] = None
                st.session_state['user_type'] = None
                st.rerun()
    else:
        st.success(f"Welcome back, {st.session_state.get('user_name', st.session_state.get('user'))}!")
        st.markdown("**You are already logged in.**")
        
        # Provide navigation options for regular user
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Upload Page", type="primary"):
                st.switch_page("pages/upload.py")
        with col2:
            if st.button("Logout"):
                # Clear session state for logout
                st.session_state['authenticated'] = False
                st.session_state['user'] = None
                st.session_state['user_type'] = None
                st.rerun()
    
    # Stop execution if user is already logged in
    st.stop()

# Login form inputs
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login", type="primary"):
    # Validate input fields
    if email and password:
        try:
            # Attempt user authentication
            login_result = login_user(email, password)
            
            # Handle admin login
            if login_result["role"] == "admin":
                # Set session state for admin
                st.session_state['authenticated'] = True
                st.session_state['user'] = email
                st.session_state['user_type'] = 'admin'
                st.success("Admin login successful!")
                st.switch_page("pages/admin.py")
                
            # Handle regular user login
            elif login_result["role"] == "user":
                # Set session state for user
                st.session_state['authenticated'] = True
                st.session_state['user'] = login_result["email"]
                st.session_state['user_name'] = login_result["name"]
                st.session_state['user_type'] = 'user'
                st.success(f"Login successful! Welcome, {login_result['name']}.")
                st.switch_page("pages/upload.py")
                
            # Handle unverified user
            elif login_result["role"] == "unverified":
                st.error("Email not verified. Please check your email and verify your account.")
                
            # Handle invalid credentials
            else:
                st.error("Incorrect credentials.")
                
        except Exception as e:
            # Handle login errors
            st.error(f"Login failed: {str(e)}")
    else:
        # Handle empty input fields
        st.error("Please enter both email and password.")
