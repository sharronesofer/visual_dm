"""
Arc system - Arc Step models and functionality.

This module implements the ArcStep model for individual steps within an arc
with completion criteria and narrative text.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from backend.infrastructure.models import BaseModel as SharedBaseModel

Base = declarative_base()


class ArcStepStatus(Enum):
    """Status of arc steps"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    BLOCKED = "blocked"


class ArcStepType(Enum):
    """Types of arc steps"""
    NARRATIVE = "narrative"
    COMBAT = "combat"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    PUZZLE = "puzzle"
    CHOICE = "choice"
    CUTSCENE = "cutscene"


class ArcStepModel(SharedBaseModel):
    """Model for individual steps within an arc"""
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    arc_id: UUID = Field(..., description="ID of the parent arc")
    step_number: int = Field(..., description="Order of this step in the arc")
    title: str = Field(..., description="Title of the arc step")
    description: Optional[str] = Field(None, description="Description of the step")
    narrative_text: Optional[str] = Field(None, description="Narrative content for the step")
    completion_criteria: Dict[str, Any] = Field(default_factory=dict, description="Criteria for completing this step")
    status: str = Field(default="pending", description="Status of the step")
    is_optional: bool = Field(default=False, description="Whether this step is optional")
    prerequisites: List[UUID] = Field(default_factory=list, description="Required previous steps")
    rewards: Dict[str, Any] = Field(default_factory=dict, description="Rewards for completing this step")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    step_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @validator('step_number')
    def validate_step_number(cls, v):
        if v < 1:
            raise ValueError('Step number must be positive')
        return v

    model_config = ConfigDict(from_attributes=True)


class ArcStepEntity(Base):
    """SQLAlchemy entity for arc steps"""
    
    __tablename__ = "arc_steps"
    
    id = Column(SQLAlchemyUUID(as_uuid=True), primary_key=True, default=uuid4)
    arc_id = Column(SQLAlchemyUUID(as_uuid=True), ForeignKey('arc_entities.id'), nullable=False, index=True)
    step_number = Column(Integer, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    narrative_text = Column(Text)
    completion_criteria = Column(JSONB, default=dict)
    status = Column(String(50), default="pending", index=True)
    is_optional = Column(Boolean, default=False, index=True)
    prerequisites = Column(JSONB, default=list)
    rewards = Column(JSONB, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    step_metadata = Column(JSONB, default=dict)

    # Relationships could be added here later
    # arc = relationship("ArcEntity", back_populates="steps")

    def __repr__(self):
        return f"<ArcStepEntity(id={self.id}, arc_id={self.arc_id}, title='{self.title}', step={self.step_number})>"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "arc_id": self.arc_id,
            "step_number": self.step_number,
            "title": self.title,
            "description": self.description,
            "narrative_text": self.narrative_text,
            "completion_criteria": self.completion_criteria,
            "status": self.status,
            "is_optional": self.is_optional,
            "prerequisites": self.prerequisites,
            "rewards": self.rewards,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "completed_at": self.completed_at,
            "step_metadata": self.step_metadata
        }


# Request/Response Models
class CreateArcStepRequest(BaseModel):
    """Request model for creating arc step"""
    
    arc_id: UUID = Field(..., description="ID of the parent arc")
    step_number: int = Field(..., ge=1, description="Order of this step in the arc")
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    narrative_text: Optional[str] = Field(None, max_length=5000)
    completion_criteria: Optional[Dict[str, Any]] = Field(default_factory=dict)
    is_optional: bool = Field(default=False)
    prerequisites: Optional[List[UUID]] = Field(default_factory=list)
    rewards: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UpdateArcStepRequest(BaseModel):
    """Request model for updating arc step"""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    narrative_text: Optional[str] = Field(None, max_length=5000)
    completion_criteria: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(None)
    is_optional: Optional[bool] = None
    prerequisites: Optional[List[UUID]] = None
    rewards: Optional[Dict[str, Any]] = None


class ArcStepResponse(BaseModel):
    """Response model for arc step"""
    
    id: UUID
    arc_id: UUID
    step_number: int
    title: str
    description: Optional[str]
    narrative_text: Optional[str]
    completion_criteria: Dict[str, Any]
    status: str
    is_optional: bool
    prerequisites: List[UUID]
    rewards: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]
    step_metadata: Dict[str, Any]

    model_config = ConfigDict(from_attributes=True)


class ArcStepListResponse(BaseModel):
    """Response model for arc step lists"""
    
    items: List[ArcStepResponse]
    total: int
    page: int
    size: int
    has_next: bool
    has_prev: bool


# Alias for repository compatibility
ArcStep = ArcStepEntity
