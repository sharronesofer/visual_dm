"""
Arc system - Arc Step models and functionality.

This module implements the ArcStep model for individual steps within an arc
with completion criteria, validation logic, and narrative text.
Enhanced with robust validation as specified in Development Bible.
"""

from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from pydantic import BaseModel, Field, validator, ConfigDict
from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID, JSONB

from sqlalchemy.orm import relationship
from backend.infrastructure.database import Base, UUIDMixin, TimestampMixin

from backend.infrastructure.shared.models.models import SharedBaseModel

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
    INVESTIGATION = "investigation"

class ArcStepValidationError(Exception):
    """Custom exception for arc step validation errors"""
    pass

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
    
    @validator('status')
    def validate_status(cls, v):
        if v not in [status.value for status in ArcStepStatus]:
            raise ValueError(f'Invalid status: {v}')
        return v
    
    @validator('completion_criteria')
    def validate_completion_criteria_structure(cls, v):
        """Validate completion criteria has required structure"""
        if not isinstance(v, dict):
            raise ValueError('Completion criteria must be a dictionary')
        
        # Import here to avoid circular imports
        from backend.systems.arc.business_rules import validate_step_completion_criteria
        errors = validate_step_completion_criteria(v)
        if errors:
            raise ValueError(f'Completion criteria validation failed: {"; ".join(errors)}')
        
        return v

    def validate_business_rules(self) -> List[str]:
        """
        Validate business rules for this arc step.
        
        Returns:
            List of validation errors
        """
        errors = []
        
        # Title validation
        if not self.title or len(self.title.strip()) < 3:
            errors.append("Step title must be at least 3 characters")
        elif len(self.title) > 200:
            errors.append("Step title should not exceed 200 characters")
        
        # Description validation
        if self.description and len(self.description) > 2000:
            errors.append("Step description should not exceed 2000 characters")
        
        # Narrative text validation
        if self.narrative_text:
            from backend.systems.arc.business_rules import validate_narrative_text
            narrative_errors = validate_narrative_text(self.narrative_text)
            errors.extend([f"Narrative: {err}" for err in narrative_errors])
        
        # Status-specific validation
        errors.extend(self._validate_status_specific_rules())
        
        # Completion criteria validation
        if self.completion_criteria:
            from backend.systems.arc.business_rules import validate_step_completion_criteria
            criteria_errors = validate_step_completion_criteria(self.completion_criteria)
            errors.extend([f"Completion criteria: {err}" for err in criteria_errors])
        
        # Prerequisites validation
        errors.extend(self._validate_prerequisites())
        
        # Rewards validation
        errors.extend(self._validate_rewards())
        
        return errors
    
    def _validate_status_specific_rules(self) -> List[str]:
        """Validate rules specific to the current status"""
        errors = []
        
        if self.status == ArcStepStatus.COMPLETED.value:
            if not self.completed_at:
                errors.append("Completed steps must have completed_at timestamp")
            if not self.completion_criteria:
                errors.append("Completed steps should have completion criteria")
        
        elif self.status == ArcStepStatus.PENDING.value:
            if self.completed_at:
                errors.append("Pending steps should not have completed_at timestamp")
        
        elif self.status == ArcStepStatus.ACTIVE.value:
            if self.completed_at:
                errors.append("Active steps should not have completed_at timestamp")
        
        elif self.status == ArcStepStatus.BLOCKED.value:
            if not self.prerequisites:
                errors.append("Blocked steps should specify prerequisites causing the block")
        
        return errors
    
    def _validate_prerequisites(self) -> List[str]:
        """Validate prerequisite relationships"""
        errors = []
        
        if self.prerequisites:
            # Check for self-reference
            if self.id in self.prerequisites:
                errors.append("Step cannot be prerequisite of itself")
            
            # Check for reasonable prerequisite count
            if len(self.prerequisites) > 5:
                errors.append("Step should not have more than 5 prerequisites for clarity")
        
        return errors
    
    def _validate_rewards(self) -> List[str]:
        """Validate reward structure"""
        errors = []
        
        if self.rewards:
            # Validate experience rewards
            experience = self.rewards.get("experience")
            if experience is not None:
                if not isinstance(experience, int):
                    errors.append("Experience reward must be an integer")
                elif experience < 0:
                    errors.append("Experience reward cannot be negative")
                elif experience > 10000:
                    errors.append("Experience reward seems excessive (>10000)")
            
            # Validate reputation rewards
            reputation = self.rewards.get("reputation")
            if reputation and isinstance(reputation, dict):
                for faction, change in reputation.items():
                    if not isinstance(change, int):
                        errors.append(f"Reputation change for {faction} must be integer")
                    elif abs(change) > 100:
                        errors.append(f"Reputation change for {faction} seems excessive (>{abs(change)})")
            
            # Validate items
            items = self.rewards.get("items")
            if items:
                if not isinstance(items, list):
                    errors.append("Items reward must be a list")
                elif len(items) > 10:
                    errors.append("Too many item rewards (>10) may overwhelm players")
        
        return errors
    
    def can_transition_to_status(self, new_status: str, prerequisite_steps: List['ArcStepModel'] = None) -> Tuple[bool, str]:
        """
        Check if step can transition to a new status.
        
        Args:
            new_status: Target status
            prerequisite_steps: List of prerequisite steps to check
            
        Returns:
            Tuple of (can_transition, reason)
        """
        try:
            new_status_enum = ArcStepStatus(new_status)
        except ValueError:
            return False, f"Invalid status: {new_status}"
        
        current_status_enum = ArcStepStatus(self.status)
        
        # Define valid transitions
        valid_transitions = {
            ArcStepStatus.PENDING: [ArcStepStatus.ACTIVE, ArcStepStatus.BLOCKED, ArcStepStatus.SKIPPED],
            ArcStepStatus.ACTIVE: [ArcStepStatus.COMPLETED, ArcStepStatus.FAILED, ArcStepStatus.BLOCKED],
            ArcStepStatus.BLOCKED: [ArcStepStatus.PENDING, ArcStepStatus.ACTIVE],
            ArcStepStatus.COMPLETED: [],  # Final state
            ArcStepStatus.FAILED: [ArcStepStatus.PENDING, ArcStepStatus.ACTIVE],  # Can retry
            ArcStepStatus.SKIPPED: []  # Final state for optional steps
        }
        
        if new_status_enum not in valid_transitions[current_status_enum]:
            return False, f"Cannot transition from {self.status} to {new_status}"
        
        # Check specific transition requirements
        if new_status_enum == ArcStepStatus.ACTIVE:
            # Check prerequisites are met
            if self.prerequisites and prerequisite_steps is not None:
                prerequisite_ids = {step.id for step in prerequisite_steps}
                for prereq_id in self.prerequisites:
                    prereq_step = next((s for s in prerequisite_steps if s.id == prereq_id), None)
                    if not prereq_step:
                        return False, f"Prerequisite step {prereq_id} not found"
                    if prereq_step.status != ArcStepStatus.COMPLETED.value:
                        return False, f"Prerequisite step '{prereq_step.title}' not completed"
        
        elif new_status_enum == ArcStepStatus.COMPLETED:
            # Check completion criteria are met (would need external validation)
            if not self.completion_criteria:
                return False, "Cannot complete step without completion criteria"
        
        elif new_status_enum == ArcStepStatus.SKIPPED:
            if not self.is_optional:
                return False, "Cannot skip non-optional step"
        
        return True, "Transition allowed"
    
    def calculate_completion_progress(self, progress_data: Dict[str, Any] = None) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate completion progress based on criteria and progress data.
        
        Args:
            progress_data: Current progress data for this step
            
        Returns:
            Tuple of (progress_percentage, progress_details)
        """
        if self.status == ArcStepStatus.COMPLETED.value:
            return 100.0, {"status": "completed", "all_requirements_met": True}
        
        if not self.completion_criteria or not progress_data:
            return 0.0, {"status": "no_data", "requirements_checked": 0}
        
        requirements = self.completion_criteria.get("requirements", [])
        if not requirements:
            return 0.0, {"status": "no_requirements", "requirements_checked": 0}
        
        success_threshold = self.completion_criteria.get("success_threshold", len(requirements))
        
        # Check each requirement
        met_requirements = 0
        requirement_details = {}
        
        for i, requirement in enumerate(requirements):
            req_key = f"requirement_{i}"
            is_met = progress_data.get(req_key, False)
            requirement_details[req_key] = {
                "description": requirement,
                "met": is_met
            }
            if is_met:
                met_requirements += 1
        
        # Calculate progress percentage
        progress_percentage = (met_requirements / success_threshold) * 100
        progress_percentage = min(progress_percentage, 100.0)  # Cap at 100%
        
        details = {
            "status": "in_progress",
            "requirements_met": met_requirements,
            "requirements_total": len(requirements),
            "success_threshold": success_threshold,
            "can_complete": met_requirements >= success_threshold,
            "requirements": requirement_details
        }
        
        return progress_percentage, details
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """
        Get a comprehensive validation summary for this step.
        
        Returns:
            Dictionary with validation results
        """
        business_errors = self.validate_business_rules()
        
        # Check status transition validity
        can_be_active, active_reason = self.can_transition_to_status("active")
        can_be_completed, complete_reason = self.can_transition_to_status("completed")
        
        return {
            "is_valid": len(business_errors) == 0,
            "business_rule_errors": business_errors,
            "status_transitions": {
                "can_activate": can_be_active,
                "activation_reason": active_reason,
                "can_complete": can_be_completed,
                "completion_reason": complete_reason
            },
            "completion_criteria_valid": bool(self.completion_criteria),
            "has_prerequisites": len(self.prerequisites) > 0,
            "is_optional": self.is_optional,
            "validation_timestamp": datetime.utcnow().isoformat()
        }

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
    
    def to_model(self) -> ArcStepModel:
        """Convert entity to model with validation"""
        return ArcStepModel(**self.to_dict())

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

class ArcStepValidationRequest(BaseModel):
    """Request model for step validation"""
    
    step_id: UUID
    progress_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    include_prerequisite_check: bool = Field(default=True)

class ArcStepProgressRequest(BaseModel):
    """Request model for updating step progress"""
    
    step_id: UUID
    progress_data: Dict[str, Any]
    auto_complete: bool = Field(default=True, description="Automatically complete if criteria met")

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

class ArcStepValidationResponse(BaseModel):
    """Response model for step validation"""
    
    step_id: UUID
    is_valid: bool
    business_rule_errors: List[str]
    status_transitions: Dict[str, Any]
    completion_progress: float
    progress_details: Dict[str, Any]
    validation_timestamp: datetime

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
