import random
import sqlite3
import string
import json
from utils.auth_utils import send_verification_email
from utils.sql_utils import execute_sql_file
from config import ADMIN_EMAIL, ADMIN_PASSWORD

DB_PATH = "database/garbage.db"
SCHEMA_PATH = "schema.sql"

def init_db_schema_if_needed():
    execute_sql_file(DB_PATH, SCHEMA_PATH)

# Generate a 6-digit numeric code
def generate_code(length=6):
    return ''.join(random.choices(string.digits, k=length))

# Check if user is admin
def is_admin(email, password):
    return email.strip().lower() == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD

# Register user with email verification
def register_user(name, email, password, code):
    email = email.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # Check if user already exists
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone() is not None:
            return False
        # Insert new user
        c.execute("INSERT INTO users (name, email, password, code, is_verified) VALUES (?, ?, ?, ?, 0)", 
                 (name, email, password, code))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("Registration error:", e)
        return False
    finally:
        conn.close()

# Send code to email and store it in the database
def send_code_and_store(email):
    code = generate_code()
    if send_verification_email(email, code):
        update_verification_code(email, code)
        return True
    return False

# Save verification code into database
def update_verification_code(email, code):
    email = email.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # If user doesn't exist yet, create a new record
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    if c.fetchone() is None:
        c.execute("INSERT INTO users (email, code, is_verified) VALUES (?, ?, 0)", (email, code))
    else:
        c.execute("UPDATE users SET code=?, is_verified=0 WHERE email=?", (code, email))
    
    conn.commit()
    conn.close()

# Verify code from user input
def verify_user(email, input_code):
    email = email.strip().lower()
    input_code = input_code.strip()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT code FROM users WHERE email=?", (email,))
    row = c.fetchone()

    print(f"Verify attempt for email: {email}, input code: {input_code}")
    print("Query result:", row)

    if row and row[0] == input_code:
        c.execute("UPDATE users SET is_verified=1 WHERE email=?", (email,))
        conn.commit()
        conn.close()
        return True

    conn.close()
    return False

# Check if email is already registered
def email_exists(email):
    email = email.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM users WHERE email=?", (email,))
    exists = c.fetchone() is not None
    conn.close()
    return exists

# Login with email + password, only if verified
def login_user(email, password):
    email = email.strip().lower()
    # First check if it is admin
    if is_admin(email, password):
        return {"role": "admin"}
    # Then check the normal user
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT name, is_verified FROM users WHERE email=? AND password=?", (email, password))
    row = c.fetchone()
    conn.close()
    if row:
        name, is_verified = row
        if is_verified == 1:
            return {"role": "user", "name": name, "email": email}
        else:
            return {"role": "unverified"}
    return {"role": "invalid"}

def save_prediction(user_email, image_filename, predicted_class, confidence, top_predictions):
    """Save user's prediction result to database"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # Get user ID
        c.execute("SELECT id FROM users WHERE email = ?", (user_email,))
        user_row = c.fetchone()
        if not user_row:
            return False
        
        user_id = user_row[0]
        
        # Convert top_predictions to JSON string for storage
        import json
        top_predictions_json = json.dumps(top_predictions)
        
        # Insert prediction record
        c.execute("""
            INSERT INTO predictions (user_id, image_filename, predicted_class, confidence, top_predictions)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, image_filename, predicted_class, confidence, top_predictions_json))
        
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("Save prediction error:", e)
        return False
    finally:
        conn.close()

def get_user_predictions(user_email, limit=50):
    """Get user's prediction history"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT p.id, p.image_filename, p.predicted_class, p.confidence, 
                   p.top_predictions, p.created_at, u.name
            FROM predictions p
            JOIN users u ON p.user_id = u.id
            WHERE u.email = ?
            ORDER BY p.created_at DESC
            LIMIT ?
        """, (user_email, limit))
        
        predictions = c.fetchall()
        return predictions
    except sqlite3.Error as e:
        print("Get predictions error:", e)
        return []
    finally:
        conn.close()

def delete_prediction(prediction_id, user_email):
    """Delete specified prediction record (user can only delete their own)"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        # Verify user permissions
        c.execute("""
            SELECT p.id FROM predictions p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = ? AND u.email = ?
        """, (prediction_id, user_email))
        
        if not c.fetchone():
            return False
        
        # Delete record
        c.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print("Delete prediction error:", e)
        return False
    finally:
        conn.close()

def get_all_user_predictions(limit=100):
    """Get all users' prediction history for admin"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT p.id, p.image_filename, p.predicted_class, p.confidence, 
                   p.top_predictions, p.created_at, u.name, u.email
            FROM predictions p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT ?
        """, (limit,))
        
        predictions = c.fetchall()
        return predictions
    except sqlite3.Error as e:
        print("Get all predictions error:", e)
        return []
    finally:
        conn.close()

def get_user_predictions_by_email(user_email, limit=50):
    """Get specific user's prediction history by email for admin"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("""
            SELECT p.id, p.image_filename, p.predicted_class, p.confidence, 
                   p.top_predictions, p.created_at, u.name, u.email
            FROM predictions p
            JOIN users u ON p.user_id = u.id
            WHERE u.email = ?
            ORDER BY p.created_at DESC
            LIMIT ?
        """, (user_email, limit))
        
        predictions = c.fetchall()
        return predictions
    except sqlite3.Error as e:
        print("Get user predictions by email error:", e)
        return []
    finally:
        conn.close()