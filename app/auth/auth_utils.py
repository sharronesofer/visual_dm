import firebase_admin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os, uuid
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../.env"))

# Get values from .env
firebase_creds_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
firebase_db_url = os.getenv("FIREBASE_DB_URL")

if not firebase_creds_path or not firebase_db_url:
    raise ValueError("Missing FIREBASE_CREDENTIALS_PATH or FIREBASE_DB_URL in .env")

# Initialize Firebase only once
if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_creds_path)
    firebase_admin.initialize_app(cred, {
        "databaseURL": firebase_db_url
    })

# Utility Functions for Authentication-Related Firebase Interactions

def create_user(username, email, password):
    """
    Creates a new user entry in Firebase.
    """
    user_id = str(uuid.uuid4())
    password_hash = generate_password_hash(password)
    timestamp = datetime.utcnow().isoformat()

    user_ref = db.reference(f'/users/{user_id}')
    user_ref.set({
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'created_at': timestamp,
    })

    return user_id

def get_user_by_username(username):
    """
    Retrieves user information from Firebase using username.
    Returns the user_id and user_data or (None, None) if not found.
    """
    users_ref = db.reference('/users')
    users_snapshot = users_ref.get()

    if users_snapshot:
        for user_id, user_data in users_snapshot.items():
            if user_data.get('username') == username:
                return user_id, user_data
    return None, None

def verify_user_password(user_data, password_attempt):
    """
    Verifies a user's password against the hashed password stored in Firebase.
    """
    stored_hash = user_data.get('password_hash')
    if stored_hash:
        return check_password_hash(stored_hash, password_attempt)
    return False

def log_auth_event(user_id, event_type="login"):
    """
    Logs authentication events (login/logout) to Firebase under the user's record.
    """
    timestamp = datetime.utcnow().isoformat()
    logs_ref = db.reference(f'/auth_logs/{user_id}')
    new_log_ref = logs_ref.push()
    new_log_ref.set({
        'event': event_type,
        'timestamp': timestamp,
    })

