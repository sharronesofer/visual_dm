"""
Authentication schemas for request/response validation and Swagger documentation.
"""

from marshmallow import Schema, fields, validate

class RegisterRequestSchema(Schema):
    """Schema for user registration request."""
    username = fields.Str(
        required=True,
        validate=validate.Length(min=3, max=50),
        metadata={
            "description": "Username for the new account",
            "example": "johndoe"
        }
    )
    email = fields.Email(
        required=True,
        metadata={
            "description": "Email address for the account",
            "example": "john.doe@example.com"
        }
    )
    password = fields.Str(
        required=True,
        validate=validate.Length(min=12),
        metadata={
            "description": "Password for the account (min 12 characters)",
            "example": "SecurePass123456"
        }
    )

class LoginRequestSchema(Schema):
    """Schema for login request."""
    username = fields.Str(
        required=True,
        metadata={
            "description": "Username or email",
            "example": "johndoe"
        }
    )
    password = fields.Str(
        required=True,
        metadata={
            "description": "Account password",
            "example": "SecurePass123"
        }
    )
    remember = fields.Bool(
        missing=False,
        metadata={
            "description": "Remember login session",
            "example": False
        }
    )

class TokenResponseSchema(Schema):
    """Schema for token response."""
    access_token = fields.Str(
        required=True,
        metadata={
            "description": "JWT access token",
            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    )
    refresh_token = fields.Str(
        required=True,
        metadata={
            "description": "JWT refresh token",
            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    )
    token_type = fields.Str(
        required=True,
        metadata={
            "description": "Token type",
            "example": "bearer"
        }
    )

class RefreshTokenRequestSchema(Schema):
    """Schema for token refresh request."""
    refresh_token = fields.Str(
        required=True,
        metadata={
            "description": "JWT refresh token",
            "example": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        }
    )

class PasswordResetRequestSchema(Schema):
    """Schema for password reset request."""
    email = fields.Email(
        required=True,
        metadata={
            "description": "Email address for password reset",
            "example": "john.doe@example.com"
        }
    )

class PasswordResetConfirmSchema(Schema):
    """Schema for password reset confirmation."""
    token = fields.Str(
        required=True,
        metadata={
            "description": "Password reset token",
            "example": "abcdef123456"
        }
    )
    new_password = fields.Str(
        required=True,
        validate=validate.Length(min=8),
        metadata={
            "description": "New password (min 8 characters)",
            "example": "NewSecurePass123"
        }
    )

class UserResponseSchema(Schema):
    """Schema for user response data."""
    id = fields.Int(
        required=True,
        metadata={
            "description": "User ID",
            "example": 1
        }
    )
    username = fields.Str(
        required=True,
        metadata={
            "description": "Username",
            "example": "johndoe"
        }
    )
    email = fields.Str(
        required=True,
        metadata={
            "description": "Email address",
            "example": "john.doe@example.com"
        }
    )
    role = fields.Str(
        required=True,
        metadata={
            "description": "User role",
            "example": "user"
        }
    ) 