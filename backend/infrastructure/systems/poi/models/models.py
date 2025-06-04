"""
Poi System Models

This module defines the data models for the poi system according to
the Development Bible standards.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB

from sqlalchemy.orm import relationship
from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin
from backend.infrastructure.shared.models import SharedBaseModel

class POIType(str, Enum):
    """Enumeration of Point of Interest types"""
    CITY = "city"
    VILLAGE = "village"
    TOWN = "town"
    SETTLEMENT = "settlement"
    OUTPOST = "outpost"
    FORTRESS = "fortress"
    TEMPLE = "temple"
    MARKET = "market"
    MINE = "mine"
    OTHER = "other"

class POIState(str, Enum):
    """Enumeration of Point of Interest states"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ABANDONED = "abandoned"
    RUINED = "ruined"
    UNDER_CONSTRUCTION = "under_construction"
    DECLINING = "declining"
    GROWING = "growing"
    NORMAL = "normal"
    RUINS = "ruins"
    DUNGEON = "dungeon"
    REPOPULATING = "repopulating"
    SPECIAL = "special"

class POIInteractionType(str, Enum):
    """Enumeration of Point of Interest interaction types"""
    TRADE = "trade"
    DIPLOMACY = "diplomacy"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    QUEST = "quest"
    SOCIAL = "social"
    NEUTRAL = "neutral"

class PoiBaseModel(SharedBaseModel):
    """Base model for poi system with common fields"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)

class PointOfInterest(PoiBaseModel):
    """Enhanced Point of Interest model"""
    
    name: str = Field(..., description="Name of the POI")
    description: Optional[str] = Field(None, description="Description of the POI")
    poi_type: POIType = Field(..., description="Type of POI")
    state: POIState = Field(default=POIState.ACTIVE, description="Current state of the POI")
    interaction_type: POIInteractionType = Field(default=POIInteractionType.NEUTRAL, description="Primary interaction type")
    location_x: Optional[float] = Field(None, description="X coordinate")
    location_y: Optional[float] = Field(None, description="Y coordinate")
    location_z: Optional[float] = Field(None, description="Z coordinate (altitude)")
    region_id: Optional[UUID] = Field(None, description="ID of the containing region")
    faction_id: Optional[UUID] = Field(None, description="ID of the controlling faction")
    population: Optional[int] = Field(None, description="Current population")
    max_population: Optional[int] = Field(None, description="Maximum population capacity")
    resources: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Available resources")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional properties")

class PoiModel(PoiBaseModel):
    """Primary model for poi system (legacy compatibility)"""
    
    name: str = Field(..., description="Name of the poi")
    description: Optional[str] = Field(None, description="Description of the poi")
    status: str = Field(default="active", description="Status of the poi")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class PoiEntity(Base):
    """SQLAlchemy entity for poi system"""
    
    __tablename__ = f"poi_entities"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    poi_type = Column(String(50), nullable=False, index=True)
    state = Column(String(50), default="active", index=True)
    interaction_type = Column(String(50), default="neutral", index=True)
    location_x = Column(Integer)
    location_y = Column(Integer)
    location_z = Column(Integer)
    region_id = Column(SQLAlchemyUUID(as_uuid=True), index=True)
    faction_id = Column(SQLAlchemyUUID(as_uuid=True), index=True)
    population = Column(Integer, default=0)
    max_population = Column(Integer)
    resources = Column(JSONB, default=dict)
    properties = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<PoiEntity(id={self.id}, name={self.name}, type={self.poi_type})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "poi_type": self.poi_type,
            "state": self.state,
            "interaction_type": self.interaction_type,
            "location_x": self.location_x,
            "location_y": self.location_y,
            "location_z": self.location_z,
            "region_id": str(self.region_id) if self.region_id else None,
            "faction_id": str(self.faction_id) if self.faction_id else None,
            "population": self.population,
            "max_population": self.max_population,
            "resources": self.resources or {},
            "properties": self.properties or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }

# Request/Response Models
class CreatePoiRequest(BaseModel):
    """Request model for creating poi"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    poi_type: POIType = Field(..., description="Type of POI")
    interaction_type: Optional[POIInteractionType] = Field(default=POIInteractionType.NEUTRAL)
    location_x: Optional[float] = Field(None)
    location_y: Optional[float] = Field(None)
    location_z: Optional[float] = Field(None)
    region_id: Optional[UUID] = Field(None)
    faction_id: Optional[UUID] = Field(None)
    population: Optional[int] = Field(None, ge=0)
    max_population: Optional[int] = Field(None, ge=0)
    resources: Optional[Dict[str, Any]] = Field(default_factory=dict)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)

class UpdatePoiRequest(BaseModel):
    """Request model for updating poi"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    poi_type: Optional[POIType] = Field(None)
    state: Optional[POIState] = Field(None)
    interaction_type: Optional[POIInteractionType] = Field(None)
    location_x: Optional[float] = Field(None)
    location_y: Optional[float] = Field(None)
    location_z: Optional[float] = Field(None)
    region_id: Optional[UUID] = Field(None)
    faction_id: Optional[UUID] = Field(None)
    population: Optional[int] = Field(None, ge=0)
    max_population: Optional[int] = Field(None, ge=0)
    resources: Optional[Dict[str, Any]] = None
    properties: Optional[Dict[str, Any]] = None

class PoiResponse(BaseModel):
    """Response model for poi"""
    
    id: UUID
    name: str
    description: Optional[str]
    poi_type: POIType
    state: POIState
    interaction_type: POIInteractionType
    location_x: Optional[float]
    location_y: Optional[float]
    location_z: Optional[float]
    region_id: Optional[UUID]
    faction_id: Optional[UUID]
    population: Optional[int]
    max_population: Optional[int]
    resources: Dict[str, Any]
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class PoiListResponse(BaseModel):
    """Response model for poi lists"""
    
    items: List[PoiResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
