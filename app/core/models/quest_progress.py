"""
Quest progress tracking system for monitoring individual character progress on quests.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.database import db
from app.core.models.base import BaseModel
from app.core.models.quest import QuestStatus, QuestStage

class QuestProgress(BaseModel):
    """Tracks a character's progress on a specific quest."""
    __tablename__ = 'quest_progress'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    character_id: Mapped[int] = mapped_column(Integer, ForeignKey('characters.id'), nullable=False)
    quest_id: Mapped[int] = mapped_column(Integer, ForeignKey('quests.id'), nullable=False)
    current_stage_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('quest_stages.id'))
    
    # Current status of the quest for this character
    status: Mapped[QuestStatus] = mapped_column(String(20), default=QuestStatus.AVAILABLE.value)
    
    # Track completion of conditions for current stage
    stage_conditions: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Track optional objectives completed
    optional_objectives: Mapped[List[str]] = mapped_column(JSON, default=list)
    
    # Track choices made during quest
    quest_choices: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Track any temporary quest state
    quest_state: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)
    
    # Track attempt history
    attempt_count: Mapped[int] = mapped_column(Integer, default=0)
    last_attempt_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Important timestamps
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationships
    character = relationship('Character', back_populates='quest_progress')
    quest = relationship('app.core.models.quest.Quest', back_populates='progress_records')
    current_stage = relationship('QuestStage')

    def __init__(self, **kwargs):
        """Initialize new quest progress tracking."""
        super().__init__(**kwargs)
        self.stage_conditions = {}
        self.optional_objectives = []
        self.quest_choices = {}
        self.quest_state = {}
        
    def start_quest(self) -> None:
        """Mark the quest as started for this character."""
        self.status = QuestStatus.ACTIVE
        self.started_at = datetime.utcnow()
        self.attempt_count += 1
        self.last_attempt_at = datetime.utcnow()
        
        # Initialize first stage if exists
        if self.quest.stages:
            self.current_stage = self.quest.stages[0]
            self._initialize_stage_conditions()
            
    def update_progress(self, condition_id: str, progress_value: Any) -> bool:
        """
        Update progress on a specific condition.
        
        Args:
            condition_id: ID of the condition to update
            progress_value: New progress value
            
        Returns:
            True if condition is now complete, False otherwise
        """
        if condition_id not in self.stage_conditions:
            return False
            
        condition = self.stage_conditions[condition_id]
        condition['current_value'] = progress_value
        condition['updated_at'] = datetime.utcnow().isoformat()
        
        # Check if condition is complete
        is_complete = self._evaluate_condition(condition)
        condition['is_complete'] = is_complete
        
        return is_complete
        
    def advance_stage(self) -> bool:
        """
        Attempt to advance to the next quest stage.
        
        Returns:
            True if advanced successfully, False otherwise
        """
        if not self.current_stage or not self.quest.stages:
            return False
            
        # Find next stage
        current_index = next(
            (i for i, stage in enumerate(self.quest.stages) 
             if stage.id == self.current_stage.id),
            -1
        )
        
        if current_index < 0 or current_index >= len(self.quest.stages) - 1:
            return False
            
        # Move to next stage
        self.current_stage = self.quest.stages[current_index + 1]
        self._initialize_stage_conditions()
        
        return True
        
    def complete_quest(self) -> None:
        """Mark the quest as completed."""
        self.status = QuestStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        
    def fail_quest(self) -> None:
        """Mark the quest as failed."""
        self.status = QuestStatus.FAILED
        self.attempt_count += 1
        self.last_attempt_at = datetime.utcnow()
        
    def reset_progress(self) -> None:
        """Reset progress for another attempt."""
        self.status = QuestStatus.AVAILABLE
        self.current_stage = None
        self.stage_conditions = {}
        self.quest_state = {}
        self.started_at = None
        self.completed_at = None
        
    def record_choice(self, choice_id: str, choice_value: Any) -> None:
        """
        Record a choice made during the quest.
        
        Args:
            choice_id: Identifier for the choice
            choice_value: The choice made
        """
        self.quest_choices[choice_id] = {
            'value': choice_value,
            'made_at': datetime.utcnow().isoformat()
        }
        
    def complete_optional_objective(self, objective_id: str) -> None:
        """
        Mark an optional objective as completed.
        
        Args:
            objective_id: ID of the optional objective
        """
        if objective_id not in self.optional_objectives:
            self.optional_objectives.append(objective_id)
            
    def set_quest_state(self, key: str, value: Any) -> None:
        """
        Set a temporary quest state value.
        
        Args:
            key: State key
            value: State value
        """
        self.quest_state[key] = value
        
    def get_quest_state(self, key: str, default: Any = None) -> Any:
        """
        Get a quest state value.
        
        Args:
            key: State key
            default: Default value if key not found
            
        Returns:
            State value or default
        """
        return self.quest_state.get(key, default)
        
    def _initialize_stage_conditions(self) -> None:
        """Initialize tracking for current stage conditions."""
        self.stage_conditions = {}
        
        if not self.current_stage:
            return
            
        for condition in self.current_stage.conditions:
            condition_id = str(condition['id'])
            self.stage_conditions[condition_id] = {
                'type': condition['type'],
                'requirements': condition['requirements'],
                'current_value': None,
                'is_complete': False,
                'updated_at': datetime.utcnow().isoformat()
            }
            
    def _evaluate_condition(self, condition: Dict[str, Any]) -> bool:
        """
        Evaluate if a condition is complete.
        
        Args:
            condition: Condition data to evaluate
            
        Returns:
            True if condition is complete, False otherwise
        """
        if not condition['current_value']:
            return False
            
        requirements = condition['requirements']
        current = condition['current_value']
        
        # Handle different condition types
        if condition['type'] == 'NUMERIC':
            return current >= requirements.get('target_value', 0)
        elif condition['type'] == 'BOOLEAN':
            return bool(current)
        elif condition['type'] == 'LIST':
            required_items = set(requirements.get('required_items', []))
            current_items = set(current if isinstance(current, list) else [current])
            return required_items.issubset(current_items)
        elif condition['type'] == 'STATE':
            return current == requirements.get('target_state')
            
        return False

