"""
Authentication routes for native clients (Unity, mobile, desktop).

These routes provide login, registration, and session management for
native clients with CAPTCHA protection against automated attacks.
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
from app.core.middleware.native_captcha_middleware import native_captcha_required
from app.core.validation.rate_limiter import rate_limit

# Create blueprint
native_auth_bp = Blueprint('native_auth', __name__)

# Request/Response schemas
class NativeRegisterSchema(Schema):
    """Registration request schema for native clients."""
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)
    first_name = fields.Str()
    last_name = fields.Str()
    device_id = fields.Str()
    platform = fields.Str()
    captcha_challenge_id = fields.Str(required=True)
    captcha_response = fields.Str(required=True)

class NativeLoginSchema(Schema):
    """Login request schema for native clients."""
    username_or_email = fields.Str(required=True)
    password = fields.Str(required=True)
    device_id = fields.Str()
    platform = fields.Str()
    version = fields.Str()
    captcha_challenge_id = fields.Str(required=True)
    captcha_response = fields.Str(required=True)

class UserResponseSchema(Schema):
    """User response schema."""
    id = fields.Int()
    username = fields.Str()
    email = fields.Email()
    first_name = fields.Str()
    last_name = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    last_login = fields.DateTime()

@native_auth_bp.route('/api/v1/auth/native/register', methods=['POST'])
@rate_limit('auth')
@native_captcha_required
def register():
    """
    Register a new user from a native client.
    ---
    tags:
      - Native Authentication
    summary: Register a new user account from a native client
    description: Register a new user with username, email, password and CAPTCHA verification
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - username
              - email
              - password
              - captcha_challenge_id
              - captcha_response
            properties:
              username:
                type: string
                description: User's desired username
              email:
                type: string
                format: email
                description: User's email address
              password:
                type: string
                description: User's password
              first_name:
                type: string
                description: User's first name
              last_name:
                type: string
                description: User's last name
              device_id:
                type: string
                description: Unique identifier for the device
              platform:
                type: string
                description: Platform identifier (e.g., Unity, iOS, Android)
              captcha_challenge_id:
                type: string
                description: CAPTCHA challenge ID from previous request
              captcha_response:
                type: string
                description: User's response to the CAPTCHA challenge
    responses:
      201:
        description: User registered successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                user:
                  type: object
                  description: User data
                token:
                  type: string
                  description: Authentication token
      400:
        description: Invalid request or validation error
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message
      409:
        description: Username or email already exists
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message
    """
    try:
        # Validate request data
        schema = NativeRegisterSchema()
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
        
        # Extract client information
        device_info = {
            'device_id': data.get('device_id'),
            'platform': data.get('platform'),
            'ip_address': request.remote_addr
        }
        
        # Register user
        user = AuthService.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name')
        )
        
        # Create session for immediate login
        session = AuthService.create_session(user.id, device_info)
        
        # Return user data and token
        response = {
            'user': UserResponseSchema().dump(user),
            'token': session.token
        }
        
        return jsonify(response), 201
        
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except ValueError as e:
        if "already exists" in str(e).lower():
            return jsonify({'error': str(e)}), 409
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Native registration error: {str(e)}")
        return jsonify({'error': 'Registration failed'}), 500

@native_auth_bp.route('/api/v1/auth/native/login', methods=['POST'])
@rate_limit('auth')
@native_captcha_required
def login():
    """
    Authenticate a user from a native client.
    ---
    tags:
      - Native Authentication
    summary: Login from a native client
    description: Authenticate with username/email and password with CAPTCHA protection
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - username_or_email
              - password
              - captcha_challenge_id
              - captcha_response
            properties:
              username_or_email:
                type: string
                description: Username or email address
              password:
                type: string
                description: User's password
              device_id:
                type: string
                description: Unique identifier for the device
              platform:
                type: string
                description: Platform identifier (e.g., Unity, iOS, Android)
              version:
                type: string
                description: Client version
              captcha_challenge_id:
                type: string
                description: CAPTCHA challenge ID from previous request
              captcha_response:
                type: string
                description: User's response to the CAPTCHA challenge
    responses:
      200:
        description: Authentication successful
        content:
          application/json:
            schema:
              type: object
              properties:
                user:
                  type: object
                  description: User data
                token:
                  type: string
                  description: Authentication token
      400:
        description: Invalid request
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message
      401:
        description: Authentication failed
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  description: Error message
    """
    try:
        # Validate request data
        schema = NativeLoginSchema()
        data = schema.load(request.json)
        
        # Extract client information
        device_info = {
            'device_id': data.get('device_id'),
            'platform': data.get('platform'),
            'version': data.get('version'),
            'ip_address': request.remote_addr
        }
        
        # Authenticate user
        user, session = AuthService.authenticate_user(
            username_or_email=data['username_or_email'],
            password=data['password'],
            device_info=device_info
        )
        
        # Return user data and token
        response = {
            'user': UserResponseSchema().dump(user),
            'token': session.token
        }
        return jsonify(response), 200
        
    except AuthenticationError as e:
        return jsonify({'error': str(e)}), 401
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Native login error: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@native_auth_bp.route('/api/v1/auth/native/logout', methods=['POST'])
def logout():
    """
    Invalidate the current session for a native client.
    ---
    tags:
      - Native Authentication
    summary: Logout from a native client
    description: Invalidate the current authentication token
    security:
      - BearerAuth: []
    responses:
      200:
        description: Logged out successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Logged out successfully
      401:
        description: Invalid or missing token
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Missing or invalid token
    """
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Invalidate session
        AuthService.invalidate_session(token)
        
        return jsonify({'message': 'Logged out successfully'}), 200
        
    except InvalidTokenError as e:
        return jsonify({'error': str(e)}), 401
    except Exception as e:
        current_app.logger.error(f"Native logout error: {str(e)}")
        return jsonify({'error': 'Logout failed'}), 500

@native_auth_bp.route('/api/v1/auth/native/validate-token', methods=['POST'])
def validate_token():
    """
    Validate an authentication token and return user information.
    ---
    tags:
      - Native Authentication
    summary: Validate token and get user information
    description: Check if a token is valid and return the associated user data
    security:
      - BearerAuth: []
    responses:
      200:
        description: Token is valid
        content:
          application/json:
            schema:
              type: object
              properties:
                user:
                  type: object
                  description: User data
                valid:
                  type: boolean
                  example: true
      401:
        description: Invalid or expired token
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Invalid or expired token
                valid:
                  type: boolean
                  example: false
    """
    try:
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'error': 'Missing or invalid token', 'valid': False}), 401
        
        token = auth_header.split(' ')[1]
        
        # Validate token and get user
        user = AuthService.validate_session(token)
        
        return jsonify({
            'user': UserResponseSchema().dump(user),
            'valid': True
        }), 200
        
    except InvalidTokenError as e:
        return jsonify({'error': str(e), 'valid': False}), 401
    except Exception as e:
        current_app.logger.error(f"Token validation error: {str(e)}")
        return jsonify({'error': 'Token validation failed', 'valid': False}), 500 