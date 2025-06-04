"""
Alliance and Betrayal System Models

This module defines the data models for the faction alliance and betrayal system
according to the Development Bible standards and Task 68 specifications.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime, timedelta
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, validator
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin


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


class AllianceBaseModel(BaseModel):
    """Base model for alliance system with common fields"""
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    is_active: bool = Field(default=True)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class AllianceModel(AllianceBaseModel):
    """Primary model for faction alliances"""
    
    name: str = Field(..., description="Name of the alliance")
    alliance_type: AllianceType = Field(..., description="Type of alliance")
    status: AllianceStatus = Field(default=AllianceStatus.PROPOSED, description="Current status")
    description: Optional[str] = Field(None, description="Description of alliance purpose")
    
    # Member factions
    leader_faction_id: UUID = Field(..., description="Faction that leads the alliance")
    member_faction_ids: List[UUID] = Field(default_factory=list, description="Member faction IDs")
    
    # Alliance terms and conditions
    terms: Dict[str, Any] = Field(default_factory=dict, description="Specific terms of the alliance")
    mutual_obligations: List[str] = Field(default_factory=list, description="What members owe each other")
    shared_enemies: List[UUID] = Field(default_factory=list, description="Common enemy faction IDs")
    shared_goals: List[str] = Field(default_factory=list, description="Common objectives")
    
    # Duration and expiry
    start_date: Optional[datetime] = Field(None, description="When alliance becomes active")
    end_date: Optional[datetime] = Field(None, description="When alliance expires (None = indefinite)")
    auto_renew: bool = Field(default=False, description="Whether to auto-renew when expiring")
    
    # Trust and reliability metrics
    trust_levels: Dict[UUID, float] = Field(default_factory=dict, description="Trust between members (0-1)")
    betrayal_risks: Dict[UUID, float] = Field(default_factory=dict, description="Betrayal risk per member (0-1)")
    reliability_history: Dict[UUID, List[Dict]] = Field(default_factory=dict, description="Historical reliability data")
    
    # Trigger conditions for alliance
    triggers: Dict[str, Any] = Field(default_factory=dict, description="What triggered alliance formation")
    threat_level: float = Field(default=0.0, ge=0.0, le=1.0, description="Severity of threat that caused alliance")
    
    # Benefits tracking
    benefits_shared: Dict[str, Any] = Field(default_factory=dict, description="Resources/benefits shared")
    military_support_provided: Dict[UUID, List[Dict]] = Field(default_factory=dict, description="Military aid given")
    economic_support_provided: Dict[UUID, List[Dict]] = Field(default_factory=dict, description="Economic aid given")


class BetrayalEvent(AllianceBaseModel):
    """Model for tracking betrayal events"""
    
    alliance_id: UUID = Field(..., description="Alliance that was betrayed")
    betrayer_faction_id: UUID = Field(..., description="Faction that committed betrayal")
    victim_faction_ids: List[UUID] = Field(default_factory=list, description="Factions that were betrayed")
    
    betrayal_reason: BetrayalReason = Field(..., description="Primary reason for betrayal")
    betrayal_type: str = Field(..., description="Type of betrayal (attack, abandonment, etc.)")
    description: str = Field(..., description="Description of what happened")
    
    # Betrayal circumstances
    hidden_attributes_influence: Dict[str, int] = Field(default_factory=dict, description="How hidden attributes influenced betrayal")
    external_pressure: Optional[Dict[str, Any]] = Field(None, description="External factors that influenced betrayal")
    opportunity_details: Optional[Dict[str, Any]] = Field(None, description="Details of opportunity that triggered betrayal")
    
    # Impact and consequences  
    damage_dealt: Dict[str, Any] = Field(default_factory=dict, description="Damage caused by betrayal")
    trust_impact: Dict[UUID, float] = Field(default_factory=dict, description="Impact on trust with other factions")
    reputation_impact: float = Field(default=0.0, description="General reputation impact")
    
    # Detection and response
    detected_immediately: bool = Field(default=True, description="Whether betrayal was immediately obvious")
    detection_delay: Optional[int] = Field(None, description="Time before betrayal was discovered (hours)")
    response_actions: List[Dict[str, Any]] = Field(default_factory=list, description="Actions taken in response")


class AllianceEntity(UUIDMixin):
    """SQLAlchemy entity for alliance system"""
    
    __tablename__ = "faction_alliances"
    
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
            "is_active": getattr(self, 'is_active', True)
        }


class BetrayalEntity(UUIDMixin):
    """SQLAlchemy entity for betrayal events"""
    
    __tablename__ = "faction_betrayals"
    
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
    is_active = Column(Boolean, default=True, nullable=False)
    entity_metadata = Column(JSONB, default=dict)

    def __repr__(self):
        return f"<BetrayalEntity(id={self.id}, betrayer={self.betrayer_faction_id}, alliance={self.alliance_id})>"


# Request/Response Models
class CreateAllianceRequest(BaseModel):
    """Request model for creating alliance"""
    
    name: str = Field(..., min_length=1, max_length=255)
    alliance_type: AllianceType = Field(...)
    description: Optional[str] = Field(None, max_length=1000)
    leader_faction_id: UUID = Field(...)
    member_faction_ids: List[UUID] = Field(default_factory=list)
    terms: Optional[Dict[str, Any]] = Field(default_factory=dict)
    mutual_obligations: Optional[List[str]] = Field(default_factory=list)
    shared_enemies: Optional[List[UUID]] = Field(default_factory=list)
    shared_goals: Optional[List[str]] = Field(default_factory=list)
    end_date: Optional[datetime] = Field(None)
    auto_renew: bool = Field(default=False)


class UpdateAllianceRequest(BaseModel):
    """Request model for updating alliance"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[AllianceStatus] = Field(None)
    description: Optional[str] = Field(None, max_length=1000)
    terms: Optional[Dict[str, Any]] = None
    mutual_obligations: Optional[List[str]] = None
    shared_enemies: Optional[List[UUID]] = None
    shared_goals: Optional[List[str]] = None
    end_date: Optional[datetime] = None
    auto_renew: Optional[bool] = None


