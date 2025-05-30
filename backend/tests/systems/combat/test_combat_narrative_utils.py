"""
Tests for backend.systems.combat.combat_narrative_utils

Comprehensive tests for combat narrative utility functions.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add the backend.systems.combat module to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.systems.combat.combat_narrative_utils import (
    narrate_action,
    log_combat_event,
    log_combat_start,
    format_combat_summary
)


class TestNarrateAction(unittest.TestCase): pass
    """Test cases for narrate_action function"""

    @patch('backend.systems.llm.services.gpt_client.GPTClient')
    def test_narrate_action_successful_hit(self, mock_gpt_client): pass
        """Test narrative generation for a successful hit"""
        mock_client = Mock()
        mock_client.call.return_value = "The warrior's sword sliced through the air, striking the orc with devastating force!"
        mock_gpt_client.return_value = mock_client

        actor_name = "Warrior"
        action_details = {
            "ability": "Sword Strike",
            "target": "Orc"
        }
        outcome = {
            "hit": True,
            "damage": 15,
            "damage_type": "slashing",
            "target_hp": 25
        }

        result = narrate_action(actor_name, action_details, outcome)

        self.assertEqual(result, "The warrior's sword sliced through the air, striking the orc with devastating force!")
        mock_client.call.assert_called_once()
        
        # Verify the prompt contains expected information
        call_args = mock_client.call.call_args
        self.assertIn("Warrior used Sword Strike on Orc", call_args[1]['user_prompt'])
        self.assertIn("hit and dealt 15 slashing", call_args[1]['user_prompt'])
        self.assertIn("Target HP after the attack: 25", call_args[1]['user_prompt'])

    @patch('backend.systems.llm.services.gpt_client.GPTClient')
    def test_narrate_action_miss(self, mock_gpt_client): pass
        """Test narrative generation for a missed attack"""
        mock_client = Mock()
        mock_client.call.return_value = "The archer's arrow whistled past the goblin's ear, missing by inches!"
        mock_gpt_client.return_value = mock_client

        actor_name = "Archer"
        action_details = {
            "ability": "Bow Shot",
            "target": "Goblin"
        }
        outcome = {
            "hit": False,
            "damage": 0,
            "damage_type": "piercing",
            "target_hp": 30
        }

        result = narrate_action(actor_name, action_details, outcome)

        self.assertEqual(result, "The archer's arrow whistled past the goblin's ear, missing by inches!")
        
        # Verify the prompt indicates a miss
        call_args = mock_client.call.call_args
        self.assertIn("missed and dealt 0 piercing", call_args[1]['user_prompt'])

    @patch('backend.systems.llm.services.gpt_client.GPTClient')
    def test_narrate_action_minimal_details(self, mock_gpt_client): pass
        """Test narrative generation with minimal action details"""
        mock_client = Mock()
        mock_client.call.return_value = "A mysterious action unfolds in the heat of battle!"
        mock_gpt_client.return_value = mock_client

        actor_name = "Unknown"
        action_details = {}  # Empty details
        outcome = {}  # Empty outcome

        result = narrate_action(actor_name, action_details, outcome)

        self.assertEqual(result, "A mysterious action unfolds in the heat of battle!")
        
        # Verify defaults are used
        call_args = mock_client.call.call_args
        self.assertIn("used an action on None", call_args[1]['user_prompt'])
        self.assertIn("missed and dealt 0 damage", call_args[1]['user_prompt'])
        self.assertIn("Target HP after the attack: ?", call_args[1]['user_prompt'])

    @patch('backend.systems.llm.services.gpt_client.GPTClient')
    def test_narrate_action_gpt_parameters(self, mock_gpt_client): pass
        """Test that GPT is called with correct parameters"""
        mock_client = Mock()
        mock_client.call.return_value = "Test narrative"
        mock_gpt_client.return_value = mock_client

        narrate_action("Test", {"ability": "Test"}, {"hit": True})

        mock_client.call.assert_called_once_with(
            system_prompt="You are a fantasy combat narrator. Describe actions vividly with immersive prose.",
            user_prompt=unittest.mock.ANY,
            temperature=0.9,
            max_tokens=150
        )


class TestLogCombatEvent(unittest.TestCase): pass
    """Test cases for log_combat_event function"""

    @patch('backend.systems.combat.combat_narrative_utils.db')
    @patch('backend.systems.combat.combat_ram.ACTIVE_BATTLES', {})
    @patch('backend.systems.combat.combat_narrative_utils.datetime')
    def test_log_combat_event_firebase_only(self, mock_datetime, mock_db): pass
        """Test logging combat event to Firebase when not in active battles"""
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        mock_ref = Mock()
        mock_ref.get.return_value = []
        mock_db.reference.return_value = mock_ref

        event_data = {
            "type": "attack",
            "actor": "player1",
            "target": "enemy1",
            "damage": 10
        }

        result = log_combat_event("combat123", event_data)

        # Verify event structure
        expected_event = {
            "type": "attack",
            "actor": "player1",
            "target": "enemy1",
            "damage": 10,
            "timestamp": "2023-01-01T12:00:00"
        }
        self.assertEqual(result, expected_event)

        # Verify Firebase operations
        mock_db.reference.assert_called_once_with("/combat_state/combat123/log")
        mock_ref.get.assert_called_once()
        mock_ref.set.assert_called_once_with([expected_event])

    @patch('backend.systems.combat.combat_narrative_utils.db')
    @patch('backend.systems.combat.combat_narrative_utils.datetime')
    def test_log_combat_event_with_active_battle(self, mock_datetime, mock_db): pass
        """Test logging combat event when combat is in active battles"""
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        mock_ref = Mock()
        mock_ref.get.return_value = []
        mock_db.reference.return_value = mock_ref

        # Mock active battle
        mock_combat = Mock()
        mock_combat.log = []
        
        with patch('backend.systems.combat.combat_ram.ACTIVE_BATTLES', {"combat123": mock_combat}): pass
            event_data = {"type": "heal", "amount": 5}
            result = log_combat_event("combat123", event_data)

            # Verify event was added to active battle log
            self.assertEqual(len(mock_combat.log), 1)
            self.assertEqual(mock_combat.log[0]["type"], "heal")
            self.assertEqual(mock_combat.log[0]["timestamp"], "2023-01-01T12:00:00")

    @patch('backend.systems.combat.combat_narrative_utils.db')
    @patch('backend.systems.combat.combat_narrative_utils.datetime')
    def test_log_combat_event_existing_firebase_log(self, mock_datetime, mock_db): pass
        """Test logging to Firebase when log already exists"""
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        existing_log = [{"type": "previous_event", "timestamp": "2023-01-01T11:00:00"}]
        mock_ref = Mock()
        mock_ref.get.return_value = existing_log
        mock_db.reference.return_value = mock_ref

        with patch('backend.systems.combat.combat_ram.ACTIVE_BATTLES', {}): pass
            event_data = {"type": "new_event"}
            log_combat_event("combat123", event_data)

            # Verify new event was appended to existing log
            expected_log = [
                {"type": "previous_event", "timestamp": "2023-01-01T11:00:00"},
                {"type": "new_event", "timestamp": "2023-01-01T12:00:00"}
            ]
            mock_ref.set.assert_called_once_with(expected_log)


class TestLogCombatStart(unittest.TestCase): pass
    """Test cases for log_combat_start function"""

    @patch('backend.systems.combat.combat_narrative_utils.db')
    @patch('backend.systems.combat.combat_narrative_utils.datetime')
    def test_log_combat_start_basic(self, mock_datetime, mock_db): pass
        """Test basic combat start logging"""
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        # Mock POI reference
        mock_poi_ref = Mock()
        mock_poi_ref.get.return_value = []
        
        # Mock NPC memory references
        mock_npc_ref = Mock()
        mock_npc_ref.get.return_value = {"rag_log": [], "summary": ""}
        
        def mock_reference(path): pass
            if "poi_state" in path: pass
                return mock_poi_ref
            elif "npc_memory" in path: pass
                return mock_npc_ref
            return Mock()
        
        mock_db.reference.side_effect = mock_reference

        result = log_combat_start("forest", "clearing1", ["player1", "npc_goblin1"])

        # Verify returned event structure
        expected_event = {
            "type": "combat_started",
            "day": "2023-01-01T12:00:00",
            "participants": ["player1", "npc_goblin1"]
        }
        self.assertEqual(result, expected_event)

        # Verify POI log was updated
        mock_poi_ref.set.assert_called_once_with([expected_event])

        # Verify NPC memory was updated
        expected_memory = {
            "rag_log": [{
                "interaction": "Was present during combat at clearing1 on 2023-01-01T12:00:00",
                "timestamp": "2023-01-01T12:00:00"
            }],
            "summary": ""
        }
        mock_npc_ref.set.assert_called_once_with(expected_memory)

    @patch('backend.systems.combat.combat_narrative_utils.db')
    @patch('backend.systems.combat.combat_narrative_utils.datetime')
    def test_log_combat_start_no_npcs(self, mock_datetime, mock_db): pass
        """Test combat start logging with no NPCs"""
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        mock_poi_ref = Mock()
        mock_poi_ref.get.return_value = []
        mock_db.reference.return_value = mock_poi_ref

        result = log_combat_start("forest", "clearing1", ["player1", "player2"])

        # Verify only POI reference was called (no NPC memory updates)
        mock_db.reference.assert_called_once_with("/poi_state/forest/clearing1/event_log")

    @patch('backend.systems.combat.combat_narrative_utils.db')
    @patch('backend.systems.combat.combat_narrative_utils.datetime')
    def test_log_combat_start_existing_poi_log(self, mock_datetime, mock_db): pass
        """Test combat start logging when POI already has events"""
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        existing_events = [{"type": "previous_event", "day": "2023-01-01T10:00:00"}]
        mock_poi_ref = Mock()
        mock_poi_ref.get.return_value = existing_events
        mock_db.reference.return_value = mock_poi_ref

        log_combat_start("forest", "clearing1", ["player1"])

        # Verify new event was appended
        expected_log = [
            {"type": "previous_event", "day": "2023-01-01T10:00:00"},
            {
                "type": "combat_started",
                "day": "2023-01-01T12:00:00",
                "participants": ["player1"]
            }
        ]
        mock_poi_ref.set.assert_called_once_with(expected_log)

    @patch('backend.systems.combat.combat_narrative_utils.db')
    @patch('backend.systems.combat.combat_narrative_utils.datetime')
    def test_log_combat_start_existing_npc_memory(self, mock_datetime, mock_db): pass
        """Test combat start logging when NPC already has memories"""
        mock_datetime.utcnow.return_value.isoformat.return_value = "2023-01-01T12:00:00"
        
        mock_poi_ref = Mock()
        mock_poi_ref.get.return_value = []
        
        existing_memory = {
            "rag_log": [{"interaction": "Previous memory", "timestamp": "2023-01-01T10:00:00"}],
            "summary": "Existing summary"
        }
        mock_npc_ref = Mock()
        mock_npc_ref.get.return_value = existing_memory
        
        def mock_reference(path): pass
            if "poi_state" in path: pass
                return mock_poi_ref
            elif "npc_memory" in path: pass
                return mock_npc_ref
            return Mock()
        
        mock_db.reference.side_effect = mock_reference

        log_combat_start("forest", "clearing1", ["npc_orc1"])

        # Verify new memory was appended
        expected_memory = {
            "rag_log": [
                {"interaction": "Previous memory", "timestamp": "2023-01-01T10:00:00"},
                {
                    "interaction": "Was present during combat at clearing1 on 2023-01-01T12:00:00",
                    "timestamp": "2023-01-01T12:00:00"
                }
            ],
            "summary": "Existing summary"
        }
        mock_npc_ref.set.assert_called_once_with(expected_memory)


class TestFormatCombatSummary(unittest.TestCase): pass
    """Test cases for format_combat_summary function"""

    def test_format_combat_summary_complete(self): pass
        """Test formatting a complete combat summary"""
        combat_state = {
            "name": "Battle of the Ancient Grove",
            "round": 3,
            "party": [
                {"name": "Aragorn", "current_hp": 45, "max_hp": 60},
                {"name": "Legolas", "current_hp": 38, "max_hp": 50}
            ],
            "enemies": [
                {"name": "Orc Warrior", "current_hp": 15, "max_hp": 40},
                {"name": "Goblin Scout", "current_hp": 0, "max_hp": 25}
            ],
            "log": [
                "Aragorn attacks Orc Warrior for 12 damage",
                "Orc Warrior misses Aragorn",
                "Legolas shoots Goblin Scout for 25 damage",
                "Goblin Scout falls unconscious"
            ]
        }

        result = format_combat_summary(combat_state)

        expected_lines = [
            "Combat: Battle of the Ancient Grove",
            "Round: 3",
            "",
            "Party:",
            "  Aragorn: 45/60 HP",
            "  Legolas: 38/50 HP",
            "",
            "Enemies:",
            "  Orc Warrior: 15/40 HP",
            "  Goblin Scout: 0/25 HP",
            "",
            "Recent Events:",
            "  Orc Warrior misses Aragorn",
            "  Legolas shoots Goblin Scout for 25 damage",
            "  Goblin Scout falls unconscious"
        ]
        expected = "\n".join(expected_lines)
        self.assertEqual(result, expected)

    def test_format_combat_summary_minimal(self): pass
        """Test formatting with minimal combat data"""
        combat_state = {}

        result = format_combat_summary(combat_state)

        expected_lines = [
            "Combat: Unnamed Battle",
            "Round: 1"
        ]
        expected = "\n".join(expected_lines)
        self.assertEqual(result, expected)

    def test_format_combat_summary_no_party(self): pass
        """Test formatting when there's no party"""
        combat_state = {
            "name": "Solo Enemy Encounter",
            "round": 1,
            "enemies": [
                {"name": "Dragon", "current_hp": 200, "max_hp": 300}
            ]
        }

        result = format_combat_summary(combat_state)

        self.assertIn("Combat: Solo Enemy Encounter", result)
        self.assertIn("Enemies:", result)
        self.assertIn("  Dragon: 200/300 HP", result)
        self.assertNotIn("Party:", result)

    def test_format_combat_summary_no_enemies(self): pass
        """Test formatting when there are no enemies"""
        combat_state = {
            "name": "Training Session",
            "round": 1,
            "party": [
                {"name": "Student", "current_hp": 30, "max_hp": 30}
            ]
        }

        result = format_combat_summary(combat_state)

        self.assertIn("Combat: Training Session", result)
        self.assertIn("Party:", result)
        self.assertIn("  Student: 30/30 HP", result)
        self.assertNotIn("Enemies:", result)

    def test_format_combat_summary_missing_character_data(self): pass
        """Test formatting with missing character data"""
        combat_state = {
            "name": "Incomplete Data Battle",
            "party": [
                {"name": "Complete", "current_hp": 50, "max_hp": 50},
                {"current_hp": 30, "max_hp": 40},  # Missing name
                {}  # Missing all data
            ],
            "enemies": [
                {"name": "Enemy", "max_hp": 100}  # Missing current_hp
            ]
        }

        result = format_combat_summary(combat_state)

        self.assertIn("  Complete: 50/50 HP", result)
        self.assertIn("  Unknown: 30/40 HP", result)
        self.assertIn("  Unknown: 0/0 HP", result)
        self.assertIn("  Enemy: 0/100 HP", result)

    def test_format_combat_summary_long_log(self): pass
        """Test formatting with a long combat log (should show only last 3)"""
        combat_state = {
            "name": "Extended Battle",
            "log": [
                "Event 1",
                "Event 2", 
                "Event 3",
                "Event 4",
                "Event 5",
                "Event 6"
            ]
        }

        result = format_combat_summary(combat_state)

        self.assertIn("Recent Events:", result)
        self.assertIn("  Event 4", result)
        self.assertIn("  Event 5", result)
        self.assertIn("  Event 6", result)
        self.assertNotIn("  Event 1", result)
        self.assertNotIn("  Event 2", result)
        self.assertNotIn("  Event 3", result)

    def test_format_combat_summary_empty_log(self): pass
        """Test formatting with empty combat log"""
        combat_state = {
            "name": "New Battle",
            "log": []
        }

        result = format_combat_summary(combat_state)

        self.assertNotIn("Recent Events:", result)


if __name__ == '__main__': pass
    unittest.main()
