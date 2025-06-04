"""
Combat class for the Visual DM combat system.

This module implements the main Combat class that orchestrates all combat functionality.
It integrates turn management, effect systems, area management, and visualization.
"""

import logging
import random
import time
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable

from backend.infrastructure.utils.combat.combat_state_class import CombatState
from backend.systems.combat.utils.turn_queue import TurnQueue
from backend.infrastructure.utils.combat.effect_pipeline import EffectPipeline, CombatEffect
from backend.infrastructure.utils.combat.object_pool import combat_pool_manager
from backend.systems.combat.utils.action_system import action_system, ActionResult, ActionType
from backend.infrastructure.utils.combat.combat_area import create_combat_area, CombatArea, Position
from backend.infrastructure.utils.combat.fog_of_war import create_fog_of_war, FogOfWar, VisibilityStatus
from backend.infrastructure.utils.combat.combat_animation_system import combat_animation_system

# Import visualization system
from backend.infrastructure.utils.combat.effect_visualizer import effect_visualizer

# Import debug interface
from backend.infrastructure.utils.combat.combat_debug_interface import combat_debug_interface

# Set up logging
logger = logging.getLogger(__name__)

class Combatant:
    """
    Represents a combatant in the combat system.
    """
    def __init__(self, character_id, character_data: Dict[str, Any]):
        self.character_id = character_id
        self.name = character_data.get('name', character_id)
        self.hp = character_data.get('hp', 100)
        self.max_hp = character_data.get('max_hp', self.hp)
        self.mp = character_data.get('mp', 0)
        self.max_mp = character_data.get('max_mp', self.mp)
        self.ac = character_data.get('ac', 10)
        self.attributes = character_data.get('attributes', {})
        self.is_enemy = character_data.get('is_enemy', False)
        self.team = character_data.get('team', 'hostile' if self.is_enemy else 'friendly')
        self.status_effects = {}
        self.initiative = 0
        
    def get_attribute_modifier(self, attribute) -> int:
        """Get the modifier for an attribute."""
        value = self.attributes.get(attribute, 10)
        return (value - 10) // 2
        
    def is_alive(self) -> bool:
        """Check if the combatant is alive."""
        return self.hp > 0
        
    def take_damage(self, amount) -> int:
        """Take damage and return actual damage taken."""
        old_hp = self.hp
        self.hp = max(0, self.hp - amount)
        return old_hp - self.hp
        
    def heal(self, amount) -> int:
        """Heal and return actual healing done."""
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