class AllianceResponse(BaseModel):
    """Response model for alliance"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    alliance_type: AllianceType
    status: AllianceStatus
    description: Optional[str]
    leader_faction_id: UUID
    member_faction_ids: List[UUID]
    terms: Dict[str, Any]
    mutual_obligations: List[str]
    shared_enemies: List[UUID]
    shared_goals: List[str]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    auto_renew: bool
    trust_levels: Dict[str, float]
    betrayal_risks: Dict[str, float]
    reliability_history: Dict[str, List[Dict]]
    triggers: Dict[str, Any]
    threat_level: float
    benefits_shared: Dict[str, Any]
    military_support_provided: Dict[str, List[Dict]]
    economic_support_provided: Dict[str, List[Dict]]
    created_at: datetime
    updated_at: Optional[datetime]
    is_active: bool


class BetrayalResponse(BaseModel):
    """Response model for betrayal event"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    alliance_id: UUID
    betrayer_faction_id: UUID
    victim_faction_ids: List[UUID]
    betrayal_reason: BetrayalReason
    betrayal_type: str
    description: str
    hidden_attributes_influence: Dict[str, int]
    external_pressure: Optional[Dict[str, Any]]
    opportunity_details: Optional[Dict[str, Any]]
    damage_dealt: Dict[str, Any]
    trust_impact: Dict[str, float]
    reputation_impact: float
    detected_immediately: bool
    detection_delay: Optional[int]
    response_actions: List[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]


class AllianceListResponse(BaseModel):
    """Response model for alliance lists"""
    
    items: List[AllianceResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


# Aliases for backward compatibility
Alliance = AllianceModel
Betrayal = BetrayalEvent 