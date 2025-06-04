"""
Authentication schemas for request/response validation.

This module provides Pydantic schemas for authentication endpoints.
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr


class UserCreate(UserBase):
    """Schema for user creation requests."""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class UserUpdate(BaseModel):
    """Schema for user update requests."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, description="Password must be at least 8 characters")
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """Schema for user response data."""
    id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: str
    user_id: str


class RefreshTokenRequest(BaseModel):
    """Schema for refresh token requests."""
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset requests."""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Schema for password reset confirmation."""
    token: str
    new_password: str = Field(..., min_length=8, description="Password must be at least 8 characters")


class RoleBase(BaseModel):
    """Base role schema."""
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for role creation."""
    pass


class RoleResponse(RoleBase):
    """Schema for role response."""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PermissionBase(BaseModel):
    """Base permission schema."""
    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    """Schema for permission creation."""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    id: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserWithRoles(UserResponse):
    """User response with roles included."""
    roles: List[RoleResponse] = []


class RoleWithPermissions(RoleResponse):
    """Role response with permissions included."""
    permissions: List[PermissionResponse] = [] 