"""
Mood Model
----------
Implements the character mood system as described in the Development Bible.
Tracks emotional states and moods with modifiers and decay mechanics.
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from uuid import UUID
import logging
from dataclasses import dataclass

from backend.systems.events.event_dispatcher import EventDispatcher
from backend.systems.events.canonical_events import EventBase

logger = logging.getLogger(__name__)

class EmotionalState(str, Enum):
    """Primary emotional states a character can experience."""
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    SURPRISED = "surprised"
    NEUTRAL = "neutral"

class MoodIntensity(str, Enum):
    """Intensity levels for moods."""
    MILD = "mild"
    MODERATE = "moderate"
    STRONG = "strong"
    EXTREME = "extreme"

@dataclass
class MoodModifier:
    """
    Represents a temporary modifier to a character's mood.
    
    Attributes:
        emotional_state: The emotion being affected
        intensity: How strongly the modifier affects the mood
        reason: Description of what caused this modifier
        expiry: When this modifier should expire (None for permanent)
        created_at: When this modifier was created
    """
    emotional_state: EmotionalState
    intensity: MoodIntensity
    reason: str
    expiry: Optional[datetime] = None
    created_at: datetime = datetime.utcnow()
    
    @property
    def is_expired(self) -> bool:
        """Check if this modifier has expired."""
        if self.expiry is None:
            return False
        return datetime.utcnow() > self.expiry
    
    @property
    def value(self) -> int:
        """Get the numeric value of this modifier based on intensity."""
        intensity_values = {
            MoodIntensity.MILD: 1,
            MoodIntensity.MODERATE: 2,
            MoodIntensity.STRONG: 3,
            MoodIntensity.EXTREME: 5
        }
        return intensity_values.get(self.intensity, 1)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "emotional_state": self.emotional_state,
            "intensity": self.intensity,
            "reason": self.reason,
            "expiry": self.expiry.isoformat() if self.expiry else None,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MoodModifier':
        """Create from dictionary."""
        expiry = None
        if data.get("expiry"):
            expiry = datetime.fromisoformat(data["expiry"])
        
        created_at = datetime.utcnow()
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])
            
        return cls(
            emotional_state=EmotionalState(data["emotional_state"]),
            intensity=MoodIntensity(data["intensity"]),
            reason=data["reason"],
            expiry=expiry,
            created_at=created_at
        )

class MoodChanged(EventBase):
    """Event emitted when a character's mood changes significantly."""
    character_id: str
    old_primary_mood: Optional[str]
    new_primary_mood: str
    old_intensity: Optional[str]
    new_intensity: str
    cause: Optional[str] = None
    
    def __init__(self, **data):
        data["event_type"] = "character.mood_changed"
        super().__init__(**data)

