"""
Token management services for authentication.

This module provides functions for creating, verifying, and managing JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from jose import JWTError, jwt
import secrets
import os
import logging

# Configuration for JWT
from backend.infrastructure.shared.config import config

TOKEN_TYPE_ACCESS = "access"
TOKEN_TYPE_REFRESH = "refresh"

logger = logging.getLogger(__name__)

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    subject: Optional[Any] = None
) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time
        subject: Token subject (usually user ID)
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    to_encode.update({"type": TOKEN_TYPE_ACCESS})
    
    if subject:
        to_encode.update({"sub": str(subject)})
        
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Use configured expiration if available, else default
        try:
            default_expire_minutes = config.jwt.access_token_expires / 60 
        except (AttributeError, TypeError):
            default_expire_minutes = 15  # 15 minutes default
        expire = datetime.utcnow() + timedelta(minutes=default_expire_minutes)
        
    # Convert datetime to timestamp for JWT
    to_encode.update({
        "exp": int(expire.timestamp()), 
        "iat": int(datetime.utcnow().timestamp())
    })
    
    try:
        return jwt.encode(
            to_encode,
            config.jwt.secret_key,
            algorithm=config.jwt.algorithm
        )
    except AttributeError:
        # Configuration error - should not use fallback in production
        if os.environ.get("ENVIRONMENT") == "production":
            raise Exception("JWT configuration not properly initialized - cannot create tokens")
        
        # Development fallback with warning
        logger.warning("JWT config not available, using development fallback")
        return jwt.encode(
            to_encode,
            os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32)),
            algorithm="HS256"
        )

def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
    subject: Optional[Any] = None
) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: The data to encode in the token
        expires_delta: Optional custom expiration time
        subject: Token subject (usually user ID)
        
    Returns:
        Encoded JWT refresh token
    """
    to_encode = data.copy()
    to_encode.update({"type": TOKEN_TYPE_REFRESH})
    
    if subject:
        to_encode.update({"sub": str(subject)})
        
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Refresh tokens should have longer expiration (7 days default)
        expire = datetime.utcnow() + timedelta(days=7)
        
    # Convert datetime to timestamp for JWT
    to_encode.update({
        "exp": int(expire.timestamp()), 
        "iat": int(datetime.utcnow().timestamp())
    })
    
    try:
        return jwt.encode(
            to_encode,
            config.jwt.secret_key,
            algorithm=config.jwt.algorithm
        )
    except AttributeError:
        # Configuration error - should not use fallback in production
        if os.environ.get("ENVIRONMENT") == "production":
            raise Exception("JWT configuration not properly initialized - cannot create tokens")
        
        # Development fallback with warning
        logger.warning("JWT config not available, using development fallback")
        return jwt.encode(
            to_encode,
            os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32)),
            algorithm="HS256"
        )

def create_token_pair(
    data: Dict[str, Any],
    subject: Optional[Any] = None
) -> Tuple[str, str]:
    """
    Create both access and refresh tokens for a user.
    
    Args:
        data: The data to encode in the tokens
        subject: Token subject (usually user ID)
        
    Returns:
        Tuple of (access_token, refresh_token)
    """
    access_token = create_access_token(data, subject=subject)
    refresh_token = create_refresh_token(data, subject=subject)
    return access_token, refresh_token

def verify_token(token: str, token_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
        token_type: Optional token type to verify (access, refresh)
        
    Returns:
        Decoded payload if valid, None if invalid
    """
    try:
        # Try with configured settings first
        try:
            payload = jwt.decode(
                token,
                config.jwt.secret_key,
                algorithms=[config.jwt.algorithm]
            )
        except AttributeError:
            # Configuration error - should not use fallback in production
            if os.environ.get("ENVIRONMENT") == "production":
                raise Exception("JWT configuration not properly initialized - cannot verify tokens")
            
            # Development fallback with warning
            logger.warning("JWT config not available, using development fallback for token verification")
            payload = jwt.decode(
                token,
                os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32)),
                algorithms=["HS256"]
            )
        
        # Check token type if specified
        if token_type and payload.get("type") != token_type:
            return None
            
        # Check if token is not expired
        exp = payload.get("exp")
        if exp and int(datetime.utcnow().timestamp()) > exp:
            return None
            
        return payload
    except JWTError:
        # Consider logging the error here for debugging
        return None

def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Create a new access token using a valid refresh token.
    
    Args:
        refresh_token: The refresh token to use
        
    Returns:
        New access token if refresh token is valid, None otherwise
    """
    payload = verify_token(refresh_token, token_type=TOKEN_TYPE_REFRESH)
    if not payload:
        return None
    
    # Remove token-specific fields and create new access token
    user_data = {k: v for k, v in payload.items() 
                 if k not in ["exp", "iat", "type"]}
    
    return create_access_token(user_data, subject=payload.get("sub"))

def decode_token_without_verification(token: str) -> Optional[Dict[str, Any]]:
    """
    Decode a token without verification (useful for debugging).
    
    Args:
        token: The JWT token to decode
        
    Returns:
        Decoded payload if decodable, None if malformed
    """
    try:
        return jwt.get_unverified_claims(token)
    except JWTError:
        return None 