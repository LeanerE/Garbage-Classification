import random
import string
import json
from datetime import datetime
from pymongo import MongoClient
from bson.objectid import ObjectId
from utils.auth_utils import send_verification_email
from config import ADMIN_EMAIL, ADMIN_PASSWORD, MONGO_URI, MONGO_DB_NAME

# MongoDB connection
client = MongoClient(MONGO_URI)
db = client[MONGO_DB_NAME]

# Collections
users_collection = db['users']
predictions_collection = db['predictions']

def generate_code(length=6):
    # Generate a verification code
    return ''.join(random.choices(string.digits, k=length))

def is_admin(email, password):
    # Check if user is admin
    return email.strip().lower() == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD

def register_user(name, email, password, code):
    # Register a new user with email verification
    email = email.strip().lower()
    try:
        # Check if user already exists
        if users_collection.find_one({"email": email}):
            return False
        
        # Insert new user
        user = {
            "name": name,
            "email": email,
            "password": password,
            "code": code,
            "is_verified": 0,
            "created_at": datetime.now()
        }
        users_collection.insert_one(user)
        return True
    except Exception as e:
        print("Registration error:", e)
        return False

def send_code_and_store(email):
    # Send verification code to email and store it
    code = generate_code()
    if send_verification_email(email, code):
        update_verification_code(email, code)
        return True
    return False

def update_verification_code(email, code):
    # Update verification code in database
    email = email.strip().lower()
    
    # Create new user record if doesn't exist
    user = users_collection.find_one({"email": email})
    if not user:
        users_collection.insert_one({
            "email": email,
            "code": code,
            "is_verified": 0
        })
    else:
        users_collection.update_one(
            {"email": email},
            {"$set": {"code": code, "is_verified": 0}}
        )

def verify_user(email, input_code):
    # Verify user's email with input code
    email = email.strip().lower()
    input_code = input_code.strip()

    user = users_collection.find_one({"email": email})
    
    print(f"Verify attempt for email: {email}, input code: {input_code}")
    print("Query result:", user)

    if user and user.get("code") == input_code:
        users_collection.update_one(
            {"email": email},
            {"$set": {"is_verified": 1}}
        )
        return True
    return False

def email_exists(email):
    # Check if email is already registered
    email = email.strip().lower()
    return users_collection.find_one({"email": email}) is not None

def login_user(email, password):
    # Login user with email and password
    email = email.strip().lower()
    # Check admin first
    if is_admin(email, password):
        return {"role": "admin"}
    
    # Then check regular user
    user = users_collection.find_one({"email": email, "password": password})
    if user:
        if user.get("is_verified") == 1:
            return {"role": "user", "name": user.get("name"), "email": email}
        else:
            return {"role": "unverified"}
    return {"role": "invalid"}

def save_prediction(user_email, image_filename, predicted_class, confidence, top_predictions, image_data):
    """Save prediction with image data to MongoDB"""
    try:
        # Get user information
        user = db.users.find_one({"email": user_email})
        user_name = user.get('name') if user else None

        # Create prediction document
        prediction = {
            "user_email": user_email,
            "user_name": user_name,
            "image_filename": image_filename,
            "image_data": image_data,
            "predicted_class": predicted_class,
            "confidence": confidence,
            "top_predictions": json.dumps(top_predictions),
            "created_at": datetime.now()
        }
        
        # Insert into predictions collection
        result = db.predictions.insert_one(prediction)
        return result.inserted_id is not None
        
    except Exception as e:
        print(f"Error saving prediction: {str(e)}")
        return False

def get_user_predictions(user_email):
    """Get predictions for a specific user from MongoDB"""
    try:
        predictions = list(db.predictions.find(
            {"user_email": user_email}
        ).sort("created_at", -1))
        
        # Convert MongoDB documents to the expected format
        formatted_predictions = []
        for pred in predictions:
            formatted_predictions.append([
                str(pred['_id']),          # prediction ID (0)
                pred['image_filename'],     # image filename (1)
                pred['predicted_class'],    # predicted class (2)
                pred['confidence'],         # confidence (3)
                pred['top_predictions'],    # top predictions (4)
                pred['created_at'],         # creation date (5)
                pred.get('user_name', ''),  # user name (6)
                pred.get('image_data', '')  # image data (7)
            ])
        
        return formatted_predictions
        
    except Exception as e:
        print(f"Error getting predictions: {e}")
        return []

def delete_prediction(prediction_id, user_email):
    # Delete a prediction from MongoDB
    try:
        # Debug information
        print(f"Attempting to delete prediction: {prediction_id}")
        print(f"User email: {user_email}")
        
        # Convert string ID to ObjectId
        object_id = ObjectId(prediction_id)
        print(f"Converted ObjectId: {object_id}")
        
        # Find the prediction first to verify it exists
        prediction = db.predictions.find_one({
            "_id": object_id,
            "user_email": user_email
        })
        
        if prediction:
            print("Found prediction to delete")
            result = db.predictions.delete_one({
                "_id": object_id,
                "user_email": user_email
            })
            print(f"Delete result: {result.deleted_count}")
            return result.deleted_count > 0
        else:
            print("Prediction not found")
            return False
        
    except Exception as e:
        print(f"Error deleting prediction: {e}")
        return False

def get_all_user_predictions():
    # Get all predictions for admin view
    try:
        predictions = list(db.predictions.find().sort("created_at", -1))
        
        # Convert MongoDB documents to the expected format
        formatted_predictions = []
        for pred in predictions:
            formatted_predictions.append((
                str(pred['_id']),  # prediction ID
                pred['image_filename'],
                pred['predicted_class'],
                pred['confidence'],
                pred['top_predictions'],
                pred['created_at'],
                pred['user_name'],
                pred['user_email']
            ))
        
        return formatted_predictions
        
    except Exception as e:
        print(f"Error getting all predictions: {e}")
        return []