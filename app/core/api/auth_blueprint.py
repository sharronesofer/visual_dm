"""
Authentication endpoints for user login, token refresh, and logout.
"""

from typing import Any, Dict, Optional
from flask import request, current_app, g, jsonify
from pydantic import BaseModel, EmailStr, constr
from marshmallow import Schema, fields
from ..utils.api_response import (
    APIResponse,
    APIStatus,
    create_validation_error,
    create_unauthorized_error
)
from ..auth.jwt_manager import JWTError
from .base_blueprint import BaseAPIBlueprint
from ..models.user import User, UserRole
from ..utils.password import verify_password
from ..utils.openapi import document_endpoint, document_response
from app.core.models.api_key import APIKey
from app.core.utils.security_utils import generate_api_key
from app.core.database import db

class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: constr(min_length=8, max_length=128)

class LoginResponseSchema(Schema):
    """Login response schema."""
    access_token = fields.String(required=True, description="JWT access token")
    refresh_token = fields.String(required=True, description="JWT refresh token")
    token_type = fields.String(required=True, description="Token type (Bearer)")
    expires_in = fields.Integer(required=True, description="Token expiration time in seconds")
    user = fields.Dict(required=True, description="User information")

class RefreshRequest(BaseModel):
    """Token refresh request schema."""
    refresh_token: str

class RefreshResponseSchema(Schema):
    """Token refresh response schema."""
    access_token = fields.String(required=True, description="New JWT access token")
    token_type = fields.String(required=True, description="Token type (Bearer)")
    expires_in = fields.Integer(required=True, description="Token expiration time in seconds")

class APIKeyCreateRequest(BaseModel):
    description: Optional[str] = None

class APIKeyRevokeRequest(BaseModel):
    key: str

class APIKeyListResponse(BaseModel):
    keys: list

class APIKeyBlueprint(BaseAPIBlueprint):
    def __init__(self):
        super().__init__('api_key', __name__, url_prefix='/api/v1/api-keys')
        self.api = Api(
            self,
            title="API Key Management API",
            description="Endpoints for API key management",
            doc="/docs"
        )
        self._register_routes()

    def _register_routes(self):
        @self.api.route('/')
        class APIKeyListResource(Resource):
            @document_endpoint(
                summary="List API keys",
                description="List all API keys for the current user.",
                tags=["api-key"],
                security=[{"ApiKeyAuth": []}],
                responses={
                    "200": document_response(200, "List of API keys"),
                    "401": {"$ref": "#/components/responses/AuthenticationError"}
                }
            )
            def get(self):
                # List all API keys for the current user
                user = g.get('current_user')
                if not user:
                    return ErrorResponse("Authentication required").to_dict(), 401
                keys = APIKey.query.filter_by(owner_id=user['id']).all()
                return jsonify([{
                    'id': k.id,
                    'key': k.key,
                    'description': k.description,
                    'is_active': k.is_active,
                    'created_at': k.created_at,
                    'last_used_at': k.last_used_at
                } for k in keys])

        @self.api.route('/create')
        class APIKeyCreateResource(Resource):
            @document_endpoint(
                summary="Create API key",
                description="Create a new API key for the current user.",
                tags=["api-key"],
                security=[{"ApiKeyAuth": []}],
                request_body={
                    "schema": {
                        "type": "object",
                        "properties": {"description": {"type": "string"}},
                        "required": []
                    }
                },
                responses={
                    "200": document_response(200, "API key created"),
                    "401": {"$ref": "#/components/responses/AuthenticationError"}
                }
            )
            def post(self):
                user = g.get('current_user')
                if not user:
                    return ErrorResponse("Authentication required").to_dict(), 401
                data = request.get_json() or {}
                description = data.get('description')
                key = generate_api_key()
                api_key = APIKey(key=key, owner_id=user['id'], description=description)
                db.session.add(api_key)
                db.session.commit()
                return jsonify({
                    'id': api_key.id,
                    'key': api_key.key,
                    'description': api_key.description,
                    'is_active': api_key.is_active,
                    'created_at': api_key.created_at
                })

        @self.api.route('/revoke')
        class APIKeyRevokeResource(Resource):
            @document_endpoint(
                summary="Revoke API key",
                description="Revoke an existing API key for the current user.",
                tags=["api-key"],
                security=[{"ApiKeyAuth": []}],
                request_body={
                    "schema": {
                        "type": "object",
                        "properties": {"key": {"type": "string"}},
                        "required": ["key"]
                    }
                },
                responses={
                    "200": document_response(200, "API key revoked"),
                    "401": {"$ref": "#/components/responses/AuthenticationError"},
                    "404": {"$ref": "#/components/responses/NotFoundError"}
                }
            )
            def post(self):
                user = g.get('current_user')
                if not user:
                    return ErrorResponse("Authentication required").to_dict(), 401
                data = request.get_json() or {}
                key = data.get('key')
                api_key = APIKey.query.filter_by(key=key, owner_id=user['id']).first()
                if not api_key:
                    return ErrorResponse("API key not found").to_dict(), 404
                api_key.is_active = False
                db.session.commit()
                return jsonify({'success': True})

        @self.api.route('/describe/<string:key>')
        class APIKeyDescribeResource(Resource):
            @document_endpoint(
                summary="Describe API key",
                description="Get details about a specific API key for the current user.",
                tags=["api-key"],
                security=[{"ApiKeyAuth": []}],
                responses={
                    "200": document_response(200, "API key details"),
                    "401": {"$ref": "#/components/responses/AuthenticationError"},
                    "404": {"$ref": "#/components/responses/NotFoundError"}
                }
            )
            def get(self, key):
                user = g.get('current_user')
                if not user:
                    return ErrorResponse("Authentication required").to_dict(), 401
                api_key = APIKey.query.filter_by(key=key, owner_id=user['id']).first()
                if not api_key:
                    return ErrorResponse("API key not found").to_dict(), 404
                return jsonify({
                    'id': api_key.id,
                    'key': api_key.key,
                    'description': api_key.description,
                    'is_active': api_key.is_active,
                    'created_at': api_key.created_at,
                    'last_used_at': api_key.last_used_at
                })

