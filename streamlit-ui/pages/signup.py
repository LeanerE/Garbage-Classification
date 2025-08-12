import streamlit as st
from utils.db_utils import register_user, generate_code, email_exists, verify_user
from utils.auth_utils import send_verification_email
import re

st.title("Sign Up")

# Helper function to validate email format
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

# Helper function to validate password strength
def is_strong_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    return True, "Password is strong"

# Registration section
st.subheader("Create Account")

name = st.text_input("Name", placeholder="Enter your name")
email = st.text_input("Email Address", placeholder="Enter your email address")
password = st.text_input("Password", type="password", placeholder="Enter a strong password")

# Show password requirements
with st.expander("Password Requirements"):
    st.markdown("""
    Your password must contain:
    - At least 8 characters
    - At least one uppercase letter (A-Z)
    - At least one lowercase letter (a-z)
    - At least one number (0-9)
    """)

if st.button("Register", type="primary"):
    # Input validation
    if not name or not email or not password:
        st.error("Please fill in all required fields.")
    elif not name.strip():
        st.error("Please enter a valid name.")
    elif not is_valid_email(email):
        st.error("Please enter a valid email address.")
    else:
        # Check password strength
        is_strong, password_message = is_strong_password(password)
        if not is_strong:
            st.error(password_message)
        elif email_exists(email):
            st.warning("This email is already registered. Please use a different email or try logging in.")
        else:
            # Attempt registration
            try:
                code = generate_code()
                success = register_user(name.strip(), email.lower().strip(), password, code)
                
                if success:
                    # Try to send verification email
                    if send_verification_email(email, code):
                        st.success("Registration successful! A verification code has been sent to your email.")
                        
                        # Store verification info in session state
                        st.session_state.verification_email = email.lower().strip()
                        st.session_state.verification_code = code
                        st.session_state.registration_successful = True
                        st.session_state.user_name = name.strip()
                        
                        # Rerun to show verification section
                        st.rerun()
                    else:
                        st.error("Registration successful, but failed to send verification email. Please contact support.")
                else:
                    st.error("Registration failed. Please try again or contact support.")
                    
            except Exception as e:
                st.error(f"An error occurred during registration: {str(e)}")

# Email verification section
if st.session_state.get('registration_successful', False):
    st.markdown("---")
    st.subheader("Email Verification")
    
    # Show verification instructions
    st.info(f"A verification code has been sent to: **{st.session_state.verification_email}**")
    st.info("Please check your email (including spam folder) and enter the verification code below.")
    
    verify_code = st.text_input(
        "Enter Verification Code", 
        key="verify_code",
        placeholder="Enter the 6-digit code",
        max_chars=6
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("Verify Code", type="primary"):
            if not verify_code.strip():
                st.error("Please enter the verification code.")
            elif len(verify_code.strip()) != 6:
                st.error("Verification code must be 6 digits.")
            else:
                try:
                    if verify_user(st.session_state.verification_email, verify_code.strip()):
                        st.success("Email verified successfully! Redirecting to login page...")
                        
                        # Clear verification session state
                        st.session_state.registration_successful = False
                        st.session_state.verification_email = None
                        st.session_state.verification_code = None
                        st.session_state.user_name = None
                        
                        # Redirect to login page
                        st.switch_page("pages/login.py")
                    else:
                        st.error("Invalid verification code. Please check and try again.")
                        
                except Exception as e:
                    st.error(f"Verification failed: {str(e)}")
    
    with col2:
        if st.button("Resend Code"):
            try:
                if st.session_state.verification_email:
                    new_code = generate_code()
                    
                    if send_verification_email(st.session_state.verification_email, new_code):
                        # Update the code in session state
                        st.session_state.verification_code = new_code
                        st.success("New verification code sent to your email!")
                    else:
                        st.error("Failed to send verification code. Please try again later.")
                        
            except Exception as e:
                st.error(f"Failed to resend code: {str(e)}")
    
    with col3:
        if st.button("Cancel Registration"):
            # Clear all registration session state
            st.session_state.registration_successful = False
            st.session_state.verification_email = None
            st.session_state.verification_code = None
            st.session_state.user_name = None
            st.info("Registration cancelled.")
            st.rerun()

# Instructions for new users
if not st.session_state.get('registration_successful', False):
    st.markdown("---")
    st.info("""
    **Registration Steps:**
    1. Fill in your name, email address, and a strong password
    2. Click "Register" to create your account
    3. Check your email for the verification code
    4. Enter the code to complete your registration
    5. You'll be redirected to the login page
    """)
