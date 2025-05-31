"""
Population System Models

This module defines the data models for the population system according to
the Development Bible standards.
"""

from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from backend.infrastructure.shared.models import BaseModel as SharedBaseModel

Base = declarative_base()


class PopulationBaseModel(SharedBaseModel):
    """Base model for population system with common fields"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class PopulationModel(PopulationBaseModel):
    """Primary model for population system"""
    
    name: str = Field(..., description="Name of the population")
    description: Optional[str] = Field(None, description="Description of the population")
    status: str = Field(default="active", description="Status of the population")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class PopulationEntity(Base):
    """SQLAlchemy entity for population system"""
    
    __tablename__ = f"population_entities"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    status = Column(String(50), default="active", index=True)
    properties = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)

    def __repr__(self):
        return f"<PopulationEntity(id={self.id}, name={self.name})>"

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
class CreatePopulationRequest(BaseModel):
    """Request model for creating population"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UpdatePopulationRequest(BaseModel):
    """Request model for updating population"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    properties: Optional[Dict[str, Any]] = None


class POIState(str, Enum):
    """POI population states for state management system"""
    TINY = "tiny"           # 1-100 residents
    SMALL = "small"         # 100-500 residents  
    MEDIUM = "medium"       # 500-2000 residents
    LARGE = "large"         # 2000-8000 residents
    HUGE = "huge"           # 8000+ residents
    DECLINING = "declining" # Any size but shrinking
    ABANDONED = "abandoned" # 0 residents, ruins only


class PopulationResponse(BaseModel):
    """Enhanced population response with all new properties"""
    id: UUID
    name: str
    description: Optional[str] = None
    entity_type: Optional[str] = None  # Make optional since it's not in all entities
    status: str
    properties: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Enhanced computed properties for Task 45 functionality
    population_count: Optional[int] = None
    capacity: Optional[int] = None
    growth_rate: Optional[float] = None
    state: Optional[str] = None
    previous_state: Optional[str] = None
    
    # War impact properties
    casualties: Optional[int] = None
    refugees: Optional[int] = None
    last_war_impact: Optional[Dict[str, Any]] = None
    last_war_date: Optional[str] = None
    
    # Catastrophe impact properties  
    catastrophe_deaths: Optional[int] = None
    catastrophe_displaced: Optional[int] = None
    catastrophe_injured: Optional[int] = None
    last_catastrophe_impact: Optional[Dict[str, Any]] = None
    last_catastrophe_date: Optional[str] = None
    
    # Resource shortage properties
    shortage_deaths: Optional[int] = None
    shortage_migrants: Optional[int] = None
    last_shortage_impact: Optional[Dict[str, Any]] = None
    last_shortage_date: Optional[str] = None
    
    # Migration properties
    last_migration_in: Optional[int] = None
    last_migration_out: Optional[int] = None
    last_migration_date: Optional[str] = None
    
    # State management properties
    state_history: Optional[List[Dict[str, Any]]] = None
    state_transition_date: Optional[str] = None
    
    # Resource and modifier properties
    resources: Optional[Dict[str, float]] = None
    resource_modifier: Optional[float] = None
    
    model_config = ConfigDict(from_attributes=True)
        
    @classmethod
    def from_orm(cls, obj):
        """Create response from ORM entity with computed properties"""
        data = {
            "id": obj.id,
            "name": obj.name,
            "description": obj.description,
            "entity_type": getattr(obj, 'entity_type', 'population'),  # Default to 'population'
            "status": obj.status,
            "properties": obj.properties or {},
            "is_active": obj.is_active,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at
        }
        
        # Extract computed properties from the properties dict
        props = obj.properties or {}
        
        # Population properties
        data["population_count"] = props.get("population_count")
        data["capacity"] = props.get("capacity")
        data["growth_rate"] = props.get("growth_rate")
        data["state"] = props.get("state")
        data["previous_state"] = props.get("previous_state")
        
        # War impact properties
        data["casualties"] = props.get("casualties")
        data["refugees"] = props.get("refugees")
        data["last_war_impact"] = props.get("last_war_impact")
        data["last_war_date"] = props.get("last_war_date")
        
        # Catastrophe impact properties
        data["catastrophe_deaths"] = props.get("catastrophe_deaths")
        data["catastrophe_displaced"] = props.get("catastrophe_displaced")
        data["catastrophe_injured"] = props.get("catastrophe_injured")
        data["last_catastrophe_impact"] = props.get("last_catastrophe_impact")
        data["last_catastrophe_date"] = props.get("last_catastrophe_date")
        
        # Resource shortage properties
        data["shortage_deaths"] = props.get("shortage_deaths")
        data["shortage_migrants"] = props.get("shortage_migrants")
        data["last_shortage_impact"] = props.get("last_shortage_impact")
        data["last_shortage_date"] = props.get("last_shortage_date")
        
        # Migration properties
        data["last_migration_in"] = props.get("last_migration_in")
        data["last_migration_out"] = props.get("last_migration_out")
        data["last_migration_date"] = props.get("last_migration_date")
        
        # State management properties
        data["state_history"] = props.get("state_history")
        data["state_transition_date"] = props.get("state_transition_date")
        
        # Resource properties
        data["resources"] = props.get("resources")
        data["resource_modifier"] = props.get("resource_modifier")
        
        return cls(**data)


class PopulationListResponse(BaseModel):
    """Response model for population lists"""
    
    items: List[PopulationResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool
