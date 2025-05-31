"""
Arc system - Arc Completion Record models and functionality.

This module implements the ArcCompletionRecord model for recording completed arcs
with outcomes, consequences, and detailed completion data.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from backend.infrastructure.models import BaseModel as SharedBaseModel

Base = declarative_base()


class ArcCompletionResult(Enum):
    """Result types for arc completion"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    ABANDONED = "abandoned"
    SKIPPED = "skipped"


class ArcCompletionRecordModel(SharedBaseModel):
    """Model for recording completed arcs with outcomes and consequences"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    arc_id: UUID = Field(..., description="ID of the completed arc")
    progression_id: UUID = Field(..., description="ID of the progression that was completed")
    player_id: Optional[UUID] = Field(None, description="ID of the player who completed the arc")
    session_id: Optional[UUID] = Field(None, description="ID of the game session")
    completion_type: str = Field(..., description="Type of completion (success, failure, partial, etc.)")
    completion_date: datetime = Field(default_factory=datetime.utcnow, description="When the arc was completed")
    total_time_spent: float = Field(default=0.0, description="Total time spent on the arc in minutes")
    steps_completed: List[int] = Field(default_factory=list, description="List of completed step numbers")
    steps_skipped: List[int] = Field(default_factory=list, description="List of skipped step numbers")
    final_outcomes: Dict[str, Any] = Field(default_factory=dict, description="Final outcomes and results")
    consequences: Dict[str, Any] = Field(default_factory=dict, description="Consequences for the world/story")
    rewards_earned: Dict[str, Any] = Field(default_factory=dict, description="Rewards earned from completion")
    choices_summary: List[Dict[str, Any]] = Field(default_factory=list, description="Summary of key choices made")
    difficulty_rating: Optional[float] = Field(None, description="Player-rated difficulty")
    satisfaction_rating: Optional[float] = Field(None, description="Player satisfaction rating")
    narrative_impact: Dict[str, Any] = Field(default_factory=dict, description="Impact on ongoing narrative")
    world_state_changes: Dict[str, Any] = Field(default_factory=dict, description="Changes to world state")
    character_development: Dict[str, Any] = Field(default_factory=dict, description="Character growth and changes")
    completion_score: Optional[float] = Field(None, description="Overall completion score")
    achievements_unlocked: List[str] = Field(default_factory=list, description="Achievements unlocked")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completion_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('completion_type')
    def validate_completion_type(cls, v):
        valid_types = ['success', 'failure', 'partial', 'abandoned', 'skipped']
        if v not in valid_types:
            raise ValueError(f'Completion type must be one of: {valid_types}')
        return v

    model_config = ConfigDict(from_attributes=True)


class ArcCompletionRecordEntity(Base):
    """SQLAlchemy entity for arc completion records"""
    
    __tablename__ = "arc_completion_records"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    arc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey('arc_entities.id'), nullable=False, index=True)
    progression_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey('arc_progressions.id'), nullable=False, index=True)
    player_id = Column(SQLAlchemyUUID(as_uuid=True), index=True)
    session_id = Column(SQLAlchemyUUID(as_uuid=True), index=True)
    completion_type = Column(String(50), nullable=False, index=True)
    completion_date = Column(DateTime, default=datetime.utcnow, index=True)
    total_time_spent = Column(Float, default=0.0)
    steps_completed = Column(JSONB, default=list)
    steps_skipped = Column(JSONB, default=list)
    final_outcomes = Column(JSONB, default=dict)
    consequences = Column(JSONB, default=dict)
    rewards_earned = Column(JSONB, default=dict)
    choices_summary = Column(JSONB, default=list)
    difficulty_rating = Column(Float)
    satisfaction_rating = Column(Float)
    narrative_impact = Column(JSONB, default=dict)
    world_state_changes = Column(JSONB, default=dict)
    character_development = Column(JSONB, default=dict)
    completion_score = Column(Float)
    achievements_unlocked = Column(JSONB, default=list)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    completion_metadata = Column(JSONB, default=dict)

    # Relationships could be added here later
    # arc = relationship("ArcEntity", back_populates="completion_records")
    # progression = relationship("ArcProgressionEntity", back_populates="completion_record")

    def __repr__(self):
        return f"<ArcCompletionRecordEntity(id={self.id}, arc_id={self.arc_id}, type='{self.completion_type}')>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "arc_id": self.arc_id,
            "progression_id": self.progression_id,
            "player_id": self.player_id,
            "session_id": self.session_id,
            "completion_type": self.completion_type,
            "completion_date": self.completion_date,
            "total_time_spent": self.total_time_spent,
            "steps_completed": self.steps_completed,
            "steps_skipped": self.steps_skipped,
            "final_outcomes": self.final_outcomes,
            "consequences": self.consequences,
            "rewards_earned": self.rewards_earned,
            "choices_summary": self.choices_summary,
            "difficulty_rating": self.difficulty_rating,
            "satisfaction_rating": self.satisfaction_rating,
            "narrative_impact": self.narrative_impact,
            "world_state_changes": self.world_state_changes,
            "character_development": self.character_development,
            "completion_score": self.completion_score,
            "achievements_unlocked": self.achievements_unlocked,
            "created_at": self.created_at,
            "completion_metadata": self.completion_metadata
        }


# Request/Response Models
class CreateArcCompletionRecordRequest(BaseModel):
    """Request model for creating arc completion record"""
    
    arc_id: UUID = Field(..., description="ID of the completed arc")
    progression_id: UUID = Field(..., description="ID of the progression that was completed")
    player_id: Optional[UUID] = Field(None, description="ID of the player")
    session_id: Optional[UUID] = Field(None, description="ID of the game session")
    completion_type: str = Field(..., description="Type of completion")
    total_time_spent: float = Field(default=0.0, ge=0.0)
    steps_completed: Optional[List[int]] = Field(default_factory=list)
    steps_skipped: Optional[List[int]] = Field(default_factory=list)
    final_outcomes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    consequences: Optional[Dict[str, Any]] = Field(default_factory=dict)
    rewards_earned: Optional[Dict[str, Any]] = Field(default_factory=dict)
    choices_summary: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    difficulty_rating: Optional[float] = Field(None, ge=1.0, le=10.0)
    satisfaction_rating: Optional[float] = Field(None, ge=1.0, le=10.0)
    narrative_impact: Optional[Dict[str, Any]] = Field(default_factory=dict)
    world_state_changes: Optional[Dict[str, Any]] = Field(default_factory=dict)
    character_development: Optional[Dict[str, Any]] = Field(default_factory=dict)
    completion_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    achievements_unlocked: Optional[List[str]] = Field(default_factory=list)


class ArcCompletionRecordResponse(BaseModel):
    """Response model for arc completion record"""
    
    id: UUID
    arc_id: UUID
    progression_id: UUID
    player_id: Optional[UUID]
    session_id: Optional[UUID]
    completion_type: str
    completion_date: datetime
    total_time_spent: float
    steps_completed: List[int]
    steps_skipped: List[int]
    final_outcomes: Dict[str, Any]
    consequences: Dict[str, Any]
    rewards_earned: Dict[str, Any]
    choices_summary: List[Dict[str, Any]]
    difficulty_rating: Optional[float]
    satisfaction_rating: Optional[float]
    narrative_impact: Dict[str, Any]
    world_state_changes: Dict[str, Any]
    character_development: Dict[str, Any]
    completion_score: Optional[float]
    achievements_unlocked: List[str]
    created_at: datetime
    completion_metadata: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class ArcCompletionRecordListResponse(BaseModel):
    """Response model for arc completion record lists"""
    
    items: List[ArcCompletionRecordResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class ArcCompletionAnalytics(BaseModel):
    """Analytics model for arc completion data"""
    
    total_completions: int
    completion_types: Dict[str, int]
    average_completion_time: Optional[float]
    average_difficulty_rating: Optional[float]
    average_satisfaction_rating: Optional[float]
    average_completion_score: Optional[float]
    most_common_outcomes: List[Dict[str, Any]]
    most_rewarding_arcs: List[Dict[str, Any]]
    completion_trends: Dict[str, Any]
    player_retention_metrics: Dict[str, Any]


# Alias for repository compatibility
ArcCompletionRecord = ArcCompletionRecordEntity
