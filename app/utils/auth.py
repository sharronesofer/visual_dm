from functools import wraps
from flask import request, jsonify
import firebase_admin
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'No authorization header'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            token = auth_header.replace('Bearer ', '')
            decoded_token = firebase_auth.verify_id_token(token)
            request.user = decoded_token
            return f(*args, **kwargs)
        except firebase_auth.InvalidIdTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        except firebase_auth.ExpiredIdTokenError:
            return jsonify({'error': 'Token expired'}), 401
        except Exception as e:
            return jsonify({'error': str(e)}), 401
    
    return decorated_function

def get_current_user():
    """Get the current user from the request context."""
    return getattr(request, 'user', None)

def initialize_firebase(testing=False):
    """Initialize Firebase Admin SDK."""
    if not firebase_admin._apps:
        if testing:
            cred = credentials.Certificate('tests/firebase-test-credentials.json')
        else:
            cred = credentials.Certificate('app/config/firebase-credentials.json')
        firebase_admin.initialize_app(cred)

def hash_password(password):
    """Hash a password using Firebase's password hashing."""
    return firebase_auth.create_user(password=password).uid

def verify_password(password, hashed_password):
    """Verify a password against its hash."""
    try:
        user = firebase_auth.get_user(hashed_password)
        return True
    except:
        return False

def create_session_token(user_id):
    """Create a custom session token for the user."""
    return firebase_auth.create_custom_token(user_id)

def verify_session_token(token):
    """Verify a custom session token."""
    try:
        decoded_token = firebase_auth.verify_id_token(token)
        return decoded_token
    except:
        return None

# Alias for require_auth to maintain compatibility
login_required = require_auth 