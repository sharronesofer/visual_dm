"""
Faction System Models

This module defines the data models for the faction system according to
the Development Bible standards.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB, ARRAY

from sqlalchemy.orm import relationship
from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin

# Enums for Alliance system
class AllianceType(str, Enum):
    """Types of alliances between factions"""
    MILITARY = "military"              # Joint defense/offense agreements
    ECONOMIC = "economic"              # Trade agreements and resource sharing
    TEMPORARY_TRUCE = "temporary_truce"  # Cease hostilities temporarily
    MUTUAL_DEFENSE = "mutual_defense"  # Defend each other against attacks
    OFFENSIVE_PACT = "offensive_pact"  # Joint attacks against common enemies
    RESEARCH = "research"              # Share technology and knowledge
    CULTURAL = "cultural"              # Cultural exchange and cooperation

class AllianceStatus(str, Enum):
    """Status of an alliance"""
    PROPOSED = "proposed"              # Alliance has been proposed but not accepted
    ACTIVE = "active"                  # Alliance is currently in effect
    SUSPENDED = "suspended"            # Alliance temporarily suspended
    BETRAYED = "betrayed"              # One member has betrayed the alliance
    DISSOLVED = "dissolved"            # Alliance formally ended
    EXPIRED = "expired"                # Alliance reached its end date

class BetrayalReason(str, Enum):
    """Reasons for betraying an alliance"""
    OPPORTUNITY = "opportunity"        # Better opportunity elsewhere
    PRESSURE = "pressure"              # External pressure from enemies
    AMBITION = "ambition"              # Personal gain and power
    FEAR = "fear"                      # Fear of ally becoming too powerful
    DESPERATION = "desperation"        # Desperate circumstances
    IDEOLOGY = "ideology"              # Ideological differences
    RESOURCES = "resources"            # Need for resources ally won't share

class FactionBaseModel(BaseModel):
    """Base model for faction system with common fields"""
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

class FactionModel(FactionBaseModel):
    """Primary model for faction system"""
    
    name: str = Field(..., description="Name of the faction")
    description: Optional[str] = Field(None, description="Description of the faction")
    status: str = Field(default="active", description="Status of the faction")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Hidden personality attributes (same as NPCs) - Development Bible range 1-10
    hidden_ambition: int = Field(default=5, ge=1, le=10, description="How aggressively the faction pursues growth, power, and territorial expansion")
    hidden_integrity: int = Field(default=5, ge=1, le=10, description="How honorable and trustworthy the faction is in treaties, agreements, and dealings")
    hidden_discipline: int = Field(default=5, ge=1, le=10, description="How organized, methodical, and strategic the faction's operations are")
    hidden_impulsivity: int = Field(default=5, ge=1, le=10, description="How quickly the faction reacts to events without careful planning")
    hidden_pragmatism: int = Field(default=5, ge=1, le=10, description="How willing the faction is to compromise principles for practical gains")
    hidden_resilience: int = Field(default=5, ge=1, le=10, description="How well the faction handles setbacks, defeats, and crises")

class FactionEntity(Base):
    """SQLAlchemy entity for faction system with Development Bible constraints"""
    
    __tablename__ = f"faction_entities"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True, unique=True)  # Bible: unique faction names
    description = Column(Text)
    status = Column(String(50), default="active", index=True)
    properties = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    
    # Hidden personality attributes - Development Bible requires 1-10 range with constraints
    hidden_ambition = Column(Integer, default=5, nullable=False)
    hidden_integrity = Column(Integer, default=5, nullable=False)
    hidden_discipline = Column(Integer, default=5, nullable=False)
    hidden_impulsivity = Column(Integer, default=5, nullable=False)
    hidden_pragmatism = Column(Integer, default=5, nullable=False)
    hidden_resilience = Column(Integer, default=5, nullable=False)
    
    # PostgreSQL check constraints as required by Development Bible
    __table_args__ = (
        CheckConstraint('hidden_ambition >= 1 AND hidden_ambition <= 10', name='chk_hidden_ambition_range'),
        CheckConstraint('hidden_integrity >= 1 AND hidden_integrity <= 10', name='chk_hidden_integrity_range'),
        CheckConstraint('hidden_discipline >= 1 AND hidden_discipline <= 10', name='chk_hidden_discipline_range'),
        CheckConstraint('hidden_impulsivity >= 1 AND hidden_impulsivity <= 10', name='chk_hidden_impulsivity_range'),
        CheckConstraint('hidden_pragmatism >= 1 AND hidden_pragmatism <= 10', name='chk_hidden_pragmatism_range'),
        CheckConstraint('hidden_resilience >= 1 AND hidden_resilience <= 10', name='chk_hidden_resilience_range'),
        CheckConstraint("status IN ('active', 'inactive', 'disbanded')", name='chk_faction_status'),
        CheckConstraint("char_length(name) >= 1 AND char_length(name) <= 255", name='chk_faction_name_length'),
    )

    def __init__(self, **kwargs):
        """Initialize faction entity with proper defaults for testing"""
        # Set defaults for hidden attributes if not provided
        kwargs.setdefault('hidden_ambition', 5)
        kwargs.setdefault('hidden_integrity', 5) 
        kwargs.setdefault('hidden_discipline', 5)
        kwargs.setdefault('hidden_impulsivity', 5)
        kwargs.setdefault('hidden_pragmatism', 5)
        kwargs.setdefault('hidden_resilience', 5)
        kwargs.setdefault('status', 'active')
        kwargs.setdefault('is_active', True)
        kwargs.setdefault('properties', {})
        
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<FactionEntity(id={self.id}, name={self.name})>"

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
            "is_active": self.is_active,
            "hidden_attributes": {
                "hidden_ambition": self.hidden_ambition,
                "hidden_integrity": self.hidden_integrity,
                "hidden_discipline": self.hidden_discipline,
                "hidden_impulsivity": self.hidden_impulsivity,
                "hidden_pragmatism": self.hidden_pragmatism,
                "hidden_resilience": self.hidden_resilience
            }
        }

    def get_hidden_attributes(self) -> Dict[str, int]:
        """Get hidden attributes as a dictionary for compatibility with existing code"""
        return {
            "hidden_ambition": self.hidden_ambition,
            "hidden_integrity": self.hidden_integrity,
            "hidden_discipline": self.hidden_discipline,
            "hidden_impulsivity": self.hidden_impulsivity,
            "hidden_pragmatism": self.hidden_pragmatism,
            "hidden_resilience": self.hidden_resilience
        }

    def update_hidden_attributes(self, attributes: Dict[str, int]) -> None:
        """Update hidden attributes from a dictionary with validation"""
        for attr_name, value in attributes.items():
            if hasattr(self, attr_name) and 1 <= value <= 10:  # Bible range validation
                setattr(self, attr_name, value)

class AllianceEntity(Base):
    """Alliance entity for faction relationships"""
    __tablename__ = "alliances"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False, index=True)
    alliance_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default="proposed", index=True)
    description = Column(Text)
    
    # Member factions
    leader_faction_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    member_faction_ids = Column(ARRAY(SQLAlchemyUUID(as_uuid=True)), default=[], nullable=False)
    
    # Alliance terms
    terms = Column(JSONB, default=dict)
    mutual_obligations = Column(ARRAY(Text), default=[])
    shared_enemies = Column(ARRAY(SQLAlchemyUUID(as_uuid=True)), default=[])
    shared_goals = Column(ARRAY(Text), default=[])
    
    # Duration
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    auto_renew = Column(Boolean, default=False)
    
    # Trust and reliability
    trust_levels = Column(JSONB, default=dict)
    betrayal_risks = Column(JSONB, default=dict)
    reliability_history = Column(JSONB, default=dict)
    
    # Formation details
    triggers = Column(JSONB, default=dict)
    threat_level = Column(Float, default=0.0)
    
    # Benefits
    benefits_shared = Column(JSONB, default=dict)
    military_support_provided = Column(JSONB, default=dict)
    economic_support_provided = Column(JSONB, default=dict)
    
    # Common entity fields
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)
    entity_metadata = Column(JSONB, default=dict)

    def __repr__(self):
        return f"<AllianceEntity(id={self.id}, name={self.name}, type={self.alliance_type})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "name": self.name,
            "alliance_type": self.alliance_type,
            "status": self.status,
            "description": self.description,
            "leader_faction_id": str(self.leader_faction_id),
            "member_faction_ids": [str(fid) for fid in (self.member_faction_ids or [])],
            "terms": self.terms or {},
            "mutual_obligations": self.mutual_obligations or [],
            "shared_enemies": [str(fid) for fid in (self.shared_enemies or [])],
            "shared_goals": self.shared_goals or [],
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "auto_renew": self.auto_renew,
            "trust_levels": self.trust_levels or {},
            "betrayal_risks": self.betrayal_risks or {},
            "reliability_history": self.reliability_history or {},
            "triggers": self.triggers or {},
            "threat_level": self.threat_level,
            "benefits_shared": self.benefits_shared or {},
            "military_support_provided": self.military_support_provided or {},
            "economic_support_provided": self.economic_support_provided or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "entity_metadata": self.entity_metadata or {}
        }

class BetrayalEntity(Base):
    """Betrayal entity for tracking alliance betrayals"""
    __tablename__ = "betrayals"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    alliance_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    betrayer_faction_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    victim_faction_ids = Column(ARRAY(SQLAlchemyUUID(as_uuid=True)), default=[], nullable=False)
    
    betrayal_reason = Column(String(50), nullable=False)
    betrayal_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    
    # Influence factors
    hidden_attributes_influence = Column(JSONB, default=dict)
    external_pressure = Column(JSONB)
    opportunity_details = Column(JSONB)
    
    # Impact
    damage_dealt = Column(JSONB, default=dict)
    trust_impact = Column(JSONB, default=dict)
    reputation_impact = Column(Float, default=0.0)
    
    # Detection
    detected_immediately = Column(Boolean, default=True)
    detection_delay = Column(Integer)
    response_actions = Column(JSONB, default=list)
    
    # Common entity fields
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, nullable=False)
    entity_metadata = Column(JSONB, default=dict)

    def __repr__(self):
        return f"<BetrayalEntity(id={self.id}, alliance={self.alliance_id}, betrayer={self.betrayer_faction_id})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "alliance_id": str(self.alliance_id),
            "betrayer_faction_id": str(self.betrayer_faction_id),
            "victim_faction_ids": [str(fid) for fid in (self.victim_faction_ids or [])],
            "betrayal_reason": self.betrayal_reason,
            "betrayal_type": self.betrayal_type,
            "description": self.description,
            "hidden_attributes_influence": self.hidden_attributes_influence or {},
            "external_pressure": self.external_pressure or {},
            "opportunity_details": self.opportunity_details or {},
            "damage_dealt": self.damage_dealt or {},
            "trust_impact": self.trust_impact or {},
            "reputation_impact": self.reputation_impact,
            "detected_immediately": self.detected_immediately,
            "detection_delay": self.detection_delay,
            "response_actions": self.response_actions or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "entity_metadata": self.entity_metadata or {}
        }

# Request/Response Models
class CreateFactionRequest(BaseModel):
    """Request model for creating faction"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    # Optional hidden attributes (will be randomly generated if not provided) - Bible range 1-10
    hidden_ambition: Optional[int] = Field(None, ge=1, le=10)
    hidden_integrity: Optional[int] = Field(None, ge=1, le=10)
    hidden_discipline: Optional[int] = Field(None, ge=1, le=10)
    hidden_impulsivity: Optional[int] = Field(None, ge=1, le=10)
    hidden_pragmatism: Optional[int] = Field(None, ge=1, le=10)
    hidden_resilience: Optional[int] = Field(None, ge=1, le=10)

