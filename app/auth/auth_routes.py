"""
Authentication routes for user registration, login, and token management.
"""

from flask import Blueprint, request, jsonify
from app.auth.auth_utils import (
    create_user,
    get_user_by_username,
    verify_user_password,
    log_auth_event,
    logout
)
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required, get_jwt_identity
)
from app.core.schemas.auth_schemas import (
    RegisterRequestSchema,
    LoginRequestSchema,
    TokenResponseSchema,
    RefreshTokenRequestSchema,
    PasswordResetRequestSchema,
    PasswordResetConfirmSchema,
    UserResponseSchema
)
from app.auth.models import User
from app.core.database import db
import re

# Marshmallow Schemas
class RegisterSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True)

class LoginSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class PasswordResetSchema(Schema):
    email = fields.Email(required=True)

class PasswordResetConfirmSchema(Schema):
    token = fields.Str(required=True)
    new_password = fields.Str(required=True)

# Helper: validate request

def validate_request(schema, data):
    try:
        return schema.load(data)
    except ValidationError as err:
        return None, err.messages

# Define blueprint
auth_bp = Blueprint("auth", __name__, url_prefix="/api/v1/auth")


@auth_bp.route('/sign_up', methods=['POST'])
def sign_up():
    data = request.get_json(force=True)
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Username, email, and password are required."}), 400

    existing_user_id, _ = get_user_by_username(username)
    if existing_user_id:
        return jsonify({"error": "Username already taken."}), 409

    user_id = create_user(username, email, password)
    log_auth_event(user_id, event_type="signup")

    return jsonify({"message": "User created successfully.", "user_id": user_id}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user and get tokens.
    ---
    tags:
      - Authentication
    summary: Login to get access token
    description: Authenticate with username/email and password to receive JWT tokens
    requestBody:
      required: true
      content:
        application/json:
          schema: LoginRequestSchema
    responses:
      200:
        description: Login successful
        content:
          application/json:
            schema: TokenResponseSchema
      400:
        description: Invalid request data
        content:
          application/json:
            schema:
              type: object
              properties:
                errors:
                  type: object
                  example: {"username": ["Username is required"]}
      401:
        description: Invalid credentials
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Invalid username or password.
    """
    data = request.get_json(force=True)
    validated, errors = validate_request(LoginRequestSchema(), data)
    if errors:
        return jsonify({'errors': errors}), 400
    user = User.query.filter_by(username=validated['username']).first()
    if not user or not user.check_password(validated['password']):
        return jsonify({'error': 'Invalid username or password.'}), 401
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    user.update_last_login()
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'token_type': 'bearer',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    }), 200

@auth_bp.route('/logout', methods=['POST'])
def logout_route():
    user_id = request.json.get('user_id')
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    success = logout(user_id)
    if not success:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User logged out and timestamped."})

# JWT-based registration endpoint
@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    ---
    tags:
      - Authentication
    summary: Create a new user account
    description: Register a new user with username, email, and password
    requestBody:
      required: true
      content:
        application/json:
          schema: RegisterRequestSchema
    responses:
      201:
        description: User registered successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: User registered successfully.
      400:
        description: Invalid request data
        content:
          application/json:
            schema:
              type: object
              properties:
                errors:
                  type: object
                  example: {"username": ["Username is required"]}
      409:
        description: Username or email already exists
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Username or email already exists.
    """
    data = request.get_json(force=True)
    validated, errors = validate_request(RegisterRequestSchema(), data)
    if errors:
        return jsonify({'errors': errors}), 400
    if User.query.filter((User.username == validated['username']) | (User.email == validated['email'])).first():
        return jsonify({'error': 'Username or email already exists.'}), 409
    try:
        user = User(
            username=validated['username'],
            email=validated['email'],
            password=validated['password']
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'User registered successfully.'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# JWT-based login endpoint
@auth_bp.route('/login', methods=['POST'])
def jwt_login():
    data = request.get_json(force=True)
    validated, errors = validate_request(LoginSchema(), data)
    if errors:
        return jsonify({'errors': errors}), 400
    user = User.query.filter_by(username=validated['username']).first()
    if not user or not user.check_password(validated['password']):
        return jsonify({'error': 'Invalid username or password.'}), 401
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    user.update_last_login()
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    }), 200

# JWT refresh endpoint
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh access token.
    ---
    tags:
      - Authentication
    summary: Get new access token
    description: Use refresh token to get a new access token
    security:
      - BearerAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema: RefreshTokenRequestSchema
    responses:
      200:
        description: Token refreshed successfully
        content:
          application/json:
            schema:
              type: object
              properties:
                access_token:
                  type: string
                  example: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
      401:
        description: Invalid or expired refresh token
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Invalid or expired refresh token.
    """
    user_id = get_jwt_identity()
    access_token = create_access_token(identity=user_id)
    return jsonify({'access_token': access_token}), 200

# Password reset request endpoint (stub, implement email sending as needed)
@auth_bp.route('/password-reset', methods=['POST'])
def password_reset():
    """
    Request password reset.
    ---
    tags:
      - Authentication
    summary: Request password reset email
    description: Send password reset instructions to user's email
    requestBody:
      required: true
      content:
        application/json:
          schema: PasswordResetRequestSchema
    responses:
      200:
        description: Reset instructions sent if email exists
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Password reset instructions sent if email exists.
      400:
        description: Invalid email format
        content:
          application/json:
            schema:
              type: object
              properties:
                errors:
                  type: object
                  example: {"email": ["Not a valid email address."]}
    """
    data = request.get_json(force=True)
    validated, errors = validate_request(PasswordResetRequestSchema(), data)
    if errors:
        return jsonify({'errors': errors}), 400
    # TODO: Implement email sending with reset token
    return jsonify({'message': 'Password reset instructions sent if email exists.'}), 200

# Password reset confirm endpoint (stub, implement token verification as needed)
@auth_bp.route('/password-reset-confirm', methods=['POST'])
def password_reset_confirm():
    """
    Confirm password reset.
    ---
    tags:
      - Authentication
    summary: Reset password with token
    description: Reset user's password using the token received via email
    requestBody:
      required: true
      content:
        application/json:
          schema: PasswordResetConfirmSchema
    responses:
      200:
        description: Password reset successful
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: Password has been reset successfully.
      400:
        description: Invalid request data
        content:
          application/json:
            schema:
              type: object
              properties:
                errors:
                  type: object
                  example: {"token": ["Invalid or expired token."]}
    """
    data = request.get_json(force=True)
    validated, errors = validate_request(PasswordResetConfirmSchema(), data)
    if errors:
        return jsonify({'errors': errors}), 400
    # TODO: Implement token verification and password update
    return jsonify({'message': 'Password has been reset if token is valid.'}), 200

# Get current user info
@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    """
    Get current user info.
    ---
    tags:
      - Authentication
    summary: Get authenticated user details
    description: Get profile information for the currently authenticated user
    security:
      - BearerAuth: []
    responses:
      200:
        description: User information retrieved successfully
        content:
          application/json:
            schema: UserResponseSchema
      401:
        description: Not authenticated
        content:
          application/json:
            schema:
              type: object
              properties:
                error:
                  type: string
                  example: Not authenticated.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found.'}), 404
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }), 200
