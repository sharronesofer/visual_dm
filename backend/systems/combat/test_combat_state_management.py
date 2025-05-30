"""
Test module for Combat State Management functionality.

This module tests the serialization, deserialization, and state
management features of the Combat class and CombatState class, 
ensuring that the combat system can properly save/load state and
handle state transitions.
"""
import unittest
import os
import json
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch

from .combat_class import Combat
from .combat_state_class import CombatState
from .turn_queue import TurnQueue
from .effect_pipeline import EffectPipeline, BuffEffect, DebuffEffect
from .object_pool import combat_pool_manager

# Test characters for consistency
TEST_CHARACTERS = {
    "player_1": MagicMock(
        id="player_1",
        name="Player Character 1",
        dexterity=14,
        hp=50,
        max_hp=50,
        attributes={"STR": 16, "DEX": 14, "CON": 12},
        position=1,
        is_dead=False
    ),
    "enemy_1": MagicMock(
        id="enemy_1",
        name="Enemy Character 1",
        dexterity=12,
        hp=30,
        max_hp=30,
        attributes={"STR": 14, "DEX": 12, "CON": 10},
        position=2,
        is_dead=False
    ),
}

class TestCombatStateManagement(unittest.TestCase):
    """Test suite for Combat State Management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a new combat instance
        self.combat = Combat(character_dict=TEST_CHARACTERS)
        
        # Set characters as player/enemy
        self.combat.combat_state.set_player_character("player_1", True)
        self.combat.combat_state.set_player_character("enemy_1", False)
        
        # Start combat to initialize turn queue
        self.combat.start_combat()
        
        # Apply some effects for testing
        player = self.combat.combat_state.get_character("player_1")
        enemy = self.combat.combat_state.get_character("enemy_1")
        
        # Create and apply test effects
        buff = BuffEffect(name="Test Buff", description="Test buff effect", duration=3)
        debuff = DebuffEffect(name="Test Debuff", description="Test debuff effect", duration=2)
        
        self.combat.effect_pipeline.apply_effect(player, player, buff)
        self.combat.effect_pipeline.apply_effect(enemy, player, debuff)
    
    def test_combat_state_serialization(self):
        """Test that combat state can be serialized to a dictionary."""
        # Get serialized state
        state_dict = self.combat.serialize()
        
        # Verify essential fields
        self.assertEqual(state_dict["combat_id"], self.combat.combat_id)
        self.assertEqual(state_dict["round_number"], self.combat.round_number)
        
        # Verify characters are included
        self.assertIn("characters", state_dict)
        self.assertIn("player_1", state_dict["characters"])
        self.assertIn("enemy_1", state_dict["characters"])
        
        # Verify character details
        self.assertEqual(state_dict["characters"]["player_1"]["name"], "Player Character 1")
        self.assertEqual(state_dict["characters"]["enemy_1"]["name"], "Enemy Character 1")
        
        # Verify effects are included
        self.assertIn("effects", state_dict)
        self.assertIn("player_1", state_dict["effects"])
        
        # Verify turn queue state
        self.assertIn("turn_queue", state_dict)
        self.assertIn("queue", state_dict["turn_queue"])
        self.assertIn("current_combatant", state_dict["turn_queue"])
    
    def test_combat_state_json_serialization(self):
        """Test that combat state can be serialized to JSON and back."""
        # Get JSON
        json_data = self.combat.to_json()
        
        # Verify it's valid JSON
        parsed_data = json.loads(json_data)
        self.assertEqual(parsed_data["combat_id"], self.combat.combat_id)
        
        # Create a new combat instance and load JSON
        new_combat = Combat()
        success = new_combat.from_json(json_data)
        
        # Verify deserialization was successful
        self.assertTrue(success)
        self.assertEqual(new_combat.combat_id, self.combat.combat_id)
        self.assertEqual(new_combat.round_number, self.combat.round_number)
        
        # Verify characters
        character_ids = list(new_combat.combat_state.get_all_characters().keys())
        self.assertIn("player_1", character_ids)
        self.assertIn("enemy_1", character_ids)
    
    def test_file_persistence(self):
        """Test that combat state can be saved to and loaded from a file."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Save to file
            save_success = self.combat.save_to_file(temp_path)
            self.assertTrue(save_success)
            
            # Create a new combat instance and load from file
            new_combat = Combat()
            load_success = new_combat.load_from_file(temp_path)
            
            # Verify loading was successful
            self.assertTrue(load_success)
            self.assertEqual(new_combat.combat_id, self.combat.combat_id)
            
            # Verify character data
            character_ids = list(new_combat.combat_state.get_all_characters().keys())
            self.assertIn("player_1", character_ids)
            self.assertIn("enemy_1", character_ids)
        finally:
            # Clean up
            os.unlink(temp_path)
    
    def test_state_transitions(self):
        """Test combat state transitions."""
        # Test pause/resume
        paused_state = self.combat.pause_combat()
        self.assertEqual(self.combat.combat_state.status, "paused")
        
        resumed_state = self.combat.resume_combat()
        self.assertEqual(self.combat.combat_state.status, "active")
        
        # Test victory/defeat transitions
        victory_state = self.combat.handle_state_transition("victory")
        self.assertEqual(self.combat.combat_state.status, "victory")
        
        # Reset for defeat test
        self.combat.combat_state.status = "active"
        defeat_state = self.combat.handle_state_transition("defeat")
        self.assertEqual(self.combat.combat_state.status, "defeat")
    
    def test_state_history_and_rollback(self):
        """Test state history tracking and rollback functionality."""
        # Get initial state
        initial_round = self.combat.round_number
        
        # Change state to create history
        self.combat.combat_state.change_status("active")
        
        # Advance a round
        self.combat.round_number += 1
        
        # Change state again to create another history entry
        self.combat.combat_state.change_status("paused")
        
        # Check history
        history = self.combat.get_state_history()
        self.assertGreaterEqual(len(history), 2)  # At least 2 entries
        
        # Rollback to previous state
        result = self.combat.undo_last_action()
        
        # Verify current state
        self.assertEqual(self.combat.combat_state.status, "active")
    
    def test_combat_state_deserialization(self):
        """Test that combat state can be deserialized from a dictionary."""
        # Get serialized state
        state_dict = self.combat.serialize()
        
        # Create a new combat instance
        new_combat = Combat()
        
        # Deserialize
        success = new_combat.deserialize(state_dict)
        
        # Verify
        self.assertTrue(success)
        self.assertEqual(new_combat.combat_id, self.combat.combat_id)
        self.assertEqual(new_combat.round_number, self.combat.round_number)
        
        # Verify characters
        character_ids = list(new_combat.combat_state.get_all_characters().keys())
        self.assertIn("player_1", character_ids)
        self.assertIn("enemy_1", character_ids)
        
        # Verify that the combat is functional after deserialization
        # Try advancing a turn
        try:
            next_state = new_combat.next_turn()
            self.assertIsNotNone(next_state)
        except Exception as e:
            self.fail(f"next_turn() raised an exception: {e}")
    
    def test_effect_serialization_deserialization(self):
        """Test that effects are properly serialized and deserialized."""
        # Get serialized state
        state_dict = self.combat.serialize()
        
        # Create a new combat instance
        new_combat = Combat()
        
        # Deserialize
        success = new_combat.deserialize(state_dict)
        self.assertTrue(success)
        
        # Get player character
        player = new_combat.combat_state.get_character("player_1")
        
        # Check that effects were restored
        effects = new_combat.effect_pipeline.get_active_effects(player)
        
        # Verify effect count
        self.assertEqual(len(effects), 2)  # Should have our test buff and debuff
        
        # Verify effect details
        effect_names = [effect.name for effect in effects]
        self.assertIn("Test Buff", effect_names)
        self.assertIn("Test Debuff", effect_names)
        
        # Verify effect still has duration
        for effect in effects:
            if effect.name == "Test Buff":
                self.assertGreaterEqual(effect.duration, 1)

if __name__ == "__main__":
    unittest.main() 