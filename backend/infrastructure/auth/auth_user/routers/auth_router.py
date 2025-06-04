"""
Core Authentication API Router

Provides the essential authentication endpoints:
- POST /auth/token - OAuth2-compatible token authentication
- POST /auth/register - User registration
- POST /auth/logout - User logout
- GET /auth/me - Get current user profile
- PUT /auth/me - Update current user profile
- POST /auth/refresh - Refresh access token
- POST /auth/password/reset - Password reset request
- POST /auth/password/reset/confirm - Confirm password reset

Implements Development Bible requirements for JWT bearer tokens,
OAuth2 compatibility, and 24-hour token expiration.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

from backend.infrastructure.auth.auth_user.services.auth_service import AuthService, TokenService
from backend.infrastructure.auth.auth_user.services.password_service import PasswordService
from backend.infrastructure.auth.auth_user.repositories import UserRepository, RoleRepository
from backend.infrastructure.auth.auth_user.schemas.auth_schemas import (
    UserCreate, UserResponse, UserUpdate, 
    TokenResponse, RefreshTokenRequest,
    PasswordResetRequest, PasswordResetConfirm
)
from backend.infrastructure.auth.auth_user.models.user_models import User
from backend.infrastructure.database import get_async_db, get_db_session
from backend.infrastructure.shared.exceptions import Auth_UserNotFoundError, Auth_UserValidationError

# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Initialize rate limiter for authentication endpoints
limiter = Limiter(key_func=get_remote_address)

# Initialize router
router = APIRouter(prefix="/auth", tags=["authentication"])

# Dependency injection for database session
async def get_db() -> AsyncSession:
    """Get database session for dependency injection."""
    async for session in get_async_db():
        yield session

# Use get_db_session as an alias for the dependency
get_db_session = get_db

# Dependency for getting current user from token
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db_session: AsyncSession = Depends(get_db_session)
) -> User:
    """Get current authenticated user from JWT token."""
    try:
        token_service = TokenService()
        payload = token_service.decode_access_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise Auth_UserNotFoundError("Invalid token: no user ID")
        
        user_repo = UserRepository(db_session)
        user = await user_repo.get_user_by_id(UUID(user_id))
        
        if not user:
            raise Auth_UserNotFoundError("User not found")
        
        if not user.is_active:
            raise Auth_UserNotFoundError("User account is disabled")
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/token", response_model=TokenResponse)
@limiter.limit("5/minute")  # Allow only 5 login attempts per minute per IP
async def login_for_access_token(
    request: Request,  # Required for rate limiting
    form_data: OAuth2PasswordRequestForm = Depends(),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    OAuth2-compatible token endpoint for user authentication.
    
    Creates access and refresh tokens with 24-hour expiration.
    Compatible with OAuth2 password flow.
    """
    try:
        # Initialize services
        auth_service = AuthService(db_session)
        token_service = TokenService()
        
        # Authenticate user
        user = await auth_service.authenticate_user(
            email=form_data.username,  # OAuth2 uses 'username' field
            password=form_data.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create tokens
        access_token = token_service.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(hours=24)  # 24-hour expiration per Dev Bible
        )
        
        refresh_token = token_service.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=24 * 3600,  # 24 hours in seconds
            refresh_token=refresh_token,
            user_id=str(user["id"])
        )
        
    except Auth_UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication service error"
        )

