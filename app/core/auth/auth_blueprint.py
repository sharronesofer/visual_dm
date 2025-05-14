"""
Authentication endpoints blueprint.
"""

from flask import Blueprint, request, current_app, g
from flask_restx import Api, Resource, fields
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.api.base_blueprint import BaseBlueprint
from app.core.utils.api_response import APIResponse, ErrorResponse
from app.core.auth.jwt_manager import JWTManager, TokenExpiredError, InvalidTokenError
from app.core.models.user import User
from app.core.middleware.rate_limiter import rate_limit
from app.core.middleware.cache import no_cache

class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str
    remember_me: Optional[bool] = False

class AuthBlueprint(BaseBlueprint):
    """Authentication endpoints blueprint."""

    def __init__(self):
        super().__init__("auth", __name__, url_prefix="/api/v1/auth")
        
        # Initialize Flask-RESTX API
        self.api = Api(
            self,
            title="Authentication API",
            description="Endpoints for user authentication",
            doc="/docs"
        )

        # Define request/response models
        self.login_model = self.api.model("LoginRequest", {
            "email": fields.String(required=True, description="User email"),
            "password": fields.String(required=True, description="User password"),
            "remember_me": fields.Boolean(required=False, description="Remember me flag")
        })

        self.token_response = self.api.model("TokenResponse", {
            "access_token": fields.String(description="JWT access token"),
            "refresh_token": fields.String(description="JWT refresh token"),
            "token_type": fields.String(description="Token type (Bearer)"),
            "expires_in": fields.Integer(description="Access token expiration time in seconds")
        })

        # Register routes
        self._register_routes()

    def _register_routes(self):
        """Register blueprint routes."""

        @self.api.route("/login")
        class LoginResource(Resource):
            @rate_limit(limit=5, period=300)  # 5 attempts per 5 minutes
            @no_cache
            @self.api.expect(self.login_model)
            @self.api.response(200, "Login successful", self.token_response)
            @self.api.response(401, "Invalid credentials")
            @self.api.response(429, "Too many login attempts")
            def post(self):
                """User login endpoint."""
                try:
                    # Validate request data
                    data = LoginRequest(**request.json)
                    
                    # Authenticate user (implement in User model)
                    user = User.authenticate(data.email, data.password)
                    if not user:
                        return ErrorResponse(
                            "Invalid credentials",
                            status_code=401
                        ).to_dict(), 401

                    # Create tokens
                    jwt_manager: JWTManager = current_app.extensions["jwt_manager"]
                    access_token, refresh_token = jwt_manager.create_token_pair(
                        str(user.id),
                        additional_claims={
                            "email": user.email,
                            "roles": user.roles
                        }
                    )

                    return APIResponse(
                        data={
                            "access_token": access_token,
                            "refresh_token": refresh_token,
                            "token_type": "Bearer",
                            "expires_in": jwt_manager.access_token_expires
                        }
                    ).to_dict(), 200

                except Exception as e:
                    current_app.logger.error(f"Login failed: {str(e)}")
                    return ErrorResponse(
                        "Login failed",
                        status_code=500
                    ).to_dict(), 500

        @self.api.route("/refresh")
        class RefreshResource(Resource):
            @rate_limit(limit=10, period=60)  # 10 attempts per minute
            @no_cache
            @self.api.response(200, "Token refresh successful", self.token_response)
            @self.api.response(401, "Invalid refresh token")
            @self.api.response(429, "Too many refresh attempts")
            def post(self):
                """Refresh access token endpoint."""
                try:
                    auth_header = request.headers.get("Authorization")
                    if not auth_header or not auth_header.startswith("Bearer "):
                        return ErrorResponse(
                            "Missing or invalid refresh token",
                            status_code=401
                        ).to_dict(), 401

                    refresh_token = auth_header.split(" ")[1]
                    jwt_manager: JWTManager = current_app.extensions["jwt_manager"]

                    # Verify refresh token
                    try:
                        claims = jwt_manager.decode_token(refresh_token, verify_type="refresh")
                    except (TokenExpiredError, InvalidTokenError) as e:
                        return ErrorResponse(
                            str(e),
                            status_code=401
                        ).to_dict(), 401

                    # Create new access token
                    user_id = claims["sub"]
                    user = User.get_by_id(user_id)
                    if not user:
                        return ErrorResponse(
                            "User not found",
                            status_code=401
                        ).to_dict(), 401

                    access_token = jwt_manager.create_access_token(
                        user_id,
                        additional_claims={
                            "email": user.email,
                            "roles": user.roles
                        }
                    )

                    return APIResponse(
                        data={
                            "access_token": access_token,
                            "refresh_token": refresh_token,  # Return same refresh token
                            "token_type": "Bearer",
                            "expires_in": jwt_manager.access_token_expires
                        }
                    ).to_dict(), 200

                except Exception as e:
                    current_app.logger.error(f"Token refresh failed: {str(e)}")
                    return ErrorResponse(
                        "Token refresh failed",
                        status_code=500
                    ).to_dict(), 500

        @self.api.route("/logout")
        class LogoutResource(Resource):
            @rate_limit(limit=10, period=60)  # 10 attempts per minute
            @no_cache
            @self.api.response(200, "Logout successful")
            @self.api.response(401, "Invalid token")
            def post(self):
                """User logout endpoint."""
                try:
                    auth_header = request.headers.get("Authorization")
                    if not auth_header or not auth_header.startswith("Bearer "):
                        return ErrorResponse(
                            "Missing or invalid token",
                            status_code=401
                        ).to_dict(), 401

                    token = auth_header.split(" ")[1]
                    jwt_manager: JWTManager = current_app.extensions["jwt_manager"]

                    # Verify token
                    try:
                        claims = jwt_manager.decode_token(token)
                    except (TokenExpiredError, InvalidTokenError):
                        # If token is already invalid, consider logout successful
                        return APIResponse(
                            message="Logged out successfully"
                        ).to_dict(), 200

                    # Add token to blacklist (implement in User model)
                    user_id = claims["sub"]
                    User.blacklist_token(token)

                    return APIResponse(
                        message="Logged out successfully"
                    ).to_dict(), 200

                except Exception as e:
                    current_app.logger.error(f"Logout failed: {str(e)}")
                    return ErrorResponse(
                        "Logout failed",
                        status_code=500
                    ).to_dict(), 500

# Create blueprint instance
auth_blueprint = AuthBlueprint() 