class QuestProgressSnapshot(BaseModel):
    """Stores snapshots of quest progress for recovery/history."""
    __tablename__ = 'quest_progress_snapshots'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    progress_id: Mapped[int] = mapped_column(Integer, ForeignKey('quest_progress.id'), nullable=False)
    
    # Snapshot data
    snapshot_data: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    reason: Mapped[str] = mapped_column(String(100))  # Why the snapshot was taken
    
    # Relationship
    progress = relationship('QuestProgress', backref='snapshots')
    
    @classmethod
    def create_snapshot(
        cls,
        progress: QuestProgress,
        reason: str = "manual"
    ) -> 'QuestProgressSnapshot':
        """
        Create a snapshot of current quest progress.
        
        Args:
            progress: QuestProgress instance to snapshot
            reason: Reason for creating snapshot
            
        Returns:
            Created snapshot instance
        """
        snapshot_data = {
            'status': progress.status,
            'current_stage_id': progress.current_stage_id,
            'stage_conditions': progress.stage_conditions,
            'optional_objectives': progress.optional_objectives,
            'quest_choices': progress.quest_choices,
            'quest_state': progress.quest_state,
            'attempt_count': progress.attempt_count,
            'timestamps': {
                'started_at': progress.started_at.isoformat() if progress.started_at else None,
                'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
                'last_attempt_at': progress.last_attempt_at.isoformat() if progress.last_attempt_at else None
            }
        }
        
        return cls(
            progress_id=progress.id,
            snapshot_data=snapshot_data,
            reason=reason
        )
        
    def restore_progress(self, progress: QuestProgress) -> None:
        """
        Restore quest progress from this snapshot.
        
        Args:
            progress: QuestProgress instance to restore to
        """
        data = self.snapshot_data
        
        progress.status = data['status']
        progress.current_stage_id = data['current_stage_id']
        progress.stage_conditions = data['stage_conditions']
        progress.optional_objectives = data['optional_objectives']
        progress.quest_choices = data['quest_choices']
        progress.quest_state = data['quest_state']
        progress.attempt_count = data['attempt_count']
        
        # Restore timestamps
        timestamps = data['timestamps']
        progress.started_at = datetime.fromisoformat(timestamps['started_at']) if timestamps['started_at'] else None
        progress.completed_at = datetime.fromisoformat(timestamps['completed_at']) if timestamps['completed_at'] else None
        progress.last_attempt_at = datetime.fromisoformat(timestamps['last_attempt_at']) if timestamps['last_attempt_at'] else None 