"""
Mood Service
------------
Service for managing character moods and emotional states.
Provides methods for adding mood modifiers, retrieving current moods, and managing mood decay.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from uuid import UUID
import json
import os

from backend.systems.events.event_dispatcher import EventDispatcher
from backend.systems.character.models.mood import (
    CharacterMood, EmotionalState, MoodIntensity, MoodModifier
)

logger = logging.getLogger(__name__)

class MoodService:
    """
    Service for managing character moods and emotional states.
    Follows the repository pattern for data access.
    """
    
    def __init__(self, data_dir: str = './data/moods'):
        """
        Initialize the service with a data directory.
        
        Args:
            data_dir: Directory where mood data is stored
        """
        self.data_dir = data_dir
        self.moods: Dict[str, CharacterMood] = {}
        self.event_dispatcher = EventDispatcher.get_instance()
        
        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)
    
    def get_mood(self, character_id: Union[str, UUID], load_if_needed: bool = True) -> CharacterMood:
        """
        Get a character's mood, loading it from storage if needed.
        
        Args:
            character_id: UUID of the character
            load_if_needed: Whether to load from disk if not in memory
            
        Returns:
            CharacterMood object
        """
        character_id_str = str(character_id)
        
        # If already loaded, return from memory
        if character_id_str in self.moods:
            return self.moods[character_id_str]
            
        # If not in memory, try to load from disk
        if load_if_needed:
            mood = self._load_mood(character_id_str)
            
            # If loaded, return it
            if mood:
                self.moods[character_id_str] = mood
                return mood
                
        # If not found, create a new one
        mood = CharacterMood(character_id_str)
        self.moods[character_id_str] = mood
        return mood
    
    def _load_mood(self, character_id: str) -> Optional[CharacterMood]:
        """
        Load a character's mood data from disk.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            CharacterMood object or None if not found
        """
        file_path = os.path.join(self.data_dir, f"{character_id}.json")
        
        # If file doesn't exist, return None
        if not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return CharacterMood.from_dict(data)
        except Exception as e:
            logger.error(f"Error loading mood data for character {character_id}: {str(e)}")
            return None
    
    def save_mood(self, character_id: Union[str, UUID]) -> bool:
        """
        Save a character's mood data to disk.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            True if successful, False otherwise
        """
        character_id_str = str(character_id)
        
        # If mood isn't in memory, nothing to save
        if character_id_str not in self.moods:
            logger.warning(f"No mood data in memory for character {character_id_str}")
            return False
            
        file_path = os.path.join(self.data_dir, f"{character_id_str}.json")
        
        try:
            # Get mood data
            mood = self.moods[character_id_str]
            
            # Convert to dict and save
            with open(file_path, 'w') as f:
                json.dump(mood.to_dict(), f, indent=2)
                
            logger.info(f"Saved mood data for character {character_id_str}")
            return True
        except Exception as e:
            logger.error(f"Error saving mood data for character {character_id_str}: {str(e)}")
            return False
    
    def update_all_moods(self, time_elapsed: Optional[timedelta] = None) -> int:
        """
        Update all loaded character moods, removing expired modifiers.
        
        Args:
            time_elapsed: Time since last update (calculated if None)
            
        Returns:
            Number of moods updated
        """
        updated_count = 0
        
        for character_id, mood in self.moods.items():
            try:
                # Update mood
                mood.update(time_elapsed)
                
                # Save changes
                self.save_mood(character_id)
                
                updated_count += 1
            except Exception as e:
                logger.error(f"Error updating mood for character {character_id}: {str(e)}")
                
        logger.info(f"Updated {updated_count} character moods")
        return updated_count
    
    def add_mood_modifier(self, 
                         character_id: Union[str, UUID], 
                         emotional_state: Union[str, EmotionalState], 
                         intensity: Union[str, MoodIntensity], 
                         reason: str, 
                         duration_hours: Optional[float] = None) -> Optional[MoodModifier]:
        """
        Add a new mood modifier to a character.
        
        Args:
            character_id: UUID of the character
            emotional_state: The emotion to modify
            intensity: How strong the modifier is
            reason: Why this modifier is being applied
            duration_hours: How long the modifier lasts (None = permanent)
            
        Returns:
            The created mood modifier or None if failed
        """
        try:
            # Get character mood
            mood = self.get_mood(character_id)
            
            # Add modifier
            modifier = mood.add_modifier(
                emotional_state=emotional_state,
                intensity=intensity,
                reason=reason,
                duration_hours=duration_hours
            )
            
            # Save changes
            self.save_mood(character_id)
            
            return modifier
        except Exception as e:
            logger.error(f"Error adding mood modifier for character {character_id}: {str(e)}")
            return None
    
    def clear_modifiers(self, character_id: Union[str, UUID]) -> int:
        """
        Remove all mood modifiers from a character.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            Number of modifiers removed
        """
        try:
            # Get character mood
            mood = self.get_mood(character_id)
            
            # Clear modifiers
            removed_count = mood.clear_modifiers()
            
            # Save changes
            self.save_mood(character_id)
            
            return removed_count
        except Exception as e:
            logger.error(f"Error clearing mood modifiers for character {character_id}: {str(e)}")
            return 0
    
    def get_current_mood(self, character_id: Union[str, UUID]) -> tuple[str, str]:
        """
        Get a character's current dominant mood and intensity.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            Tuple of (dominant_mood, intensity)
        """
        try:
            # Get character mood
            mood = self.get_mood(character_id)
            
            # Get dominant mood
            return mood.get_dominant_mood()
        except Exception as e:
            logger.error(f"Error getting current mood for character {character_id}: {str(e)}")
            return EmotionalState.NEUTRAL, MoodIntensity.MILD
    
    def get_mood_description(self, character_id: Union[str, UUID]) -> str:
        """
        Get a text description of a character's current mood.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            String description like "extremely angry" or "mildly happy"
        """
        try:
            # Get character mood
            mood = self.get_mood(character_id)
            
            # Get mood description
            return mood.get_mood_description()
        except Exception as e:
            logger.error(f"Error getting mood description for character {character_id}: {str(e)}")
            return "neutral"
    
    def set_base_mood(self, 
                     character_id: Union[str, UUID], 
                     emotional_state: Union[str, EmotionalState], 
                     value: int) -> bool:
        """
        Set the base value for an emotional state.
        
        Args:
            character_id: UUID of the character
            emotional_state: The emotion to modify
            value: New base value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get character mood
            mood = self.get_mood(character_id)
            
            # Set base mood
            mood.set_base_mood(emotional_state, value)
            
            # Save changes
            self.save_mood(character_id)
            
            return True
        except Exception as e:
            logger.error(f"Error setting base mood for character {character_id}: {str(e)}")
            return False
    
    def get_emotional_state_values(self, character_id: Union[str, UUID]) -> Dict[str, int]:
        """
        Get the current values for all emotional states.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            Dictionary of emotional states to their current values
        """
        try:
            # Get character mood
            mood = self.get_mood(character_id)
            
            # Calculate values
            values = mood.calculate_mood_values()
            
            # Convert enum keys to strings
            return {str(k): v for k, v in values.items()}
        except Exception as e:
            logger.error(f"Error getting emotional state values for character {character_id}: {str(e)}")
            return {str(EmotionalState.NEUTRAL): 3}
    
    def get_active_modifiers(self, character_id: Union[str, UUID]) -> List[Dict[str, Any]]:
        """
        Get all active mood modifiers for a character.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            List of modifier dictionaries
        """
        try:
            # Get character mood
            mood = self.get_mood(character_id)
            
            # Get active modifiers
            return [mod.to_dict() for mod in mood.mood_modifiers if not mod.is_expired]
        except Exception as e:
            logger.error(f"Error getting active modifiers for character {character_id}: {str(e)}")
            return [] 