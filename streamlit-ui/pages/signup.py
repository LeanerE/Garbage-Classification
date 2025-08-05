import streamlit as st
from utils.db_utils import register_user, generate_code, email_exists, verify_user
from utils.auth_utils import send_verification_email

st.title("Sign Up")

# Registration section
st.subheader("Create Account")

name = st.text_input("Name")
email = st.text_input("Email")
password = st.text_input("Password", type="password")

if st.button("Register", type="primary"):
    if not name or not email or not password:
        st.error("Please enter your name, email and password.")
    elif email_exists(email):
        st.warning("This email is already registered.")
    else:
        code = generate_code()
        success = register_user(name, email, password, code)
        if success:
            if send_verification_email(email, code):
                st.success("Registration successful! Verification code sent to your email.")
                # Store authentication info in session state
                st.session_state.verification_email = email
                st.session_state.verification_code = code
                st.session_state.registration_successful = True
            else:
                st.error("Failed to send verification email. Please check configuration.")
        else:
            st.error("Registration failed. Please try again.")

# Email verification section
if st.session_state.get('registration_successful', False):
    st.markdown("---")
    st.subheader("Email Verification")
    
    st.info(f"A verification code has been sent to: **{st.session_state.verification_email}**")
    st.info("Please check your email and enter the verification code below.")
    
    verify_code = st.text_input("Enter Verification Code", key="verify_code")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Verify Code", type="primary"):
            if verify_code.strip():
                if verify_user(st.session_state.verification_email, verify_code):
                    # clean session state
                    st.session_state.registration_successful = False
                    st.session_state.verification_email = None
                    st.session_state.verification_code = None
                    st.switch_page("pages/login.py")
                else:
                    st.error("Incorrect verification code. Please try again.")
            else:
                st.error("Please enter the verification code.")
    
    with col2:
        if st.button("Resend Code"):
            if st.session_state.verification_email:
                new_code = generate_code()
                if send_verification_email(st.session_state.verification_email, new_code):
                    st.session_state.verification_code = new_code
                    st.success("New verification code sent!")
                else:
                    st.error("Failed to send verification code.")

# Instructions for users who haven't registered yet
if not st.session_state.get('registration_successful', False):
    st.markdown("---")
    st.info("""
    **How to register:**
    1. Enter your email and password above
    2. Click "Register" to create your account
    3. Check your email for the verification code
    4. Enter the code below to complete registration
    """)