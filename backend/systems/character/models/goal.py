"""
Goal Model
----------
Implements the character goal system as described in the Development Bible.
Defines goal structures with attributes for priority, status, and progress tracking.
"""

from enum import Enum
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Set
from uuid import UUID, uuid4
import logging

from backend.systems.events.event_dispatcher import EventDispatcher
from backend.systems.events.canonical_events import EventBase

logger = logging.getLogger(__name__)

class GoalStatus(str, Enum):
    """Possible statuses for character goals."""
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    PAUSED = "paused"

class GoalPriority(str, Enum):
    """Priority levels for character goals."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    
class GoalType(str, Enum):
    """Types of character goals."""
    NARRATIVE = "narrative"    # Story-related goals
    PERSONAL = "personal"      # Character's own desires
    FACTIONAL = "factional"    # Related to character's faction
    SURVIVAL = "survival"      # Basic needs and survival
    RELATIONSHIP = "relationship"  # Goals involving other characters
    ACHIEVEMENT = "achievement"    # Status/skill improvement
    CUSTOM = "custom"          # Custom goal types

class GoalCreated(EventBase):
    """Event emitted when a new goal is created."""
    character_id: str
    goal_id: str
    goal_type: str
    description: str
    priority: str
    
    def __init__(self, **data):
        data["event_type"] = "character.goal_created"
        super().__init__(**data)

class GoalCompleted(EventBase):
    """Event emitted when a goal is completed."""
    character_id: str
    goal_id: str
    goal_type: str
    description: str
    
    def __init__(self, **data):
        data["event_type"] = "character.goal_completed"
        super().__init__(**data)

class GoalFailed(EventBase):
    """Event emitted when a goal is failed."""
    character_id: str
    goal_id: str
    goal_type: str
    description: str
    reason: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "character.goal_failed"
        super().__init__(**data)

class GoalAbandoned(EventBase):
    """Event emitted when a goal is abandoned."""
    character_id: str
    goal_id: str
    goal_type: str
    description: str
    reason: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "character.goal_abandoned"
        super().__init__(**data)

class GoalProgressUpdated(EventBase):
    """Event emitted when goal progress is updated."""
    character_id: str
    goal_id: str
    old_progress: float
    new_progress: float
    
    def __init__(self, **data):
        data["event_type"] = "character.goal_progress_updated"
        super().__init__(**data)

class Goal:
    """
    Represents a character goal with progress tracking.
    
    A goal encapsulates something a character wants to achieve,
    with a progress value, status, and priority level.
    """
    
    def __init__(self, 
                character_id: Union[str, UUID], 
                description: str, 
                goal_type: Union[str, GoalType] = GoalType.PERSONAL,
                priority: Union[str, GoalPriority] = GoalPriority.MEDIUM,
                goal_id: Optional[Union[str, UUID]] = None,
                parent_goal_id: Optional[Union[str, UUID]] = None,
                status: Union[str, GoalStatus] = GoalStatus.ACTIVE,
                progress: float = 0.0,
                metadata: Optional[Dict[str, Any]] = None,
                created_at: Optional[datetime] = None):
        """
        Initialize a new goal.
        
        Args:
            character_id: UUID of the character
            description: Text description of the goal
            goal_type: Type of goal
            priority: Priority level
            goal_id: UUID of the goal (generated if None)
            parent_goal_id: UUID of parent goal if this is a subgoal
            status: Current goal status
            progress: Current progress (0.0 to 1.0)
            metadata: Additional goal-specific data
            created_at: When the goal was created
        """
        # Convert string types to enums if needed
        if isinstance(goal_type, str):
            goal_type = GoalType(goal_type)
        if isinstance(priority, str):
            priority = GoalPriority(priority)
        if isinstance(status, str):
            status = GoalStatus(status)
            
        self.character_id = str(character_id)
        self.description = description
        self.goal_type = goal_type
        self.priority = priority
        self.goal_id = str(goal_id or uuid4())
        self.parent_goal_id = str(parent_goal_id) if parent_goal_id else None
        self.status = status
        self.progress = max(0.0, min(1.0, progress))  # Clamp to [0.0, 1.0]
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.subgoals: List[Goal] = []
        
        self.event_dispatcher = EventDispatcher.get_instance()
    
    @property
    def is_complete(self) -> bool:
        """Check if the goal is completed."""
        return self.status == GoalStatus.COMPLETED
    
    @property
    def is_active(self) -> bool:
        """Check if the goal is active."""
        return self.status == GoalStatus.ACTIVE
    
    @property
    def is_failed(self) -> bool:
        """Check if the goal is failed."""
        return self.status == GoalStatus.FAILED
    
    @property
    def is_abandoned(self) -> bool:
        """Check if the goal is abandoned."""
        return self.status == GoalStatus.ABANDONED
    
    @property
    def is_paused(self) -> bool:
        """Check if the goal is paused."""
        return self.status == GoalStatus.PAUSED
    
    @property
    def has_subgoals(self) -> bool:
        """Check if the goal has subgoals."""
        return len(self.subgoals) > 0
    
    def add_subgoal(self, 
                   description: str, 
                   goal_type: Union[str, GoalType] = GoalType.PERSONAL,
                   priority: Union[str, GoalPriority] = None,
                   status: Union[str, GoalStatus] = GoalStatus.ACTIVE,
                   progress: float = 0.0,
                   metadata: Optional[Dict[str, Any]] = None) -> 'Goal':
        """
        Add a subgoal to this goal.
        
        Args:
            description: Text description of the subgoal
            goal_type: Type of subgoal
            priority: Priority level (defaults to parent priority)
            status: Current subgoal status
            progress: Current progress (0.0 to 1.0)
            metadata: Additional subgoal-specific data
            
        Returns:
            The created subgoal
        """
        # Use parent's priority if none specified
        if priority is None:
            priority = self.priority
            
        # Create subgoal with parent reference
        subgoal = Goal(
            character_id=self.character_id,
            description=description,
            goal_type=goal_type,
            priority=priority,
            parent_goal_id=self.goal_id,
            status=status,
            progress=progress,
            metadata=metadata
        )
        
        # Add to subgoals list
        self.subgoals.append(subgoal)
        
        # Emit event
        self.event_dispatcher.emit(GoalCreated(
            character_id=self.character_id,
            goal_id=subgoal.goal_id,
            goal_type=str(subgoal.goal_type),
            description=subgoal.description,
            priority=str(subgoal.priority)
        ))
        
        logger.info(f"Added subgoal '{description}' to goal {self.goal_id} for character {self.character_id}")
        return subgoal
    
    def update_progress(self, new_progress: float, update_parent: bool = True) -> None:
        """
        Update the goal's progress value.
        
        Args:
            new_progress: New progress value (0.0 to 1.0)
            update_parent: Whether to update parent goal progress
        """
        # Clamp to [0.0, 1.0]
        new_progress = max(0.0, min(1.0, new_progress))
        
        # Store old progress for event
        old_progress = self.progress
        
        # Update progress
        self.progress = new_progress
        self.updated_at = datetime.utcnow()
        
        # Check for completion
        if self.progress >= 1.0 and self.status == GoalStatus.ACTIVE:
            self.complete()
        
        # Emit progress update event
        self.event_dispatcher.emit(GoalProgressUpdated(
            character_id=self.character_id,
            goal_id=self.goal_id,
            old_progress=old_progress,
            new_progress=self.progress
        ))
        
        logger.info(f"Updated progress of goal {self.goal_id} from {old_progress:.2f} to {self.progress:.2f}")
    
    def complete(self) -> None:
        """Mark the goal as completed and update parent if needed."""
        if self.status == GoalStatus.COMPLETED:
            return
            
        self.status = GoalStatus.COMPLETED
        self.progress = 1.0
        self.updated_at = datetime.utcnow()
        
        # Emit completion event
        self.event_dispatcher.emit(GoalCompleted(
            character_id=self.character_id,
            goal_id=self.goal_id,
            goal_type=str(self.goal_type),
            description=self.description
        ))
        
        logger.info(f"Completed goal {self.goal_id}: {self.description}")
    
    def fail(self, reason: Optional[str] = None) -> None:
        """
        Mark the goal as failed.
        
        Args:
            reason: Optional reason for failure
        """
        if self.status == GoalStatus.FAILED:
            return
            
        self.status = GoalStatus.FAILED
        self.updated_at = datetime.utcnow()
        
        if reason:
            self.metadata["failure_reason"] = reason
        
        # Emit failure event
        self.event_dispatcher.emit(GoalFailed(
            character_id=self.character_id,
            goal_id=self.goal_id,
            goal_type=str(self.goal_type),
            description=self.description,
            reason=reason
        ))
        
        logger.info(f"Failed goal {self.goal_id}: {self.description}" + (f" - Reason: {reason}" if reason else ""))
    
    def abandon(self, reason: Optional[str] = None) -> None:
        """
        Mark the goal as abandoned.
        
        Args:
            reason: Optional reason for abandonment
        """
        if self.status == GoalStatus.ABANDONED:
            return
            
        self.status = GoalStatus.ABANDONED
        self.updated_at = datetime.utcnow()
        
        if reason:
            self.metadata["abandonment_reason"] = reason
        
        # Emit abandonment event
        self.event_dispatcher.emit(GoalAbandoned(
            character_id=self.character_id,
            goal_id=self.goal_id,
            goal_type=str(self.goal_type),
            description=self.description,
            reason=reason
        ))
        
        logger.info(f"Abandoned goal {self.goal_id}: {self.description}" + (f" - Reason: {reason}" if reason else ""))
    
    def pause(self) -> None:
        """Mark the goal as paused."""
        if self.status != GoalStatus.ACTIVE:
            return
            
        self.status = GoalStatus.PAUSED
        self.updated_at = datetime.utcnow()
        
        logger.info(f"Paused goal {self.goal_id}: {self.description}")
    
    def resume(self) -> None:
        """Resume a paused goal."""
        if self.status != GoalStatus.PAUSED:
            return
            
        self.status = GoalStatus.ACTIVE
        self.updated_at = datetime.utcnow()
        
        logger.info(f"Resumed goal {self.goal_id}: {self.description}")
    
    def update_priority(self, new_priority: Union[str, GoalPriority]) -> None:
        """
        Update the goal's priority.
        
        Args:
            new_priority: New priority level
        """
        # Convert string to enum if needed
        if isinstance(new_priority, str):
            new_priority = GoalPriority(new_priority)
            
        self.priority = new_priority
        self.updated_at = datetime.utcnow()
        
        logger.info(f"Updated priority of goal {self.goal_id} to {new_priority}")
    
    def calculate_subgoal_progress(self) -> float:
        """
        Calculate progress based on subgoals.
        
        Returns:
            Calculated progress value
        """
        if not self.subgoals:
            return self.progress
            
        # Calculate average progress of active/completed subgoals
        valid_subgoals = [sg for sg in self.subgoals if sg.status in (GoalStatus.ACTIVE, GoalStatus.COMPLETED)]
        if not valid_subgoals:
            return 0.0
            
        total_progress = sum(sg.progress for sg in valid_subgoals)
        return total_progress / len(valid_subgoals)
    
    def to_dict(self, include_subgoals: bool = True) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.
        
        Args:
            include_subgoals: Whether to include subgoals in output
            
        Returns:
            Dictionary representation
        """
        result = {
            "goal_id": self.goal_id,
            "character_id": self.character_id,
            "description": self.description,
            "goal_type": str(self.goal_type),
            "priority": str(self.priority),
            "status": str(self.status),
            "progress": self.progress,
            "parent_goal_id": self.parent_goal_id,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        
        if include_subgoals:
            result["subgoals"] = [sg.to_dict(include_subgoals=False) for sg in self.subgoals]
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Goal':
        """
        Create from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            Goal object
        """
        created_at = None
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
            
        # Create goal
        goal = cls(
            character_id=data["character_id"],
            description=data["description"],
            goal_type=data["goal_type"],
            priority=data["priority"],
            goal_id=data["goal_id"],
            parent_goal_id=data.get("parent_goal_id"),
            status=data["status"],
            progress=data["progress"],
            metadata=data.get("metadata", {}),
            created_at=created_at
        )
        
        # Add updated_at if present
        if data.get("updated_at"):
            goal.updated_at = datetime.fromisoformat(data["updated_at"])
            
        # Add subgoals if present
        for subgoal_data in data.get("subgoals", []):
            subgoal = Goal.from_dict(subgoal_data)
            goal.subgoals.append(subgoal)
            
        return goal 