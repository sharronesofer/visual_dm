"""
Character System
----------------
Central system for character management, including:
- Core character attributes and mechanics
- Memory management
- Relationships between entities
- Character moods and emotional states
- Character goals and motivations
"""

# Export core character models
from .models.character import Character
from .models.character_builder import CharacterBuilder
from .models.relationship import Relationship, RelationshipType
from .models.mood import CharacterMood, EmotionalState, MoodIntensity, MoodModifier
from .models.goal import Goal, GoalType, GoalPriority, GoalStatus

# Export memory system
from .memory.memory import Memory, MemoryType
from .memory.memory_manager import MemoryManager

# Export services
from .services.character_service import CharacterService
from .services.relationship_service import RelationshipService
from .services.mood_service import MoodService
from .services.goal_service import GoalService

__all__ = [
    # Core Models
    'Character',
    'CharacterBuilder',
    
    # Relationship Models
    'Relationship',
    'RelationshipType',
    
    # Mood Models
    'CharacterMood',
    'EmotionalState',
    'MoodIntensity',
    'MoodModifier',
    
    # Goal Models
    'Goal',
    'GoalType',
    'GoalPriority',
    'GoalStatus',
    
    # Memory Models
    'Memory',
    'MemoryType',
    'MemoryManager',
    
    # Services
    'CharacterService',
    'RelationshipService',
    'MoodService',
    'GoalService',
]

# Singleton factory to get service instances
_character_service = None
_relationship_service = None
_mood_service = None
_goal_service = None
_memory_manager = None

def get_character_service() -> CharacterService:
    """Get the singleton character service instance."""
    global _character_service
    if _character_service is None:
        _character_service = CharacterService()
    return _character_service

def get_relationship_service() -> RelationshipService:
    """Get the singleton relationship service instance."""
    global _relationship_service
    if _relationship_service is None:
        from sqlalchemy.orm import Session
        from backend.db import get_session
        _relationship_service = RelationshipService(db_session=get_session())
    return _relationship_service

def get_mood_service() -> MoodService:
    """Get the singleton mood service instance."""
    global _mood_service
    if _mood_service is None:
        _mood_service = MoodService()
    return _mood_service

def get_goal_service() -> GoalService:
    """Get the singleton goal service instance."""
    global _goal_service
    if _goal_service is None:
        _goal_service = GoalService()
    return _goal_service

def get_memory_manager() -> MemoryManager:
    """Get the singleton memory manager instance."""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager()
    return _memory_manager
