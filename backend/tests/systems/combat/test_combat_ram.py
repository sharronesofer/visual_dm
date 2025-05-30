from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
"""
Tests for backend.systems.combat.combat_ram

Comprehensive tests for the CombatStateManager singleton and combat state management.
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add the backend.systems.combat module to the path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from backend.systems.combat.combat_ram import CombatStateManager, combat_state_manager, ACTIVE_BATTLES
from backend.systems.events import CombatEvent


class TestCombatStateManager(unittest.TestCase): pass
    """Test cases for CombatStateManager singleton"""

    def setUp(self): pass
        """Set up test fixtures"""
        # Clear any existing state
        if hasattr(CombatStateManager, '_instance'): pass
            CombatStateManager._instance = None
        
        # Create mock combat objects
        self.mock_combat1 = Mock()
        self.mock_combat1.id = "combat1"
        self.mock_combat1.name = "Test Combat 1"
        
        self.mock_combat2 = Mock()
        self.mock_combat2.id = "combat2"
        self.mock_combat2.name = "Test Combat 2"

    def tearDown(self): pass
        """Clean up after tests"""
        # Reset singleton instance
        if hasattr(CombatStateManager, '_instance'): pass
            CombatStateManager._instance = None

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_singleton_pattern(self, mock_event_dispatcher): pass
        """Test that CombatStateManager follows singleton pattern"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        # Get two instances
        instance1 = CombatStateManager.get_instance()
        instance2 = CombatStateManager.get_instance()
        
        # Should be the same instance
        self.assertIs(instance1, instance2)
        
        # Should have subscribed to combat events
        mock_dispatcher.subscribe.assert_called_once()

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_direct_instantiation_raises_error(self, mock_event_dispatcher): pass
        """Test that direct instantiation raises RuntimeError"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        # First instance should work
        CombatStateManager.get_instance()
        
        # Direct instantiation should raise error
        with self.assertRaises(RuntimeError) as context: pass
            CombatStateManager()
        
        self.assertIn("singleton", str(context.exception).lower())

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_add_combat(self, mock_event_dispatcher): pass
        """Test adding a combat to the manager"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        
        # Add combat
        manager.add_combat("combat1", self.mock_combat1)
        
        # Verify combat was added
        self.assertEqual(manager.get_combat("combat1"), self.mock_combat1)
        
        # Verify event was published
        mock_dispatcher.publish_sync.assert_called_once()
        event_call = mock_dispatcher.publish_sync.call_args[0][0]
        self.assertEqual(event_call.event_type, "combat.event")
        self.assertEqual(event_call.event_subtype, "state_registered")
        self.assertEqual(event_call.metadata["combat_id"], "combat1")

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_get_combat_existing(self, mock_event_dispatcher): pass
        """Test getting an existing combat"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        manager.add_combat("combat1", self.mock_combat1)
        
        # Get combat
        result = manager.get_combat("combat1")
        
        self.assertEqual(result, self.mock_combat1)

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_get_combat_nonexistent(self, mock_event_dispatcher): pass
        """Test getting a non-existent combat returns None"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        
        # Get non-existent combat
        result = manager.get_combat("nonexistent")
        
        self.assertIsNone(result)

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_remove_combat_existing(self, mock_event_dispatcher): pass
        """Test removing an existing combat"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        manager.add_combat("combat1", self.mock_combat1)
        
        # Remove combat
        result = manager.remove_combat("combat1")
        
        self.assertTrue(result)
        self.assertIsNone(manager.get_combat("combat1"))
        
        # Verify event was published (add + remove = 2 calls)
        self.assertEqual(mock_dispatcher.publish_sync.call_count, 2)
        remove_event_call = mock_dispatcher.publish_sync.call_args[0][0]
        self.assertEqual(remove_event_call.event_type, "combat.event")
        self.assertEqual(remove_event_call.event_subtype, "state_unregistered")
        self.assertEqual(remove_event_call.metadata["combat_id"], "combat1")

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_remove_combat_nonexistent(self, mock_event_dispatcher): pass
        """Test removing a non-existent combat returns False"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        
        # Remove non-existent combat
        result = manager.remove_combat("nonexistent")
        
        self.assertFalse(result)

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_get_all_combats(self, mock_event_dispatcher): pass
        """Test getting all combats"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        manager.add_combat("combat1", self.mock_combat1)
        manager.add_combat("combat2", self.mock_combat2)
        
        # Get all combats
        all_combats = manager.get_all_combats()
        
        self.assertEqual(len(all_combats), 2)
        self.assertEqual(all_combats["combat1"], self.mock_combat1)
        self.assertEqual(all_combats["combat2"], self.mock_combat2)
        
        # Should return a copy, not the original dict
        all_combats["combat3"] = Mock()
        self.assertEqual(len(manager.get_all_combats()), 2)

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_get_all_combats_empty(self, mock_event_dispatcher): pass
        """Test getting all combats when none exist"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        
        # Get all combats
        all_combats = manager.get_all_combats()
        
        self.assertEqual(len(all_combats), 0)
        self.assertIsInstance(all_combats, dict)

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_clear_all_combats(self, mock_event_dispatcher): pass
        """Test clearing all combats"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        manager.add_combat("combat1", self.mock_combat1)
        manager.add_combat("combat2", self.mock_combat2)
        
        # Clear all combats
        manager.clear_all_combats()
        
        # Verify all combats are gone
        self.assertEqual(len(manager.get_all_combats()), 0)
        self.assertIsNone(manager.get_combat("combat1"))
        self.assertIsNone(manager.get_combat("combat2"))
        
        # Verify events were published (add + add + clear = 4 calls total)
        self.assertEqual(mock_dispatcher.publish_sync.call_count, 4)

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_clear_all_combats_empty(self, mock_event_dispatcher): pass
        """Test clearing all combats when none exist"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        
        # Clear all combats (none exist)
        manager.clear_all_combats()
        
        # Should still work without error
        self.assertEqual(len(manager.get_all_combats()), 0)

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_handle_combat_event_created(self, mock_event_dispatcher): pass
        """Test handling combat.created event"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        manager.add_combat("combat1", self.mock_combat1)
        
        # Create a combat.created event
        event = CombatEvent(
            combat_id="combat1",
            event_subtype="created",
            entities_involved=[],
            metadata={"combat_id": "combat1"}
        )
        
        # Handle the event (should log but not change state)
        manager._handle_combat_event(event)
        
        # Combat should still exist
        self.assertEqual(manager.get_combat("combat1"), self.mock_combat1)

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_handle_combat_event_ended(self, mock_event_dispatcher): pass
        """Test handling combat.ended event"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        manager.add_combat("combat1", self.mock_combat1)
        
        # Create a combat.ended event
        event = CombatEvent(
            combat_id="combat1",
            event_subtype="ended",
            entities_involved=[],
            metadata={"combat_id": "combat1"}
        )
        
        # Handle the event (should log but not remove combat immediately)
        manager._handle_combat_event(event)
        
        # Combat should still exist (not removed immediately)
        self.assertEqual(manager.get_combat("combat1"), self.mock_combat1)

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_handle_combat_event_deleted(self, mock_event_dispatcher): pass
        """Test handling combat.deleted event"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        manager.add_combat("combat1", self.mock_combat1)
        
        # Create a combat.deleted event
        event = CombatEvent(
            combat_id="combat1",
            event_subtype="deleted",
            entities_involved=[],
            metadata={"combat_id": "combat1"}
        )
        
        # Handle the event (should log but not remove combat immediately)
        manager._handle_combat_event(event)
        
        # Combat should still exist (not removed immediately)
        self.assertEqual(manager.get_combat("combat1"), self.mock_combat1)

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_handle_combat_event_unknown(self, mock_event_dispatcher): pass
        """Test handling unknown combat event"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        manager = CombatStateManager.get_instance()
        
        # Create an unknown event
        event = CombatEvent(
            combat_id="combat1",
            event_subtype="unknown",
            entities_involved=[],
            metadata={"combat_id": "combat1"}
        )
        
        # Handle the event (should do nothing)
        manager._handle_combat_event(event)
        
        # Should not cause any errors


