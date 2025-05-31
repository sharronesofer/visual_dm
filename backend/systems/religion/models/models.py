"""
Religion System Models

This module defines the data models for the religion system according to
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

Base = declarative_base()


class ReligionBaseModel(BaseModel):
    """Base model for religion system with common fields"""
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ReligionModel(ReligionBaseModel):
    """Primary model for religion system"""
    
    name: str = Field(..., description="Name of the religion")
    description: Optional[str] = Field(None, description="Description of the religion")
    status: str = Field(default="active", description="Status of the religion")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ReligionEntity(Base):
    """SQLAlchemy entity for religion system"""
    
    __tablename__ = f"religion_entities"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(50), default="active", index=True)
    properties = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<ReligionEntity(id={self.id}, name={self.name})>"

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


# Request/Response Models with Unity Frontend Compatibility
class CreateReligionRequest(BaseModel):
    """Request model for creating religion - Unity frontend compatible"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    
    # Unity frontend expected fields
    type: Optional[str] = Field("Monotheistic", description="Religion type (Monotheistic, Polytheistic, etc.)")
    origin_story: Optional[str] = Field(None, description="Origin story of the religion")
    core_beliefs: Optional[List[str]] = Field(default_factory=list, description="Core beliefs")
    tenets: Optional[List[str]] = Field(default_factory=list, description="Religious tenets")
    practices: Optional[List[str]] = Field(default_factory=list, description="Religious practices")
    holy_places: Optional[List[str]] = Field(default_factory=list, description="Holy places")
    sacred_texts: Optional[List[str]] = Field(default_factory=list, description="Sacred texts")
    clergy_structure: Optional[str] = Field(None, description="Clergy organizational structure")
    
    # Legacy field for backward compatibility
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UpdateReligionRequest(BaseModel):
    """Request model for updating religion - Unity frontend compatible"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    
    # Unity frontend expected fields
    type: Optional[str] = Field(None, description="Religion type")
    origin_story: Optional[str] = Field(None, description="Origin story")
    core_beliefs: Optional[List[str]] = Field(None, description="Core beliefs")
    tenets: Optional[List[str]] = Field(None, description="Religious tenets")
    practices: Optional[List[str]] = Field(None, description="Religious practices")
    holy_places: Optional[List[str]] = Field(None, description="Holy places")
    sacred_texts: Optional[List[str]] = Field(None, description="Sacred texts")
    clergy_structure: Optional[str] = Field(None, description="Clergy structure")
    
    # Legacy field for backward compatibility
    properties: Optional[Dict[str, Any]] = None


class ReligionResponse(BaseModel):
    """Response model for religion - Unity frontend compatible"""
    
    model_config = ConfigDict(from_attributes=True)
    
    # Core fields
    id: UUID
    name: str
    description: Optional[str] = None
    status: str = "active"
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool = True
    
    # Unity frontend expected fields
    type: str = Field(default="Monotheistic", description="Religion type")
    origin_story: Optional[str] = Field(None, description="Origin story")
    core_beliefs: List[str] = Field(default_factory=list, description="Core beliefs")
    practices: List[str] = Field(default_factory=list, description="Religious practices")
    clergy_structure: Optional[str] = Field(None, description="Clergy structure")
    holy_texts: List[str] = Field(default_factory=list, description="Sacred texts")
    deities: List[Dict[str, Any]] = Field(default_factory=list, description="Associated deities")
    followers_count: int = Field(default=0, description="Number of followers")
    influence_regions: List[str] = Field(default_factory=list, description="Regions of influence")
    
    # Legacy field for custom properties
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    @classmethod
    def from_entity(cls, entity: ReligionEntity) -> "ReligionResponse":
        """Create response from SQLAlchemy entity with Unity field mapping"""
        
        # Extract Unity fields from properties or use defaults
        props = entity.properties or {}
        
        return cls(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            status=entity.status,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_active=entity.is_active,
            
            # Map Unity fields from properties
            type=props.get("type", "Monotheistic"),
            origin_story=props.get("origin_story"),
            core_beliefs=props.get("core_beliefs", []),
            practices=props.get("practices", []),
            clergy_structure=props.get("clergy_structure"),
            holy_texts=props.get("holy_texts", []),
            deities=props.get("deities", []),
            followers_count=props.get("followers_count", 0),
            influence_regions=props.get("influence_regions", []),
            
            properties=props
        )


class ReligionListResponse(BaseModel):
    """Response model for religion lists"""
    
    items: List[ReligionResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


# Sub-resource models for Unity frontend compatibility
class DeityRequest(BaseModel):
    """Request model for creating/updating deities"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    domain: Optional[str] = None
    alignment: Optional[str] = None
    symbols: Optional[List[str]] = Field(default_factory=list)
    holy_days: Optional[List[str]] = Field(default_factory=list)
    powers: Optional[List[str]] = Field(default_factory=list)


class DeityResponse(BaseModel):
    """Response model for deities"""
    
    id: UUID
    name: str
    description: Optional[str]
    domain: Optional[str]
    alignment: Optional[str]
    symbols: List[str]
    holy_days: List[str]
    powers: List[str]
    worshiper_count: int = 0
    religion_id: UUID


class ReligiousPracticeRequest(BaseModel):
    """Request model for religious practices"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    frequency: Optional[str] = None
    participants: Optional[int] = 0
    location_type: Optional[str] = None
    required_items: Optional[List[str]] = Field(default_factory=list)


class ReligiousPracticeResponse(BaseModel):
    """Response model for religious practices"""
    
    id: UUID
    name: str
    description: Optional[str]
    frequency: Optional[str]
    participants: int
    location_type: Optional[str]
    required_items: List[str]
    religion_id: UUID


class ReligiousEventRequest(BaseModel):
    """Request model for religious events"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    event_type: Optional[str] = None
    date: Optional[datetime] = None
    duration: Optional[int] = 1
    location: Optional[str] = None
    participants: Optional[List[str]] = Field(default_factory=list)


class ReligiousEventResponse(BaseModel):
    """Response model for religious events"""
    
    id: UUID
    name: str
    description: Optional[str]
    event_type: Optional[str]
    date: datetime
    duration: int
    location: Optional[str]
    participants: List[str]
    religion_id: UUID


class ReligiousInfluenceRequest(BaseModel):
    """Request model for religious influence"""
    
    influence_level: Optional[float] = 0.0
    follower_count: Optional[int] = 0
    temples_count: Optional[int] = 0
    clergy_count: Optional[int] = 0


class ReligiousInfluenceResponse(BaseModel):
    """Response model for religious influence"""
    
    id: UUID
    religion_id: UUID
    region_id: str
    influence_level: float
    follower_count: int
    temples_count: int
    clergy_count: int
    last_updated: datetime