class Combat:
    def __init__(self, character_dict=None, combat_state=None, area_size=(20.0, 20.0)):
        """
        Initialize a combat instance.
        
        Args:
            character_dict: Optional dictionary of characters to include
            combat_state: Optional pre-existing combat state to use
            area_size: Size of the combat area (width, height)
        """
        self.combat_id = str(uuid.uuid4())
        self.timestamp = time.time()
        
        # Initialize subsystems
        self.turn_queue = TurnQueue()
        self.effect_pipeline = EffectPipeline()
        
        # Initialize new subsystems
        self.combat_area = create_combat_area(f"Area {self.combat_id[:6]}", area_size)
        self.fog_of_war = create_fog_of_war(self.combat_area)
        
        # Register turn callbacks for effect processing
        self.turn_queue.register_turn_start_callback(self._on_turn_start)
        self.turn_queue.register_turn_end_callback(self._on_turn_end)
        
        # Set up character tracking
        if combat_state:
            self.combat_state = combat_state
        else:
            self.combat_state = CombatState()
            if character_dict:
                self.combat_state.add_characters(character_dict)
                
                # Initialize positions for all characters
                self._initialize_character_positions(character_dict)
        
        # Track current round
        self.round_number = 0
        
        # Track if debug mode is enabled
        self.debug_mode = False
        
        # Register combat with debug interface if available
        if combat_debug_interface:
            # Don't automatically set as active to avoid interfering with other combats
            combat_debug_interface.test_combats[self.combat_id] = self
        
        logger.info(f"Combat initialized with ID {self.combat_id}")
    
    def _initialize_character_positions(self, character_dict: Dict[str, Any]) -> None:
        """
        Initialize positions for all characters in the combat.
        
        Args:
            character_dict: Dictionary of characters to position
        """
        # Get area size for positioning
        area_width, area_height = self.combat_area.size
        
        # Separate characters into allies and enemies for positioning
        allies = []
        enemies = []
        
        for char_id, char_data in character_dict.items():
            if char_data.get('is_enemy', False):
                enemies.append(char_id)
            else:
                allies.append(char_id)
                
        # Calculate spacing
        ally_spacing = min(2.0, area_width / max(len(allies), 1))
        enemy_spacing = min(2.0, area_width / max(len(enemies), 1))
        
        # Position allies at bottom of the area
        for i, ally_id in enumerate(allies):
            # Calculate position across the width
            x_pos = (i + 0.5) * ally_spacing
            # Place at bottom of area with some padding
            z_pos = area_height * 0.25
            
            # Add to combat area
            position = (x_pos, 0.0, z_pos)
            self.combat_area.add_entity(ally_id, position)
            
            # Initialize entity in fog of war
            char_data = character_dict[ally_id]
            self.fog_of_war.update_entity(
                ally_id,
                stealth=char_data.get('stealth', 10.0),
                detection=char_data.get('perception', 50.0),
                position=position
            )
        
        # Position enemies at top of the area
        for i, enemy_id in enumerate(enemies):
            # Calculate position across the width
            x_pos = (i + 0.5) * enemy_spacing
            # Place at top of area with some padding
            z_pos = area_height * 0.75
            
            # Add to combat area
            position = (x_pos, 0.0, z_pos)
            self.combat_area.add_entity(enemy_id, position)
            
            # Initialize entity in fog of war
            char_data = character_dict[enemy_id]
            self.fog_of_war.update_entity(
                enemy_id,
                stealth=char_data.get('stealth', 10.0),
                detection=char_data.get('perception', 50.0),
                position=position
            )
    
    def _on_turn_start(self, combatant_id) -> None:
        """
        Callback for when a combatant's turn starts.
        
        Args:
            combatant_id: ID of the combatant whose turn is starting
        """
        character = self.combat_state.get_character(combatant_id)
        if character:
            # Reset action economy for the character
            action_system.reset_combatant_actions(character)
            
            # Process turn start effects
            self.effect_pipeline.process_turn_start(character)
            
            # Update fog of war perception for the current character
            self.fog_of_war.update_all_visibility()
            
            # Play turn start animation if available
            combat_animation_system.play_action_animation(
                "turn_start",
                combatant_id,
                [combatant_id],
                {"animation_type": "emphasis"}
            )
            
            logger.debug(f"Turn started for combatant {combatant_id}")
    
    def _on_turn_end(self, combatant_id) -> None:
        """
        Callback for when a combatant's turn ends.
        
        Args:
            combatant_id: ID of the combatant whose turn is ending
        """
        character = self.combat_state.get_character(combatant_id)
        if character:
            # Process end of turn effects
            self.effect_pipeline.process_turn_end(character)
            
            logger.debug(f"Turn ended for combatant {combatant_id}")
    
    def start_combat(self) -> Dict[str, Any]:
        """
        Start a combat encounter.
        
        Returns:
            Dictionary with combat state information
        """
        logger.info(f"Starting combat {self.combat_id}")
        
        # Reset all subsystems
        self.round_number = 1
        
        # Set up turn order
        self._initialize_turn_queue()
        
        # Get first character in turn order
        current_character_id = self.turn_queue.current_combatant
        current_character = self.combat_state.get_character(current_character_id)
        
        # Update fog of war with initial visibility
        self.fog_of_war.update_all_visibility()
        
        # Return initial state
        return self.get_combat_state()
    
    def _initialize_turn_queue(self) -> None:
        """Initialize the turn queue with all combatants."""
        # Roll initiative for all characters
        for character in self.combat_state.get_all_characters():
            if character.is_alive():
                # Roll initiative (d20 + dex modifier)
                dex_mod = character.get_attribute_modifier('DEX')
                initiative = random.randint(1, 20) + dex_mod
                character.initiative = initiative
                
                self.turn_queue.add_combatant(character.character_id, initiative)
        
        # Sort by initiative
        self.turn_queue.sort_by_initiative()
    
    def next_turn(self) -> Dict[str, Any]:
        """
        Advance to the next turn in combat.
        
        Returns:
            Updated combat state
        """
        # Process end of turn for current character
        current_id = self.turn_queue.current_combatant
        if current_id:
            self._on_turn_end(current_id)
        
        # Advance to next turn
        next_combatant = self.turn_queue.next_turn()
        
        # Check if we've completed a full round
        if self.turn_queue.is_new_round():
            self.round_number += 1
            logger.info(f"Starting round {self.round_number} in combat {self.combat_id}")
        
        # Process turn start for new character
        if next_combatant:
            self._on_turn_start(next_combatant)
        
        return self.get_combat_state()
    
    def take_action(self, character_id, action_id, target_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Have a character take an action in combat.
        
        Args:
            character_id: ID of the character taking the action
            action_id: ID of the action to take
            target_id: Optional ID of the target
            
        Returns:
            Action result and updated combat state
        """
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Verify it's the character's turn
        if self.turn_queue.current_combatant != character_id:
            raise ValueError(f"It's not {character_id}'s turn")
        
        # Get the target if specified
        target = None
        if target_id:
            target = self.combat_state.get_character(target_id)
            if not target:
                raise ValueError(f"Target {target_id} not found")
        
        # Execute the action
        result = action_system.execute_action(character, action_id, target, self)
        
        # Apply any effects from the action
        if result.effects:
            for effect in result.effects:
                self.effect_pipeline.apply_effect(effect, target or character)
        
        # Check if combat should end
        if self._check_combat_end():
            result.combat_ended = True
            result.winner = self._determine_winner()
        
        return {
            "action_result": result,
            "combat_state": self.get_combat_state()
        }
    
    def apply_effect(self, effect, target_id, source_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Apply an effect to a target character.
        
        Args:
            effect: The effect to apply
            target_id: ID of the target character
            source_id: Optional ID of the source character
            
        Returns:
            Effect result and updated combat state
        """
        target = self.combat_state.get_character(target_id)
        if not target:
            raise ValueError(f"Target {target_id} not found")
        
        # Apply the effect
        result = self.effect_pipeline.apply_effect(effect, target, source_id)
        
        # Play effect animation if available
        combat_animation_system.play_effect_animation(
            effect.name,
            source_id,
            [target_id],
            {"effect_type": type(effect).__name__}
        )
        
        return {
            "effect_result": result,
            "combat_state": self.get_combat_state()
        }
    
    def get_combat_state(self) -> Dict[str, Any]:
        """
        Get the current state of the combat.
        
        Returns:
            Dictionary containing current combat state
        """
        return {
            "combat_id": self.combat_id,
            "round_number": self.round_number,
            "current_turn": self.turn_queue.current_combatant,
            "turn_order": self.turn_queue.get_turn_order(),
            "characters": [
                {
                    "id": char.character_id,
                    "name": char.name,
                    "hp": char.hp,
                    "max_hp": char.max_hp,
                    "mp": char.mp,
                    "max_mp": char.max_mp,
                    "ac": char.ac,
                    "status_effects": char.status_effects,
                    "is_alive": char.is_alive(),
                    "team": char.team,
                    "initiative": char.initiative
                }
                for char in self.combat_state.get_all_characters()
            ],
            "area": {
                "size": self.combat_area.size,
                "entities": {
                    "entity_id": {"position": pos}
                    for entity_id, pos in self.combat_area.entity_positions.items()
                }
            },
            "visibility": self.fog_of_war.get_visibility_map(),
            "is_ended": self._check_combat_end()
        }
    
    def _check_combat_end(self) -> bool:
        """Check if combat should end."""
        alive_teams = set()
        for character in self.combat_state.get_all_characters():
            if character.is_alive():
                alive_teams.add(character.team)
        
        # Combat ends when only one team (or no teams) remain
        return len(alive_teams) <= 1
    
    def _determine_winner(self) -> Optional[str]:
        """Determine the winning team."""
        alive_teams = set()
        for character in self.combat_state.get_all_characters():
            if character.is_alive():
                alive_teams.add(character.team)
        
        if len(alive_teams) == 1:
            return list(alive_teams)[0]
        
        return None
    
    def end_combat(self) -> Dict[str, Any]:
        """
        End the combat and clean up resources.
        
        Returns:
            Final combat state and results
        """
        logger.info(f"Ending combat {self.combat_id}")
        
        winner = self._determine_winner()
        final_state = self.get_combat_state()
        
        # Clean up resources
        combat_pool_manager.return_combat_objects(self.combat_id)
        
        # Remove from debug interface if registered
        if combat_debug_interface:
            del combat_debug_interface.test_combats[self.combat_id]
        
        return {
            "combat_id": self.combat_id,
            "winner": winner,
            "rounds": self.round_number,
            "final_state": final_state
        }