"""
Arc system - Arc Progression models and functionality.

This module implements the ArcProgression model for tracking player progression
through arc steps with analytics and comprehensive reporting.
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


class ProgressionMethod(Enum):
    """Methods of progression tracking"""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    HYBRID = "hybrid"
    EVENT_DRIVEN = "event_driven"


class ArcProgressionModel(SharedBaseModel):
    """Model for tracking player progression through arcs"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    arc_id: UUID = Field(..., description="ID of the arc being tracked")
    player_id: Optional[UUID] = Field(None, description="ID of the player (if applicable)")
    session_id: Optional[UUID] = Field(None, description="ID of the game session")
    current_step: int = Field(default=0, description="Current step number in the arc")
    completed_steps: List[int] = Field(default_factory=list, description="List of completed step numbers")
    progress_percentage: float = Field(default=0.0, description="Overall progress percentage")
    start_time: datetime = Field(default_factory=datetime.utcnow, description="When progression started")
    last_activity: datetime = Field(default_factory=datetime.utcnow, description="Last activity timestamp")
    completion_time: Optional[datetime] = Field(None, description="When arc was completed")
    status: str = Field(default="active", description="Progression status")
    analytics_data: Dict[str, Any] = Field(default_factory=dict, description="Analytics and metrics data")
    choices_made: List[Dict[str, Any]] = Field(default_factory=list, description="Player choices and decisions")
    time_spent: float = Field(default=0.0, description="Total time spent in minutes")
    difficulty_rating: Optional[float] = Field(None, description="Player-rated difficulty")
    satisfaction_rating: Optional[float] = Field(None, description="Player satisfaction rating")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    progression_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('progress_percentage')
    def validate_progress_percentage(cls, v):
        if v < 0.0 or v > 100.0:
            raise ValueError('Progress percentage must be between 0 and 100')
        return v

    model_config = ConfigDict(from_attributes=True)


class ArcProgressionEntity(Base):
    """SQLAlchemy entity for arc progression tracking"""
    
    __tablename__ = "arc_progressions"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    arc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey('arc_entities.id'), nullable=False, index=True)
    player_id = Column(SQLAlchemyUUID(as_uuid=True), index=True)
    session_id = Column(SQLAlchemyUUID(as_uuid=True), index=True)
    current_step = Column(Integer, default=0, index=True)
    completed_steps = Column(JSONB, default=list)
    progress_percentage = Column(Float, default=0.0, index=True)
    start_time = Column(DateTime, default=datetime.utcnow, index=True)
    last_activity = Column(DateTime, default=datetime.utcnow, index=True)
    completion_time = Column(DateTime)
    status = Column(String(50), default="active", index=True)
    analytics_data = Column(JSONB, default=dict)
    choices_made = Column(JSONB, default=list)
    time_spent = Column(Float, default=0.0)
    difficulty_rating = Column(Float)
    satisfaction_rating = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    progression_metadata = Column(JSONB, default=dict)

    def __repr__(self):
        return f"<ArcProgressionEntity(id={self.id}, arc_id={self.arc_id}, progress={self.progress_percentage}%)>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary"""
        return {
            "id": str(self.id),
            "arc_id": str(self.arc_id),
            "player_id": str(self.player_id) if self.player_id else None,
            "session_id": str(self.session_id) if self.session_id else None,
            "current_step": self.current_step,
            "completed_steps": self.completed_steps or [],
            "progress_percentage": self.progress_percentage,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "completion_time": self.completion_time.isoformat() if self.completion_time else None,
            "status": self.status,
            "analytics_data": self.analytics_data or {},
            "choices_made": self.choices_made or [],
            "time_spent": self.time_spent,
            "difficulty_rating": self.difficulty_rating,
            "satisfaction_rating": self.satisfaction_rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "progression_metadata": self.progression_metadata or {}
        }


# Request/Response Models
class CreateArcProgressionRequest(BaseModel):
    """Request model for creating arc progression"""
    
    arc_id: UUID = Field(..., description="ID of the arc to track")
    player_id: Optional[UUID] = Field(None, description="ID of the player")
    session_id: Optional[UUID] = Field(None, description="ID of the game session")


class UpdateArcProgressionRequest(BaseModel):
    """Request model for updating arc progression"""
    
    current_step: Optional[int] = Field(None, ge=0)
    completed_steps: Optional[List[int]] = None
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    status: Optional[str] = Field(None)
    analytics_data: Optional[Dict[str, Any]] = None
    choices_made: Optional[List[Dict[str, Any]]] = None
    time_spent: Optional[float] = Field(None, ge=0.0)
    difficulty_rating: Optional[float] = Field(None, ge=1.0, le=10.0)
    satisfaction_rating: Optional[float] = Field(None, ge=1.0, le=10.0)


class ArcProgressionResponse(BaseModel):
    """Response model for arc progression"""
    
    id: UUID
    arc_id: UUID
    player_id: Optional[UUID]
    session_id: Optional[UUID]
    current_step: int
    completed_steps: List[int]
    progress_percentage: float
    start_time: datetime
    last_activity: datetime
    completion_time: Optional[datetime]
    status: str
    analytics_data: Dict[str, Any]
    choices_made: List[Dict[str, Any]]
    time_spent: float
    difficulty_rating: Optional[float]
    satisfaction_rating: Optional[float]
    created_at: datetime
    updated_at: Optional[datetime]
    progression_metadata: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class ArcProgressionListResponse(BaseModel):
    """Response model for arc progression lists"""
    
    items: List[ArcProgressionResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


class ArcProgressionAnalytics(BaseModel):
    """Analytics model for arc progression data"""
    
    total_progressions: int
    active_progressions: int
    completed_progressions: int
    average_completion_time: Optional[float]
    average_progress_percentage: float
    average_difficulty_rating: Optional[float]
    average_satisfaction_rating: Optional[float]
    most_common_stopping_points: List[Dict[str, Any]]
    completion_rate: float
    engagement_metrics: Dict[str, Any]


# Alias for repository compatibility
ArcProgression = ArcProgressionEntity
