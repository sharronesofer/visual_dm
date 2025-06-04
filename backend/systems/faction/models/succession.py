"""
Faction Succession Models

This module defines the data models for faction succession crises according to
Task 69 requirements and Development Bible standards.
"""

from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB, ARRAY
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin


class SuccessionType(Enum):
    """Types of succession mechanisms by faction type"""
    ECONOMIC_COMPETITION = "economic_competition"  # Royal Bay Trading Company - highest net worth
    HEREDITARY = "hereditary"  # Military/Kingdom - bloodline succession
    MILITARY_COUP = "military_coup"  # Military - ambitious generals
    RELIGIOUS_ELECTION = "religious_election"  # Religious - council/clergy
    DIVINE_MANDATE = "divine_mandate"  # Religious - claimed divine appointment
    DEMOCRATIC_ELECTION = "democratic_election"  # Guild/Democratic - elections
    MERIT_SELECTION = "merit_selection"  # Guild/Democratic - merit-based


class SuccessionCrisisStatus(Enum):
    """Status of succession crisis"""
    PENDING = "pending"  # Crisis triggered but not resolved
    IN_PROGRESS = "in_progress"  # Active succession competition
    RESOLVED = "resolved"  # Crisis resolved, new leader chosen
    FAILED = "failed"  # Crisis failed to resolve, faction may split
    SCHISM = "schism"  # Faction split into multiple factions


class SuccessionTrigger(Enum):
    """Events that can trigger succession crisis"""
    LEADER_DEATH_NATURAL = "leader_death_natural"
    LEADER_DEATH_VIOLENT = "leader_death_violent"
    LEADER_REMOVAL_FAILURE = "leader_removal_failure"
    LEADERSHIP_CHALLENGE = "leadership_challenge"
    EXTERNAL_PRESSURE = "external_pressure"
    HIDDEN_AMBITION_COUP = "hidden_ambition_coup"


class SuccessionCandidate(BaseModel):
    """Represents a candidate in succession crisis"""
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    character_id: UUID = Field(..., description="ID of the character candidate")
    character_name: str = Field(..., description="Name of the candidate")
    succession_score: float = Field(default=0.0, description="Overall succession score")
    faction_support: float = Field(default=0.0, description="Support from faction members (0-100)")
    external_support: float = Field(default=0.0, description="Support from external factions")
    
    # Candidate qualifications
    qualifications: Dict[str, Any] = Field(default_factory=dict, description="Type-specific qualifications")
    
    # Campaign details
    campaign_strategy: Optional[str] = Field(None, description="Succession campaign strategy")
    resources_spent: float = Field(default=0.0, description="Resources spent on succession campaign")
    
    # Hidden attributes driving ambition
    hidden_ambition: int = Field(default=3, ge=0, le=6, description="Candidate's ambition level")
    hidden_integrity: int = Field(default=3, ge=0, le=6, description="Candidate's integrity level")
    
    # Special attributes
    is_legitimate_heir: bool = Field(default=False, description="For hereditary succession")
    net_worth: Optional[float] = Field(None, description="For economic succession")
    military_rank: Optional[int] = Field(None, description="For military succession")
    religious_authority: Optional[int] = Field(None, description="For religious succession")


