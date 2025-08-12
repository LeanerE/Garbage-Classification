import base64
import streamlit as st
from datetime import datetime
from utils.prediction_utils import GarbageClassifier
from utils.db_utils import save_prediction

st.title("Upload Image for Classification")

# Authentication check
if not st.session_state.get('authenticated'):
    st.warning("You must log in first.")
    st.page_link("pages/login.py", label="Login")
    st.stop()

# Admin access check
if st.session_state.get('user_type') == 'admin':
    st.error("Access denied. This page is for regular users only.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Admin Panel", type="primary"):
            st.switch_page("pages/admin.py")
    with col2:
        if st.button("Go Home"):
            st.switch_page("app.py")
    st.stop()

# User info and logout
if st.session_state.get('user'):
    col1, col2 = st.columns([3, 1])
    with col1:
        st.success(f"Welcome, {st.session_state.get('user_name', st.session_state['user'])}!")
    with col2:
        if st.button("Logout", type="secondary"):
            st.session_state['authenticated'] = False
            st.session_state['user'] = None
            st.switch_page("pages/login.py")

# Initialize classifier
@st.cache_resource
def load_classifier():
    return GarbageClassifier()

classifier = load_classifier()

# File upload
uploaded_file = st.file_uploader(
    "Select an image file", 
    type=["jpg", "jpeg", "png"],
    help="Supported formats: JPG, JPEG, PNG"
)

if uploaded_file:
    # Show image with fixed size
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(uploaded_file, caption="Uploaded Image", width=400)
    
    # Auto-analyze
    with st.spinner("Analyzing image..."):
        prediction_result = classifier.predict_single(uploaded_file)
        
        if prediction_result:
            predicted_class = prediction_result['predicted_class']
            confidence = prediction_result['confidence']
            top_predictions = prediction_result['top_predictions']
            
            # Save to database
            if st.session_state.get('authenticated') and st.session_state.get('user'):
                try:
                    image_bytes = uploaded_file.getvalue()
                    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    file_extension = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else 'jpg'
                    image_filename = f"prediction_{timestamp}.{file_extension}"
                    
                    save_prediction(
                        st.session_state['user'],
                        image_filename,
                        predicted_class,
                        confidence,
                        top_predictions,
                        image_base64
                    )
                except Exception as e:
                    st.warning(f"Failed to save: {str(e)}")
            
            # Get recycling info
            recycling_info = classifier.get_recycling_info(predicted_class)
            
            # Display results
            st.markdown("---")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Confidence", f"{confidence:.1%}")
            with col2:
                st.metric("Category", predicted_class.title())
            with col3:
                st.metric("Waste Type", recycling_info['category'])
            
            # Recycling guidance
            if recycling_info['category'] == 'Recyclable':
                st.success(f"This {predicted_class} can be recycled. {recycling_info['instructions']}")
            elif recycling_info['category'] == 'Hazardous Waste':
                st.error(f"This {predicted_class} is hazardous waste. {recycling_info['instructions']}")
            elif recycling_info['category'] == 'Organic Waste':
                st.warning(f"This {predicted_class} is organic waste. {recycling_info['instructions']}")
            else:
                st.info(f"This {predicted_class} should be disposed as general waste. {recycling_info['instructions']}")
            
            # Top predictions
            st.markdown("**Top Predictions:**")
            for i, (class_name, prob) in enumerate(top_predictions[:3], 1):
                st.write(f"{i}. {class_name.title()}: {prob:.1%}")
                
        else:
            st.error("Failed to analyze the image. Please try again.")

else:
    st.info("Upload an image to get started. Supported formats: JPG, JPEG, PNG")
