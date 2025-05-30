"""
Token management services for authentication.

This module provides functions for creating, verifying, and managing JWT tokens.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt

# Configuration for JWT
from backend.core.config import config

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
    if subject:
        to_encode.update({"sub": str(subject)})
        
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Use configured expiration if available, else default
        default_expire_minutes = config.jwt.access_token_expires / 60 
        expire = datetime.utcnow() + timedelta(minutes=default_expire_minutes)
        
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        config.jwt.secret_key,
        algorithm=config.jwt.algorithm
    )

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: The JWT token to verify
        
    Returns:
        Decoded payload if valid, None if invalid
    """
    try:
        payload = jwt.decode(
            token,
            config.jwt.secret_key,
            algorithms=[config.jwt.algorithm]
        )
        return payload
    except JWTError:
        # Consider logging the error here
        return None 