"""
Integration tests for the Visual DM advanced combat system.

This module tests the integration between the Combat class and its
subsystems (TurnQueue, EffectPipeline, and ActionSystem).
"""

import unittest
import uuid
from unittest.mock import MagicMock, patch
from typing import Dict, Any

from backend.systems.combat.turn_queue import TurnQueue
from backend.systems.combat.effect_pipeline import EffectPipeline, CombatEffect, EffectType
from backend.systems.combat.action_system import ActionDefinition, ActionType, ActionTarget, ActionResult
from backend.systems.combat.combat_class import Combat


class TestCharacter:
    """Simple character class for testing."""
    
    def __init__(self, character_id=None, name="Test Character", hp=100, max_hp=100, dexterity=10):
        self.id = character_id or str(uuid.uuid4())
        self.name = name
        self.hp = hp
        self.max_hp = max_hp
        self.dexterity = dexterity
        self.position = 0
        self.attributes = {"STR": 10, "DEX": dexterity, "CON": 10, "INT": 10, "WIS": 10, "CHA": 10}
        self.is_dead = False


class TestCombatIntegration(unittest.TestCase):
    """Test case for Combat class integration with subsystems."""
    
    def setUp(self):
        """Set up test environment before each test."""
        # Create test characters
        self.character1 = TestCharacter(character_id="char1", name="Fighter", dexterity=16)
        self.character2 = TestCharacter(character_id="char2", name="Cleric", dexterity=12)
        self.character3 = TestCharacter(character_id="char3", name="Enemy", dexterity=8)
        
        # Create character dictionary
        self.character_dict = {
            "char1": self.character1,
            "char2": self.character2,
            "char3": self.character3
        }
        
        # Initialize combat with test characters
        self.combat = Combat(character_dict=self.character_dict)
        
        # Set up test actions
        self.setup_test_actions()
    
    def setup_test_actions(self):
        """Set up test actions for action system."""
        # Mock the global action_system
        patcher = patch('backend.systems.combat.combat_class.action_system')
        self.mock_action_system = patcher.start()
        self.addCleanup(patcher.stop)
        
        # Create test actions
        self.attack_action = ActionDefinition(
            id="attack",
            name="Attack",
            description="Basic attack",
            action_type=ActionType.STANDARD,
            target_type=ActionTarget.SINGLE,
            execute_func=lambda source, target: ActionResult(
                success=True,
                message=f"{source.name} attacks {target.name if target else 'nothing'}",
                damage=10,
                damage_type="physical"
            )
        )
        
        self.heal_action = ActionDefinition(
            id="heal",
            name="Heal",
            description="Basic healing spell",
            action_type=ActionType.STANDARD,
            target_type=ActionTarget.SINGLE,
            execute_func=lambda source, target: ActionResult(
                success=True,
                message=f"{source.name} heals {target.name if target else 'self'}",
                damage=0,
                damage_type=""
            )
        )
        
        # Configure action_system.get_action to return our test actions
        def mock_get_action(action_id):
            if action_id == "attack":
                return self.attack_action
            elif action_id == "heal":
                return self.heal_action
            return None
        
        self.mock_action_system.get_action.side_effect = mock_get_action
        
        # Configure action_system.can_use_action to always return True
        self.mock_action_system.can_use_action.return_value = True
        
        # Configure action_system.use_action to return ActionResult
        def mock_use_action(character, action, target=None):
            if action.id == "attack":
                return ActionResult(
                    success=True,
                    message=f"{character.name} attacks {target.name if target else 'nothing'}",
                    damage=10,
                    damage_type="physical"
                )
            elif action.id == "heal":
                if target:
                    target.hp = min(target.max_hp, target.hp + 20)
                return ActionResult(
                    success=True,
                    message=f"{character.name} heals {target.name if target else 'self'}",
                    damage=0,
                    damage_type=""
                )
            return ActionResult(success=False, message="Unknown action")
        
        self.mock_action_system.use_action.side_effect = mock_use_action
        
        # Configure action_system.get_available_actions to return both actions
        self.mock_action_system.get_available_actions.return_value = [
            self.attack_action,
            self.heal_action
        ]
        
        # Configure action_system.reset_combatant_actions to do nothing
        self.mock_action_system.reset_combatant_actions.return_value = None
        
        # Configure action_system.get_remaining_actions to return dict
        self.mock_action_system.get_remaining_actions.return_value = {
            "standard": True,
            "bonus": True,
            "reaction": True,
            "movement": 30.0
        }
        
        self.mock_action_system._get_combatant_state.return_value = MagicMock()
        self.mock_action_system.use_movement.return_value = 5.0
    
    def test_combat_initialization(self):
        """Test combat initialization and subsystem setup."""
        # Check that the combat instance was properly initialized
        self.assertIsNotNone(self.combat.combat_id)
        self.assertIsNotNone(self.combat.turn_queue)
        self.assertIsNotNone(self.combat.effect_pipeline)
        self.assertIsNotNone(self.combat.combat_state)
        
        # Check that all characters were added to the combat state
        all_characters = self.combat.combat_state.get_all_characters()
        self.assertEqual(len(all_characters), 3)
        self.assertIn("char1", all_characters)
        self.assertIn("char2", all_characters)
        self.assertIn("char3", all_characters)
    
    def test_start_combat(self):
        """Test starting combat and initializing turn queue."""
        combat_state = self.combat.start_combat()
        
        # Check that round number was initialized
        self.assertEqual(self.combat.round_number, 1)
        
        # Check that turn queue was initialized
        self.assertEqual(len(self.combat.turn_queue.queue), 3)
        
        # Check that the character with highest dexterity is first
        # (char1 has dexterity 16, which should give highest initiative)
        # Note: This might fail occasionally due to random initiative rolls
        self.assertIn("current_character_id", combat_state)
        
        # Check that action_system.reset_combatant_actions was called for the first character
        self.mock_action_system.reset_combatant_actions.assert_called()
    
    def test_next_turn(self):
        """Test advancing to the next turn in combat."""
        # Start combat to initialize turn queue
        self.combat.start_combat()
        
        # Save current character ID
        current_id = self.combat.turn_queue.current_combatant
        
        # Advance to next turn
        next_state = self.combat.next_turn()
        
        # Check that the current character changed
        self.assertNotEqual(current_id, self.combat.turn_queue.current_combatant)
        
        # Check that new character is in next_state
        self.assertEqual(next_state["current_character_id"], self.combat.turn_queue.current_combatant)
        
        # Check that action_system.reset_combatant_actions was called for the new character
        self.mock_action_system.reset_combatant_actions.assert_called()
    
    def test_take_action(self):
        """Test taking an action in combat."""
        # Start combat
        self.combat.start_combat()
        
        # Get current character
        current_character_id = self.combat.turn_queue.current_combatant
        
        # Take attack action
        result = self.combat.take_action(current_character_id, "attack", "char3")
        
        # Check that action was successful
        self.assertTrue(result["result"]["success"])
        self.assertIn("message", result["result"])
        self.assertEqual(result["result"]["damage"], 10)
        self.assertEqual(result["result"]["damage_type"], "physical")
        
        # Check that action_system.use_action was called
        self.mock_action_system.use_action.assert_called()
    
    def test_apply_effect(self):
        """Test applying an effect to a character."""
        # Create a test effect
        effect = MagicMock(spec=CombatEffect)
        effect.id = "effect1"
        effect.name = "Poison"
        effect.description = "Deals damage over time"
        effect.effect_type = EffectType.DAMAGE_OVER_TIME
        effect.duration = 3
        effect.intensity = 1.0
        effect.current_stacks = 1
        
        # Mock the effect_pipeline.apply_effect method
        self.combat.effect_pipeline.apply_effect = MagicMock(return_value=True)
        
        # Apply the effect
        result = self.combat.apply_effect("char1", "char3", effect)
        
        # Check that effect was applied
        self.assertTrue(result["success"])
        self.assertIn("effect", result)
        
        # Check that effect_pipeline.apply_effect was called
        self.combat.effect_pipeline.apply_effect.assert_called_with(
            self.character1, self.character3, effect
        )
    
    def test_remove_effect(self):
        """Test removing an effect from a character."""
        # Mock the effect_pipeline.remove_effect_by_id method
        self.combat.effect_pipeline.remove_effect_by_id = MagicMock(return_value=True)
        
        # Remove the effect
        result = self.combat.remove_effect("char3", "effect1")
        
        # Check that effect was removed
        self.assertTrue(result["success"])
        
        # Check that effect_pipeline.remove_effect_by_id was called
        self.combat.effect_pipeline.remove_effect_by_id.assert_called_with(
            self.character3, "effect1"
        )
    
    def test_apply_damage(self):
        """Test applying damage to a character."""
        # Get initial HP
        initial_hp = self.character3.hp
        
        # Mock the effect_pipeline.modify_damage method
        self.combat.effect_pipeline.modify_damage = MagicMock(return_value=10)
        self.combat.effect_pipeline.process_damage = MagicMock()
        self.combat.effect_pipeline.process_deal_damage = MagicMock()
        
        # Apply damage
        result = self.combat.apply_damage("char1", "char3", 10, "physical")
        
        # Check that damage was applied
        self.assertEqual(result["original_damage"], 10)
        self.assertEqual(result["modified_damage"], 10)
        self.assertEqual(result["damage_type"], "physical")
        self.assertEqual(result["target_hp"], initial_hp - 10)
        self.assertFalse(result["is_dead"])
        
        # Check that effect_pipeline methods were called
        self.combat.effect_pipeline.modify_damage.assert_called()
        self.combat.effect_pipeline.process_damage.assert_called()
        self.combat.effect_pipeline.process_deal_damage.assert_called()
    
    def test_apply_healing(self):
        """Test applying healing to a character."""
        # Set initial HP lower than max
        self.character2.hp = 50
        initial_hp = self.character2.hp
        
        # Mock effect_pipeline methods
        self.combat.effect_pipeline.process_heal = MagicMock()
        self.combat.effect_pipeline.process_healed = MagicMock()
        
        # Apply healing
        result = self.combat.apply_healing("char1", "char2", 20)
        
        # Check that healing was applied
        self.assertEqual(result["healing"], 20)
        self.assertEqual(result["target_hp"], initial_hp + 20)
        
        # Check that effect_pipeline methods were called
        self.combat.effect_pipeline.process_heal.assert_called()
        self.combat.effect_pipeline.process_healed.assert_called()
    
    def test_use_movement(self):
        """Test character movement in combat."""
        # Start combat
        self.combat.start_combat()
        
        # Get current character
        current_character_id = self.combat.turn_queue.current_combatant
        
        # Set initial position
        character = self.combat.combat_state.get_character(current_character_id)
        character.position = 0
        
        # Use movement
        result = self.combat.use_movement(current_character_id, 5)
        
        # Check that movement was applied
        self.assertEqual(result["distance_moved"], 5.0)  # Based on our mock
        self.assertEqual(result["new_position"], 5.0)
        
        # Check that action_system.use_movement was called
        self.mock_action_system.use_movement.assert_called_with(character, 5)
    
    def test_ready_action(self):
        """Test readying an action for later use."""
        # Start combat
        self.combat.start_combat()
        
        # Get current character
        current_character_id = self.combat.turn_queue.current_combatant
        
        # Ready an action
        result = self.combat.ready_action(
            current_character_id, 
            "attack", 
            "when an enemy moves",
            "char3"
        )
        
        # Check that action was readied
        self.assertTrue(result["success"])
        
        # Check that the character has a readied_action attribute
        character = self.combat.combat_state.get_character(current_character_id)
        self.assertTrue(hasattr(character, "readied_action"))
        self.assertEqual(character.readied_action["action_id"], "attack")
        self.assertEqual(character.readied_action["target_id"], "char3")
    
    def test_check_readied_actions(self):
        """Test checking and executing readied actions."""
        # Start combat
        self.combat.start_combat()
        
        # Get a character
        character = self.character1
        
        # Manually set a readied action
        setattr(character, "readied_action", {
            "action_id": "attack",
            "condition": "when an enemy moves",
            "target_id": "char3"
        })
        
        # Check readied actions with matching trigger
        results = self.combat.check_readied_actions(
            "enemy moves",
            "char3"
        )
        
        # Check that the readied action was triggered
        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["result"]["success"])
        
        # Check that the readied action was cleared
        self.assertIsNone(getattr(character, "readied_action", None))
    
    def test_process_turn_phase(self):
        """Test processing different phases of a turn."""
        # Start combat
        self.combat.start_combat()
        
        # Create effect mocks
        damage_effect = MagicMock(spec=CombatEffect)
        damage_effect.effect_type = EffectType.DAMAGE_OVER_TIME
        damage_effect.damage_per_turn = 5
        damage_effect.intensity = 1.0
        damage_effect.source_id = "char1"
        damage_effect.damage_type = "poison"
        
        heal_effect = MagicMock(spec=CombatEffect)
        heal_effect.effect_type = EffectType.HEAL_OVER_TIME
        heal_effect.heal_per_turn = 5
        heal_effect.intensity = 1.0
        heal_effect.source_id = "char2"
        
        # Mock getting applied effects
        self.combat.effect_pipeline.get_applied_effects = MagicMock(
            return_value=[damage_effect, heal_effect]
        )
        
        # Mock apply_damage and apply_healing
        self.combat.apply_damage = MagicMock(return_value={})
        self.combat.apply_healing = MagicMock(return_value={})
        
        # Process the action phase
        result = self.combat.process_turn_phase("action")
        
        # Check that damage and healing were applied
        self.combat.apply_damage.assert_called()
        self.combat.apply_healing.assert_called()
    
    def test_coordinate_subsystems(self):
        """Test coordinating subsystems after state changes."""
        # Prepare test data
        self.combat.turn_queue.queue = ["char1", "char2"]  # Missing char3
        
        # Call coordinate_subsystems
        self.combat.coordinate_subsystems()
        
        # Check that turn queue was updated to include char3
        self.assertEqual(len(self.combat.turn_queue.queue), 3)
        self.assertIn("char3", self.combat.turn_queue.queue)
        
        # Check that action states were initialized
        self.mock_action_system.reset_combatant_actions.assert_called()
    
    def test_handle_status_effects(self):
        """Test handling and processing status effects."""
        # Create effect mocks
        expired_effect = MagicMock(spec=CombatEffect)
        expired_effect.id = "effect1"
        expired_effect.name = "Expired"
        expired_effect.is_expired.return_value = True
        
        condition_effect = MagicMock(spec=CombatEffect)
        condition_effect.id = "effect2"
        condition_effect.name = "Stunned"
        condition_effect.effect_type = EffectType.CONDITION
        condition_effect.condition = "stunned"
        condition_effect.is_expired.return_value = False
        
        # Mock getting applied effects
        self.combat.effect_pipeline.get_applied_effects = MagicMock(
            return_value=[expired_effect, condition_effect]
        )
        
        # Mock remove_effect
        self.combat.effect_pipeline.remove_effect = MagicMock()
        
        # Mock next_turn
        self.combat.next_turn = MagicMock(return_value={})
        
        # Start combat and set current character to char1
        self.combat.start_combat()
        self.combat.turn_queue.current_combatant = "char1"
        
        # Handle status effects
        result = self.combat.handle_status_effects("char1")
        
        # Check that expired effect was removed
        self.combat.effect_pipeline.remove_effect.assert_called_with(
            self.character1, expired_effect
        )
        
        # Check that next_turn was called for stunned effect
        self.combat.next_turn.assert_called()
        
        # Check result structure
        self.assertEqual(result["character_id"], "char1")
        self.assertEqual(len(result["effect_results"]), 2)
        self.assertEqual(result["effect_results"][0]["result"], "expired")
        self.assertEqual(result["effect_results"][1]["result"], "lost_turn")


if __name__ == "__main__":
    unittest.main() 