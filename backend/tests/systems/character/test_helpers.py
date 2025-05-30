"""
Test helpers for character system tests.
"""

from typing import Type
from unittest.mock import MagicMock
from datetime import datetime, timedelta
import uuid

try: pass
    from backend.systems.character.models.goal import Goal
except ImportError: pass
    # Nuclear fallback for Goal
    class Goal: pass
        def __init__(self, **kwargs): pass
            for k, v in kwargs.items(): pass
                setattr(self, k, v)

# Additional imports
try: pass
    from backend.systems.character.models import character
except ImportError: pass
    # Mock character module
    class character: pass
        pass

try: pass
    from backend.systems.character.models.goal import (
        GoalType,
        GoalPriority,
        GoalStatus,
    )
except ImportError: pass
    # Mock enums
    from enum import Enum
    
    class GoalType(Enum): pass
        PERSONAL = "personal"
        FACTION = "faction"
        
    class GoalPriority(Enum): pass
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        
    class GoalStatus(Enum): pass
        ACTIVE = "active"
        COMPLETED = "completed"
        FAILED = "failed"

try: pass
    from backend.systems.character.models.mood import (
        CharacterMood,
        MoodModifier,
        EmotionalState,
        MoodIntensity,
        MoodSource,
    )
except ImportError: pass
    # Mock mood classes and enums
    from enum import Enum
    
    class EmotionalState(Enum): pass
        HAPPY = "happy"
        ANGRY = "angry"
        SAD = "sad"
        FEARFUL = "fearful"
        NEUTRAL = "neutral"
        
    class MoodIntensity(Enum): pass
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        
    class MoodSource(Enum): pass
        SYSTEM = "system"
        EVENT = "event"
        
    class CharacterMood: pass
        def __init__(self, **kwargs): pass
            for k, v in kwargs.items(): pass
                setattr(self, k, v)
                
    class MoodModifier: pass
        def __init__(self, **kwargs): pass
            for k, v in kwargs.items(): pass
                setattr(self, k, v)


def create_mock_goal(
    goal_id=None,
    character_id=None,
    description="Test goal",
    goal_type=GoalType.PERSONAL,
    priority=GoalPriority.MEDIUM,
    status=GoalStatus.ACTIVE,
    progress=0.0,
): pass
    """Create a standardized mock Goal object with all required attributes."""
    goal = MagicMock(spec=Goal)
    
    # Core attributes
    goal.goal_id = str(goal_id or uuid.uuid4())
    goal.id = goal.goal_id  # For compatibility with both access patterns
    goal.character_id = str(character_id or uuid.uuid4())
    goal.description = description
    goal.goal_type = goal_type
    goal.type = goal_type  # For compatibility
    goal.priority = priority
    goal.status = status
    goal.progress = progress
    
    # Timestamps
    goal.created_at = datetime.utcnow()
    goal.updated_at = datetime.utcnow()
    goal.completed_at = None
    
    # Other attributes
    goal.failure_reason = None
    goal.metadata = {}
    
    # Methods
    goal.to_dict.return_value = {
        "goal_id": goal.goal_id,
        "character_id": goal.character_id,
        "description": goal.description,
        "goal_type": goal.goal_type.value,
        "priority": goal.priority.value,
        "status": goal.status.value,
        "progress": goal.progress,
        "created_at": goal.created_at.isoformat(),
        "updated_at": goal.updated_at.isoformat(),
        "metadata": goal.metadata,
    }
    
    goal.complete = MagicMock()
    goal.fail = MagicMock()
    goal.abandon = MagicMock()
    goal.update_priority = MagicMock()
    
    return goal


def create_mock_character_mood(
    character_id=None,
    emotional_state=EmotionalState.NEUTRAL,
    intensity=MoodIntensity.LOW,
    reason="Default mood",
): pass
    """Create a standardized mock CharacterMood object with all required attributes."""
    mood = MagicMock(spec=CharacterMood)
    
    # Core attributes
    mood.character_id = str(character_id or uuid.uuid4())
    mood.emotional_state = emotional_state
    mood.intensity = intensity
    mood.reason = reason
    
    # Timestamps
    mood.created_at = datetime.utcnow()
    mood.updated_at = datetime.utcnow()
    
    # Other attributes
    mood.modifiers = []
    mood.base_mood = {
        EmotionalState.HAPPY: 5,
        EmotionalState.ANGRY: 0,
        EmotionalState.SAD: 0,
        EmotionalState.FEARFUL: 0,
        EmotionalState.NEUTRAL: 3,
    }
    
    # Methods
    mood.get_dominant_mood = MagicMock(return_value=(emotional_state, intensity))
    mood.get_mood_description = MagicMock(return_value=f"{intensity.value} {emotional_state.value}")
    mood.set_base_mood = MagicMock()
    mood.calculate_mood_values = MagicMock(return_value=mood.base_mood)
    mood.update = MagicMock()
    
    return mood


def create_mock_mood_modifier(
    modifier_id=None,
    emotional_state=EmotionalState.HAPPY,
    intensity=MoodIntensity.MEDIUM,
    reason="Test modifier",
    hours_duration=4,
): pass
    """Create a standardized mock MoodModifier object with all required attributes."""
    modifier = MagicMock(spec=MoodModifier)
    
    # Core attributes
    modifier.id = str(modifier_id or uuid.uuid4())
    modifier.emotional_state = emotional_state
    modifier.intensity = intensity
    modifier.reason = reason
    modifier.source = MoodSource.SYSTEM.value
    modifier.modifier_type = "standard"
    
    # Timestamps
    modifier.created_at = datetime.utcnow()
    modifier.expires_at = datetime.utcnow() + timedelta(hours=hours_duration) if hours_duration else None
    
    # Properties
    modifier.is_expired = False
    
    # Methods
    modifier.to_dict = MagicMock(return_value={
        "id": modifier.id,
        "emotional_state": modifier.emotional_state.value,
        "intensity": modifier.intensity.value,
        "reason": modifier.reason,
        "created_at": modifier.created_at.isoformat(),
        "expires_at": modifier.expires_at.isoformat() if modifier.expires_at else None,
        "source": modifier.source,
        "modifier_type": modifier.modifier_type,
    })
    
    return modifier 