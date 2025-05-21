"""
Core models for quest system.
Defines data structures for quests and quest steps.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class QuestStep:
    """Represents a single step within a quest."""
    
    id: int
    description: str
    type: str  # 'dialogue', 'collect', 'visit', 'kill', etc.
    completed: bool = False
    required_items: List[Dict[str, Any]] = field(default_factory=list)
    required_skills: List[Dict[str, Any]] = field(default_factory=list)
    target_npc_id: Optional[str] = None
    target_location_id: Optional[str] = None
    target_item_id: Optional[str] = None
    target_enemy_id: Optional[str] = None
    target_enemy_type: Optional[str] = None
    quantity: int = 1
    required_count: int = 1
    current_count: int = 0
    time_requirement: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert step to dictionary for storage."""
        return {
            'id': self.id,
            'description': self.description,
            'type': self.type,
            'completed': self.completed,
            'required_items': self.required_items,
            'required_skills': self.required_skills,
            'target_npc_id': self.target_npc_id,
            'target_location_id': self.target_location_id,
            'target_item_id': self.target_item_id,
            'target_enemy_id': self.target_enemy_id,
            'target_enemy_type': self.target_enemy_type,
            'quantity': self.quantity,
            'required_count': self.required_count,
            'current_count': self.current_count,
            'time_requirement': self.time_requirement
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestStep':
        """Create step from dictionary."""
        return cls(
            id=data.get('id', 0),
            description=data.get('description', ''),
            type=data.get('type', ''),
            completed=data.get('completed', False),
            required_items=data.get('required_items', []),
            required_skills=data.get('required_skills', []),
            target_npc_id=data.get('target_npc_id'),
            target_location_id=data.get('target_location_id'),
            target_item_id=data.get('target_item_id'),
            target_enemy_id=data.get('target_enemy_id'),
            target_enemy_type=data.get('target_enemy_type'),
            quantity=data.get('quantity', 1),
            required_count=data.get('required_count', 1),
            current_count=data.get('current_count', 0),
            time_requirement=data.get('time_requirement')
        )


@dataclass
class Quest:
    """Represents a quest with its steps and metadata."""
    
    id: str
    title: str
    description: str
    steps: List[QuestStep] = field(default_factory=list)
    status: str = 'pending'  # 'pending', 'active', 'completed', 'failed', 'expired'
    type: str = 'side'  # 'main', 'side', 'daily', 'event', 'personal', 'location', 'story'
    difficulty: str = 'medium'  # 'easy', 'medium', 'hard', 'epic'
    level: int = 1
    theme: str = 'general'  # 'combat', 'exploration', 'social', 'mystery', 'trade', etc.
    rewards: Dict[str, Any] = field(default_factory=dict)
    player_id: Optional[str] = None
    npc_id: Optional[str] = None
    location_id: Optional[str] = None
    arc_id: Optional[str] = None
    chapter_index: Optional[int] = None
    time_dependent: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamps if not provided."""
        now = datetime.utcnow().isoformat()
        if not self.created_at:
            self.created_at = now
        if not self.updated_at:
            self.updated_at = now
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert quest to dictionary for storage."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'steps': [step.to_dict() for step in self.steps],
            'status': self.status,
            'type': self.type,
            'difficulty': self.difficulty,
            'level': self.level,
            'theme': self.theme,
            'rewards': self.rewards,
            'player_id': self.player_id,
            'npc_id': self.npc_id,
            'location_id': self.location_id,
            'arc_id': self.arc_id,
            'chapter_index': self.chapter_index,
            'time_dependent': self.time_dependent,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'completed_at': self.completed_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Quest':
        """Create quest from dictionary."""
        # Convert step dictionaries to QuestStep objects
        steps = []
        for step_data in data.get('steps', []):
            steps.append(QuestStep.from_dict(step_data))
            
        return cls(
            id=data.get('id', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            steps=steps,
            status=data.get('status', 'pending'),
            type=data.get('type', 'side'),
            difficulty=data.get('difficulty', 'medium'),
            level=data.get('level', 1),
            theme=data.get('theme', 'general'),
            rewards=data.get('rewards', {}),
            player_id=data.get('player_id'),
            npc_id=data.get('npc_id'),
            location_id=data.get('location_id'),
            arc_id=data.get('arc_id'),
            chapter_index=data.get('chapter_index'),
            time_dependent=data.get('time_dependent', False),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            completed_at=data.get('completed_at')
        )
    
    def is_complete(self) -> bool:
        """Check if all steps in the quest are completed."""
        return all(step.completed for step in self.steps)
    
    def update_step(self, step_id: int, completed: bool = True) -> bool:
        """
        Update a step's completion status.
        
        Args:
            step_id: ID of the step to update
            completed: New completion status
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        for step in self.steps:
            if step.id == step_id:
                step.completed = completed
                self.updated_at = datetime.utcnow().isoformat()
                
                # If all steps are complete, mark quest as completed
                if self.is_complete() and self.status != 'completed':
                    self.status = 'completed'
                    self.completed_at = datetime.utcnow().isoformat()
                
                return True
        
        return False 