class TestModuleGlobals(unittest.TestCase): pass
    """Test module-level globals and backwards compatibility"""

    def test_combat_state_manager_global(self): pass
        """Test that the global combat_state_manager is available"""
        from backend.systems.combat.combat_ram import combat_state_manager
        
        self.assertIsInstance(combat_state_manager, CombatStateManager)

    def test_active_battles_backwards_compatibility(self): pass
        """Test that ACTIVE_BATTLES provides backwards compatibility"""
        from backend.systems.combat.combat_ram import ACTIVE_BATTLES, combat_state_manager
        
        # ACTIVE_BATTLES should reference the manager's internal dict
        self.assertIs(ACTIVE_BATTLES, combat_state_manager._active_battles)

    @patch('backend.systems.combat.combat_ram.EventDispatcher')
    def test_active_battles_integration(self, mock_event_dispatcher): pass
        """Test that ACTIVE_BATTLES works with the manager"""
        mock_dispatcher = Mock()
        mock_event_dispatcher.get_instance.return_value = mock_dispatcher
        
        # Reset singleton for clean test
        if hasattr(CombatStateManager, '_instance'): pass
            CombatStateManager._instance = None
        
        # Import fresh instances
        from backend.systems.combat.combat_ram import ACTIVE_BATTLES, combat_state_manager
        
        mock_combat = Mock()
        
        # Add through manager
        combat_state_manager.add_combat("test", mock_combat)
        
        # Should be accessible through ACTIVE_BATTLES
        self.assertEqual(ACTIVE_BATTLES["test"], mock_combat)
        
        # Remove through manager
        combat_state_manager.remove_combat("test")
        
        # Should be gone from ACTIVE_BATTLES
        self.assertNotIn("test", ACTIVE_BATTLES)


if __name__ == '__main__': pass
    unittest.main()
