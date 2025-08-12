import base64
import io
import streamlit as st
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from utils.db_utils import get_user_predictions, delete_prediction

st.title("Prediction History")

# Check authentication
if not st.session_state.get('authenticated'):
    st.warning("You must log in first.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Go to Login Page", type="primary"):
            st.switch_page("pages/login.py")
    with col2:
        if st.button("Go to Sign Up"):
            st.switch_page("pages/signup.py")
    st.stop()

# Check if user is admin (admin should not access user prediction history)
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

# Show user info
user_name = st.session_state.get('user_name', st.session_state.get('user'))
st.success(f"Welcome, {user_name}!")

# Get user's prediction history
predictions = get_user_predictions(st.session_state['user'])

if not predictions:
    st.info("No prediction history found. Start by uploading an image!")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Upload New Image", type="primary"):
            st.switch_page("pages/upload.py")
    with col2:
        if st.button("Go Home"):
            st.switch_page("app.py")
    st.stop()

# Display prediction history
st.subheader("Your Recent Predictions")

# Add filter options
col1, col2 = st.columns([2, 1])
with col1:
    # Get unique categories for dropdown
    unique_categories = sorted(list(set([pred[2] for pred in predictions])))
    filter_category = st.selectbox("Filter by waste category", ["All Categories"] + unique_categories)
with col2:
    sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Confidence (High)", "Confidence (Low)"])

# Filter and sort predictions
filtered_predictions = predictions
if filter_category != "All Categories":
    filtered_predictions = [p for p in predictions if p[2] == filter_category]

# Sort predictions
if sort_by == "Date (Oldest)":
    filtered_predictions = sorted(filtered_predictions, key=lambda x: x[5])
elif sort_by == "Confidence (High)":
    filtered_predictions = sorted(filtered_predictions, key=lambda x: x[3], reverse=True)
elif sort_by == "Confidence (Low)":
    filtered_predictions = sorted(filtered_predictions, key=lambda x: x[3])

# Display predictions
# Limit to show only 4 predictions at a time
max_display = 4
total_filtered = len(filtered_predictions)

# Add pagination controls
if total_filtered > max_display:
    # Initialize current page
    if 'current_page' not in st.session_state:
        st.session_state['current_page'] = 1
    
    current_page = st.session_state['current_page']
    total_pages = (total_filtered + max_display - 1) // max_display
    
    # Simple pagination with buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("Previous", disabled=current_page <= 1):
            st.session_state['current_page'] = current_page - 1
            st.rerun()
    with col2:
        st.write(f"Page {current_page} of {total_pages}")
    with col3:
        if st.button("Next", disabled=current_page >= total_pages):
            st.session_state['current_page'] = current_page + 1
            st.rerun()

# Get the predictions to display
current_page = st.session_state.get('current_page', 1)
start_idx = (current_page - 1) * max_display
end_idx = min(start_idx + max_display, total_filtered)
predictions_to_show = filtered_predictions[start_idx:end_idx]

for pred in predictions_to_show:
    try:
        pred_id = pred[0]
        image_filename = pred[1]
        predicted_class = pred[2]
        confidence = pred[3]
        top_predictions_str = pred[4]
        created_at = pred[5]
        user_name = pred[6]
        image_data = pred[7] if len(pred) > 7 else None

        with st.expander(f"{predicted_class.title()} - {confidence:.1%} - {created_at}"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                try:
                    if image_data:
                        image_bytes = base64.b64decode(image_data)
                        st.image(
                            io.BytesIO(image_bytes),
                            caption=f"Prediction: {predicted_class}",
                            use_container_width=True
                        )
                    else:
                        st.error("Image not available")
                except Exception as e:
                    st.error(f"Error displaying image: {str(e)}")
            
            with col2:
                st.write(f"**Predicted Class:** {predicted_class.title()}")
                st.write(f"**Confidence:** {confidence:.1%}")
                st.write(f"**Date:** {created_at}")
                
                try:
                    top_predictions = json.loads(top_predictions_str)
                    st.write("**Top Predictions:**")
                    for i, (class_name, prob) in enumerate(top_predictions[:3], 1):
                        st.write(f"{i}. {class_name.title()}: {prob:.1%}")
                except:
                    pass
            
            with col3:
                if st.button("Delete", key=f"delete_{pred_id}"):
                    if delete_prediction(pred_id, st.session_state['user']):
                        st.success("Deleted successfully!")
                        st.rerun()
                    else:
                        st.error("Failed to delete")

    except Exception as e:
        st.error(f"Error processing prediction: {str(e)}")
        continue

# Show statistics
st.markdown("---")
st.subheader("Statistics")

total_predictions = len(predictions)
if total_predictions > 0:
    # Calculate statistics
    class_counts = {}
    total_confidence = 0
    success_count = 0  # Count predictions with confidence > 50%
    unique_dates = set()
    
    for pred in predictions:
        predicted_class = pred[2]
        confidence = pred[3]
        created_at = pred[5]
        
        class_counts[predicted_class] = class_counts.get(predicted_class, 0) + 1
        total_confidence += confidence
        
        # Count successful classifications (confidence > 50%)
        if confidence > 0.5:
            success_count += 1
        
        # Extract date from created_at for active days calculation
        try:
            date_only = created_at.split()[0]  # Get date part only
            unique_dates.add(date_only)
        except:
            pass
    
    avg_confidence = total_confidence / total_predictions
    success_rate = (success_count / total_predictions) * 100 if total_predictions > 0 else 0
    active_days = len(unique_dates)
    
    # Display stats in the new format
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Uploads", total_predictions, help="Total number of images uploaded for classification")
    with col2:
        st.metric("Classification Success Rate", f"{success_rate:.1f}%", help="Percentage of successful classifications")
    with col3:
        st.metric("Active Days", active_days, help="Total number of days with at least one upload")
    
    # Waste Category Breakdown Chart
    st.markdown("---")
    st.subheader("Waste Category Breakdown")
    
    # Prepare data for the chart
    category_counts = {}
    for pred in predictions:
        predicted_class = pred[2]
        category_counts[predicted_class] = category_counts.get(predicted_class, 0) + 1
    
    if category_counts:
        # Create pie chart
        fig = px.pie(
            values=list(category_counts.values()),
            names=list(category_counts.keys()),
            title="Distribution of Waste Categories",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for chart display.")

# Navigation
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    if st.button("Upload New Image", type="primary"):
        st.switch_page("pages/upload.py")
with col2:
    if st.button("Go Home"):
        st.switch_page("app.py") 