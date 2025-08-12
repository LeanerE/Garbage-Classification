import streamlit as st
import pandas as pd
from pymongo import MongoClient
from datetime import datetime, timedelta
import plotly.express as px
from utils.db_utils import get_all_user_predictions
from config import MONGO_URI, MONGO_DB_NAME

# Page configuration
st.set_page_config(
  page_title="Admin Panel - AI Garbage Classification",
  page_icon="🔧",
  layout="wide",
  initial_sidebar_state="expanded"
)

st.title("Admin Panel")

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Check if it is admin
if not st.session_state.get('authenticated') or st.session_state.get('user_type') != 'admin':
  st.error("Access denied. You must be logged in as an administrator to access this page.")
  st.markdown("Please login with admin credentials to access the admin panel.")
  col1, col2 = st.columns(2)
  with col1:
      if st.button("Go to Login", type="primary"):
          st.switch_page("pages/login.py")
  with col2:
      if st.button("Go Home"):
          st.switch_page("app.py")
  st.stop()

# Show admin information    
admin_name = 'Eric'
st.success(f"Welcome, Admin {admin_name}!")
st.markdown("---")

# Sidebar navigation
with st.sidebar:
  st.markdown("## Admin Functions")
  page = st.selectbox(
      "Choose Function",
      ["Dashboard", "User Management"],
      index=0
  )
  
  st.markdown("---")
  st.markdown("### Quick Actions")
  if st.button("Go Home", use_container_width=True):
      st.switch_page("app.py")
  if st.button("Refresh Data", use_container_width=True):
      st.rerun()
  
  st.markdown("---")
  if st.button("Logout", use_container_width=True):
      for key in ['authenticated', 'user', 'user_type', 'user_name']:
          if key in st.session_state:
              del st.session_state[key]
      st.switch_page("pages/login.py")

if page == "Dashboard":
  st.header("System Dashboard")
  
  try:
      # Get database statistics
      total_users = db.users.count_documents({})
      verified_users = db.users.count_documents({"is_verified": 1})
      unverified_users = db.users.count_documents({"is_verified": 0})
      total_predictions = db.predictions.count_documents({})
      
      # Get recent activity (last 7 days)
      week_ago = datetime.now() - timedelta(days=7)
      recent_predictions = db.predictions.count_documents({"created_at": {"$gte": week_ago}})
      recent_users = db.users.count_documents({"created_at": {"$gte": week_ago}})
      
      # Main metrics
      col1, col2, col3, col4 = st.columns(4)
      with col1:
          st.metric("Total Users", total_users, delta=f"+{recent_users} this week")
      with col2:
          st.metric("Verified Users", verified_users, delta=f"{(verified_users/total_users*100):.1f}%" if total_users > 0 else "0%")
      with col3:
          st.metric("Unverified Users", unverified_users)
      with col4:
          st.metric("Total Predictions", total_predictions, delta=f"+{recent_predictions} this week")
      
      st.markdown("---")
      
      # Charts section
      col1, col2 = st.columns(2)
      
      with col1:
          st.subheader("User Verification Status")
          if total_users > 0:
              fig_pie = px.pie(
                  values=[verified_users, unverified_users],
                  names=['Verified', 'Unverified'],
                  color_discrete_map={'Verified': '#28a745', 'Unverified': '#ffc107'},
                  title="User Verification Distribution"
              )
              fig_pie.update_traces(textposition='inside', textinfo='percent+label')
              st.plotly_chart(fig_pie, use_container_width=True)
          else:
              st.info("No user data available")
      
      with col2:
          st.subheader("Prediction Categories")
          try:
              # Get prediction category distribution
              pipeline = [
                  {"$group": {"_id": "$predicted_class", "count": {"$sum": 1}}},
                  {"$sort": {"count": -1}}
              ]
              category_data = list(db.predictions.aggregate(pipeline))
              
              if category_data:
                  categories = [item['_id'].title() for item in category_data]
                  counts = [item['count'] for item in category_data]
                  
                  fig_bar = px.bar(
                      x=categories,
                      y=counts,
                      color=counts,
                      color_continuous_scale="viridis",
                      title="Predictions by Category"
                  )
                  fig_bar.update_layout(
                      xaxis_title="Category",
                      yaxis_title="Count",
                      showlegend=False
                  )
                  st.plotly_chart(fig_bar, use_container_width=True)
              else:
                  st.info("No prediction data available")
          except Exception as e:
              st.error(f"Error loading prediction data: {e}")
  
  except Exception as e:
      st.error(f"Error accessing database: {e}")

