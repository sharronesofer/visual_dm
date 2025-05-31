"""
Loot System Models

This module defines the data models for the loot system according to
the Development Bible standards.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class LootBaseModel(BaseModel):
    """Base model for loot system with common fields"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class LootModel(LootBaseModel):
    """Primary model for loot system"""
    
    name: str = Field(..., description="Name of the loot")
    description: Optional[str] = Field(None, description="Description of the loot")
    status: str = Field(default="active", description="Status of the loot")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class LootEntity(Base):
    """SQLAlchemy entity for loot system"""
    
    __tablename__ = f"loot_entities"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(50), default="active", index=True)
    properties = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<LootEntity(id={self.id}, name={self.name})>"

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
class CreateLootRequest(BaseModel):
    """Request model for creating loot"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UpdateLootRequest(BaseModel):
    """Request model for updating loot"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    properties: Optional[Dict[str, Any]] = None


class LootResponse(BaseModel):
    """Response model for loot"""
    
    id: UUID
    name: str
    description: Optional[str]
    status: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class LootListResponse(BaseModel):
    """Response model for loot lists"""
    
    items: List[LootResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