@router.post("/register", response_model=UserResponse)
@limiter.limit("3/hour")  # Allow only 3 registrations per hour per IP
async def register_user(
    request: Request,  # Required for rate limiting
    user_data: UserCreate,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Register a new user account.
    
    Creates a new user with hashed password and default permissions.
    """
    try:
        auth_service = AuthService(db_session)
        
        # Check if user already exists
        user_repo = UserRepository(db_session)
        existing_user = await user_repo.get_user_by_email(user_data.email)
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        user = await auth_service.create_user(
            email=user_data.email,
            password=user_data.password
        )
        
        return UserResponse(
            id=str(user["id"]),
            email=user["email"],
            is_active=user["is_active"],
            created_at=user["created_at"],
            updated_at=user["updated_at"]
        )
        
    except Auth_UserValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="User registration failed"
        )

@router.post("/logout")
async def logout_user(
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Logout current user.
    
    In a full implementation, this would invalidate the token.
    For now, returns success (client should discard token).
    """
    # TODO: Implement token blacklisting for secure logout
    # For now, client-side token removal is sufficient
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile information."""
    return UserResponse(
        id=str(current_user.id),
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_db_session)
):
    """Update current user profile information."""
    try:
        user_repo = UserRepository(db_session)
        
        # Build update data (only include non-None fields)
        update_data = {}
        if user_update.email is not None:
            # Check if new email is already taken
            existing_user = await user_repo.get_user_by_email(user_update.email)
            if existing_user and existing_user.id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already taken"
                )
            update_data["email"] = user_update.email
        
        if user_update.password is not None:
            # Hash new password
            password_service = PasswordService()
            update_data["password_hash"] = password_service.hash_password(user_update.password)
        
        # Update user
        updated_user = await user_repo.update_user(current_user.id, update_data)
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=str(updated_user.id),
            email=updated_user.email,
            is_active=updated_user.is_active,
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Profile update failed"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Refresh access token using refresh token.
    
    Provides new access token with 24-hour expiration.
    """
    try:
        token_service = TokenService()
        
        # Validate refresh token
        payload = token_service.decode_refresh_token(refresh_request.refresh_token)
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Verify user still exists and is active
        user_repo = UserRepository(db_session)
        user = await user_repo.get_user_by_id(UUID(user_id))
        
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        access_token = token_service.create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(hours=24)
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=24 * 3600,
            refresh_token=refresh_request.refresh_token,  # Keep same refresh token
            user_id=str(user.id)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh failed"
        )

@router.post("/password/reset")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Request password reset for user account.
    
    Sends password reset token to user's email.
    """
    try:
        user_repo = UserRepository(db_session)
        user = await user_repo.get_user_by_email(reset_request.email)
        
        if not user:
            # Don't reveal if email exists or not (security)
            return {"message": "If the email exists, a reset link has been sent"}
        
        # Generate reset token
        password_service = PasswordService()
        reset_token = password_service.generate_reset_token()
        
        # Save reset token to user (with expiration)
        await user_repo.update_user(user.id, {
            "password_reset_token": reset_token,
            "password_reset_sent_at": datetime.utcnow()
        })
        
        # TODO: Send email with reset link
        # For now, just return success message
        
        return {"message": "If the email exists, a reset link has been sent"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset request failed"
        )

@router.post("/password/reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    db_session: AsyncSession = Depends(get_db_session)
):
    """
    Confirm password reset with token and set new password.
    """
    try:
        user_repo = UserRepository(db_session)
        password_service = PasswordService()
        
        # Find user by reset token
        # Note: In production, you'd want to add token expiration check
        users = await user_repo.list_users()
        user = None
        for u in users:
            if u.password_reset_token == reset_data.token:
                user = u
                break
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired reset token"
            )
        
        # Check token expiration (1 hour)
        if user.password_reset_sent_at:
            expiry_time = user.password_reset_sent_at + timedelta(hours=1)
            if datetime.utcnow() > expiry_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Reset token has expired"
                )
        
        # Update password and clear reset token
        new_password_hash = password_service.hash_password(reset_data.new_password)
        await user_repo.update_user(user.id, {
            "password_hash": new_password_hash,
            "password_reset_token": None,
            "password_reset_sent_at": None
        })
        
        return {"message": "Password successfully reset"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset confirmation failed"
        )

# Rate limiting placeholder (to be implemented with middleware)
# TODO: Implement rate limiting as specified in Development Bible:
# - 100 requests/minute for standard endpoints  
# - 10 requests/minute for auth endpoints 