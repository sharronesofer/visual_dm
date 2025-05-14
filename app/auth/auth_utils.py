#"This module handles user creation, authentication, and event logging. It communicates with Firebase to manage user records and logs. It's strictly a backend utility for identity/auth tracking, not game state or simulation systems."

import firebase_admin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from uuid import uuid4
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db, auth
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import bcrypt
from typing import Dict, Any, Optional, Tuple
import jwt
from typing import Dict, Any, Optional
from app.utils.firebase.init import initialize_firebase
from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity
from app.core.models.user import User
from app.core.database import db
from flask import current_app
from datetime import timedelta

env_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=env_path)

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

def logout(user_id):
    """
    Appends a 'logout_at' timestamp to the user's Firebase record.
    """
    timestamp = datetime.utcnow().isoformat()
    user_ref = db.reference(f'/users/{user_id}')
    if user_ref.get() is not None:
        user_ref.update({'logout_at': timestamp})
        log_auth_event(user_id, event_type="logout")
        return True
    return False

def register_user(username: str, password: str, email: str) -> Dict[str, Any]:
    """
    Register a new user with the given credentials.
    
    Args:
        username: The desired username
        password: The user's password
        email: The user's email address
        
    Returns:
        Dict containing user info and token
    """
    try:
        # Check if username already exists
        existing = db.reference("/users").order_by_child("username").equal_to(username).get()
        if existing:
            raise ValueError("Username already taken")
            
        # Create Firebase auth user
        user = auth.create_user(
            email=email,
            password=password,
            display_name=username
        )
        
        # Hash password for storage
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)
        
        # Store additional user data
        user_data = {
            "username": username,
            "email": email,
            "password_hash": hashed.decode(),
            "created_at": datetime.utcnow().isoformat(),
            "last_login": None,
            "active_character": None
        }
        
        db.reference(f"/users/{user.uid}").set(user_data)
        
        # Create custom token
        token = auth.create_custom_token(user.uid)
        
        return {
            "user_id": user.uid,
            "username": username,
            "token": token.decode()
        }
        
    except Exception as e:
        raise ValueError(f"Failed to register user: {str(e)}")

def verify_password(stored_hash: str, password: str) -> bool:
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode(), stored_hash.encode())

def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Get user data by ID."""
    return db.reference(f"/users/{user_id}").get()

def update_last_login(user_id: str) -> None:
    """Update user's last login timestamp."""
    db.reference(f"/users/{user_id}/last_login").set(datetime.utcnow().isoformat())

def login_user(username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]], str]:
    """
    Authenticate a user and return their data.
    
    Args:
        username: User's username
        password: User's password
        
    Returns:
        Tuple of (success, user_data, message)
    """
    try:
        # Get user data
        users_ref = db.reference("/users")
        users = users_ref.get() or {}
        
        # Find user by username
        user_data = None
        user_id = None
        for uid, data in users.items():
            if data.get("username") == username:
                user_data = data
                user_id = uid
                break
                
        if not user_data:
            return False, None, "User not found"
            
        # Check password
        salt = user_data.get("salt", "")
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        if hashed != user_data.get("password"):
            return False, None, "Invalid password"
            
        # Generate JWT token
        token = jwt.encode(
            {
                "user_id": user_id,
                "username": username,
                "exp": datetime.utcnow().timestamp() + 86400  # 24 hours
            },
            os.getenv("JWT_SECRET", "dev-secret"),
            algorithm="HS256"
        )
        
        # Update last login
        users_ref.child(user_id).update({
            "last_login": datetime.utcnow().isoformat(),
            "current_token": token
        })
        
        user_data["token"] = token
        return True, user_data, "Login successful"
        
    except Exception as e:
        return False, None, f"Login error: {str(e)}"

def logout_user(user_id: str) -> bool:
    """
    Log out a user.
    
    Args:
        user_id: ID of the user to log out
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Update last logout timestamp
        db.reference(f"/users/{user_id}").update({
            "last_logout": datetime.utcnow().isoformat(),
            "current_token": None
        })
        return True
    except Exception as e:
        print(f"Error logging out user: {e}")
        return False

def initialize_auth():
    """Initialize authentication services"""
    # Ensure Firebase is initialized
    initialize_firebase()
    
    # ... existing code ...

def get_current_user(token: str) -> Dict[str, Any]:
    """
    Get the current user from a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Dict containing user data if valid, None otherwise
    """
    try:
        # Verify token
        decoded = jwt.decode(
            token,
            os.getenv("JWT_SECRET", "dev-secret"),
            algorithms=["HS256"]
        )
        
        # Get user data
        user_id = decoded.get("user_id")
        if not user_id:
            return None
            
        return get_user_by_id(user_id)
        
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
    except Exception as e:
        print(f"Error getting current user: {e}")
        return None

def require_auth(f):
    """
    Decorator to require authentication for routes.
    
    Args:
        f: Function to wrap
        
    Returns:
        Wrapped function that checks for valid authentication
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({
                'success': False,
                'message': 'No authorization header'
            }), 401
            
        try:
            # Extract token
            token_type, token = auth_header.split()
            if token_type.lower() != 'bearer':
                return jsonify({
                    'success': False,
                    'message': 'Invalid token type'
                }), 401
                
            # Verify token and get user
            user = get_current_user(token)
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'Invalid or expired token'
                }), 401
                
            # Add user to request context
            request.user = user
            return f(*args, **kwargs)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Authentication error: {str(e)}'
            }), 401
            
    return decorated

class AuthService:
    """Service for user authentication and JWT token management."""
    @staticmethod
    def authenticate_user(username_or_email, password):
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and user.check_password(password):
            return user
        return None

    @staticmethod
    def generate_tokens(user):
        access_token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role,
                'username': user.username
            },
            expires_delta=timedelta(minutes=current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', 15))
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', 30))
        )
        return access_token, refresh_token

    @staticmethod
    def blacklist_token(jti):
        # Store the JWT ID (jti) in Redis or DB for blacklisting
        from app import redis_client
        redis_client.setex(f"jwt_blacklist:{jti}", timedelta(days=30), "true")

    @staticmethod
    def is_token_blacklisted(jti):
        from app import redis_client
        return redis_client.get(f"jwt_blacklist:{jti}") is not None
