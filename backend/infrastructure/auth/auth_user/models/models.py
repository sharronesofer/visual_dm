"""
Auth_User System Models

This module defines the data models for the auth_user system according to
the Development Bible standards.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from backend.infrastructure.shared.models import BaseModel as SharedBaseModel

Base = declarative_base()


class Auth_UserBaseModel(SharedBaseModel):
    """Base model for auth_user system with common fields"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class Auth_UserModel(Auth_UserBaseModel):
    """Primary model for auth_user system"""
    
    name: str = Field(..., description="Name of the auth_user")
    description: Optional[str] = Field(None, description="Description of the auth_user")
    status: str = Field(default="active", description="Status of the auth_user")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class Auth_UserEntity(Base):
    """SQLAlchemy entity for auth_user system"""
    
    __tablename__ = f"auth_user_entities"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(50), default="active", index=True)
    properties = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<Auth_UserEntity(id={self.id}, name={self.name})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "status": self.status,
            "properties": self.properties or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }


# Request/Response Models
class CreateAuth_UserRequest(BaseModel):
    """Request model for creating auth_user"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UpdateAuth_UserRequest(BaseModel):
    """Request model for updating auth_user"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    properties: Optional[Dict[str, Any]] = None


class Auth_UserResponse(BaseModel):
    """Response model for auth_user"""
    
    id: UUID
    name: str
    description: Optional[str]
    status: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class Auth_UserListResponse(BaseModel):
    """Response model for auth_user lists"""
    
    items: List[Auth_UserResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