class SuccessionCrisisModel(BaseModel):
    """Primary model for succession crisis"""
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    faction_id: UUID = Field(..., description="ID of the faction in crisis")
    faction_name: str = Field(..., description="Name of the faction")
    
    # Crisis details
    succession_type: SuccessionType = Field(..., description="Type of succession mechanism")
    status: SuccessionCrisisStatus = Field(default=SuccessionCrisisStatus.PENDING)
    trigger: SuccessionTrigger = Field(..., description="What triggered the crisis")
    
    # Timing
    crisis_start: datetime = Field(default_factory=datetime.utcnow)
    crisis_end: Optional[datetime] = Field(None)
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in days")
    
    # Previous leader
    previous_leader_id: Optional[UUID] = Field(None, description="ID of previous leader")
    previous_leader_name: Optional[str] = Field(None, description="Name of previous leader")
    
    # Candidates
    candidates: List[SuccessionCandidate] = Field(default_factory=list)
    winner_id: Optional[UUID] = Field(None, description="ID of winning candidate")
    
    # Crisis effects
    faction_stability: float = Field(default=1.0, description="Faction stability during crisis (0-1)")
    instability_effects: Dict[str, Any] = Field(default_factory=dict)
    
    # External interference
    interfering_factions: List[UUID] = Field(default_factory=list)
    interference_details: Dict[str, Any] = Field(default_factory=dict)
    
    # Resolution details
    resolution_method: Optional[str] = Field(None, description="How the crisis was resolved")
    faction_split: bool = Field(default=False, description="Whether faction split during crisis")
    new_factions: List[UUID] = Field(default_factory=list, description="IDs of new factions if split occurred")
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SuccessionCrisisEntity(UUIDMixin):
    """SQLAlchemy entity for succession crisis system"""
    
    __tablename__ = "faction_succession_crises"
    
    faction_id = Column(SQLAlchemyUUID(as_uuid=True), nullable=False, index=True)
    faction_name = Column(String(255), nullable=False, index=True)
    
    # Crisis details
    succession_type = Column(String(50), nullable=False, index=True)
    status = Column(String(50), default="pending", index=True)
    trigger = Column(String(50), nullable=False, index=True)
    
    # Timing
    crisis_start = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    crisis_end = Column(DateTime)
    estimated_duration = Column(Integer)
    
    # Previous leader
    previous_leader_id = Column(SQLAlchemyUUID(as_uuid=True))
    previous_leader_name = Column(String(255))
    
    # Candidates (stored as JSONB)
    candidates = Column(JSONB, default=list)
    winner_id = Column(SQLAlchemyUUID(as_uuid=True))
    
    # Crisis effects
    faction_stability = Column(Float, default=1.0, nullable=False)
    instability_effects = Column(JSONB, default=dict)
    
    # External interference
    interfering_factions = Column(ARRAY(SQLAlchemyUUID(as_uuid=True)), default=[])
    interference_details = Column(JSONB, default=dict)
    
    # Resolution details
    resolution_method = Column(String(255))
    faction_split = Column(Boolean, default=False, nullable=False)
    new_factions = Column(ARRAY(SQLAlchemyUUID(as_uuid=True)), default=[])
    
    # Additional metadata
    entity_metadata = Column(JSONB, default=dict)

    def __repr__(self):
        return f"<SuccessionCrisisEntity(id={self.id}, faction={self.faction_name}, status={self.status})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "faction_id": str(self.faction_id),
            "faction_name": self.faction_name,
            "succession_type": self.succession_type,
            "status": self.status,
            "trigger": self.trigger,
            "crisis_start": self.crisis_start.isoformat() if self.crisis_start else None,
            "crisis_end": self.crisis_end.isoformat() if self.crisis_end else None,
            "estimated_duration": self.estimated_duration,
            "previous_leader_id": str(self.previous_leader_id) if self.previous_leader_id else None,
            "previous_leader_name": self.previous_leader_name,
            "candidates": self.candidates or [],
            "winner_id": str(self.winner_id) if self.winner_id else None,
            "faction_stability": self.faction_stability,
            "instability_effects": self.instability_effects or {},
            "interfering_factions": [str(fid) for fid in (self.interfering_factions or [])],
            "interference_details": self.interference_details or {},
            "resolution_method": self.resolution_method,
            "faction_split": self.faction_split,
            "new_factions": [str(fid) for fid in (self.new_factions or [])],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "metadata": self.entity_metadata or {}
        }


# Request/Response Models
class CreateSuccessionCrisisRequest(BaseModel):
    """Request model for creating succession crisis"""
    
    faction_id: UUID = Field(..., description="ID of faction entering crisis")
    trigger: SuccessionTrigger = Field(..., description="What triggered the crisis")
    succession_type: Optional[SuccessionType] = Field(None, description="Override succession type")
    previous_leader_id: Optional[UUID] = Field(None, description="ID of previous leader")
    estimated_duration: Optional[int] = Field(None, description="Estimated duration in days")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UpdateSuccessionCrisisRequest(BaseModel):
    """Request model for updating succession crisis"""
    
    status: Optional[SuccessionCrisisStatus] = Field(None)
    faction_stability: Optional[float] = Field(None, ge=0.0, le=1.0)
    instability_effects: Optional[Dict[str, Any]] = None
    resolution_method: Optional[str] = Field(None)
    winner_id: Optional[UUID] = Field(None)
    faction_split: Optional[bool] = Field(None)
    new_factions: Optional[List[UUID]] = None
    metadata: Optional[Dict[str, Any]] = None


class AddCandidateRequest(BaseModel):
    """Request model for adding succession candidate"""
    
    character_id: UUID = Field(..., description="ID of candidate character")
    character_name: str = Field(..., description="Name of candidate")
    qualifications: Optional[Dict[str, Any]] = Field(default_factory=dict)
    campaign_strategy: Optional[str] = Field(None)
    is_legitimate_heir: bool = Field(default=False)
    net_worth: Optional[float] = Field(None)
    military_rank: Optional[int] = Field(None)
    religious_authority: Optional[int] = Field(None)


class SuccessionCrisisResponse(BaseModel):
    """Response model for succession crisis"""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    faction_id: UUID
    faction_name: str
    succession_type: SuccessionType
    status: SuccessionCrisisStatus
    trigger: SuccessionTrigger
    crisis_start: datetime
    crisis_end: Optional[datetime]
    estimated_duration: Optional[int]
    previous_leader_id: Optional[UUID]
    previous_leader_name: Optional[str]
    candidates: List[SuccessionCandidate]
    winner_id: Optional[UUID]
    faction_stability: float
    instability_effects: Dict[str, Any]
    interfering_factions: List[UUID]
    interference_details: Dict[str, Any]
    resolution_method: Optional[str]
    faction_split: bool
    new_factions: List[UUID]
    created_at: datetime
    updated_at: Optional[datetime]
    metadata: Dict[str, Any]


class SuccessionCrisisListResponse(BaseModel):
    """Response model for succession crisis lists"""
    
    items: List[SuccessionCrisisResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool 