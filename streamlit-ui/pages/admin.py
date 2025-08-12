import streamlit as st
import sqlite3
import json
from datetime import datetime
from utils.db_utils import get_all_user_predictions, get_user_predictions_by_email

st.title("Admin Panel")

# Check if it is admin
if not st.session_state.get('authenticated') or st.session_state.get('user_type') != 'admin':
    st.error("Access denied. You must be logged in as an administrator to access this page.")
    st.markdown("Please login with admin credentials to access the admin panel.")
    st.page_link("pages/login.py", label="Login")
    st.stop()

# Show admin information
st.success(f"Welcome, Admin! ({st.session_state.get('user')})")

# Sidebar navigation
st.sidebar.title("Admin Functions")
page = st.sidebar.selectbox(
    "Choose Function",
    ["Dashboard", "User Management", "User Predictions"]
)

if page == "Dashboard":
    st.header("Admin Dashboard")
    
    # Getting database statistics
    conn = sqlite3.connect("database/garbage.db")
    c = conn.cursor()
    
    try:
        # 
        c.execute("SELECT COUNT(*) FROM users")
        total_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE is_verified = 1")
        verified_users = c.fetchone()[0]
        
        c.execute("SELECT COUNT(*) FROM users WHERE is_verified = 0")
        unverified_users = c.fetchone()[0]
        
        # Get total predictions count
        c.execute("SELECT COUNT(*) FROM predictions")
        total_predictions = c.fetchone()[0]
        
        # User statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Verified Users", verified_users)
        with col3:
            st.metric("Unverified Users", unverified_users)
        with col4:
            st.metric("Total Predictions", total_predictions)
        
        # Recently registered users
        st.subheader("Recent Registrations")
        c.execute("SELECT name, email, created_at, is_verified FROM users ORDER BY created_at DESC LIMIT 10")
        recent_users = c.fetchall()
        
        if recent_users:
            for user in recent_users:
                status = "Verified" if user[3] else "Unverified"
                created_at = user[2] if user[2] else "Unknown"
                name = user[0] if user[0] else user[1]
                st.write(f"**{name}** ({user[1]}) - {created_at} - {status}")
        else:
            st.info("No users found.")
    
    except Exception as e:
        st.error(f"Error accessing database: {e}")
    
    finally:
        conn.close()

elif page == "User Management":
    st.header("User Management")
    
    conn = sqlite3.connect("database/garbage.db")
    c = conn.cursor()
    
    try:
        # Get all users
        c.execute("SELECT name, email, is_verified, created_at FROM users ORDER BY created_at DESC")
        users = c.fetchall()
        
        if users:
            st.subheader("All Users")
            
            for i, user in enumerate(users):
                name = user[0] if user[0] else user[1]
                with st.expander(f"User: {name}"):
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.write(f"**Name:** {name}")
                        st.write(f"**Email:** {user[1]}")
                        st.write(f"**Status:** {'Verified' if user[2] else 'Unverified'}")
                        created_at = user[3] if user[3] else "Unknown"
                        st.write(f"**Registered:** {created_at}")
                    
                    with col2:
                        if st.button(f"Delete User", key=f"delete_{i}"):
                            c.execute("DELETE FROM users WHERE email = ?", (user[1],))
                            conn.commit()
                            st.success(f"User {name} deleted!")
                            st.rerun()
                        
                        if not user[2]:  # If user is not authenticated
                            if st.button(f"Verify User", key=f"verify_{i}"):
                                c.execute("UPDATE users SET is_verified = 1 WHERE email = ?", (user[1],))
                                conn.commit()
                                st.success(f"User {name} verified!")
                                st.rerun()
        else:
            st.info("No users found.")

        # Export data
        st.subheader("Export Data")
        if st.button("Export Users to CSV"):
            try:
                import pandas as pd
                c.execute("SELECT name, email, is_verified, created_at FROM users")
                data = c.fetchall()
                df = pd.DataFrame(data, columns=['Name', 'Email', 'Verified', 'Created At'])
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            except ImportError:
                st.error("pandas is required for CSV export. Install with: pip install pandas")
    
    except Exception as e:
        st.error(f"Error accessing database: {e}")
    
    finally:
        conn.close()

