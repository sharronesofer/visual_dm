"""
Equipment System Models

This module defines the data models for the equipment system according to
the Development Bible standards.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB

from sqlalchemy.orm import relationship
from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin
from backend.infrastructure.shared.models import SharedBaseModel

class EquipmentBaseModel(SharedBaseModel):
    """Base model for equipment system with common fields"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

class EquipmentModel(EquipmentBaseModel):
    """Primary model for equipment system"""
    
    name: str = Field(..., description="Name of the equipment")
    description: Optional[str] = Field(None, description="Description of the equipment")
    status: str = Field(default="active", description="Status of the equipment")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class EquipmentEntity(Base):
    """SQLAlchemy entity for equipment system"""
    
    __tablename__ = f"equipment_entities"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(50), default="active", index=True)
    properties = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<EquipmentEntity(id={self.id}, name={self.name})>"

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

# Backward compatibility alias
Equipment = EquipmentModel

class EquipmentDurabilityLog(Base):
    """SQLAlchemy entity for equipment durability logging"""
    
    __tablename__ = "equipment_durability_logs"
    
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, nullable=False, index=True)
    previous_durability = Column(Float, nullable=False)
    new_durability = Column(Float, nullable=False)
    change_amount = Column(Float, nullable=False)
    change_reason = Column(String(100), nullable=False)
    event_details = Column(JSONB, default=dict)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<EquipmentDurabilityLog(id={self.id}, equipment_id={self.equipment_id})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "previous_durability": self.previous_durability,
            "new_durability": self.new_durability,
            "change_amount": self.change_amount,
            "change_reason": self.change_reason,
            "event_details": self.event_details or {},
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }

class EquipmentSet(Base):
    """SQLAlchemy entity for equipment sets"""
    
    __tablename__ = "equipment_sets"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    item_ids = Column(JSONB, default=list)  # List of item IDs in this set
    set_bonuses = Column(JSONB, default=dict)  # Dict mapping piece count to bonuses
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<EquipmentSet(id={self.id}, name={self.name})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "item_ids": self.item_ids or [],
            "set_bonuses": self.set_bonuses or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }

    @classmethod
    def get_by_id(cls, set_id: int):
        """Get equipment set by ID"""
        # This would need a proper session, but for now return None
        return None

    def get_service_modifier(self, service_name: str, default: float = 1.0) -> float:
        """Get service modifier for this set"""
        # Placeholder implementation
        return default

# Request/Response Models
class CreateEquipmentRequest(BaseModel):
    """Request model for creating equipment"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UpdateEquipmentRequest(BaseModel):
    """Request model for updating equipment"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    properties: Optional[Dict[str, Any]] = None

class EquipmentResponse(BaseModel):
    """Response model for equipment"""
    
    id: UUID
    name: str
    description: Optional[str]
    status: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class EquipmentListResponse(BaseModel):
    """Response model for equipment lists"""
    
    items: List[EquipmentResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
