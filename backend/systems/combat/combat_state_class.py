"""
CombatState module for the Visual DM combat system.

This module implements the core state management for combat, providing
methods for tracking characters, serialization/deserialization, and
handling state transitions. It serves as the central data store for
an ongoing combat instance.
"""

import logging
import uuid
import json
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from app.combat.combat_class import Combatant

# Set up logging
logger = logging.getLogger(__name__)

class CombatState:
    """
    Manages the state of a combat encounter, including characters,
    round tracking, and state transitions.
    """
    
    def __init__(self, character_dict: Optional[Dict[str, Any]] = None):
        """
        Initialize a new combat state.
        
        Args:
            character_dict: Optional dictionary of characters to include, 
                            keyed by character ID
        """
        self.combat_id = str(uuid.uuid4())
        self.name = "Combat"
        self.start_time = datetime.now().isoformat()
        self.round_number = 0
        self.log = []
        self.status = "initializing"  # initializing, active, paused, victory, defeat, retreated, surrendered
        
        # Character tracking
        self.characters: Dict[str, Any] = {}
        if character_dict:
            self.add_characters(character_dict)
        
        # Team tracking (for UI and game logic)
        self.player_character_ids: Set[str] = set()
        self.enemy_character_ids: Set[str] = set()
        
        # State change history for undo/rollback
        self.state_history: List[Dict[str, Any]] = []
        
        logger.debug(f"Combat state initialized with ID {self.combat_id}")
    
    def add_character(self, character_id: str, character: Any) -> None:
        """
        Add a character to the combat state.
        
        Args:
            character_id: ID for the character
            character: Character object to add
        """
        self.characters[character_id] = character
        logger.debug(f"Added character {character_id} to combat {self.combat_id}")
    
    def add_characters(self, character_dict: Dict[str, Any]) -> None:
        """
        Add multiple characters to the combat state.
        
        Args:
            character_dict: Dictionary of characters keyed by ID
        """
        for character_id, character in character_dict.items():
            self.add_character(character_id, character)
    
    def set_player_character(self, character_id: str, is_player: bool = True) -> None:
        """
        Set a character as a player or enemy character.
        
        Args:
            character_id: ID of the character
            is_player: True if the character is a player character, False otherwise
        """
        if character_id not in self.characters:
            logger.warning(f"Cannot set player status for non-existent character {character_id}")
            return
            
        if is_player:
            self.player_character_ids.add(character_id)
            self.enemy_character_ids.discard(character_id)
        else:
            self.enemy_character_ids.add(character_id)
            self.player_character_ids.discard(character_id)
            
        logger.debug(f"Set character {character_id} as {'player' if is_player else 'enemy'}")
    
    def get_character(self, character_id: str) -> Optional[Any]:
        """
        Get a character by ID.
        
        Args:
            character_id: ID of the character to get
            
        Returns:
            Character object if found, None otherwise
        """
        return self.characters.get(character_id)
    
    def get_all_characters(self) -> Dict[str, Any]:
        """
        Get all characters in the combat.
        
        Returns:
            Dictionary of all characters keyed by ID
        """
        return self.characters
    
    def get_player_characters(self) -> Dict[str, Any]:
        """
        Get all player characters.
        
        Returns:
            Dictionary of player characters
        """
        return {char_id: self.characters[char_id] 
                for char_id in self.player_character_ids 
                if char_id in self.characters}
    
    def get_enemy_characters(self) -> Dict[str, Any]:
        """
        Get all enemy characters.
        
        Returns:
            Dictionary of enemy characters
        """
        return {char_id: self.characters[char_id] 
                for char_id in self.enemy_character_ids 
                if char_id in self.characters}
    
    def remove_character(self, character_id: str) -> bool:
        """
        Remove a character from combat.
        
        Args:
            character_id: ID of the character to remove
            
        Returns:
            True if the character was removed, False otherwise
        """
        if character_id not in self.characters:
            return False
            
        del self.characters[character_id]
        self.player_character_ids.discard(character_id)
        self.enemy_character_ids.discard(character_id)
        
        logger.debug(f"Removed character {character_id} from combat {self.combat_id}")
        return True
    
    def add_log(self, message: str) -> None:
        """
        Add a message to the combat log.
        
        Args:
            message: Message to add
        """
        self.log.append(f"[Round {self.round_number}] {message}")
        logger.debug(f"Combat log: {message}")
    
    def change_status(self, new_status: str) -> None:
        """
        Change the combat status.
        
        Args:
            new_status: New status for the combat
        """
        old_status = self.status
        self.status = new_status
        logger.info(f"Combat {self.combat_id} status changed from {old_status} to {new_status}")
        
        # Save state for history
        self._save_state_snapshot()
    
    def _save_state_snapshot(self) -> None:
        """Save the current state for history tracking."""
        snapshot = self.to_dict()
        self.state_history.append(snapshot)
        
        # Limit history size to avoid memory issues
        if len(self.state_history) > 20:
            self.state_history.pop(0)
    
    def get_previous_state(self) -> Optional[Dict[str, Any]]:
        """
        Get the previous state from history.
        
        Returns:
            Previous state dictionary if available, None otherwise
        """
        if len(self.state_history) > 1:
            return self.state_history[-2]  # Return second-to-last entry
        return None
    
    def rollback_to_previous_state(self) -> bool:
        """
        Rollback to the previous state.
        
        Returns:
            True if rollback was successful, False otherwise
        """
        if len(self.state_history) <= 1:
            return False
            
        # Pop current state
        self.state_history.pop()
        
        # Get previous state
        previous_state = self.state_history[-1]
        
        # Load from previous state
        self.from_dict(previous_state)
        
        logger.info(f"Rolled back combat {self.combat_id} to previous state")
        return True
    
    def is_player_turn(self, character_id: str) -> bool:
        """
        Check if it's a player character's turn.
        
        Args:
            character_id: ID of the character
            
        Returns:
            True if it's a player character's turn, False otherwise
        """
        return character_id in self.player_character_ids
    
    def is_over(self) -> bool:
        """
        Check if the combat is over.
        
        Returns:
            True if the combat is over, False otherwise
        """
        return self.status in ["victory", "defeat", "retreated", "surrendered"]
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the combat state to a dictionary for serialization.
        
        Returns:
            Dictionary representation of the combat state
        """
        # Create base state
        state_dict = {
            "combat_id": self.combat_id,
            "name": self.name,
            "start_time": self.start_time,
            "round_number": self.round_number,
            "log": self.log,
            "status": self.status,
            "player_character_ids": list(self.player_character_ids),
            "enemy_character_ids": list(self.enemy_character_ids),
        }
        
        # Add character IDs but not full objects
        # Characters themselves are serialized via the Combat class
        state_dict["character_ids"] = list(self.characters.keys())
        
        return state_dict
    
    def from_dict(self, state_dict: Dict[str, Any], character_dict: Optional[Dict[str, Any]] = None) -> None:
        """
        Load the combat state from a dictionary.
        
        Args:
            state_dict: Dictionary to load from
            character_dict: Optional dictionary of characters
        """
        self.combat_id = state_dict.get("combat_id", str(uuid.uuid4()))
        self.name = state_dict.get("name", "Combat")
        self.start_time = state_dict.get("start_time", datetime.now().isoformat())
        self.round_number = state_dict.get("round_number", 0)
        self.log = state_dict.get("log", [])
        self.status = state_dict.get("status", "initializing")
        
        # Update sets from lists
        self.player_character_ids = set(state_dict.get("player_character_ids", []))
        self.enemy_character_ids = set(state_dict.get("enemy_character_ids", []))
        
        # Load characters if provided
        if character_dict:
            self.characters = character_dict
        
        logger.info(f"Loaded combat state from dictionary, ID: {self.combat_id}")
    
    def to_json(self) -> str:
        """
        Convert the combat state to a JSON string.
        
        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict())
    
    def from_json(self, json_str: str, character_dict: Optional[Dict[str, Any]] = None) -> None:
        """
        Load the combat state from a JSON string.
        
        Args:
            json_str: JSON string to load from
            character_dict: Optional dictionary of characters
        """
        state_dict = json.loads(json_str)
        self.from_dict(state_dict, character_dict)

    def get_current_actor(self):
        return self.turn_order[self.current_turn_index]

    def get_opponents(self, actor):
        return self.enemies if actor in self.party else self.party

    def advance_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
        if self.current_turn_index == 0:
            self.round += 1

    def accept_surrender(self):
        """
        Handles surrender acceptance by the player.
        Flags enemies as 'defeated' without killing them.
        Ends combat.
        """
        for enemy in self.enemies:
            enemy.status_effects.append("surrendered")
            enemy.current_hp = max(1, enemy.current_hp)  # Ensure they're alive
        self.log.append("[Surrender Accepted] Combat ends peacefully.")
        self.status = "surrender_resolved"
        return True

    def handle_retreat(self):
        """
        Finalizes a retreat: ends combat and logs consequences.
        Could trigger world events later (e.g., chase or rumor).
        """
        self.log.append("[Retreat Confirmed] Enemies have fled the battlefield.")
        self.status = "retreated_resolved"
        return True