auth_blueprint = BaseAPIBlueprint("auth", __name__)

@auth_blueprint.route("/login", methods=["POST"])
@document_endpoint(
    summary="User login",
    description="Authenticate user and return access and refresh tokens",
    tags=["auth"],
    request_body={
        "schema": {
            "type": "object",
            "properties": {
                "email": {"type": "string", "format": "email"},
                "password": {"type": "string", "minLength": 8, "maxLength": 128}
            },
            "required": ["email", "password"]
        }
    },
    responses={
        "200": document_response(
            200,
            "Login successful",
            LoginResponseSchema
        ),
        "400": {"$ref": "#/components/responses/ValidationError"},
        "401": {"$ref": "#/components/responses/AuthenticationError"}
    }
)
@auth_blueprint.validate_json(LoginRequest)
def login(data: LoginRequest) -> Any:
    """
    User login endpoint.

    Args:
        data: Login request data

    Returns:
        Login response with tokens
    """
    # Find user by email
    user = User.get_by_email(data.email)
    if not user:
        return create_unauthorized_error(
            "Invalid email or password"
        ).to_response()

    # Verify password
    if not verify_password(data.password, user.password_hash):
        return create_unauthorized_error(
            "Invalid email or password"
        ).to_response()

    # Create tokens
    additional_claims = {
        "roles": [role.value for role in user.roles],
        "email": user.email
    }
    
    access_token, refresh_token = current_app.jwt_manager.create_token_pair(
        str(user.id),
        additional_claims
    )

    response_data = {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "Bearer",
        "expires_in": current_app.jwt_manager.access_token_expires,
        "user": user.to_dict()
    }

    return APIResponse.success(data=response_data).to_response()

@auth_blueprint.route("/refresh", methods=["POST"])
@document_endpoint(
    summary="Refresh access token",
    description="Create new access token using refresh token",
    tags=["auth"],
    request_body={
        "schema": {
            "type": "object",
            "properties": {
                "refresh_token": {"type": "string"}
            },
            "required": ["refresh_token"]
        }
    },
    responses={
        "200": document_response(
            200,
            "Token refresh successful",
            RefreshResponseSchema
        ),
        "400": {"$ref": "#/components/responses/ValidationError"},
        "401": {"$ref": "#/components/responses/AuthenticationError"}
    }
)
@auth_blueprint.validate_json(RefreshRequest)
def refresh(data: RefreshRequest) -> Any:
    """
    Token refresh endpoint.

    Args:
        data: Refresh request data

    Returns:
        New access token
    """
    try:
        access_token = current_app.jwt_manager.refresh_access_token(
            data.refresh_token
        )

        response_data = {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": current_app.jwt_manager.access_token_expires
        }

        return APIResponse.success(data=response_data).to_response()

    except JWTError as e:
        return create_unauthorized_error(str(e)).to_response()

@auth_blueprint.route("/logout", methods=["POST"])
@document_endpoint(
    summary="User logout",
    description="Invalidate user's refresh token",
    tags=["auth"],
    security=[{"bearerAuth": []}],
    responses={
        "200": document_response(
            200,
            "Logout successful"
        ),
        "401": {"$ref": "#/components/responses/AuthenticationError"}
    }
)
@auth_blueprint.require_auth
def logout(user_data: Dict[str, Any]) -> Any:
    """
    User logout endpoint.

    Args:
        user_data: User data from JWT token

    Returns:
        Success response
    """
    # In a more complex implementation, we might want to:
    # 1. Add the token to a blacklist
    # 2. Clear any user sessions
    # 3. Revoke refresh tokens
    # For now, we'll just return success since JWT tokens are stateless
    
    return APIResponse.success(
        data={"message": "Successfully logged out"}
    ).to_response()

@auth_blueprint.route("/me", methods=["GET"])
@document_endpoint(
    summary="Get current user",
    description="Get information about the currently authenticated user",
    tags=["auth"],
    security=[{"bearerAuth": []}],
    responses={
        "200": document_response(
            200,
            "User information retrieved successfully"
        ),
        "401": {"$ref": "#/components/responses/AuthenticationError"}
    }
)
@auth_blueprint.require_auth
def get_current_user(user_data: Dict[str, Any]) -> Any:
    """
    Get current user endpoint.

    Args:
        user_data: User data from JWT token

    Returns:
        Current user information
    """
    user = User.get_by_id(user_data["sub"])
    if not user:
        return create_unauthorized_error(
            "User not found"
        ).to_response()

    return APIResponse.success(
        data=user.to_dict()
    ).to_response() 