"""
Authentication services package.

This package contains core authentication functionality organized into:
- auth_service: User authentication and authorization
- token_service: JWT token handling
- password_service: Password hashing and verification
- security_service: Encryption and secure token generation
"""

# Core authentication functionality
from .auth_service import (
    get_current_active_user,
    check_permissions,
    oauth2_scheme
)

# Token handling functionality
from .token_service import (
    create_access_token,
    verify_token
)

# Password handling functionality
from .password_service import (
    verify_password,
    get_password_hash,
    pwd_context
)

# Security functionality
from .security_service import (
    encrypt_data,
    decrypt_data,
    generate_api_key,
    generate_secure_token
)

__all__ = [
    # Auth service
    "get_current_active_user",
    "check_permissions",
    "oauth2_scheme",
    
    # Token service
    "create_access_token",
    "verify_token",
    
    # Password service
    "verify_password",
    "get_password_hash",
    "pwd_context",
    
    # Security service
    "encrypt_data",
    "decrypt_data",
    "generate_api_key",
    "generate_secure_token"
] 