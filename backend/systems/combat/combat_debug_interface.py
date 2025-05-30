"""
CombatDebugInterface module for the Visual DM combat system.

This module implements a runtime debug interface for testing and iterating on the
combat system. It provides controls for manipulating combat state, adding/removing
entities, and testing effects.

Following the design principles from the Development Bible, this implementation:
1. Provides runtime debug controls for combat testing
2. Has no scene/prefab/tag dependencies
3. Works entirely at runtime
4. Supports rapid iteration and testing
"""

import logging
import random
from typing import Dict, List, Any, Optional, Callable, Set, Union
import uuid

from .combat_class import Combat
from .effect_pipeline import (
    CombatEffect, BuffEffect, DebuffEffect, 
    DamageOverTimeEffect, HealOverTimeEffect,
    ConditionEffect, ResistanceEffect, VulnerabilityEffect, 
    ImmunityEffect, EffectType, EffectStackingBehavior
)
from .action_system import ActionType, ActionTarget

# Set up logging
logger = logging.getLogger(__name__)

class CombatDebugInterface:
    """
    Provides runtime debug controls for testing combat functionality.
    
    This is a development tool for testing combat mechanics and should not
    be included in production builds.
    """
    
    def __init__(self):
        """Initialize the debug interface with no active combat."""
        self.active_combat: Optional[Combat] = None
        self.command_history: List[Dict[str, Any]] = []
        self.test_characters: Dict[str, Dict[str, Any]] = {}
        self.test_combats: Dict[str, Combat] = {}
        self.debug_enabled = True
        self.debug_logs: List[str] = []
        self.auto_log = True
        logger.info("CombatDebugInterface initialized")
    
    def log(self, message: str) -> None:
        """
        Add a message to the debug log.
        
        Args:
            message: Message to log
        """
        if self.auto_log:
            logger.debug(f"[DEBUG] {message}")
        self.debug_logs.append(message)
        
        # Keep log size reasonable
        if len(self.debug_logs) > 1000:
            self.debug_logs = self.debug_logs[-1000:]
    
    def set_active_combat(self, combat: Optional[Combat]) -> None:
        """
        Set the active combat for debugging.
        
        Args:
            combat: Combat instance to debug, or None to clear
        """
        self.active_combat = combat
        self.log(f"Set active combat to {combat.combat_id if combat else 'None'}")
    
    def create_test_combat(self) -> str:
        """
        Create a new test combat with random characters.
        
        Returns:
            ID of the created combat
        """
        # Create some test characters if none exist
        if not self.test_characters:
            self._create_test_characters()
        
        # Create a combat with the test characters
        combat = Combat(character_dict=self.test_characters)
        combat_id = combat.combat_id
        
        # Store and start the combat
        self.test_combats[combat_id] = combat
        combat.start_combat()
        
        # Set as active
        self.set_active_combat(combat)
        
        self.log(f"Created test combat {combat_id} with {len(self.test_characters)} characters")
        return combat_id
    
    def _create_test_characters(self, count: int = 4) -> None:
        """
        Create test characters for debugging.
        
        Args:
            count: Number of characters to create
        """
        character_types = ["warrior", "mage", "cleric", "rogue"]
        
        for i in range(count):
            char_type = character_types[i % len(character_types)]
            char_id = f"test_{char_type}_{uuid.uuid4().hex[:6]}"
            
            # Create character with basic stats based on type
            character = {
                "character_id": char_id,
                "name": f"Test {char_type.capitalize()}",
                "type": char_type,
                "health": {
                    "current": 100,
                    "max": 100
                },
                "attributes": {
                    "STR": 10 + (5 if char_type == "warrior" else 0),
                    "DEX": 10 + (5 if char_type == "rogue" else 0),
                    "CON": 10,
                    "INT": 10 + (5 if char_type == "mage" else 0),
                    "WIS": 10 + (5 if char_type == "cleric" else 0),
                    "CHA": 10
                },
                "position": (i * 2, 0, 0),  # Space them apart
                "effects": [],
                "is_enemy": i >= count // 2  # Half enemies, half allies
            }
            
            self.test_characters[char_id] = character
        
        self.log(f"Created {count} test characters")
    
    def add_test_character(self, character_type: str) -> str:
        """
        Add a single test character of a specific type.
        
        Args:
            character_type: Type of character to add (warrior, mage, etc.)
            
        Returns:
            ID of the created character
        """
        char_id = f"test_{character_type}_{uuid.uuid4().hex[:6]}"
        
        # Create character with basic stats based on type
        character = {
            "character_id": char_id,
            "name": f"Test {character_type.capitalize()}",
            "type": character_type,
            "health": {
                "current": 100,
                "max": 100
            },
            "attributes": {
                "STR": 10 + (5 if character_type == "warrior" else 0),
                "DEX": 10 + (5 if character_type == "rogue" else 0),
                "CON": 10,
                "INT": 10 + (5 if character_type == "mage" else 0),
                "WIS": 10 + (5 if character_type == "cleric" else 0),
                "CHA": 10
            },
            "position": (len(self.test_characters) * 2, 0, 0),
            "effects": [],
            "is_enemy": False  # Default to ally
        }
        
        self.test_characters[char_id] = character
        
        # Add to active combat if one exists
        if self.active_combat:
            self.active_combat.add_character(character)
            
        self.log(f"Added test character {char_id} of type {character_type}")
        return char_id
    
    def apply_test_effect(self, effect_type: str, source_id: Optional[str] = None, target_id: Optional[str] = None) -> Optional[str]:
        """
        Apply a test effect to a character.
        
        Args:
            effect_type: Type of effect to apply (buff, debuff, etc.)
            source_id: Optional character ID for the source
            target_id: Optional character ID for the target
            
        Returns:
            ID of the applied effect, or None if failed
        """
        if not self.active_combat:
            self.log("No active combat")
            return None
            
        # Get source and target
        characters = self.active_combat.combat_state.get_all_characters()
        
        if not source_id:
            # Use a random character as source
            source_id = random.choice(list(characters.keys()))
            
        if not target_id:
            # Use a random character as target
            target_id = random.choice(list(characters.keys()))
            
        source = characters.get(source_id)
        target = characters.get(target_id)
        
        if not source or not target:
            self.log(f"Source or target not found: {source_id}, {target_id}")
            return None
            
        # Create the appropriate effect based on type
        effect = None
        effect_duration = random.randint(2, 5)  # Random duration
        
        if effect_type.lower() == "buff":
            effect = BuffEffect(
                name="Test Buff",
                description="A test buff effect",
                duration=effect_duration,
                intensity=1.0
            )
        elif effect_type.lower() == "debuff":
            effect = DebuffEffect(
                name="Test Debuff",
                description="A test debuff effect",
                duration=effect_duration,
                intensity=1.0
            )
        elif effect_type.lower() == "damage_over_time" or effect_type.lower() == "dot":
            effect = DamageOverTimeEffect(
                name="Test DoT",
                description="A test damage over time effect",
                duration=effect_duration,
                intensity=1.0,
                damage_per_turn=10.0,
                damage_type="fire"
            )
        elif effect_type.lower() == "heal_over_time" or effect_type.lower() == "hot":
            effect = HealOverTimeEffect(
                name="Test HoT",
                description="A test heal over time effect",
                duration=effect_duration,
                intensity=1.0,
                heal_per_turn=10.0
            )
        elif effect_type.lower() == "condition":
            effect = ConditionEffect(
                name="Test Condition",
                description="A test condition effect",
                duration=effect_duration,
                intensity=1.0,
                condition="stunned"
            )
        elif effect_type.lower() == "resistance":
            effect = ResistanceEffect(
                name="Test Resistance",
                description="A test resistance effect",
                duration=effect_duration,
                intensity=1.0,
                damage_types=["fire", "cold"],
                resistance_multiplier=0.5
            )
        elif effect_type.lower() == "vulnerability":
            effect = VulnerabilityEffect(
                name="Test Vulnerability",
                description="A test vulnerability effect",
                duration=effect_duration,
                intensity=1.0,
                damage_types=["fire", "cold"],
                vulnerability_multiplier=2.0
            )
        elif effect_type.lower() == "immunity":
            effect = ImmunityEffect(
                name="Test Immunity",
                description="A test immunity effect",
                duration=effect_duration,
                intensity=1.0,
                damage_types=["fire", "cold"]
            )
        else:
            # Generic effect
            effect = CombatEffect(
                name=f"Test {effect_type}",
                description=f"A test {effect_type} effect",
                duration=effect_duration,
                intensity=1.0
            )
            
        # Apply the effect
        result = self.active_combat.apply_effect(source_id, target_id, effect)
        
        if not result.get("success", False):
            self.log(f"Failed to apply effect: {result.get('message', 'Unknown error')}")
            return None
            
        effect_id = result.get("effect", {}).get("id")
        self.log(f"Applied {effect_type} effect {effect_id} from {source_id} to {target_id}")
        return effect_id
    
    def damage_character(self, character_id: Optional[str] = None, amount: float = 10.0, damage_type: str = "physical") -> bool:
        """
        Apply damage to a character.
        
        Args:
            character_id: Optional character ID to damage (random if None)
            amount: Amount of damage to apply
            damage_type: Type of damage to apply
            
        Returns:
            True if damage was applied, False otherwise
        """
        if not self.active_combat:
            self.log("No active combat")
            return False
            
        # Get the character
        characters = self.active_combat.combat_state.get_all_characters()
        
        if not character_id:
            # Use a random character
            character_id = random.choice(list(characters.keys()))
            
        # Apply damage
        result = self.active_combat.apply_damage(None, character_id, amount, damage_type)
        
        if not result.get("success", False):
            self.log(f"Failed to damage character: {result.get('message', 'Unknown error')}")
            return False
            
        self.log(f"Applied {amount} {damage_type} damage to {character_id}")
        return True
    
    def heal_character(self, character_id: Optional[str] = None, amount: float = 10.0) -> bool:
        """
        Apply healing to a character.
        
        Args:
            character_id: Optional character ID to heal (random if None)
            amount: Amount of healing to apply
            
        Returns:
            True if healing was applied, False otherwise
        """
        if not self.active_combat:
            self.log("No active combat")
            return False
            
        # Get the character
        characters = self.active_combat.combat_state.get_all_characters()
        
        if not character_id:
            # Use a random character
            character_id = random.choice(list(characters.keys()))
            
        # Apply healing
        result = self.active_combat.apply_healing(None, character_id, amount)
        
        if not result.get("success", False):
            self.log(f"Failed to heal character: {result.get('message', 'Unknown error')}")
            return False
            
        self.log(f"Applied {amount} healing to {character_id}")
        return True
    
    def force_next_turn(self) -> bool:
        """
        Force the combat to advance to the next turn.
        
        Returns:
            True if the combat advanced, False otherwise
        """
        if not self.active_combat:
            self.log("No active combat")
            return False
            
        # Advance the turn
        result = self.active_combat.next_turn()
        current = result.get("turn", {}).get("current_character")
        
        self.log(f"Advanced to next turn, current character: {current}")
        return True
    
    def force_next_round(self) -> bool:
        """
        Force the combat to advance an entire round.
        
        Returns:
            True if the combat advanced, False otherwise
        """
        if not self.active_combat:
            self.log("No active combat")
            return False
            
        # Track starting character to detect full round
        starting_character = self.active_combat.turn_queue.current_combatant
        
        # Advance turns until we come back to the starting character
        while True:
            self.active_combat.next_turn()
            current = self.active_combat.turn_queue.current_combatant
            
            if current == starting_character:
                break
                
        self.log(f"Advanced a full round, current round: {self.active_combat.round_number}")
        return True
    
    def toggle_character_enemy_status(self, character_id: Optional[str] = None) -> bool:
        """
        Toggle a character's enemy status.
        
        Args:
            character_id: Optional character ID to toggle (random if None)
            
        Returns:
            True if the status was toggled, False otherwise
        """
        if not self.active_combat:
            self.log("No active combat")
            return False
            
        # Get the character
        characters = self.active_combat.combat_state.get_all_characters()
        
        if not character_id:
            # Use a random character
            character_id = random.choice(list(characters.keys()))
            
        character = characters.get(character_id)
        
        if not character:
            self.log(f"Character not found: {character_id}")
            return False
            
        # Toggle enemy status
        is_enemy = character.get("is_enemy", False)
        character["is_enemy"] = not is_enemy
        
        self.log(f"Toggled character {character_id} enemy status to {not is_enemy}")
        return True
    
    def reset_combat(self) -> bool:
        """
        Reset the active combat to initial state.
        
        Returns:
            True if the combat was reset, False otherwise
        """
        if not self.active_combat:
            self.log("No active combat")
            return False
            
        # Store combat ID and characters
        combat_id = self.active_combat.combat_id
        characters = self.active_combat.combat_state.get_all_characters()
        
        # Create a new combat with the same characters
        new_combat = Combat(character_dict=characters)
        new_combat.start_combat()
        
        # Replace in test_combats dict
        self.test_combats[combat_id] = new_combat
        
        # Update active combat
        self.set_active_combat(new_combat)
        
        self.log(f"Reset combat {combat_id}")
        return True
    
    def take_random_action(self, character_id: Optional[str] = None) -> bool:
        """
        Have a character take a random action.
        
        Args:
            character_id: Optional character ID to act (current turn character if None)
            
        Returns:
            True if an action was taken, False otherwise
        """
        if not self.active_combat:
            self.log("No active combat")
            return False
            
        # Get the character
        if not character_id:
            # Use current turn character
            character_id = self.active_combat.turn_queue.current_combatant
            
        if not character_id:
            self.log("No current character")
            return False
            
        # Get available actions
        result = self.active_combat.get_available_actions(character_id)
        actions = result.get("actions", [])
        
        if not actions:
            self.log(f"No available actions for {character_id}")
            return False
            
        # Pick a random action
        action = random.choice(actions)
        action_id = action.get("id")
        
        # Pick a random target if needed
        target_id = None
        characters = list(self.active_combat.combat_state.get_all_characters().keys())
        
        if action.get("target_type") in ["SINGLE", "MULTI"]:
            target_id = random.choice(characters)
            
        # Take the action
        try:
            result = self.active_combat.take_action(character_id, action_id, target_id)
            success = result.get("result", {}).get("success", False)
            message = result.get("result", {}).get("message", "Unknown result")
            
            self.log(f"Character {character_id} took action {action_id} on {target_id}: {success}, {message}")
            return success
        except Exception as e:
            self.log(f"Error taking action: {str(e)}")
            return False
    
    def get_debug_log(self) -> List[str]:
        """
        Get the current debug log.
        
        Returns:
            List of log messages
        """
        return self.debug_logs
    
    def clear_debug_log(self) -> None:
        """Clear the debug log."""
        self.debug_logs.clear()
        self.log("Debug log cleared")
    
    def get_debug_state(self) -> Dict[str, Any]:
        """
        Get the current debug state including all test combats and characters.
        
        Returns:
            Dictionary with debug state
        """
        return {
            "test_combats": [combat_id for combat_id in self.test_combats],
            "active_combat_id": self.active_combat.combat_id if self.active_combat else None,
            "test_characters": [char_id for char_id in self.test_characters],
            "debug_enabled": self.debug_enabled,
            "log_count": len(self.debug_logs)
        }
    
    def run_stress_test(self, rounds: int = 5) -> Dict[str, Any]:
        """
        Run a stress test on the active combat.
        
        Args:
            rounds: Number of rounds to simulate
            
        Returns:
            Dictionary with test results
        """
        if not self.active_combat:
            self.log("No active combat")
            return {"success": False, "message": "No active combat"}
            
        # Track performance
        import time
        start_time = time.time()
        error_count = 0
        
        # Run the specified number of rounds
        for round_num in range(rounds):
            self.log(f"Starting round {round_num + 1}")
            
            # Track starting character to detect full round
            starting_character = self.active_combat.turn_queue.current_combatant
            
            # Process each character's turn
            while True:
                current_character = self.active_combat.turn_queue.current_combatant
                
                # Take a random action (may fail)
                try:
                    self.take_random_action(current_character)
                except Exception as e:
                    self.log(f"Error during stress test: {str(e)}")
                    error_count += 1
                
                # Apply a random effect occasionally
                if random.random() < 0.3:  # 30% chance
                    try:
                        effect_types = ["buff", "debuff", "damage_over_time", "heal_over_time", "condition"]
                        self.apply_test_effect(random.choice(effect_types))
                    except Exception as e:
                        self.log(f"Error applying effect during stress test: {str(e)}")
                        error_count += 1
                
                # Move to next turn
                self.active_combat.next_turn()
                
                # Check if we've completed a round
                if self.active_combat.turn_queue.current_combatant == starting_character:
                    break
        
        # Calculate results
        end_time = time.time()
        duration = end_time - start_time
        
        self.log(f"Stress test completed: {rounds} rounds in {duration:.2f} seconds with {error_count} errors")
        
        return {
            "success": True,
            "rounds": rounds,
            "duration": duration,
            "errors": error_count,
            "avg_round_time": duration / rounds if rounds > 0 else 0
        }

# Create a singleton instance for global access
combat_debug_interface = CombatDebugInterface() 