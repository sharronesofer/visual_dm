"""
Core authentication services including user authentication, authorization,
and permission checking.
"""

from typing import Optional, Any, Dict, List
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
import os
import logging

from backend.infrastructure.auth.auth_user.services.token_service import (
    verify_token, create_access_token, create_refresh_token
)

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

logger = logging.getLogger(__name__)


class AuthService:
    """
    Authentication service class providing user authentication, authorization,
    and permission checking functionality.
    """
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def authenticate_user(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with email and password.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            User data if authentication successful, None otherwise
        """
        # TODO: Implement database user lookup and password verification
        # from backend.infrastructure.auth.auth_user.services.password_service import verify_password
        # from backend.infrastructure.auth.auth_user.models.user_models import User
        # from sqlalchemy import select
        # 
        # result = await self.db_session.execute(
        #     select(User).filter(User.email == email)
        # )
        # user = result.scalar_one_or_none()
        # 
        # if not user or not verify_password(password, user.password_hash):
        #     return None
        # 
        # return user
        
        # SECURITY: Only allow test credentials in development/test environments
        if os.environ.get("ENVIRONMENT") in ["test", "development"] and os.environ.get("ALLOW_TEST_CREDENTIALS") == "true":
            if email == "test@example.com" and password == "test123":
                logger.warning("Using test credentials - only allowed in development/test environments")
                return {
                    "id": UUID("12345678-1234-5678-9012-123456789012"),
                    "email": email,
                    "is_active": True,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
        
        # In production or when test credentials are disabled, return None
        logger.info(f"Authentication failed for {email}")
        return None

    async def create_user(self, email: str, password: str) -> Dict[str, Any]:
        """
        Create a new user account.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Created user data
        """
        # TODO: Implement user creation with database
        # from backend.infrastructure.auth.auth_user.services.password_service import hash_password
        # from backend.infrastructure.auth.auth_user.models.user_models import User
        
        # hashed_password = hash_password(password)
        # user = User(email=email, password_hash=hashed_password)
        # self.db_session.add(user)
        # await self.db_session.commit()
        # await self.db_session.refresh(user)
        # return user
        
        # Placeholder implementation
        user_id = UUID("12345678-1234-5678-9012-123456789012")
        return {
            "id": user_id,
            "email": email,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

    def check_permissions(self, user: Dict[str, Any], required_permissions: List[str]) -> bool:
        """
        Check if user has all required permissions.
        
        Args:
            user: User data dictionary
            required_permissions: List of permission strings required
            
        Returns:
            True if user has all permissions, False otherwise
        """
        user_permissions = user.get("permissions", [])
        user_roles = user.get("roles", [])
        
        # Check direct permissions
        for permission in required_permissions:
            if permission in user_permissions:
                continue
            
            # Check role-based permissions
            # TODO: Implement role-permission lookup from database
            # For now, assume admin role has all permissions
            if "admin" in user_roles:
                continue
                
            return False
        
        return True


class TokenService:
    """
    Token service class providing JWT token management functionality.
    """
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        return create_access_token(data, expires_delta)
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a JWT refresh token.""" 
        return create_refresh_token(data)
    
    def decode_access_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify an access token."""
        return verify_token(token, token_type="access")
    
    def decode_refresh_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decode and verify a refresh token."""
        return verify_token(token, token_type="refresh")


async def get_current_active_user(
    token: str = Depends(oauth2_scheme)
) -> Dict[str, Any]:
    """
    Dependency to get the current authenticated and active user.
    
    Args:
        token: The JWT token from the request
        
    Returns:
        User data dictionary
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials (no subject)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # TODO: Implement database user lookup when database integration is ready
    # Example implementation:
    # from backend.infrastructure.database import get_async_db
    # from backend.infrastructure.shared.models import User
    # 
    # user = await session.get(User, user_id)
    # if user is None:
    #     raise HTTPException(status_code=404, detail="User not found")
    # if not user.is_active:
    #     raise HTTPException(status_code=400, detail="Inactive user")
    # return user
    
    # Placeholder: returning enriched payload until DB integration
    return {
        "id": user_id,
        "email": payload.get("email"),
        "is_active": True,
        "roles": payload.get("roles", []),
        **payload
    }


def check_permissions(user: Dict[str, Any], required_permissions: List[str]) -> bool:
    """
    Check if user has all required permissions.
    
    Args:
        user: User data dictionary
        required_permissions: List of permission strings required
        
    Returns:
        True if user has all permissions, False otherwise
    """
    user_permissions = user.get("permissions", [])
    user_roles = user.get("roles", [])
    
    # Check direct permissions
    for permission in required_permissions:
        if permission in user_permissions:
            continue
        
        # Check role-based permissions
        # TODO: Implement role-permission lookup from database
        # For now, assume admin role has all permissions
        if "admin" in user_roles:
            continue
            
        return False
    
    return True


def require_permissions(required_permissions: List[str]):
    """
    Decorator factory for endpoints that require specific permissions.
    
    Args:
        required_permissions: List of permission strings required
        
    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract user from kwargs or dependencies
            user = kwargs.get("current_user")
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            if not check_permissions(user, required_permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {required_permissions}"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def check_user_character_access(
    user_id: str,
    character_id: str,
    permission: str = "read"
) -> bool:
    """
    Check if a user has access to a specific character.
    
    Args:
        user_id: ID of the user
        character_id: ID of the character
        permission: Type of permission needed (read, write, admin)
        
    Returns:
        True if user has access, False otherwise
    """
    # TODO: Implement character-user relationship check
    # This would integrate with the auth_utils relationship functions
    # from backend.systems.utils import check_permission
    # return await check_permission(user_id, character_id, permission)
    
    # Placeholder implementation
    return True


async def get_user_accessible_characters(user_id: str) -> List[str]:
    """
    Get list of character IDs that a user has access to.
    
    Args:
        user_id: ID of the user
        
    Returns:
        List of character IDs
    """
    # TODO: Implement character access lookup
    # from backend.systems.utils import get_user_characters
    # characters = await get_user_characters(user_id)
    # return [char["target_id"] for char in characters]
    
    # Placeholder implementation
    return [] 