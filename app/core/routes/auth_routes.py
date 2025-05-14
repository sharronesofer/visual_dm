"""
Authentication routes for user registration, login, and password management.
"""

from flask import Blueprint, request, jsonify, current_app
from marshmallow import Schema, fields, validate
from app.core.services.auth_service import AuthService
from app.core.utils.security import validate_password, validate_username, validate_email
from app.core.exceptions import (
    ValidationError,
    AuthenticationError,
    UserNotFoundError,
    InvalidTokenError
)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

# Request/Response schemas
class RegisterSchema(Schema):
    """Registration request schema."""
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    first_name = fields.Str()
    last_name = fields.Str()

class LoginSchema(Schema):
    """Login request schema."""
    username_or_email = fields.Str(required=True)
    password = fields.Str(required=True)
    device_info = fields.Str()

class PasswordResetRequestSchema(Schema):
    """Password reset request schema."""
    email = fields.Email(required=True)

class PasswordResetSchema(Schema):
    """Password reset schema."""
    token = fields.Str(required=True)
    new_password = fields.Str(required=True)

class UserResponseSchema(Schema):
    """User response schema."""
    id = fields.Int()
    username = fields.Str()
    email = fields.Str()
    full_name = fields.Str()
    role = fields.Str()
    is_active = fields.Bool()
    is_verified = fields.Bool()
    created_at = fields.DateTime()
    last_login = fields.DateTime()

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        # Validate request data
        schema = RegisterSchema()
        data = schema.load(request.json)
        
        # Validate password strength
        is_valid, error = validate_password(data['password'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Validate username format
        is_valid, error = validate_username(data['username'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Validate email format
        is_valid, error = validate_email(data['email'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Register user
        user = AuthService.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        # Return user data
        return jsonify(UserResponseSchema().dump(user)), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Authenticate a user and create a session."""
    try:
        # Validate request data
        schema = LoginSchema()
        data = schema.load(request.json)
        
        # Get client IP
        ip_address = request.remote_addr
        
        # Authenticate user
        user, session = AuthService.authenticate_user(
            username_or_email=data['username_or_email'],
            password=data['password'],
            device_info=data.get('device_info'),
            ip_address=ip_address
        )
        
        # Return user data and session token
        response = {
            'user': UserResponseSchema().dump(user),
            'session_token': session.token
        }
        return jsonify(response), 200
        
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify a user's email address."""
    try:
        user = AuthService.verify_email(token)
        return jsonify({'message': 'Email verified successfully'}), 200
        
    except InvalidTokenError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Email verification error: {str(e)}")
        return jsonify({'error': 'Email verification failed'}), 500

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Initiate password reset process."""
    try:
        # Validate request data
        schema = PasswordResetRequestSchema()
        data = schema.load(request.json)
        
        # Initiate password reset
        AuthService.initiate_password_reset(data['email'])
        
        # Don't reveal if email exists
        return jsonify({'message': 'If an account exists with this email, a password reset link has been sent'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Password reset request error: {str(e)}")
        return jsonify({'error': 'Failed to process password reset request'}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset a user's password."""
    try:
        # Validate request data
        schema = PasswordResetSchema()
        data = schema.load(request.json)
        
        # Validate new password
        is_valid, error = validate_password(data['new_password'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        # Reset password
        AuthService.reset_password(data['token'], data['new_password'])
        
        return jsonify({'message': 'Password reset successfully'}), 200
        
    except InvalidTokenError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Password reset error: {str(e)}")
        return jsonify({'error': 'Password reset failed'}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Invalidate the current session."""
    try:
        # Get session token from header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid session token'}), 401
        
        session_token = auth_header.split(' ')[1]
        
        # Invalidate session
        AuthService.invalidate_session(session_token)
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except InvalidTokenError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500 