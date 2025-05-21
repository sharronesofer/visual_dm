"""
Combat class module for the Visual DM combat system.

This module serves as the central coordinator for the combat system,
integrating the various subsystems (TurnQueue, EffectPipeline, etc.)
and providing a clean API for the rest of the application.
"""

import logging
import random
import time
import uuid
from typing import Dict, List, Any, Optional, Set, Tuple, Union, Callable

from .combat_state_class import CombatState
from .turn_queue import TurnQueue
from .effect_pipeline import EffectPipeline, CombatEffect
from .object_pool import combat_pool_manager
from .action_system import action_system, ActionResult, ActionType
from .combat_area import create_combat_area, CombatArea, Position
from .fog_of_war import create_fog_of_war, FogOfWar, VisibilityStatus
from .combat_animation_system import combat_animation_system
try:
    from .effect_visualizer import effect_visualizer
except ImportError:
    effect_visualizer = None
try:
    from .combat_debug_interface import combat_debug_interface
except ImportError:
    combat_debug_interface = None

# Set up logging
logger = logging.getLogger(__name__)

class Combat:
    def __init__(self, character_dict=None, combat_state=None, area_size=(20.0, 20.0)):
        """
        Initialize a new combat instance.
        
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
    
    def _on_turn_start(self, combatant_id: str) -> None:
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
    
    def _on_turn_end(self, combatant_id: str) -> None:
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
        Start a new combat encounter.
        
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
        
        # If we have a valid first combatant, process turn start effects
        # This is now handled by the turn queue callbacks, but we manually
        # trigger the first one since we're just initializing
        if current_character_id:
            self._on_turn_start(current_character_id)
        
        # Set initial visibility for all characters
        self.fog_of_war.update_all_visibility()
        
        return self.get_combat_state()
    
    def _initialize_turn_queue(self) -> None:
        """Set up the initial turn queue for all combatants."""
        # Clear existing queue
        self.turn_queue.clear()
        
        # Get all characters from combat state
        all_characters = self.combat_state.get_all_characters()
        
        # Add each character to turn queue with initiative rolls
        for character_id, character in all_characters.items():
            # Calculate initiative
            initiative = self._calculate_initiative(character)
            
            # Add to turn queue
            self.turn_queue.add_combatant(character_id, initiative)
        
        logger.info(f"Turn queue initialized with {len(all_characters)} combatants")
    
    def _calculate_initiative(self, character: Any) -> float:
        """
        Calculate initiative for a character.
        
        Args:
            character: Character to calculate initiative for
            
        Returns:
            Initiative value
        """
        # Default implementation - use dexterity modifier + random roll
        dexterity = getattr(character, 'dexterity', 10)
        dex_modifier = (dexterity - 10) // 2
        
        # Roll d20
        roll = random.randint(1, 20)
        
        initiative = roll + dex_modifier
        logger.debug(f"Character {character} rolled initiative: {initiative} "
                    f"(roll: {roll}, dex mod: {dex_modifier})")
        
        return initiative
    
    def next_turn(self) -> Dict[str, Any]:
        """
        Advance to the next turn in combat.
        
        Returns:
            Dictionary with updated combat state
        """
        # Use the enhanced TurnQueue to advance the queue
        # This will trigger our registered callbacks for turn end/start
        previous, current = self.turn_queue.advance_queue()
        
        # Check if we've completed a round (when we return to the first combatant)
        if previous and current and self.turn_queue.is_start_of_round:
            self.round_number += 1
            logger.info(f"Combat {self.combat_id} advancing to round {self.round_number}")
        
        return self.get_combat_state()
    
    def take_action(self, character_id: str, action_id: str, 
                   target_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Have a character take an action in combat.
        
        Args:
            character_id: ID of the character taking the action
            action_id: ID of the action to take
            target_id: Optional ID of the target
            
        Returns:
            Dictionary with action result and updated combat state
            
        Raises:
            ValueError: If the action or characters are invalid
        """
        # Validate character exists
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Get target if provided
        target = None
        if target_id:
            target = self.combat_state.get_character(target_id)
            if not target:
                raise ValueError(f"Target {target_id} not found")
        
        # Verify it's the character's turn (unless it's a reaction)
        action = action_system.get_action(action_id)
        if not action:
            raise ValueError(f"Action {action_id} not found")
            
        is_reaction = action.action_type == ActionType.REACTION
        current_character_id = self.turn_queue.current_combatant
        if character_id != current_character_id and not is_reaction:
            raise ValueError(f"It is not {character_id}'s turn")
        
        # Check if action can be used
        if not action_system.can_use_action(character, action, target):
            return {
                "result": {
                    "success": False,
                    "message": f"Cannot use action {action.name} at this time",
                    "damage": 0,
                    "damage_type": "",
                    "effects": []
                },
                "combat_state": self.get_combat_state()
            }
        
        # Process effects before action
        can_proceed = self.effect_pipeline.process_before_action(character, action, target)
        if not can_proceed:
            return {
                "result": {
                    "success": False,
                    "message": "Action prevented by effects",
                    "damage": 0,
                    "damage_type": "",
                    "effects": []
                },
                "combat_state": self.get_combat_state()
            }
        
        # Take the action
        result = action_system.use_action(character, action, target)
        
        # Process effects after action
        self.effect_pipeline.process_after_action(character, action, target)
        
        # Return result and updated state
        return {
            "result": {
                "success": result.success,
                "message": result.message,
                "damage": result.damage,
                "damage_type": result.damage_type,
                "effects": [self._effect_to_dict(e) for e in result.effects]
            },
            "combat_state": self.get_combat_state()
        }
    
    def _effect_to_dict(self, effect: 'CombatEffect') -> Dict[str, Any]:
        """
        Convert an effect to a dictionary for serialization.
        
        Args:
            effect: Effect to convert
            
        Returns:
            Dictionary representation of the effect
        """
        return {
            "id": effect.id,
            "name": effect.name,
            "description": effect.description,
            "effect_type": effect.effect_type.name,
            "duration": effect.duration,
            "intensity": effect.intensity,
            "source_id": effect.source_id,
            "target_id": effect.target_id,
            "current_stacks": effect.current_stacks,
            "max_stacks": effect.max_stacks,
            "stacking_behavior": effect.stacking_behavior.name,
            "tags": effect.tags
        }
    
    def _dict_to_effect(self, effect_dict: Dict[str, Any]) -> Optional['CombatEffect']:
        """
        Convert a dictionary to an effect.
        
        Args:
            effect_dict: Dictionary to convert
            
        Returns:
            Combat effect or None if creation fails
        """
        try:
            # Import at function level to avoid circular imports
            from .effect_pipeline import (CombatEffect, EffectType, EffectStackingBehavior,
                                        BuffEffect, DebuffEffect, DamageOverTimeEffect,
                                        HealOverTimeEffect, ConditionEffect,
                                        ResistanceEffect, VulnerabilityEffect, ImmunityEffect)
            
            # Get effect type
            effect_type_str = effect_dict.get("effect_type", "BUFF")
            effect_type = EffectType[effect_type_str]
            
            # Get stacking behavior
            stacking_behavior_str = effect_dict.get("stacking_behavior", "NONE")
            stacking_behavior = EffectStackingBehavior[stacking_behavior_str]
            
            # Create appropriate effect type
            if effect_type == EffectType.BUFF:
                effect = BuffEffect()
            elif effect_type == EffectType.DEBUFF:
                effect = DebuffEffect()
            elif effect_type == EffectType.DAMAGE_OVER_TIME:
                effect = DamageOverTimeEffect(
                    damage_per_turn=effect_dict.get("damage_per_turn", 0),
                    damage_type=effect_dict.get("damage_type", "fire")
                )
            elif effect_type == EffectType.HEAL_OVER_TIME:
                effect = HealOverTimeEffect(
                    heal_per_turn=effect_dict.get("heal_per_turn", 0)
                )
            elif effect_type == EffectType.CONDITION:
                effect = ConditionEffect(
                    condition=effect_dict.get("condition", "")
                )
            elif effect_type == EffectType.RESISTANCE:
                effect = ResistanceEffect(
                    damage_types=effect_dict.get("damage_types", []),
                    resistance_multiplier=effect_dict.get("resistance_multiplier", 0.5)
                )
            elif effect_type == EffectType.VULNERABILITY:
                effect = VulnerabilityEffect(
                    damage_types=effect_dict.get("damage_types", []),
                    vulnerability_multiplier=effect_dict.get("vulnerability_multiplier", 2.0)
                )
            elif effect_type == EffectType.IMMUNITY:
                effect = ImmunityEffect(
                    damage_types=effect_dict.get("damage_types", []),
                    immune_effects=effect_dict.get("immune_effects", [])
                )
            else:
                # Default to base CombatEffect
                effect = CombatEffect()
            
            # Set common properties
            effect.id = effect_dict.get("id", effect.id)
            effect.name = effect_dict.get("name", effect.name)
            effect.description = effect_dict.get("description", effect.description)
            effect.effect_type = effect_type
            effect.duration = effect_dict.get("duration", effect.duration)
            effect.intensity = effect_dict.get("intensity", effect.intensity)
            effect.source_id = effect_dict.get("source_id", effect.source_id)
            effect.target_id = effect_dict.get("target_id", effect.target_id)
            effect.current_stacks = effect_dict.get("current_stacks", effect.current_stacks)
            effect.max_stacks = effect_dict.get("max_stacks", effect.max_stacks)
            effect.stacking_behavior = stacking_behavior
            effect.tags = effect_dict.get("tags", effect.tags)
            
            return effect
        except Exception as e:
            logger.error(f"Error creating effect from dictionary: {e}")
            return None
    
    def _character_to_dict(self, character: Any) -> Dict[str, Any]:
        """
        Convert a character to a dictionary for serialization.
        
        Args:
            character: Character to convert
            
        Returns:
            Dictionary representation of the character
        """
        # Build a basic representation with common attributes
        character_dict = {
            "id": getattr(character, "id", str(uuid.uuid4())),
            "name": getattr(character, "name", "Character"),
            "hp": getattr(character, "hp", 0),
            "max_hp": getattr(character, "max_hp", 0),
            "attributes": getattr(character, "attributes", {}),
            "position": getattr(character, "position", 0),
        }
        
        # Add other attributes that might be useful
        if hasattr(character, "dexterity"):
            character_dict["dexterity"] = character.dexterity
        
        if hasattr(character, "is_dead"):
            character_dict["is_dead"] = character.is_dead
        
        # Add any readied actions
        if hasattr(character, "readied_action"):
            character_dict["readied_action"] = character.readied_action
        
        return character_dict
    
    def serialize(self) -> Dict[str, Any]:
        """
        Serialize the combat state to a dictionary.
        
        Returns:
            Dictionary representing the full combat state
        """
        # Get characters and serialize them
        characters = self.combat_state.get_all_characters()
        character_dicts = {char_id: self._character_to_dict(character) 
                         for char_id, character in characters.items()}
        
        # Get active effects for each character
        effect_dicts = {}
        for char_id, character in characters.items():
            effects = self.effect_pipeline.get_active_effects(character)
            effect_dicts[char_id] = [self._effect_to_dict(effect) for effect in effects]
        
        # Get turn queue state
        turn_queue_state = {
            "queue": self.turn_queue.queue,
            "current_combatant": self.turn_queue.current_combatant,
            "is_start_of_round": self.turn_queue.is_start_of_round
        }
        
        # Serialize the combat state
        combat_state_dict = {
            "combat_id": self.combat_id,
            "timestamp": self.timestamp,
            "round_number": self.round_number,
            "characters": character_dicts,
            "effects": effect_dicts,
            "turn_queue": turn_queue_state,
            "log": self.combat_state.log,
            "status": getattr(self.combat_state, "status", "active")
        }
        
        return combat_state_dict
    
    def deserialize(self, state_dict: Dict[str, Any]) -> bool:
        """
        Deserialize a dictionary to restore combat state.
        
        Args:
            state_dict: Dictionary with serialized combat state
            
        Returns:
            True if deserialization was successful
        """
        try:
            # Restore basic combat properties
            self.combat_id = state_dict.get("combat_id", self.combat_id)
            self.timestamp = state_dict.get("timestamp", self.timestamp)
            self.round_number = state_dict.get("round_number", self.round_number)
            
            # Restore characters
            character_dicts = state_dict.get("characters", {})
            characters = {}
            for char_id, char_dict in character_dicts.items():
                # Create a basic character object
                # For full restoration, specific character types would need custom logic
                character = type("CharacterProxy", (), char_dict)
                characters[char_id] = character
            
            # Create a new combat state
            from .combat_state_class import CombatState
            self.combat_state = CombatState(characters)
            
            # Restore combat state properties
            self.combat_state.combat_id = self.combat_id
            self.combat_state.log = state_dict.get("log", [])
            self.combat_state.status = state_dict.get("status", "active")
            
            # Set player/enemy characters
            turn_queue_state = state_dict.get("turn_queue", {})
            for char_id in turn_queue_state.get("queue", []):
                if char_id in characters:
                    # Determine if this is a player or enemy character
                    # This is a simplified heuristic and might need adjustment
                    if "player" in characters[char_id].name.lower():
                        self.combat_state.set_player_character(char_id, True)
                    else:
                        self.combat_state.set_player_character(char_id, False)
            
            # Restore turn queue
            self.turn_queue.clear()
            for char_id in turn_queue_state.get("queue", []):
                if char_id in characters:
                    # Use DEX as initiative base
                    initiative = getattr(characters[char_id], "dexterity", 10)
                    self.turn_queue.add_combatant(char_id, initiative)
            
            # Set current combatant
            current_combatant = turn_queue_state.get("current_combatant")
            if current_combatant:
                self.turn_queue.current_combatant = current_combatant
            
            # Restore effects
            effect_dicts = state_dict.get("effects", {})
            for char_id, effects in effect_dicts.items():
                if char_id in characters:
                    character = characters[char_id]
                    # Clear existing effects
                    self.effect_pipeline.clear_effects(character)
                    # Add effects from dictionary
                    for effect_dict in effects:
                        effect = self._dict_to_effect(effect_dict)
                        if effect:
                            source_id = effect.source_id
                            source = characters.get(source_id, None)
                            self.effect_pipeline.apply_effect(source, character, effect)
            
            logger.info(f"Successfully deserialized combat state for ID {self.combat_id}")
            return True
        except Exception as e:
            logger.error(f"Error deserializing combat state: {e}")
            return False
    
    def to_json(self) -> str:
        """
        Serialize the combat state to a JSON string.
        
        Returns:
            JSON string representation
        """
        import json
        return json.dumps(self.serialize())
    
    def from_json(self, json_string: str) -> bool:
        """
        Deserialize a JSON string to restore combat state.
        
        Args:
            json_string: JSON string with serialized combat state
            
        Returns:
            True if deserialization was successful
        """
        import json
        try:
            state_dict = json.loads(json_string)
            return self.deserialize(state_dict)
        except Exception as e:
            logger.error(f"Error deserializing JSON combat state: {e}")
            return False
    
    def save_to_file(self, filepath: str) -> bool:
        """
        Save the combat state to a file.
        
        Args:
            filepath: Path to save the file to
            
        Returns:
            True if saving was successful
        """
        try:
            json_data = self.to_json()
            with open(filepath, 'w') as f:
                f.write(json_data)
            logger.info(f"Saved combat state to {filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving combat state to file: {e}")
            return False
    
    def load_from_file(self, filepath: str) -> bool:
        """
        Load the combat state from a file.
        
        Args:
            filepath: Path to load the file from
            
        Returns:
            True if loading was successful
        """
        try:
            with open(filepath, 'r') as f:
                json_data = f.read()
            success = self.from_json(json_data)
            if success:
                logger.info(f"Loaded combat state from {filepath}")
            return success
        except Exception as e:
            logger.error(f"Error loading combat state from file: {e}")
            return False
    
    def pause_combat(self) -> Dict[str, Any]:
        """
        Pause the combat.
        
        Returns:
            Dictionary with combat state
        """
        # Update combat state status
        if hasattr(self.combat_state, "change_status"):
            self.combat_state.change_status("paused")
        
        logger.info(f"Combat {self.combat_id} paused")
        
        return self.get_combat_state()
    
    def resume_combat(self) -> Dict[str, Any]:
        """
        Resume the combat from paused state.
        
        Returns:
            Dictionary with combat state
        """
        # Update combat state status
        if hasattr(self.combat_state, "change_status"):
            self.combat_state.change_status("active")
        
        logger.info(f"Combat {self.combat_id} resumed")
        
        return self.get_combat_state()
    
    def handle_state_transition(self, new_state: str) -> Dict[str, Any]:
        """
        Handle a combat state transition.
        
        Args:
            new_state: New state to transition to
            
        Returns:
            Dictionary with updated combat state
        """
        # Update combat state status
        if hasattr(self.combat_state, "change_status"):
            self.combat_state.change_status(new_state)
        
        logger.info(f"Combat {self.combat_id} transitioned to {new_state}")
        
        if new_state == "victory" or new_state == "defeat":
            return self.end_combat()
        
        return self.get_combat_state()
    
    def get_state_history(self) -> List[Dict[str, Any]]:
        """
        Get the combat state history.
        
        Returns:
            List of dictionaries with historical combat states
        """
        if hasattr(self.combat_state, "state_history"):
            return self.combat_state.state_history
        return []
    
    def undo_last_action(self) -> Dict[str, Any]:
        """
        Undo the last action by rolling back to the previous state.
        
        Returns:
            Dictionary with rolled back combat state
        """
        if hasattr(self.combat_state, "rollback_to_previous_state"):
            success = self.combat_state.rollback_to_previous_state()
            if success:
                logger.info(f"Rolled back combat {self.combat_id} to previous state")
            else:
                logger.warning(f"Failed to roll back combat {self.combat_id}, no previous state available")
        
        return self.get_combat_state()
    
    def apply_effect(self, source_id: Optional[str], target_id: str, 
                   effect: CombatEffect) -> Dict[str, Any]:
        """
        Apply an effect to a target character.
        
        Args:
            source_id: ID of the source character (None for system effects)
            target_id: ID of the target character
            effect: Effect to apply
            
        Returns:
            Dictionary with effect result and updated combat state
        """
        # Get target character
        target = self.combat_state.get_character(target_id)
        if not target:
            return {
                "success": False,
                "message": f"Target {target_id} not found",
                "effect": None,
                "combat_state": self.get_combat_state()
            }
        
        # Apply the effect
        result = self.effect_pipeline.apply_effect(target, effect, source_id)
        
        # If effect was applied successfully, visualize it
        if result["success"] and effect_visualizer:
            effect_visualizer.visualize_effect(effect, target_id)
            
        # Play effect animation
        if result["success"]:
            combat_animation_system.play_reaction_animation(
                effect.effect_type.name.lower(),
                target_id,
                {
                    "effect_name": effect.name,
                    "intensity": effect.intensity
                }
            )
            
        return {
            "success": result["success"],
            "message": result["message"],
            "effect": self._effect_to_dict(effect) if result["success"] else None,
            "combat_state": self.get_combat_state()
        }
    
    def remove_effect(self, target_id: str, effect_id: str) -> Dict[str, Any]:
        """
        Remove an effect from a target.
        
        Args:
            target_id: ID of the effect target
            effect_id: ID of the effect to remove
            
        Returns:
            Dictionary with result and updated combat state
            
        Raises:
            ValueError: If the character or effect is invalid
        """
        # Validate character exists
        target = self.combat_state.get_character(target_id)
        if not target:
            raise ValueError(f"Target character {target_id} not found")
        
        # Remove the effect
        result = self.effect_pipeline.remove_effect_by_id(target, effect_id)
        
        # Return the result
        return {
            "success": result,
            "combat_state": self.get_combat_state()
        }
    
    def calculate_damage(self, source_id: str, target_id: str, 
                        base_damage: float, damage_type: str) -> Dict[str, Any]:
        """
        Calculate damage from source to target, considering effects.
        
        Args:
            source_id: ID of the damage source
            target_id: ID of the damage target
            base_damage: Base damage amount before modifications
            damage_type: Type of damage being dealt
            
        Returns:
            Dictionary with calculated damage and modifiers
            
        Raises:
            ValueError: If characters are invalid
        """
        # Validate characters exist
        source = self.combat_state.get_character(source_id)
        if not source:
            raise ValueError(f"Source character {source_id} not found")
            
        target = self.combat_state.get_character(target_id)
        if not target:
            raise ValueError(f"Target character {target_id} not found")
        
        # Let the effect pipeline modify the damage
        modified_damage = self.effect_pipeline.modify_damage(
            source, target, base_damage, damage_type
        )
        
        logger.debug(f"Damage calculation: {base_damage} -> {modified_damage} "
                   f"({damage_type}) from {source_id} to {target_id}")
        
        return {
            "original_damage": base_damage,
            "modified_damage": modified_damage,
            "damage_type": damage_type,
            "source_id": source_id,
            "target_id": target_id
        }
    
    def apply_damage(self, source_id: Optional[str], target_id: str, 
                   damage: float, damage_type: str) -> Dict[str, Any]:
        """
        Apply damage to a target, considering effects and triggering events.
        
        Args:
            source_id: Optional ID of the damage source
            target_id: ID of the damage target
            damage: Damage amount to apply
            damage_type: Type of damage being dealt
            
        Returns:
            Dictionary with result and updated combat state
            
        Raises:
            ValueError: If characters are invalid
        """
        # Validate target exists
        target = self.combat_state.get_character(target_id)
        if not target:
            raise ValueError(f"Target character {target_id} not found")
        
        # Validate source if provided
        source = None
        if source_id:
            source = self.combat_state.get_character(source_id)
            if not source:
                raise ValueError(f"Source character {source_id} not found")
        
        # Calculate modified damage through effect pipeline
        if source:
            modified_damage = self.effect_pipeline.modify_damage(
                source, target, damage, damage_type
            )
        else:
            # If no source, still let effects modify the damage
            modified_damage = self.effect_pipeline.modify_damage(
                None, target, damage, damage_type
            )
        
        # Apply damage to target
        current_hp = getattr(target, 'hp', 0)
        new_hp = max(0, current_hp - modified_damage)
        setattr(target, 'hp', new_hp)
        
        # Process damage events
        if source:
            self.effect_pipeline.process_deal_damage(source, target, modified_damage)
        self.effect_pipeline.process_damage(target, modified_damage)
        
        # Check for death
        if new_hp <= 0:
            self.handle_death(target_id, source_id)
        
        return {
            "original_damage": damage,
            "modified_damage": modified_damage,
            "damage_type": damage_type,
            "target_hp": new_hp,
            "is_dead": new_hp <= 0,
            "combat_state": self.get_combat_state()
        }
    
    def apply_healing(self, source_id: Optional[str], target_id: str, 
                    healing: float) -> Dict[str, Any]:
        """
        Apply healing to a target, considering effects and triggering events.
        
        Args:
            source_id: Optional ID of the healing source
            target_id: ID of the healing target
            healing: Healing amount to apply
            
        Returns:
            Dictionary with result and updated combat state
            
        Raises:
            ValueError: If characters are invalid
        """
        # Validate target exists
        target = self.combat_state.get_character(target_id)
        if not target:
            raise ValueError(f"Target character {target_id} not found")
        
        # Validate source if provided
        source = None
        if source_id:
            source = self.combat_state.get_character(source_id)
            if not source:
                raise ValueError(f"Source character {source_id} not found")
        
        # Apply healing to target
        current_hp = getattr(target, 'hp', 0)
        max_hp = getattr(target, 'max_hp', 0)
        new_hp = min(max_hp, current_hp + healing)
        setattr(target, 'hp', new_hp)
        
        # Process healing events
        if source:
            self.effect_pipeline.process_heal(source, target, healing)
        self.effect_pipeline.process_healed(target, source, healing)
        
        return {
            "healing": healing,
            "target_hp": new_hp,
            "target_max_hp": max_hp,
            "combat_state": self.get_combat_state()
        }
    
    def get_available_actions(self, character_id: str) -> Dict[str, Any]:
        """
        Get the available actions for a character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dictionary with available actions and their details
            
        Raises:
            ValueError: If the character is invalid
        """
        # Validate character exists
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Get available actions
        available_actions = action_system.get_available_actions(character)
        
        # Format for response
        formatted_actions = []
        for action in available_actions:
            formatted_actions.append({
                "id": action.id,
                "name": action.name,
                "description": action.description,
                "action_type": action.action_type.name,
                "cooldown": action.cooldown,
                "current_cooldown": action.current_cooldown,
                "requires_target": action.requires_target,
                "cost": action.cost
            })
        
        return {
            "character_id": character_id,
            "available_actions": formatted_actions
        }
    
    def get_combat_state(self) -> Dict[str, Any]:
        """
        Get the current state of the combat.
        
        Returns:
            Dictionary with full combat state
        """
        # Get current character in turn order
        current_character_id = self.turn_queue.current_combatant
        
        # Get all characters
        all_characters = self.combat_state.get_all_characters()
        
        # Convert characters to dictionaries with additional info
        character_dicts = {}
        for character_id, character in all_characters.items():
            char_dict = self._character_to_dict(character)
            
            # Add position information
            position = self.combat_area.get_entity_position(character_id)
            if position:
                char_dict["position"] = position
                
            # Add visibility information for current character
            if current_character_id:
                visibility = self.fog_of_war.calculate_visibility(current_character_id, character_id)
                char_dict["visibility"] = visibility
                
            # Add to dictionary
            character_dicts[character_id] = char_dict
        
        # Get turn order
        turn_order = self.turn_queue.get_turn_order()
        
        # Build combat state
        combat_state = {
            "combat_id": self.combat_id,
            "round": self.round_number,
            "current_character": current_character_id,
            "turn_order": turn_order,
            "characters": character_dicts,
            "terrain": [feature.to_dict() for feature in self.combat_area.terrain_features.values()],
            "area": {
                "id": self.combat_area.area_id,
                "name": self.combat_area.name,
                "size": self.combat_area.size,
                "grid_size": self.combat_area.grid_size
            },
            "active_animations": combat_animation_system.get_active_animations(),
            "debug_mode": self.debug_mode
        }
        
        return combat_state
    
    def add_character(self, character: Any) -> str:
        """
        Add a character to the combat.
        
        Args:
            character: Character to add
            
        Returns:
            ID of the added character
        """
        # Generate ID if not present
        character_id = getattr(character, "id", str(uuid.uuid4()))
        
        # Add to combat state
        self.combat_state.add_character(character_id, character)
        
        # Add to turn queue with initiative
        initiative = self._calculate_initiative(character)
        self.turn_queue.add_combatant(character_id, initiative)
        
        logger.info(f"Added character {character_id} to combat {self.combat_id}")
        
        return character_id
    
    def remove_character(self, character_id: str) -> bool:
        """
        Remove a character from combat.
        
        Args:
            character_id: ID of the character to remove
            
        Returns:
            True if the character was removed, False otherwise
        """
        # Remove from combat state
        if not self.combat_state.remove_character(character_id):
            return False
        
        # Remove from turn queue
        self.turn_queue.remove_combatant(character_id)
        
        logger.info(f"Removed character {character_id} from combat {self.combat_id}")
        
        return True
    
    def end_combat(self) -> Dict[str, Any]:
        """
        End the combat encounter.
        
        Returns:
            Final combat state
        """
        logger.info(f"Ending combat {self.combat_id}")
        
        # Get final state
        final_state = self.get_combat_state()
        
        # Clean up resources
        self.turn_queue.clear()
        self.effect_pipeline.clear_all_effects()
        
        return final_state
    
    def handle_death(self, character_id: str, killer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Handle a character's death in combat.
        
        Args:
            character_id: ID of the character that died
            killer_id: Optional ID of the character that caused the death
            
        Returns:
            Updated combat state
        """
        # Validate characters exist
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        killer = None
        if killer_id:
            killer = self.combat_state.get_character(killer_id)
        
        # Handle death logic
        logger.info(f"Character {character_id} has died in combat {self.combat_id}")
        
        # Set character as dead
        setattr(character, "is_dead", True)
        setattr(character, "hp", 0)
        
        # Remove from turn queue
        self.turn_queue.remove_combatant(character_id)
        
        # Check if combat should end (e.g., all players dead or all enemies dead)
        # This would be game-specific logic, so we'll leave it simple for now
        
        return self.get_combat_state()
    
    def delay_turn(self, character_id: str) -> Dict[str, Any]:
        """
        Delay a character's turn until the end of the round.
        
        Args:
            character_id: ID of the character delaying their turn
            
        Returns:
            Updated combat state
            
        Raises:
            ValueError: If it's not the character's turn
        """
        # Validate character exists
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Check if it's the character's turn
        if self.turn_queue.current_combatant != character_id:
            raise ValueError(f"It is not {character_id}'s turn")
        
        # Delay the turn
        if not self.turn_queue.delay_turn(character_id):
            raise ValueError(f"Failed to delay turn for {character_id}")
        
        return self.get_combat_state()
    
    def move_character(self, character_id: str, destination: Union[Position, List[float], Tuple[float, float, float]], avoid_others: bool = True) -> Dict[str, Any]:
        """
        Move a character to a new position on the combat area.
        
        Args:
            character_id: ID of the character to move
            destination: Target position (x, y, z) or (x, z)
            avoid_others: Whether to avoid other characters
            
        Returns:
            Dictionary with movement result and updated combat state
        """
        character = self.combat_state.get_character(character_id)
        if not character:
            return {
                "success": False,
                "message": f"Character {character_id} not found",
                "path": [],
                "combat_state": self.get_combat_state()
            }
        
        # Convert destination to proper position format
        if isinstance(destination, (list, tuple)):
            if len(destination) == 2:
                # If only x, z provided, assume y=0
                dest_position = (destination[0], 0.0, destination[1])
            elif len(destination) == 3:
                dest_position = tuple(destination)
            else:
                return {
                    "success": False, 
                    "message": "Invalid destination format",
                    "path": [], 
                    "combat_state": self.get_combat_state()
                }
        else:
            dest_position = destination
        
        # Check if character can move (has movement left, not stunned, etc.)
        can_move = True  # Simplified for now
        if not can_move:
            return {
                "success": False,
                "message": "Character cannot move",
                "path": [],
                "combat_state": self.get_combat_state()
            }
        
        # Calculate path
        path = self.combat_area.calculate_path(character_id, dest_position, avoid_entities=avoid_others)
        
        if not path:
            # Try to find a nearby valid position
            nearest_pos = self.combat_area.get_nearest_position(dest_position)
            if nearest_pos != dest_position:
                # Try again with nearest valid position
                path = self.combat_area.calculate_path(character_id, nearest_pos, avoid_entities=avoid_others)
        
        if not path:
            return {
                "success": False,
                "message": "No valid path to destination",
                "path": [],
                "combat_state": self.get_combat_state()
            }
        
        # Calculate movement cost
        if len(path) >= 2:
            start, end = path[0], path[-1]
            movement_cost = self.combat_area.get_movement_cost(start, end)
        else:
            movement_cost = 0
        
        # Move character to destination
        success = self.combat_area.move_entity(character_id, path[-1])
        
        if not success:
            return {
                "success": False,
                "message": "Failed to move character",
                "path": path,
                "combat_state": self.get_combat_state()
            }
        
        # Update fog of war
        self.fog_of_war.update_entity(character_id, position=path[-1])
        self.fog_of_war.update_all_visibility()
        
        # Play movement animation
        combat_animation_system.play_action_animation(
            "move",
            character_id,
            [],
            {
                "move_type": "walk",
                "path": path,
                "duration": 0.5
            }
        )
        
        return {
            "success": True,
            "message": f"Character moved to {path[-1]}",
            "path": path,
            "movement_cost": movement_cost,
            "combat_state": self.get_combat_state()
        }
    
    def recompute_initiative(self, character_id: str, new_initiative: Optional[int] = None) -> Dict[str, Any]:
        """
        Update a character's initiative and reorder the turn queue.
        
        Args:
            character_id: ID of the character to update
            new_initiative: Optional new initiative value (recalculated if not provided)
            
        Returns:
            Updated combat state
            
        Raises:
            ValueError: If the character is invalid
        """
        # Validate character exists
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Calculate new initiative if not provided
        if new_initiative is None:
            new_initiative = self._calculate_initiative(character)
        
        # Update the queue
        self.turn_queue.recompute_initiative(character_id, new_initiative)
        
        logger.info(f"Recomputed initiative for character {character_id}: {new_initiative}")
        
        return self.get_combat_state()
    
    def get_effect_types(self) -> Dict[str, Any]:
        """
        Get all available effect types.
        
        Returns:
            Dictionary with effect types and descriptions
        """
        return {
            effect_type.name: effect_type.value 
            for effect_type in EffectType
        }
    
    def get_character_effects(self, character_id: str) -> Dict[str, Any]:
        """
        Get all active effects on a character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dictionary with active effects and their details
            
        Raises:
            ValueError: If the character is invalid
        """
        # Validate character exists
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Get active effects
        active_effects = self.effect_pipeline.get_applied_effects(character)
        
        # Format for response
        formatted_effects = [self._effect_to_dict(effect) for effect in active_effects]
        
        return {
            "character_id": character_id,
            "active_effects": formatted_effects
        }
    
    def clear_character_effects(self, character_id: str) -> Dict[str, Any]:
        """
        Clear all effects from a character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dictionary with result and updated combat state
            
        Raises:
            ValueError: If the character is invalid
        """
        # Validate character exists
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Clear effects
        count = self.effect_pipeline.clear_effects(character)
        
        return {
            "effects_removed": count,
            "combat_state": self.get_combat_state()
        }
    
    def use_movement(self, character_id: str, distance: float) -> Dict[str, Any]:
        """
        Have a character use movement in combat.
        
        Args:
            character_id: ID of the character moving
            distance: Distance to move (positive or negative)
            
        Returns:
            Dictionary with movement result and updated combat state
            
        Raises:
            ValueError: If the character is invalid or cannot move
        """
        # Validate character exists
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Verify it's the character's turn
        current_character_id = self.turn_queue.current_combatant
        if character_id != current_character_id:
            raise ValueError(f"It is not {character_id}'s turn")
        
        # Use movement through action system
        actual_distance = action_system.use_movement(character, distance)
        
        # Update position
        current_position = getattr(character, "position", 0)
        new_position = current_position + actual_distance
        setattr(character, "position", new_position)
        
        # Get remaining movement
        remaining = action_system.get_remaining_actions(character)["movement"]
        
        logger.debug(f"Character {character_id} moved {actual_distance} units "
                   f"from position {current_position} to {new_position}, "
                   f"with {remaining} movement remaining")
        
        return {
            "distance_moved": actual_distance,
            "new_position": new_position,
            "remaining_movement": remaining,
            "combat_state": self.get_combat_state()
        }
    
    def ready_action(self, character_id: str, action_id: str, 
                    condition: str, target_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Ready an action to be used later based on a trigger condition.
        
        Args:
            character_id: ID of the character readying the action
            action_id: ID of the action to ready
            condition: Trigger condition for the readied action
            target_id: Optional ID of the target
            
        Returns:
            Dictionary with result and updated combat state
            
        Raises:
            ValueError: If the character, action, or target are invalid
        """
        # Validate character exists
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Verify it's the character's turn
        current_character_id = self.turn_queue.current_combatant
        if character_id != current_character_id:
            raise ValueError(f"It is not {character_id}'s turn")
        
        # Get the action
        action = action_system.get_action(action_id)
        if not action:
            raise ValueError(f"Action {action_id} not found")
        
        # Validate target if provided
        target = None
        if target_id:
            target = self.combat_state.get_character(target_id)
            if not target:
                raise ValueError(f"Target {target_id} not found")
        
        # Check if standard action is available (readying uses the standard action)
        if action_system.get_remaining_actions(character)["standard"] is False:
            return {
                "success": False,
                "message": "No standard action available to ready",
                "combat_state": self.get_combat_state()
            }
        
        # Ready the action (mark standard action as used)
        state = action_system._get_combatant_state(character)
        state.used_standard_action = True
        
        # Store the readied action in character data
        setattr(character, "readied_action", {
            "action_id": action_id,
            "condition": condition,
            "target_id": target_id
        })
        
        logger.info(f"Character {character_id} readied action {action.name} "
                  f"with condition: {condition}")
        
        return {
            "success": True,
            "message": f"Readied {action.name} to trigger on: {condition}",
            "combat_state": self.get_combat_state()
        }
    
    def check_readied_actions(self, trigger: str, 
                             subject_id: str, object_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Check and execute readied actions based on a trigger.
        
        Args:
            trigger: The trigger description
            subject_id: ID of the character triggering the readied action
            object_id: Optional ID of the object of the trigger
            
        Returns:
            List of results from executed readied actions
        """
        # Get all characters to check for readied actions
        all_characters = self.combat_state.get_all_characters()
        
        results = []
        
        # Check each character for applicable readied actions
        for character_id, character in all_characters.items():
            readied_action = getattr(character, "readied_action", None)
            if not readied_action:
                continue
                
            # Simple condition matching (can be enhanced with more sophisticated logic)
            if trigger.lower() in readied_action["condition"].lower():
                action_id = readied_action["action_id"]
                target_id = readied_action["target_id"]
                
                logger.info(f"Trigger '{trigger}' matched readied action for {character_id}: "
                          f"{action_id} on {target_id}")
                
                # Execute the readied action
                try:
                    result = self.take_action(character_id, action_id, target_id)
                    results.append(result)
                    
                    # Clear the readied action
                    setattr(character, "readied_action", None)
                except ValueError as e:
                    logger.error(f"Failed to execute readied action: {e}")
                    results.append({
                        "success": False,
                        "message": str(e),
                        "character_id": character_id
                    })
        
        return results
    
    def register_reaction_trigger(self, trigger_type: str, callback: Callable) -> None:
        """
        Register a callback for a reaction trigger.
        
        Args:
            trigger_type: Type of trigger to register for
            callback: Callback function to execute when trigger occurs
        """
        action_system.register_reaction_trigger(trigger_type, callback)
    
    def trigger_reaction(self, trigger_type: str, source_id: str, 
                        target_id: Optional[str] = None, data: Any = None) -> List[Dict[str, Any]]:
        """
        Trigger reactions for an event.
        
        Args:
            trigger_type: Type of trigger
            source_id: ID of the trigger source
            target_id: Optional ID of the trigger target
            data: Optional additional data
            
        Returns:
            List of results from triggered reactions
        """
        # Validate source exists
        source = self.combat_state.get_character(source_id)
        if not source:
            raise ValueError(f"Source character {source_id} not found")
        
        # Validate target if provided
        target = None
        if target_id:
            target = self.combat_state.get_character(target_id)
            if not target:
                raise ValueError(f"Target character {target_id} not found")
        
        # Trigger reactions through action system
        results = action_system.trigger_reaction(trigger_type, source, target, data)
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "success": result.success,
                "message": result.message,
                "damage": result.damage,
                "damage_type": result.damage_type,
                "effects": [self._effect_to_dict(e) for e in result.effects]
            })
        
        return formatted_results
    
    def get_available_reactions(self, character_id: str, trigger_type: str, 
                              source_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available reactions for a character based on a trigger.
        
        Args:
            character_id: ID of the character to check
            trigger_type: Type of trigger
            source_id: Optional ID of the trigger source
            
        Returns:
            Dictionary with available reactions
            
        Raises:
            ValueError: If the character is invalid
        """
        # Validate character exists
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        # Validate source if provided
        source = None
        if source_id:
            source = self.combat_state.get_character(source_id)
            if not source:
                raise ValueError(f"Source character {source_id} not found")
        
        # Get available reactions
        available_reactions = action_system.get_available_reactions(character, trigger_type, source)
        
        # Format for response
        formatted_reactions = []
        for reaction in available_reactions:
            formatted_reactions.append({
                "id": reaction.id,
                "name": reaction.name,
                "description": reaction.description,
                "action_type": reaction.action_type.name,
                "target_type": reaction.target_type.name
            })
        
        return {
            "character_id": character_id,
            "trigger_type": trigger_type,
            "available_reactions": formatted_reactions
        }
    
    def process_turn_phase(self, phase: str) -> Dict[str, Any]:
        """
        Process a specific phase of the current turn.
        
        Args:
            phase: The phase to process ("start", "action", "end")
            
        Returns:
            Dictionary with updated combat state
            
        Raises:
            ValueError: If there is no current character or invalid phase
        """
        current_character_id = self.turn_queue.current_combatant
        if not current_character_id:
            raise ValueError("No current character in combat")
            
        character = self.combat_state.get_character(current_character_id)
        if not character:
            raise ValueError(f"Current character {current_character_id} not found")
        
        if phase == "start":
            # Already handled by turn queue callbacks
            pass
            
        elif phase == "action":
            # Process mid-turn effects
            active_effects = self.effect_pipeline.get_applied_effects(character)
            for effect in active_effects:
                if effect.effect_type == EffectType.DAMAGE_OVER_TIME:
                    # Process damage over time effects
                    damage = effect.damage_per_turn * effect.intensity
                    self.apply_damage(effect.source_id, current_character_id, damage, effect.damage_type)
                    
                elif effect.effect_type == EffectType.HEAL_OVER_TIME:
                    # Process healing over time effects
                    healing = effect.heal_per_turn * effect.intensity
                    self.apply_healing(effect.source_id, current_character_id, healing)
        
        elif phase == "end":
            # Already handled by turn queue callbacks
            pass
            
        else:
            raise ValueError(f"Invalid turn phase: {phase}")
            
        return self.get_combat_state()
    
    def coordinate_subsystems(self) -> None:
        """
        Ensure proper coordination between all combat subsystems.
        
        This method should be called during initialization and after
        significant state changes to maintain system coherence.
        """
        logger.debug("Coordinating combat subsystems")
        
        # Get all characters
        all_characters = self.combat_state.get_all_characters()
        
        # Synchronize turn queue with combat state
        turn_queue_ids = set(self.turn_queue.queue)
        combat_state_ids = set(all_characters.keys())
        
        # Add missing characters to turn queue
        for character_id in combat_state_ids - turn_queue_ids:
            character = self.combat_state.get_character(character_id)
            if character:
                initiative = self._calculate_initiative(character)
                self.turn_queue.add_combatant(character_id, initiative)
                logger.debug(f"Added missing character {character_id} to turn queue")
        
        # Remove extra characters from turn queue
        for character_id in turn_queue_ids - combat_state_ids:
            self.turn_queue.remove_combatant(character_id)
            logger.debug(f"Removed extra character {character_id} from turn queue")
        
        # Ensure all characters have action states
        for character_id, character in all_characters.items():
            if not hasattr(character, "_action_state"):
                action_system.reset_combatant_actions(character)
                logger.debug(f"Initialized action state for character {character_id}")
    
    def handle_status_effects(self, character_id: str) -> Dict[str, Any]:
        """
        Process and update status effects for a character.
        
        Args:
            character_id: ID of the character to process
            
        Returns:
            Dictionary with effect results and updated combat state
            
        Raises:
            ValueError: If the character is invalid
        """
        # Validate character exists
        character = self.combat_state.get_character(character_id)
        if not character:
            raise ValueError(f"Character {character_id} not found")
        
        results = []
        
        # Get all active effects
        active_effects = self.effect_pipeline.get_applied_effects(character)
        
        # Process each effect
        for effect in active_effects:
            # Check if effect has expired
            if effect.is_expired():
                # Remove expired effect
                self.effect_pipeline.remove_effect(character, effect)
                results.append({
                    "effect_id": effect.id,
                    "name": effect.name,
                    "result": "expired"
                })
                continue
                
            # Handle condition effects
            if effect.effect_type == EffectType.CONDITION:
                condition = getattr(effect, "condition", "")
                
                # Apply condition-specific logic
                if condition == "stunned":
                    # Stunned characters lose their turn
                    if character_id == self.turn_queue.current_combatant:
                        self.next_turn()
                        results.append({
                            "effect_id": effect.id,
                            "name": effect.name,
                            "result": "lost_turn"
                        })
                
                elif condition == "prone":
                    # Prone characters have reduced movement
                    state = action_system._get_combatant_state(character)
                    if state.remaining_movement > 0:
                        state.remaining_movement /= 2
                        results.append({
                            "effect_id": effect.id,
                            "name": effect.name,
                            "result": "reduced_movement"
                        })
        
        return {
            "character_id": character_id,
            "effect_results": results,
            "combat_state": self.get_combat_state()
        }
    
    def register_system_hooks(self) -> None:
        """
        Register callback hooks between subsystems for proper integration.
        """
        # Register effect pipeline hooks with action system
        self.effect_pipeline.register_effect_applied_callback(
            lambda target, effect: logger.debug(f"Effect {effect.name} applied to {target}")
        )
        
        self.effect_pipeline.register_effect_removed_callback(
            lambda target, effect: logger.debug(f"Effect {effect.name} removed from {target}")
        )
        
        self.effect_pipeline.register_effect_expired_callback(
            lambda target, effect: logger.debug(f"Effect {effect.name} expired on {target}")
        )
        
        # Register action system reaction triggers
        self.register_reaction_trigger("damage_taken", 
            lambda source, target, data: logger.debug(f"{target} taking damage from {source}")
        )
        
        self.register_reaction_trigger("movement", 
            lambda source, target, data: logger.debug(f"{source} moving near {target}")
        )
        
        self.register_reaction_trigger("spell_cast", 
            lambda source, target, data: logger.debug(f"{source} casting spell at {target}")
        )
    
    def execute_simultaneous_actions(self, character_ids: List[str], 
                                   action_ids: List[str], 
                                   target_ids: List[Optional[str]] = None) -> Dict[str, Any]:
        """
        Execute multiple actions simultaneously with proper ordering.
        
        Args:
            character_ids: List of character IDs taking actions
            action_ids: List of action IDs to take
            target_ids: Optional list of target IDs
            
        Returns:
            Dictionary with results and updated combat state
            
        Raises:
            ValueError: If lists have different lengths or characters/actions are invalid
        """
        if len(character_ids) != len(action_ids):
            raise ValueError("Character IDs and action IDs must have the same length")
            
        if target_ids and len(target_ids) != len(character_ids):
            raise ValueError("Target IDs must have the same length as character IDs")
            
        if not target_ids:
            target_ids = [None] * len(character_ids)
            
        results = []
        
        # First pass: Validate all actions can be taken
        for i, (character_id, action_id) in enumerate(zip(character_ids, action_ids)):
            character = self.combat_state.get_character(character_id)
            if not character:
                raise ValueError(f"Character {character_id} not found")
                
            action = action_system.get_action(action_id)
            if not action:
                raise ValueError(f"Action {action_id} not found")
                
            target = None
            if target_ids[i]:
                target = self.combat_state.get_character(target_ids[i])
                if not target:
                    raise ValueError(f"Target {target_ids[i]} not found")
            
            # Check if action can be used
            if not action_system.can_use_action(character, action, target):
                raise ValueError(f"Character {character_id} cannot use action {action_id}")
        
        # Second pass: Execute all actions in priority order
        # Sort by action type priority: Reactions > Standard > Bonus > Movement
        action_priority = {
            ActionType.REACTION: 0,
            ActionType.STANDARD: 1,
            ActionType.BONUS: 2,
            ActionType.MOVEMENT: 3,
            ActionType.FREE: 4
        }
        
        # Create tuples of (priority, index, character_id, action_id, target_id)
        prioritized_actions = []
        for i, (character_id, action_id) in enumerate(zip(character_ids, action_ids)):
            action = action_system.get_action(action_id)
            priority = action_priority.get(action.action_type, 99)
            prioritized_actions.append((priority, i, character_id, action_id, target_ids[i]))
            
        # Sort by priority
        prioritized_actions.sort()
        
        # Execute in priority order
        for _, _, character_id, action_id, target_id in prioritized_actions:
            try:
                result = self.take_action(character_id, action_id, target_id)
                results.append(result)
            except ValueError as e:
                logger.error(f"Failed to execute action: {e}")
                results.append({
                    "result": {
                        "success": False,
                        "message": str(e),
                        "damage": 0,
                        "damage_type": "",
                        "effects": []
                    }
                })
        
        return {
            "results": results,
            "combat_state": self.get_combat_state()
        }
    
    def toggle_debug_mode(self) -> Dict[str, Any]:
        """
        Toggle debug mode for the combat.
        
        Returns:
            Updated combat state
        """
        self.debug_mode = not self.debug_mode
        
        if combat_debug_interface and self.debug_mode:
            # Set this combat as active in the debug interface
            combat_debug_interface.set_active_combat(self)
        
        logger.info(f"Debug mode {'enabled' if self.debug_mode else 'disabled'} for combat {self.combat_id}")
        
        return self.get_combat_state()
    
    def get_visible_entities(self, observer_id: str) -> Dict[str, str]:
        """
        Get all entities visible to an observer.
        
        Args:
            observer_id: ID of the observing character
            
        Returns:
            Dictionary mapping entity IDs to visibility levels
        """
        return self.fog_of_war.get_visible_entities(observer_id)
    
    def execute_perception_check(self, observer_id: str, target_id: str, bonus: float = 0.0) -> Dict[str, Any]:
        """
        Execute a perception check to detect a target.
        
        Args:
            observer_id: ID of the observing character
            target_id: ID of the target character
            bonus: Bonus to the check
            
        Returns:
            Dictionary with result and updated combat state
        """
        # Execute check
        success, margin = self.fog_of_war.simulate_perception_check(observer_id, target_id, bonus)
        
        # Play animation
        animation_type = "perception_success" if success else "perception_fail"
        combat_animation_system.play_action_animation(
            "perception",
            observer_id,
            [target_id],
            {"animation_type": animation_type}
        )
        
        return {
            "success": success,
            "margin": margin,
            "observer_id": observer_id,
            "target_id": target_id,
            "visibility": self.fog_of_war.calculate_visibility(observer_id, target_id),
            "combat_state": self.get_combat_state()
        }
