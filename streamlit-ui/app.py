import streamlit as st
import plotly.express as px
import pandas as pd
from utils.db_utils import get_user_predictions
from datetime import datetime, timedelta

st.set_page_config(
    page_title="AI Garbage Classification System", 
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Main title
st.title("AI Garbage Classification System")
st.markdown("---")

# Check user authentication status
is_authenticated = st.session_state.get('authenticated', False)
user_type = st.session_state.get('user_type', 'user')
user_name = st.session_state.get('user_name', st.session_state.get('user', ''))

# Sidebar navigation
with st.sidebar:
    st.markdown("## System Navigation")
    
    if is_authenticated:
        if user_type == 'admin':
            st.success(f"Administrator: {user_name}")
            st.markdown("---")
            if st.button("Admin Panel", use_container_width=True):
                st.switch_page("pages/admin.py")
            if st.button("Home", use_container_width=True):
                st.rerun()
            if st.button("Logout", use_container_width=True):
                for key in ['authenticated', 'user', 'user_type', 'user_name']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        else:
            st.success(f"User: {user_name}")
            st.markdown("---")
            if st.button("Upload Image", use_container_width=True):
                st.switch_page("pages/upload.py")
            if st.button("Prediction History", use_container_width=True):
                st.switch_page("pages/history.py")
            if st.button("Logout", use_container_width=True):
                for key in ['authenticated', 'user', 'user_type', 'user_name']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
    else:
        st.info("Please login to use the system")
        if st.button("Login", use_container_width=True):
            st.switch_page("pages/login.py")
        if st.button("Sign Up", use_container_width=True):
            st.switch_page("pages/signup.py")

# Main content area
if is_authenticated and user_type != 'admin':
    # User dashboard
    st.markdown("## Personal Dashboard")
    
    # Get user statistics
    try:
        user_predictions = get_user_predictions(st.session_state['user'])
        total_predictions = len(user_predictions)
        
        if total_predictions > 0:
            # Statistics for different categories
            categories = [pred[2] for pred in user_predictions]
            category_counts = pd.Series(categories).value_counts()
            
            # Recent predictions (last 7 days)
            recent_predictions = [
                pred for pred in user_predictions 
                if isinstance(pred[5], datetime) and pred[5] > datetime.now() - timedelta(days=7)
            ]
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Predictions", total_predictions)
            
            with col2:
                st.metric("This Week", len(recent_predictions))
            
            with col3:
                most_common = category_counts.index[0] if len(category_counts) > 0 else "None"
                st.metric("Most Common Category", most_common)
            
            with col4:
                avg_confidence = sum([pred[3] for pred in user_predictions]) / len(user_predictions)
                st.metric("Average Confidence", f"{avg_confidence:.1f}%")
            
            # Classification statistics charts
            if len(category_counts) > 0:
                st.markdown("### Classification Statistics")
                col1, col2 = st.columns(2)
                
                with col1:
                    fig_pie = px.pie(
                        values=category_counts.values, 
                        names=category_counts.index,
                        title="Waste Category Distribution"
                    )
                    st.plotly_chart(fig_pie, use_container_width=True)
                
                with col2:
                    fig_bar = px.bar(
                        x=category_counts.index, 
                        y=category_counts.values,
                        title="Predictions by Category",
                        color=category_counts.values,
                        color_continuous_scale="viridis"
                    )
                    fig_bar.update_layout(showlegend=False)
                    st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No prediction records yet. Start using the system now!")
            
    except Exception as e:
        st.error(f"Error retrieving statistics: {e}")
    
    # Quick actions
    st.markdown("### Quick Actions")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Classify Now**")
        st.markdown("Upload waste images to get AI classification results and recycling advice")
        if st.button("Start Upload", key="quick_upload", use_container_width=True):
            st.switch_page("pages/upload.py")
    
    with col2:
        st.markdown("**View History**")
        st.markdown("Browse your prediction history and statistical analysis")
        if st.button("View History", key="quick_history", use_container_width=True):
            st.switch_page("pages/history.py")

elif is_authenticated and user_type == 'admin':
    # Admin simplified view
    st.markdown("## Administrator Console")
    st.info("Welcome back, Administrator! Click the sidebar to access management functions.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Enter Admin Panel", type="primary", use_container_width=True):
            st.switch_page("pages/admin.py")
    with col2:
        if st.button("User Management", use_container_width=True):
            st.switch_page("pages/admin.py")

else:
    # System introduction for non-logged users
    st.markdown("## System Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### AI Smart Recognition")
        st.markdown("Uses advanced deep learning models to accurately identify 10 types of waste with over 95% accuracy")
    
    with col2:
        st.markdown("### Recycling Guidance")
        st.markdown("Provides detailed waste classification suggestions and recycling methods to help you properly handle various types of waste")
    
    with col3:
        st.markdown("### Data Analysis")
        st.markdown("Records your classification history and provides personal environmental data analysis and statistical charts")
    
    st.markdown("---")
    
    # System introduction
    st.markdown("""
    ## About the System
    
    This system is an AI-based waste classification recognition platform designed to help users correctly classify waste and promote environmental awareness.
    
    ### Supported Waste Types
    """)
    
    # Waste type display
    categories = {
        "Battery": "Various batteries require special recycling treatment",
        "Biological": "Food waste, organic waste, etc.", 
        "Cardboard": "Packaging cardboard, delivery boxes, etc.",
        "Clothes": "Old clothes, textiles, etc.",
        "Glass": "Glass bottles, glassware, etc.",
        "Metal": "Metal products, cans, etc.",
        "Paper": "Waste paper, newspapers, books, etc.",
        "Plastic": "Plastic bottles, plastic bags, etc.",
        "Shoes": "Various shoes and shoe materials",
        "Trash": "Non-recyclable mixed waste"
    }
    
    cols = st.columns(2)
    for i, (category, description) in enumerate(categories.items()):
        with cols[i % 2]:
            st.markdown(f"**{category}**: {description}")
    
    st.markdown("---")
    
    # User guide
    st.markdown("""
    ## User Guide
    
    1. **Register Account** - Create your personal account
    2. **Upload Image** - Take or upload waste images
    3. **Get Results** - AI automatically identifies and provides classification suggestions
    4. **View History** - Review your classification records and statistics
    
    ### Usage Tips
    - Ensure images are clear with waste items in the center
    - Good lighting conditions help improve recognition accuracy
    - Single item recognition works better than mixed waste
    """)
    
    # Call to action
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Start Your Environmental Journey Now!")
        col_login, col_signup = st.columns(2)
        with col_login:
            if st.button("Login Now", type="primary", use_container_width=True):
                st.switch_page("pages/login.py")
        with col_signup:
            if st.button("Free Registration", use_container_width=True):
                st.switch_page("pages/signup.py")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>AI Garbage Classification System | Making Environmental Protection Smarter | © 2024</p>
    <p><small>Based on Deep Learning Technology • Supports 10 Waste Categories • 90%+ Accuracy</small></p>
</div>
""", unsafe_allow_html=True)