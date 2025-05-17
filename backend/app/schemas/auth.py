from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

from .base import BaseSchema, IDSchema, TimestampSchema


class TokenSchema(BaseSchema):
    """Token response schema"""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field("bearer", description="Token type")


class TokenPayload(BaseSchema):
    """Token payload schema"""
    sub: Optional[str] = Field(None, description="Subject (user ID)")
    exp: Optional[datetime] = Field(None, description="Expiration time")


class UserBase(BaseSchema):
    """Base user schema"""
    email: EmailStr = Field(..., description="User email")
    username: str = Field(..., description="Username", min_length=3, max_length=50)
    is_active: bool = Field(True, description="Is user active")
    is_superuser: bool = Field(False, description="Is user a superuser")


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., description="Password", min_length=8)
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "email": "user@example.com",
                "username": "testuser",
                "password": "password123",
                "is_active": True,
                "is_superuser": False
            }
        }
    }


class UserUpdate(BaseSchema):
    """User update schema"""
    email: Optional[EmailStr] = Field(None, description="User email")
    username: Optional[str] = Field(None, description="Username", min_length=3, max_length=50)
    password: Optional[str] = Field(None, description="Password", min_length=8)
    is_active: Optional[bool] = Field(None, description="Is user active")
    is_superuser: Optional[bool] = Field(None, description="Is user a superuser")


class User(UserBase, IDSchema, TimestampSchema):
    """Complete user schema"""
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "username": "testuser",
                "is_active": True,
                "is_superuser": False,
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-02T00:00:00"
            }
        }
    }


class UserInDB(User):
    """User in database schema with hashed password"""
    hashed_password: str = Field(..., description="Hashed password")


class LoginRequest(BaseSchema):
    """Login request schema"""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "username": "user@example.com",
                "password": "password123"
            }
        }
    } 