class UpdateFactionRequest(BaseModel):
    """Request model for updating faction"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    status: Optional[str] = Field(None)
    properties: Optional[Dict[str, Any]] = None
    
    # Optional hidden attributes updates - Bible range 1-10
    hidden_ambition: Optional[int] = Field(None, ge=1, le=10)
    hidden_integrity: Optional[int] = Field(None, ge=1, le=10)
    hidden_discipline: Optional[int] = Field(None, ge=1, le=10)
    hidden_impulsivity: Optional[int] = Field(None, ge=1, le=10)
    hidden_pragmatism: Optional[int] = Field(None, ge=1, le=10)
    hidden_resilience: Optional[int] = Field(None, ge=1, le=10)

class FactionResponse(BaseModel):
    """Response model for faction"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    description: Optional[str]
    status: str
    properties: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    # Hidden attributes in response
    hidden_ambition: int
    hidden_integrity: int
    hidden_discipline: int
    hidden_impulsivity: int
    hidden_pragmatism: int
    hidden_resilience: int
    
    def get_hidden_attributes(self) -> Dict[str, int]:
        """Get hidden attributes as a dictionary for compatibility with behavior calculations"""
        return {
            "hidden_ambition": self.hidden_ambition,
            "hidden_integrity": self.hidden_integrity,
            "hidden_discipline": self.hidden_discipline,
            "hidden_impulsivity": self.hidden_impulsivity,
            "hidden_pragmatism": self.hidden_pragmatism,
            "hidden_resilience": self.hidden_resilience
        }

class FactionListResponse(BaseModel):
    """Response model for faction lists"""
    
    items: List[FactionResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

# Aliases for backward compatibility
Faction = FactionModel
