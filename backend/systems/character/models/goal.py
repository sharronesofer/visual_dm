"""
Character system - Goal models.

This module provides goal and objective models for characters,
supporting dynamic goal tracking and achievement systems.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Enum as SQLEnum
from backend.infrastructure.database import Base
from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional, List
from uuid import UUID


class GoalType(Enum):
    """Enumeration of goal types."""
    PERSONAL = "personal"
    QUEST = "quest"
    FACTION = "faction"
    SKILL = "skill"
    EXPLORATION = "exploration"
    COMBAT = "combat"
    SOCIAL = "social"
    ECONOMIC = "economic"
    SURVIVAL = "survival"
    CUSTOM = "custom"


class GoalPriority(Enum):
    """Enumeration of goal priority levels."""
    VERY_LOW = "very_low"
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"


class GoalStatus(Enum):
    """Enumeration of goal status values."""
    PENDING = "pending"
    ACTIVE = "active"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    ON_HOLD = "on_hold"


class Goal(Base):
    """
    Goal model representing character objectives and aspirations.
    
    Tracks character goals including personal objectives, quest goals,
    faction missions, and other aspirations with progress tracking.
    """
    
    __tablename__ = 'character_goals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    character_id = Column(String(255), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(1000), nullable=False)
    goal_type = Column(SQLEnum(GoalType), nullable=False, default=GoalType.PERSONAL)
    priority = Column(SQLEnum(GoalPriority), nullable=False, default=GoalPriority.NORMAL)
    status = Column(SQLEnum(GoalStatus), nullable=False, default=GoalStatus.PENDING)
    progress = Column(Float, default=0.0)  # 0.0 to 1.0 (0% to 100%)
    target_value = Column(Float, nullable=True)  # Optional target for measurable goals
    current_value = Column(Float, default=0.0)  # Current progress value
    goal_metadata = Column(JSON, default=dict)  # Additional goal-specific data
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Goal {self.title} ({self.status.value}): {self.progress:.1%}>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert goal to dictionary representation."""
        return {
            "id": self.id,
            "character_id": self.character_id,
            "title": self.title,
            "description": self.description,
            "goal_type": self.goal_type.value if self.goal_type else None,
            "priority": self.priority.value if self.priority else None,
            "status": self.status.value if self.status else None,
            "progress": self.progress,
            "target_value": self.target_value,
            "current_value": self.current_value,
            "metadata": self.goal_metadata or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Goal":
        """Create goal from dictionary representation."""
        goal = cls()
        goal.character_id = data.get("character_id")
        goal.title = data.get("title")
        goal.description = data.get("description")
        
        # Handle enum conversions
        if "goal_type" in data:
            if isinstance(data["goal_type"], str):
                goal.goal_type = GoalType(data["goal_type"])
            else:
                goal.goal_type = data["goal_type"]
        
        if "priority" in data:
            if isinstance(data["priority"], str):
                goal.priority = GoalPriority(data["priority"])
            else:
                goal.priority = data["priority"]
        
        if "status" in data:
            if isinstance(data["status"], str):
                goal.status = GoalStatus(data["status"])
            else:
                goal.status = data["status"]
        
        goal.progress = data.get("progress", 0.0)
        goal.target_value = data.get("target_value")
        goal.current_value = data.get("current_value", 0.0)
        goal.goal_metadata = data.get("metadata", {})
        
        return goal
    
    def update_progress(self, new_progress: float) -> None:
        """
        Update goal progress.
        
        Args:
            new_progress: New progress value (0.0 to 1.0)
        """
        self.progress = max(0.0, min(1.0, new_progress))
        self.updated_at = datetime.utcnow()
        
        # Auto-complete if progress reaches 100%
        if self.progress >= 1.0 and self.status != GoalStatus.COMPLETED:
            self.complete()
    
    def update_current_value(self, new_value: float) -> None:
        """
        Update current value and recalculate progress.
        
        Args:
            new_value: New current value
        """
        self.current_value = new_value
        
        # Recalculate progress if target value is set
        if self.target_value and self.target_value > 0:
            self.progress = min(1.0, self.current_value / self.target_value)
        
        self.updated_at = datetime.utcnow()
        
        # Auto-complete if progress reaches 100%
        if self.progress >= 1.0 and self.status != GoalStatus.COMPLETED:
            self.complete()
    
    def complete(self) -> None:
        """Mark goal as completed."""
        self.status = GoalStatus.COMPLETED
        self.progress = 1.0
        self.completed_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def fail(self, reason: Optional[str] = None) -> None:
        """
        Mark goal as failed.
        
        Args:
            reason: Optional reason for failure
        """
        self.status = GoalStatus.FAILED
        self.updated_at = datetime.utcnow()
        
        if reason:
            if not self.goal_metadata:
                self.goal_metadata = {}
            self.goal_metadata["failure_reason"] = reason
    
    def abandon(self, reason: Optional[str] = None) -> None:
        """
        Mark goal as abandoned.
        
        Args:
            reason: Optional reason for abandonment
        """
        self.status = GoalStatus.ABANDONED
        self.updated_at = datetime.utcnow()
        
        if reason:
            if not self.goal_metadata:
                self.goal_metadata = {}
            self.goal_metadata["abandonment_reason"] = reason
    
    def activate(self) -> None:
        """Activate the goal."""
        if self.status == GoalStatus.PENDING:
            self.status = GoalStatus.ACTIVE
            self.updated_at = datetime.utcnow()
    
    def put_on_hold(self, reason: Optional[str] = None) -> None:
        """
        Put goal on hold.
        
        Args:
            reason: Optional reason for putting on hold
        """
        self.status = GoalStatus.ON_HOLD
        self.updated_at = datetime.utcnow()
        
        if reason:
            if not self.goal_metadata:
                self.goal_metadata = {}
            self.goal_metadata["hold_reason"] = reason
    
    def is_overdue(self) -> bool:
        """Check if goal is overdue."""
        if not self.deadline:
            return False
        return datetime.utcnow() > self.deadline and self.status not in [GoalStatus.COMPLETED, GoalStatus.FAILED, GoalStatus.ABANDONED]
    
    def is_active(self) -> bool:
        """Check if goal is currently active."""
        return self.status in [GoalStatus.ACTIVE, GoalStatus.IN_PROGRESS]
    
    def is_completed(self) -> bool:
        """Check if goal is completed."""
        return self.status == GoalStatus.COMPLETED
    
    def get_metadata_value(self, key: str, default: Any = None) -> Any:
        """Get a specific value from goal metadata."""
        if not self.goal_metadata:
            return default
        return self.goal_metadata.get(key, default)
    
    def set_metadata_value(self, key: str, value: Any) -> None:
        """Set a specific value in goal metadata."""
        if not self.goal_metadata:
            self.goal_metadata = {}
        self.goal_metadata[key] = value
        self.updated_at = datetime.utcnow()
