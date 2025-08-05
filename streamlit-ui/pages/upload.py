import streamlit as st
import time
import os
from datetime import datetime
from utils.prediction_utils import GarbageClassifier
from utils.db_utils import save_prediction
import numpy as np

st.title("Upload Image for Classification")

# Check authentication
if not st.session_state.get('authenticated'):
    st.warning("You must log in first.")
    st.markdown("Please go to the Login page to authenticate.")
    st.page_link("pages/login.py", label="Login")
    st.stop()

# Check if user is admin (admin should not access user upload page)
if st.session_state.get('user_type') == 'admin':
    st.error("Access denied. This page is for regular users only.")
    st.info("Admin users should use the Admin Panel for system management.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Admin Panel", type="primary"):
            st.switch_page("pages/admin.py")
    with col2:
        if st.button("Go Home"):
            st.switch_page("app.py")
    st.stop()

# Show user info and logout option
if st.session_state.get('user'):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"Welcome, {st.session_state.get('user_name', st.session_state['user'])}!")
    with col2:
        if st.button("Logout", type="secondary"):
            st.session_state['authenticated'] = False
            st.session_state['user'] = None
            st.success("Logged out successfully!")
            st.switch_page("pages/login.py")

# Initialize classifier (load models once)
@st.cache_resource
def load_classifier():
    return GarbageClassifier()

classifier = load_classifier()

# Main upload functionality
st.markdown("---")
st.subheader("Choose an image to classify")

uploaded_file = st.file_uploader(
    "Select an image file", 
    type=["jpg", "jpeg", "png"],
    help="Supported formats: JPG, JPEG, PNG"
)

if uploaded_file:
    st.markdown("---")
    st.subheader("Preview")
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    
    # Prediction section
    st.markdown("---")
    st.subheader("Analysis Results")
    
    with st.spinner("Analyzing image with AI models..."):
        # Make prediction
        prediction_result = classifier.predict_single(uploaded_file)
        
        if prediction_result:
            predicted_class = prediction_result['predicted_class']
            confidence = prediction_result['confidence']
            top_predictions = prediction_result['top_predictions']
            
            # Save prediction result to database
            if st.session_state.get('authenticated') and st.session_state.get('user'):
                # Generate unique filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_extension = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'jpg'
                image_filename = f"prediction_{timestamp}.{file_extension}"
                
                # Create uploads directory if it doesn't exist
                uploads_dir = "uploads"
                if not os.path.exists(uploads_dir):
                    os.makedirs(uploads_dir)
                
                # Save the image file to disk
                image_path = os.path.join(uploads_dir, image_filename)
                try:
                    with open(image_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                except Exception as e:
                    st.error(f"Failed to save image file: {e}")
                    image_filename = None
                
                # Save to database only if image was saved successfully
                if image_filename:
                    save_success = save_prediction(
                        st.session_state['user'],
                        image_filename,
                        predicted_class,
                        confidence,
                        top_predictions
                    )
                    
                    if save_success:
                        st.success("Prediction saved to your history!")
                    else:
                        st.warning("Failed to save prediction to history.")
                else:
                    st.error("Failed to save image file.")
            
            # Get recycling information
            recycling_info = classifier.get_recycling_info(predicted_class)
            
            # Display main results
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Confidence", f"{confidence:.1%}")
            with col2:
                st.metric("Category", predicted_class.title())
            with col3:
                st.metric("Waste Type", recycling_info['category'])
            
            # Display detailed classification
            st.markdown("**Detailed Classification:**")
            
            # Create a more detailed info box
            info_text = f"""
            - **Primary Category:** {predicted_class.title()}
            - **Waste Classification:** {recycling_info['category']}
            - **Environmental Impact:** {recycling_info['impact']}
            - **Disposal Instructions:** {recycling_info['instructions']}
            """
            st.info(info_text)
            
            # Show top 3 predictions
            st.markdown("**Model Confidence Rankings:**")
            for i, (class_name, prob) in enumerate(top_predictions, 1):
                st.write(f"{i}. **{class_name.title()}**: {prob:.1%}")
            
            # Show recycling tips based on category
            st.markdown("**Recycling Tips:**")
            if recycling_info['category'] == 'Recyclable':
                st.success(f"This {predicted_class} can be recycled! {recycling_info['instructions']}")
            elif recycling_info['category'] == 'Hazardous Waste':
                st.error(f"⚠️ This {predicted_class} is hazardous waste. {recycling_info['instructions']}")
            elif recycling_info['category'] == 'Organic Waste':
                st.warning(f"This {predicted_class} is organic waste. {recycling_info['instructions']}")
            elif recycling_info['category'] == 'Textile Waste':
                st.info(f"This {predicted_class} is textile waste. {recycling_info['instructions']}")
            else:
                st.warning(f"This {predicted_class} should be disposed of as general waste. {recycling_info['instructions']}")
                
        else:
            st.error("Failed to analyze the image. Please try again with a different image.")

else:
    # Show instructions for use
    st.info("""
    **How to use:**
    1. Click 'Browse files' above to select an image
    2. Choose a clear photo of the item you want to classify
    3. Wait for the AI analysis to complete (uses 3 different models)
    4. View the classification results and recycling tips
    """)
    
    # Example photo captions
    st.markdown("**Tips for best results:**")
    st.markdown("""
    - Take photos in good lighting
    - Ensure the item is clearly visible
    - Avoid blurry or dark images
    - Include the entire item in the frame
    - Supported categories: battery, biological, cardboard, clothes, glass, metal, paper, plastic, shoes, trash
    """)