class CharacterMood:
    """
    Manages a character's mood and emotional state.
    
    Features:
    - Tracks multiple emotional states with intensity values
    - Supports temporary mood modifiers with decay
    - Emits events on significant mood changes
    - Provides dominant mood calculation
    """
    
    def __init__(self, character_id: Union[str, UUID]):
        """Initialize mood tracker for a character."""
        self.character_id = str(character_id)
        self.mood_modifiers: List[MoodModifier] = []
        self.base_mood: Dict[EmotionalState, int] = {
            state: 0 for state in EmotionalState
        }
        # Default to neutral
        self.base_mood[EmotionalState.NEUTRAL] = 3
        
        self.event_dispatcher = EventDispatcher.get_instance()
        self.last_update = datetime.utcnow()
    
    def add_modifier(self, 
                    emotional_state: Union[str, EmotionalState], 
                    intensity: Union[str, MoodIntensity], 
                    reason: str, 
                    duration_hours: Optional[float] = None) -> MoodModifier:
        """
        Add a new mood modifier.
        
        Args:
            emotional_state: The emotion to modify
            intensity: How strong the modifier is
            reason: Why this modifier is being applied
            duration_hours: How long the modifier lasts (None = permanent)
            
        Returns:
            The created mood modifier
        """
        # Convert string types to enums if needed
        if isinstance(emotional_state, str):
            emotional_state = EmotionalState(emotional_state)
        if isinstance(intensity, str):
            intensity = MoodIntensity(intensity)
            
        # Calculate expiry time
        expiry = None
        if duration_hours is not None:
            expiry = datetime.utcnow() + timedelta(hours=duration_hours)
            
        # Create the modifier
        modifier = MoodModifier(
            emotional_state=emotional_state,
            intensity=intensity,
            reason=reason,
            expiry=expiry
        )
        
        # Store old mood for event emission
        old_mood, old_intensity = self.get_dominant_mood()
        
        # Add to list
        self.mood_modifiers.append(modifier)
        
        # Calculate new mood
        new_mood, new_intensity = self.get_dominant_mood()
        
        # If dominant mood changed, emit event
        if old_mood != new_mood or old_intensity != new_intensity:
            self.event_dispatcher.emit(MoodChanged(
                character_id=self.character_id,
                old_primary_mood=old_mood,
                new_primary_mood=new_mood,
                old_intensity=old_intensity,
                new_intensity=new_intensity,
                cause=reason
            ))
            
        logger.info(f"Added {intensity} {emotional_state} mood modifier to character {self.character_id}: {reason}")
        return modifier
    
    def remove_expired_modifiers(self) -> int:
        """
        Remove all expired mood modifiers.
        
        Returns:
            Number of modifiers removed
        """
        # Store old mood for event emission
        old_mood, old_intensity = self.get_dominant_mood()
        
        # Filter out expired modifiers
        original_count = len(self.mood_modifiers)
        self.mood_modifiers = [mod for mod in self.mood_modifiers if not mod.is_expired]
        removed_count = original_count - len(self.mood_modifiers)
        
        # If modifiers were removed, check if dominant mood changed
        if removed_count > 0:
            new_mood, new_intensity = self.get_dominant_mood()
            
            # If dominant mood changed, emit event
            if old_mood != new_mood or old_intensity != new_intensity:
                self.event_dispatcher.emit(MoodChanged(
                    character_id=self.character_id,
                    old_primary_mood=old_mood,
                    new_primary_mood=new_mood,
                    old_intensity=old_intensity,
                    new_intensity=new_intensity,
                    cause="Mood modifiers expired"
                ))
                
            logger.info(f"Removed {removed_count} expired mood modifiers from character {self.character_id}")
            
        return removed_count
    
    def clear_modifiers(self) -> int:
        """
        Remove all mood modifiers.
        
        Returns:
            Number of modifiers removed
        """
        # Store old mood for event emission
        old_mood, old_intensity = self.get_dominant_mood()
        
        # Clear modifiers
        removed_count = len(self.mood_modifiers)
        self.mood_modifiers = []
        
        # Reset to neutral base mood
        for state in EmotionalState:
            self.base_mood[state] = 0
        self.base_mood[EmotionalState.NEUTRAL] = 3
        
        # Calculate new mood
        new_mood, new_intensity = self.get_dominant_mood()
        
        # If dominant mood changed, emit event
        if old_mood != new_mood or old_intensity != new_intensity:
            self.event_dispatcher.emit(MoodChanged(
                character_id=self.character_id,
                old_primary_mood=old_mood,
                new_primary_mood=new_mood,
                old_intensity=old_intensity,
                new_intensity=new_intensity,
                cause="All mood modifiers cleared"
            ))
            
        logger.info(f"Cleared all mood modifiers from character {self.character_id}")
        return removed_count
    
    def update(self, time_elapsed: Optional[timedelta] = None) -> None:
        """
        Update mood state, removing expired modifiers.
        
        Args:
            time_elapsed: Time since last update (calculated if None)
        """
        if time_elapsed is None:
            time_elapsed = datetime.utcnow() - self.last_update
            
        # Remove expired modifiers
        self.remove_expired_modifiers()
        
        # Update last update time
        self.last_update = datetime.utcnow()
    
    def calculate_mood_values(self) -> Dict[EmotionalState, int]:
        """
        Calculate current values for all emotional states.
        
        Returns:
            Dictionary of emotional states to their current values
        """
        # Start with base values
        result = self.base_mood.copy()
        
        # Add modifiers
        for modifier in self.mood_modifiers:
            if not modifier.is_expired:
                result[modifier.emotional_state] = result.get(modifier.emotional_state, 0) + modifier.value
                
        return result
    
    def get_dominant_mood(self) -> tuple[str, str]:
        """
        Get the character's dominant mood and its intensity.
        
        Returns:
            Tuple of (dominant_mood, intensity)
        """
        # Calculate all mood values
        mood_values = self.calculate_mood_values()
        
        # Find the dominant mood
        dominant_mood = EmotionalState.NEUTRAL
        highest_value = -1
        
        for mood, value in mood_values.items():
            if value > highest_value:
                highest_value = value
                dominant_mood = mood
                
        # Determine intensity based on value
        intensity = MoodIntensity.MILD
        if highest_value >= 8:
            intensity = MoodIntensity.EXTREME
        elif highest_value >= 5:
            intensity = MoodIntensity.STRONG
        elif highest_value >= 3:
            intensity = MoodIntensity.MODERATE
            
        return dominant_mood, intensity
    
    def get_mood_description(self) -> str:
        """
        Get a text description of the character's current mood.
        
        Returns:
            String description like "extremely angry" or "mildly happy"
        """
        mood, intensity = self.get_dominant_mood()
        return f"{intensity} {mood}"
    
    def set_base_mood(self, 
                     emotional_state: Union[str, EmotionalState], 
                     value: int) -> None:
        """
        Set the base value for an emotional state.
        
        Args:
            emotional_state: The emotion to modify
            value: New base value
        """
        # Convert string type to enum if needed
        if isinstance(emotional_state, str):
            emotional_state = EmotionalState(emotional_state)
            
        # Store old mood for event emission
        old_mood, old_intensity = self.get_dominant_mood()
        
        # Update base mood
        self.base_mood[emotional_state] = value
        
        # Calculate new mood
        new_mood, new_intensity = self.get_dominant_mood()
        
        # If dominant mood changed, emit event
        if old_mood != new_mood or old_intensity != new_intensity:
            self.event_dispatcher.emit(MoodChanged(
                character_id=self.character_id,
                old_primary_mood=old_mood,
                new_primary_mood=new_mood,
                old_intensity=old_intensity,
                new_intensity=new_intensity,
                cause=f"Base mood changed for {emotional_state}"
            ))
            
        logger.info(f"Set base mood {emotional_state} to {value} for character {self.character_id}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "character_id": self.character_id,
            "base_mood": {str(k): v for k, v in self.base_mood.items()},
            "mood_modifiers": [mod.to_dict() for mod in self.mood_modifiers],
            "last_update": self.last_update.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CharacterMood':
        """Create from dictionary."""
        mood = cls(data["character_id"])
        
        # Restore base mood
        for state_str, value in data.get("base_mood", {}).items():
            state = EmotionalState(state_str)
            mood.base_mood[state] = value
            
        # Restore modifiers
        for mod_data in data.get("mood_modifiers", []):
            mood.mood_modifiers.append(MoodModifier.from_dict(mod_data))
            
        # Restore last update time
        if data.get("last_update"):
            mood.last_update = datetime.fromisoformat(data["last_update"])
            
        return mood 