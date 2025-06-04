"""
Quest System Infrastructure Models

This module defines the data models for the quest system according to
the Development Bible standards, matching the business logic and JSON schemas.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.orm import relationship

from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin
from backend.infrastructure.shared.models import SharedBaseModel


# SQLAlchemy Database Entities

class QuestEntity(Base, UUIDMixin, TimestampMixin):
    """SQLAlchemy entity for quest system matching business logic and JSON schema"""
    
    __tablename__ = "quests"
    
    # Core quest fields (matching JSON schema)
    title = Column(String(255), nullable=False, index=True)  # Changed from 'name' to 'title' for consistency
    description = Column(Text, nullable=False)
    status = Column(String(50), nullable=False, default="pending", index=True)
    difficulty = Column(String(20), nullable=False, index=True)
    theme = Column(String(50), nullable=False, index=True)
    
    # Association fields
    npc_id = Column(String(255), nullable=True, index=True)
    player_id = Column(String(255), nullable=True, index=True)
    location_id = Column(String(255), nullable=True, index=True)
    
    # Quest metadata
    level = Column(Integer, nullable=False, default=1, index=True)
    is_main_quest = Column(Boolean, default=False, index=True)
    tags = Column(JSONB, default=list)
    properties = Column(JSONB, default=dict)
    
    # Quest progression
    steps = Column(JSONB, default=list)  # Array of quest step objects
    rewards = Column(JSONB, default=dict)  # Quest reward object
    
    # Timing
    expires_at = Column(DateTime, nullable=True, index=True)
    
    # Quest Chain Support (matching business logic)
    chain_id = Column(String(255), nullable=True, index=True)
    chain_position = Column(Integer, nullable=True)
    chain_prerequisites = Column(JSONB, default=list)  # Array of quest IDs
    chain_unlocks = Column(JSONB, default=list)  # Array of quest IDs
    is_chain_final = Column(Boolean, default=False)

    def __repr__(self):
        return f"<QuestEntity(id={self.id}, title='{self.title}', status='{self.status}')>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary matching JSON schema format"""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "difficulty": self.difficulty,
            "theme": self.theme,
            "npc_id": self.npc_id,
            "player_id": self.player_id,
            "location_id": self.location_id,
            "level": self.level,
            "steps": self.steps or [],
            "rewards": self.rewards or {},
            "is_main_quest": self.is_main_quest,
            "tags": self.tags or [],
            "properties": self.properties or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "chain_id": self.chain_id,
            "chain_position": self.chain_position,
            "chain_prerequisites": self.chain_prerequisites or [],
            "chain_unlocks": self.chain_unlocks or [],
            "is_chain_final": self.is_chain_final
        }


class QuestChainEntity(Base, UUIDMixin, TimestampMixin):
    """SQLAlchemy entity for quest chains"""
    
    __tablename__ = "quest_chains"
    
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    theme = Column(String(50), nullable=False, index=True)
    difficulty = Column(String(20), nullable=False, index=True)
    min_level = Column(Integer, nullable=False, index=True)
    max_level = Column(Integer, nullable=True)
    quest_ids = Column(JSONB, default=list)  # Array of quest IDs
    chain_type = Column(String(50), nullable=False, default="sequential")
    is_main_story = Column(Boolean, default=False, index=True)
    rewards = Column(JSONB, default=dict)  # Chain completion rewards
    metadata = Column(JSONB, default=dict)

    def __repr__(self):
        return f"<QuestChainEntity(id={self.id}, name='{self.name}', type='{self.chain_type}')>"


