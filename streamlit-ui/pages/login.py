import streamlit as st
from utils.db_utils import login_user

st.title("Login")

# Redirect if already logged in
if st.session_state.get('authenticated'):
    user_type = st.session_state.get('user_type', 'user')
    
    if user_type == 'admin':
        st.success(f"Welcome back, Admin!")
        st.markdown("**You are logged in as administrator.**")
        
        # Provide Jump Options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Admin Panel", type="primary"):
                st.switch_page("pages/admin.py")
        with col2:
            if st.button("Logout"):
                st.session_state['authenticated'] = False
                st.session_state['user'] = None
                st.session_state['user_type'] = None
                st.success("Logged out successfully!")
                st.rerun()
    else:
        st.success(f"Welcome back, {st.session_state.get('user_name', st.session_state.get('user'))}!")
        st.markdown("**You are already logged in.**")
        
        # Provide Jump Options
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Upload Page", type="primary"):
                st.switch_page("pages/upload.py")
        with col2:
            if st.button("Logout"):
                st.session_state['authenticated'] = False
                st.session_state['user'] = None
                st.session_state['user_type'] = None
                st.success("Logged out successfully!")
                st.rerun()
    
    st.stop()

email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Login", type="primary"):
    if email and password:
        login_result = login_user(email, password)
        
        if login_result["role"] == "admin":
            st.session_state['authenticated'] = True
            st.session_state['user'] = email
            st.session_state['user_type'] = 'admin'
            st.success("Admin login successful!")
            st.switch_page("pages/admin.py")
            
        elif login_result["role"] == "user":
            st.session_state['authenticated'] = True
            st.session_state['user'] = login_result["email"]
            st.session_state['user_name'] = login_result["name"]
            st.session_state['user_type'] = 'user'
            st.success(f"Login successful! Welcome, {login_result['name']}.")
            st.switch_page("pages/upload.py")
            
        elif login_result["role"] == "unverified":
            st.error("Email not verified. Please check your email and verify your account.")
            
        else:
            st.error("Incorrect credentials.")
    else:
        st.error("Please enter both email and password.")