elif page == "User Management":
  st.header("User Management")
  
  try:
      # Search and filter options
      col1, col2, col3 = st.columns([2, 1, 1])
      with col1:
          search_term = st.text_input("Search users", placeholder="Enter name or email...")
      with col2:
          filter_status = st.selectbox("Filter by status", ["All", "Verified", "Unverified"])
      with col3:
          sort_by = st.selectbox("Sort by", ["Registration Date", "Name", "Email"])
      
      # Build query
      query = {}
      if search_term:
          query["$or"] = [
              {"name": {"$regex": search_term, "$options": "i"}},
              {"email": {"$regex": search_term, "$options": "i"}}
          ]
      
      if filter_status == "Verified":
          query["is_verified"] = 1
      elif filter_status == "Unverified":
          query["is_verified"] = 0
      
      # Get users with sorting
      sort_field = "created_at" if sort_by == "Registration Date" else sort_by.lower()
      users = list(db.users.find(query).sort(sort_field, -1))
      
      if users:
          st.success(f"Found {len(users)} users")
          
          st.markdown("---")
          st.subheader("User List")
          
          # Pagination
          items_per_page = 10
          total_pages = (len(users) + items_per_page - 1) // items_per_page
          
          if 'admin_user_page' not in st.session_state:
              st.session_state['admin_user_page'] = 1
          
          if total_pages > 1:
              col1, col2, col3 = st.columns([1, 2, 1])
              with col1:
                  if st.button("Previous", disabled=st.session_state['admin_user_page'] <= 1):
                      st.session_state['admin_user_page'] -= 1
                      st.rerun()
              with col2:
                  st.write(f"Page {st.session_state['admin_user_page']} of {total_pages}")
              with col3:
                  if st.button("Next", disabled=st.session_state['admin_user_page'] >= total_pages):
                      st.session_state['admin_user_page'] += 1
                      st.rerun()
          
          # Display users for current page
          start_idx = (st.session_state['admin_user_page'] - 1) * items_per_page
          end_idx = min(start_idx + items_per_page, len(users))
          current_users = users[start_idx:end_idx]
          
          for i, user in enumerate(current_users, start=start_idx):
              name = user.get("name") if user.get("name") else user.get("email")
              status_text = "Verified" if user.get("is_verified") else "Unverified"
              status_color = "green" if user.get("is_verified") else "orange"
              user_email = user.get("email")
              
              # Get user's prediction statistics
              user_predictions = list(db.predictions.find({"user_email": user_email}))
              pred_count = len(user_predictions)
              
              # Calculate prediction statistics
              if user_predictions:
                  # Get most predicted class
                  class_counts = {}
                  total_confidence = 0
                  for pred in user_predictions:
                      predicted_class = pred.get("predicted_class", "Unknown")
                      class_counts[predicted_class] = class_counts.get(predicted_class, 0) + 1
                      total_confidence += pred.get("confidence", 0)
                  
                  most_predicted = max(class_counts, key=class_counts.get) if class_counts else "None"
                  avg_confidence = (total_confidence / pred_count * 100) if pred_count > 0 else 0
                  last_prediction = max(pred.get("created_at", datetime.min) for pred in user_predictions)
              else:
                  most_predicted = "None"
                  avg_confidence = 0
                  last_prediction = "Never"
              
              with st.expander(f"{name} - {user_email} - :{status_color}[{status_text}] - {pred_count} predictions"):
                  col1, col2 = st.columns([3, 1])
                  
                  with col1:
                      st.markdown("### User Information")
                      st.markdown(f"**Name:** {name}")
                      st.markdown(f"**Email:** {user_email}")
                      st.markdown(f"**Status:** :{status_color}[{status_text}]")
                      created_at = user.get("created_at").strftime("%Y-%m-%d %H:%M:%S") if user.get("created_at") else "Unknown"
                      st.markdown(f"**Registered:** {created_at}")
                      
                      st.markdown("### Prediction Summary")
                      st.markdown(f"**Total Predictions:** {pred_count}")
                      if pred_count > 0:
                          st.markdown(f"**Most Predicted Class:** {most_predicted.title()}")
                          st.markdown(f"**Average Confidence:** {avg_confidence:.1f}%")
                          st.markdown(f"**Last Prediction:** {last_prediction}")
                          
                          # Show class distribution if user has predictions
                          if len(class_counts) > 1:
                              st.markdown("**Class Distribution:**")
                              for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
                                  percentage = (count / pred_count) * 100
                                  st.markdown(f"• {class_name.title()}: {count} ({percentage:.1f}%)")
                      else:
                          st.markdown("*No predictions made yet*")
                  
                  with col2:
                      st.markdown("### Actions")
                      
                      if not user.get("is_verified"):
                          if st.button(f"Verify User", key=f"verify_{i}"):
                              db.users.update_one(
                                  {"email": user_email},
                                  {"$set": {"is_verified": 1}}
                              )
                              st.success(f"User {name} verified!")
                              st.rerun()
                      else:
                          st.info("User is verified")
                      
                      st.markdown("---")
                      
                      if st.button(f"Delete User", key=f"delete_{i}", type="secondary"):
                          # Simple confirmation using session state
                          confirm_key = f"confirm_delete_{i}"
                          if confirm_key not in st.session_state:
                              st.session_state[confirm_key] = False
                          
                          if not st.session_state[confirm_key]:
                              st.warning("Click again to confirm deletion")
                              st.session_state[confirm_key] = True
                          else:
                              db.users.delete_one({"email": user_email})
                              db.predictions.delete_many({"user_email": user_email})
                              st.success(f"User {name} deleted!")
                              del st.session_state[confirm_key]
                              st.rerun()
      else:
          st.info("No users found matching your criteria.")
  
  except Exception as e:
      st.error(f"Error accessing database: {e}")

# Footer
st.markdown("---")
st.markdown("*Admin Panel - AI Garbage Classification System*")