elif page == "User Predictions":
    st.header("User Predictions History")
    
    # Get all predictions
    all_predictions = get_all_user_predictions()
    
    if not all_predictions:
        st.info("No predictions found in the system.")
        st.stop()
    
    # Calculate user statistics first
    user_stats = {}
    for pred in all_predictions:
        user_email = pred[7]  # user_email
        user_name = pred[6]   # user_name
        display_name = user_name if user_name else user_email
        
        if user_email not in user_stats:
            user_stats[user_email] = {
                'name': display_name,
                'email': user_email,
                'total_predictions': 0,
                'last_activity': None,
                'class_counts': {},
                'avg_confidence': 0,
                'total_confidence': 0
            }
        
        user_stats[user_email]['total_predictions'] += 1
        user_stats[user_email]['last_activity'] = pred[5]  # created_at
        
        # Count classes
        predicted_class = pred[2]
        user_stats[user_email]['class_counts'][predicted_class] = user_stats[user_email]['class_counts'].get(predicted_class, 0) + 1
        
        # Calculate confidence
        confidence = pred[3]
        user_stats[user_email]['total_confidence'] += confidence
    
    # Calculate average confidence for each user
    for user_email in user_stats:
        total_preds = user_stats[user_email]['total_predictions']
        total_conf = user_stats[user_email]['total_confidence']
        user_stats[user_email]['avg_confidence'] = total_conf / total_preds if total_preds > 0 else 0
    
    # Display user statistics
    st.subheader("User Activity Summary")
    
    # Search and filter options
    col1, col2 = st.columns([2, 1])
    with col1:
        search_user = st.text_input("Search by user email or name", placeholder="Enter user email or name...")
    with col2:
        sort_by = st.selectbox("Sort by", ["Total Predictions", "Last Activity", "Average Confidence"])
    
    # Filter users
    filtered_users = list(user_stats.values())
    if search_user:
        filtered_users = [u for u in filtered_users if search_user.lower() in u['email'].lower() or search_user.lower() in u['name'].lower()]
    
    # Sort users
    if sort_by == "Total Predictions":
        filtered_users = sorted(filtered_users, key=lambda x: x['total_predictions'], reverse=True)
    elif sort_by == "Last Activity":
        filtered_users = sorted(filtered_users, key=lambda x: x['last_activity'], reverse=True)
    elif sort_by == "Average Confidence":
        filtered_users = sorted(filtered_users, key=lambda x: x['avg_confidence'], reverse=True)
    
    # Display user summary
    st.write(f"**Found {len(filtered_users)} users with prediction activity**")
    
    for i, user in enumerate(filtered_users):
        with st.expander(f"{user['name']} - {user['total_predictions']} predictions - Last: {user['last_activity']}"):
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.write(f"**User:** {user['name']}")
                st.write(f"**Email:** {user['email']}")
                st.write(f"**Total Predictions:** {user['total_predictions']}")
                st.write(f"**Average Confidence:** {user['avg_confidence']:.1%}")
            
            with col2:
                st.write(f"**Last Activity:** {user['last_activity']}")
                st.write("**Most Predicted Classes:**")
                sorted_classes = sorted(user['class_counts'].items(), key=lambda x: x[1], reverse=True)
                for class_name, count in sorted_classes[:3]:
                    percentage = (count / user['total_predictions']) * 100
                    st.write(f"• {class_name.title()}: {count} ({percentage:.1f}%)")
            
            with col3:
                if st.button(f"View Details", key=f"view_details_{i}"):
                    st.session_state['view_user_email'] = user['email']
                    st.rerun()
    
    # Show specific user detailed history if requested
    if st.session_state.get('view_user_email'):
        st.markdown("---")
        st.subheader(f"Detailed History for {st.session_state['view_user_email']}")
        
        user_predictions = get_user_predictions_by_email(st.session_state['view_user_email'])
        
        if user_predictions:
            # Show user summary
            user_email = st.session_state['view_user_email']
            user_info = user_stats.get(user_email, {})
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Predictions", user_info.get('total_predictions', 0))
            with col2:
                st.metric("Average Confidence", f"{user_info.get('avg_confidence', 0):.1%}")
            with col3:
                most_common = max(user_info.get('class_counts', {}).items(), key=lambda x: x[1])[0] if user_info.get('class_counts') else "None"
                st.metric("Most Predicted", most_common.title())
            
            # Show detailed predictions
            st.write("**Recent Predictions:**")
            for pred in user_predictions[:10]:  # Show last 10 predictions
                pred_id, image_filename, predicted_class, confidence, top_predictions_json, created_at, user_name, user_email = pred
                
                try:
                    top_predictions = json.loads(top_predictions_json)
                except:
                    top_predictions = []
                
                with st.expander(f"{predicted_class.title()} - {confidence:.1%} - {created_at}"):
                    st.write(f"**Image:** {image_filename}")
                    st.write(f"**Confidence:** {confidence:.1%}")
                    if top_predictions:
                        st.write("**Top Predictions:**")
                        for j, (class_name, prob) in enumerate(top_predictions[:3], 1):
                            st.write(f"  {j}. {class_name.title()}: {prob:.1%}")
        
        if st.button("Back to User Summary"):
            st.session_state['view_user_email'] = None
            st.rerun()

# logout function
st.sidebar.markdown("---")
if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.session_state['user'] = None
    st.session_state['user_type'] = None
    st.success("Logged out successfully!")
    st.switch_page("pages/login.py") 