"""
Security utilities for authentication, authorization, and encryption.
Provides functions for user authentication, token management, and data encryption.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from .config_utils import config
from .error_utils import AuthenticationError, AuthorizationError

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate a password hash."""
    return pwd_context.hash(password)

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        config.security.secret_key,
        algorithm=config.security.algorithm
    )

def verify_token(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Verify and decode a JWT token."""
    try:
        payload = jwt.decode(
            token,
            config.security.secret_key,
            algorithms=[config.security.algorithm]
        )
        return payload
    except JWTError:
        raise AuthenticationError("Invalid authentication credentials")

def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """Get the current authenticated user from the token."""
    try:
        payload = verify_token(token)
        user_id: str = payload.get("sub")
        if user_id is None:
            raise AuthenticationError("Invalid authentication credentials")
        return {"id": user_id, **payload}
    except JWTError:
        raise AuthenticationError("Invalid authentication credentials")

def check_permissions(user, required_permissions: list) -> None:
    """Check if user has required permissions using RBAC."""
    missing_permissions = [
        perm for perm in required_permissions
        if not user.has_permission(perm)
    ]
    if missing_permissions:
        raise AuthorizationError(
            "Insufficient permissions",
            details={"missing_permissions": missing_permissions}
        )

def encrypt_data(data: str) -> str:
    """Encrypt sensitive data."""
    # Implementation depends on specific encryption requirements
    # This is a placeholder for the actual encryption logic
    return data

def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data."""
    # Implementation depends on specific encryption requirements
    # This is a placeholder for the actual decryption logic
    return encrypted_data

def generate_api_key() -> str:
    """Generate a secure API key."""
    import secrets
    import string
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(40)) 