class QuestChainProgressEntity(Base, UUIDMixin, TimestampMixin):
    """SQLAlchemy entity for quest chain progress tracking"""
    
    __tablename__ = "quest_chain_progress"
    
    chain_id = Column(String(255), nullable=False, index=True)
    player_id = Column(String(255), nullable=False, index=True)
    current_quest_id = Column(String(255), nullable=True)
    completed_quests = Column(JSONB, default=list)  # Array of completed quest IDs
    available_quests = Column(JSONB, default=list)  # Array of available quest IDs
    status = Column(String(50), nullable=False, default="active", index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    metadata = Column(JSONB, default=dict)

    def __repr__(self):
        return f"<QuestChainProgressEntity(id={self.id}, chain_id='{self.chain_id}', player_id='{self.player_id}')>"


# Pydantic Request/Response Models (matching JSON schema)

class QuestStepModel(BaseModel):
    """Quest step model matching JSON schema"""
    id: int
    title: str
    description: str
    completed: bool = False
    required: bool = True
    order: int = 0
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class QuestRewardModel(BaseModel):
    """Quest reward model matching JSON schema"""
    gold: int = 0
    experience: int = 0
    reputation: Dict[str, Any] = Field(default_factory=dict)
    items: List[Dict[str, Any]] = Field(default_factory=list)
    special: Dict[str, Any] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


class CreateQuestRequest(BaseModel):
    """Request model for creating quest matching JSON schema"""
    
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=2000)
    difficulty: str = Field(..., pattern="^(easy|medium|hard|epic)$")
    theme: str = Field(..., pattern="^(combat|exploration|social|mystery|crafting|trade|aid|knowledge|general)$")
    npc_id: Optional[str] = None
    location_id: Optional[str] = None
    level: int = Field(default=1, ge=1, le=100)
    steps: List[QuestStepModel] = Field(default_factory=list)
    rewards: Optional[QuestRewardModel] = None
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict)
    expires_at: Optional[datetime] = None
    chain_id: Optional[str] = None
    chain_position: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class UpdateQuestRequest(BaseModel):
    """Request model for updating quest"""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    status: Optional[str] = Field(None, pattern="^(pending|active|completed|failed|abandoned|expired)$")
    difficulty: Optional[str] = Field(None, pattern="^(easy|medium|hard|epic)$")
    theme: Optional[str] = Field(None, pattern="^(combat|exploration|social|mystery|crafting|trade|aid|knowledge|general)$")
    npc_id: Optional[str] = None
    player_id: Optional[str] = None
    location_id: Optional[str] = None
    level: Optional[int] = Field(None, ge=1, le=100)
    steps: Optional[List[QuestStepModel]] = None
    rewards: Optional[QuestRewardModel] = None
    properties: Optional[Dict[str, Any]] = None
    expires_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class QuestResponse(BaseModel):
    """Response model for quest matching JSON schema"""
    
    id: UUID
    title: str
    description: str
    status: str
    difficulty: str
    theme: str
    npc_id: Optional[str] = None
    player_id: Optional[str] = None
    location_id: Optional[str] = None
    level: int
    steps: List[QuestStepModel]
    rewards: QuestRewardModel
    is_main_quest: bool = False
    tags: List[str] = Field(default_factory=list)
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    chain_id: Optional[str] = None
    chain_position: Optional[int] = None
    chain_prerequisites: List[str] = Field(default_factory=list)
    chain_unlocks: List[str] = Field(default_factory=list)
    is_chain_final: bool = False

    model_config = ConfigDict(from_attributes=True)


class QuestListResponse(BaseModel):
    """Response model for quest lists"""
    
    items: List[QuestResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool

    model_config = ConfigDict(from_attributes=True)


class QuestStepUpdateRequest(BaseModel):
    """Request model for updating quest steps"""
    
    step_id: int
    completed: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None

    model_config = ConfigDict(from_attributes=True)


class QuestActionRequest(BaseModel):
    """Request model for quest actions (assign, abandon, etc.)"""
    
    action: str = Field(..., pattern="^(assign|abandon|complete_step|reset)$")
    player_id: Optional[str] = None
    step_id: Optional[int] = None
    reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


# Quest Chain Models

class QuestChainResponse(BaseModel):
    """Response model for quest chains"""
    
    id: UUID
    name: str
    description: str
    theme: str
    difficulty: str
    min_level: int
    max_level: Optional[int] = None
    quest_ids: List[str] = Field(default_factory=list)
    chain_type: str = "sequential"
    is_main_story: bool = False
    rewards: Optional[QuestRewardModel] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CreateQuestChainRequest(BaseModel):
    """Request model for creating quest chains"""
    
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=2000)
    theme: str = Field(..., pattern="^(combat|exploration|social|mystery|crafting|trade|aid|knowledge|general)$")
    difficulty: str = Field(..., pattern="^(easy|medium|hard|epic)$")
    min_level: int = Field(..., ge=1, le=100)
    max_level: Optional[int] = Field(None, ge=1, le=100)
    chain_type: str = Field(default="sequential", pattern="^(sequential|branching|parallel)$")
    is_main_story: bool = False
    rewards: Optional[QuestRewardModel] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    model_config = ConfigDict(from_attributes=True)


# Legacy aliases for backward compatibility
Quest = QuestResponse
QuestStep = QuestStepModel
