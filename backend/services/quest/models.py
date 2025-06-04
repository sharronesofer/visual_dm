"""
Quest System Business Logic Models

This module defines pure business logic models for the quest system
according to the Development Bible standards.
"""

from typing import Optional, List, Dict, Any, Protocol
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field


class QuestStatus(Enum):
    """Quest status enumeration"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    ABANDONED = "abandoned"
    EXPIRED = "expired"


class QuestDifficulty(Enum):
    """Quest difficulty enumeration"""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EPIC = "epic"


class QuestTheme(Enum):
    """Quest theme enumeration"""
    COMBAT = "combat"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    MYSTERY = "mystery"
    CRAFTING = "crafting"
    TRADE = "trade"
    AID = "aid"
    KNOWLEDGE = "knowledge"
    GENERAL = "general"


# Enum aliases for backward compatibility
QuestStatusEnum = QuestStatus
QuestDifficultyEnum = QuestDifficulty
QuestThemeEnum = QuestTheme


class QuestStepData:
    """Business domain quest step data structure"""
    def __init__(self,
                 id: int,
                 title: str,
                 description: str,
                 completed: bool = False,
                 required: bool = True,
                 order: int = 0,
                 metadata: Optional[Dict[str, Any]] = None):
        self.id = id
        self.title = title
        self.description = description
        self.completed = completed
        self.required = required
        self.order = order
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'completed': self.completed,
            'required': self.required,
            'order': self.order,
            'metadata': self.metadata
        }


class QuestRewardData:
    """Business domain quest reward data structure"""
    def __init__(self,
                 gold: int = 0,
                 experience: int = 0,
                 reputation: Optional[Dict[str, Any]] = None,
                 items: Optional[List[Dict[str, Any]]] = None,
                 special: Optional[Dict[str, Any]] = None):
        self.gold = gold
        self.experience = experience
        self.reputation = reputation or {}
        self.items = items or []
        self.special = special or {}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'gold': self.gold,
            'experience': self.experience,
            'reputation': self.reputation,
            'items': self.items,
            'special': self.special
        }


@dataclass
class QuestData:
    """
    Core quest data structure
    
    This represents a quest in the game system including all metadata,
    requirements, rewards, and progress tracking.
    """
    id: UUID
    title: str
    description: str
    status: QuestStatus
    difficulty: QuestDifficulty
    theme: QuestTheme
    npc_id: Optional[str] = None
    player_id: Optional[str] = None
    location_id: Optional[str] = None
    level: int = 1
    steps: List[QuestStepData] = field(default_factory=list)
    rewards: Optional[QuestRewardData] = None
    is_main_quest: bool = False
    tags: List[str] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    # Quest Chain Support
    chain_id: Optional[str] = None           # ID of the quest chain this quest belongs to
    chain_position: Optional[int] = None     # Position in the chain (0-indexed)
    chain_prerequisites: List[str] = field(default_factory=list)  # Quest IDs that must be completed first
    chain_unlocks: List[str] = field(default_factory=list)        # Quest IDs this quest unlocks when completed
    is_chain_final: bool = False             # True if this is the final quest in a chain

    def get_progress(self) -> float:
        """Calculate quest completion progress"""
        if not self.steps:
            return 0.0
        
        completed_steps = sum(1 for step in self.steps if step.completed)
        return completed_steps / len(self.steps)

    def is_completed(self) -> bool:
        """Check if all required steps are completed"""
        if not self.steps:
            return False
        
        required_steps = [step for step in self.steps if step.required]
        if not required_steps:
            return False
        
        return all(step.completed for step in required_steps)

    def get_next_step(self) -> Optional[QuestStepData]:
        """Get the next incomplete step"""
        for step in sorted(self.steps, key=lambda s: s.order):
            if not step.completed:
                return step
        return None

    def complete_step(self, step_id: int) -> bool:
        """Mark a step as completed"""
        for step in self.steps:
            if step.id == step_id:
                step.completed = True
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'status': self.status.value,
            'difficulty': self.difficulty.value,
            'theme': self.theme.value,
            'npc_id': self.npc_id,
            'player_id': self.player_id,
            'location_id': self.location_id,
            'level': self.level,
            'steps': [step.to_dict() for step in self.steps],
            'rewards': self.rewards.to_dict(),
            'properties': self.properties,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }


class CreateQuestData:
    """Business domain data for quest creation"""
    def __init__(self,
                 title: str,
                 description: str,
                 difficulty: QuestDifficulty = QuestDifficulty.MEDIUM,
                 theme: QuestTheme = QuestTheme.GENERAL,
                 npc_id: Optional[str] = None,
                 location_id: Optional[str] = None,
                 level: int = 1,
                 steps: Optional[List[Dict[str, Any]]] = None,
                 rewards: Optional[Dict[str, Any]] = None,
                 properties: Optional[Dict[str, Any]] = None,
                 expires_at: Optional[datetime] = None):
        self.title = title
        self.description = description
        self.difficulty = difficulty
        self.theme = theme
        self.npc_id = npc_id
        self.location_id = location_id
        self.level = level
        self.steps = steps or []
        self.rewards = rewards or {}
        self.properties = properties or {}
        self.expires_at = expires_at


class UpdateQuestData:
    """Business domain data for quest updates"""
    def __init__(self, **update_fields):
        self.update_fields = update_fields

    def get_fields(self) -> Dict[str, Any]:
        return self.update_fields


# Business Logic Protocols (dependency injection)
class QuestRepository(Protocol):
    """Protocol for quest data access"""
    
    def get_quest_by_id(self, quest_id: UUID) -> Optional[QuestData]:
        """Get quest by ID"""
        ...
    
    def get_quest_by_title(self, title: str) -> Optional[QuestData]:
        """Get quest by title"""
        ...
    
    def create_quest(self, quest_data: QuestData) -> QuestData:
        """Create a new quest"""
        ...
    
    def update_quest(self, quest_data: QuestData) -> QuestData:
        """Update existing quest"""
        ...
    
    def delete_quest(self, quest_id: UUID) -> bool:
        """Delete quest"""
        ...
    
    def list_quests(self, 
                   page: int = 1, 
                   size: int = 50, 
                   status: Optional[str] = None,
                   search: Optional[str] = None) -> tuple[List[QuestData], int]:
        """List quests with pagination"""
        ...
    
    def get_player_quests(self, player_id: str, status: Optional[str] = None) -> List[QuestData]:
        """Get quests for a specific player"""
        ...
    
    def get_npc_quests(self, npc_id: str, status: Optional[str] = None) -> List[QuestData]:
        """Get quests for a specific NPC"""
        ...
    
    def get_location_quests(self, location_id: str, status: Optional[str] = None) -> List[QuestData]:
        """Get quests for a specific location"""
        ...
    
    def get_quest_statistics(self) -> Dict[str, Any]:
        """Get quest statistics"""
        ...


class QuestValidationService(Protocol):
    """Protocol for quest validation"""
    
    def validate_quest_data(self, quest_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quest creation/update data"""
        ...
    
    def validate_quest_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate quest steps"""
        ...
    
    def validate_quest_rewards(self, rewards: Dict[str, Any]) -> Dict[str, Any]:
        """Validate quest rewards"""
        ...


class QuestGenerationService(Protocol):
    """Protocol for quest generation"""
    
    def generate_quest_for_npc(self, npc_data: Dict[str, Any], context: Dict[str, Any]) -> Optional[QuestData]:
        """Generate a quest for an NPC"""
        ...
    
    def generate_quest_steps(self, theme: QuestTheme, difficulty: QuestDifficulty, context: Dict[str, Any]) -> List[QuestStepData]:
        """Generate quest steps"""
        ...
    
    def generate_quest_rewards(self, difficulty: QuestDifficulty, level: int) -> QuestRewardData:
        """Generate quest rewards"""
        ...


@dataclass
class QuestChainData:
    """
    Quest chain data structure
    
    Represents a series of connected quests that tell a story or achieve a goal.
    """
    id: str
    name: str
    description: str
    theme: QuestTheme
    difficulty: QuestDifficulty
    min_level: int
    max_level: Optional[int] = None
    quest_ids: List[str] = field(default_factory=list)
    chain_type: str = "sequential"  # "sequential", "branching", "parallel"
    is_main_story: bool = False
    rewards: Optional[QuestRewardData] = None  # Completion rewards for entire chain
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None

    def validate_chain_structure(self) -> List[str]:
        """Validate that the quest chain has a valid structure"""
        errors = []
        
        if not self.quest_ids:
            errors.append("Quest chain must contain at least one quest")
        
        if self.chain_type == "sequential" and len(self.quest_ids) < 2:
            errors.append("Sequential quest chain must contain at least 2 quests")
        
        if self.min_level <= 0:
            errors.append("Minimum level must be positive")
        
        if self.max_level and self.max_level < self.min_level:
            errors.append("Maximum level must be greater than minimum level")
        
        return errors


class ChainType(Enum):
    """Quest chain type enumeration"""
    SEQUENTIAL = "sequential"
    BRANCHING = "branching"
    PARALLEL = "parallel"


# Additional enum aliases
ChainTypeEnum = ChainType


@dataclass
class QuestChainProgressData:
    """
    Quest chain progress tracking
    
    Tracks a player's progress through a quest chain.
    """
    id: str
    chain_id: str
    player_id: str
    current_quest_id: Optional[str] = None
    completed_quests: List[str] = field(default_factory=list)
    available_quests: List[str] = field(default_factory=list)
    status: str = "active"  # "active", "completed", "abandoned"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LocationData:
    """Location information for difficulty calculations"""
    id: str
    name: str
    x: float
    y: float
    z: float = 0.0
    base_danger_level: int = 1      # 1-10 scale
    zone_modifiers: Dict[str, float] = field(default_factory=dict)  # Additional zone-specific modifiers
    poi_type: str = "generic"       # POI type (town, dungeon, wilderness, etc.)


@dataclass
class PlayerHomeData:
    """Player's home/starting location data"""
    player_id: str
    home_location_id: str
    home_x: float
    home_y: float
    home_z: float = 0.0
    player_level: int = 1
    exploration_bonus: float = 1.0  # Multiplier for player's exploration skills 