"""
Debug tests for the TurnQueue class to identify the persistent 'player_1' issue.
"""

import unittest
import sys
import gc
import weakref
import logging
from unittest.mock import MagicMock

from backend.systems.combat.turn_queue import TurnQueue

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestCharacter:
    """Simple character class for testing that avoids MagicMock comparison issues."""
    
    def __init__(self, char_id, dexterity, name):
        self.id = char_id
        self.dexterity = dexterity
        self.name = name
        self.attributes = {"DEX": dexterity}
    
    def calculate_initiative(self):
        return self.dexterity
    
    def __repr__(self):
        return f"TestCharacter(id={self.id}, dexterity={self.dexterity})"

class TestTurnQueueDebug(unittest.TestCase):
    """Test class for debugging TurnQueue state persistence issues."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear all instances first
        TurnQueue.clear_all_instances()
        
        # Create test characters using our custom class instead of MagicMock
        self.char1 = TestCharacter("test_char1", 10, "Test Character 1")
        self.char2 = TestCharacter("test_char2", 12, "Test Character 2")
        self.char3 = TestCharacter("test_char3", 15, "Test Character 3")
        
        # Create a new queue for each test
        self.queue = TurnQueue()
    
    def test_debug_player1_in_queue(self):
        """
        Test if 'player_1' string is in any TurnQueue instances.
        
        This is a debug test that inspects all TurnQueue instances
        to check if they contain 'player_1' string, which might
        cause test failures.
        """
        # First add our test characters
        self.queue.add_combatant(self.char1)
        self.queue.add_combatant(self.char2)
        self.queue.add_combatant(self.char3)
        
        # Dump current state
        combatants = [c for c in self.queue.queue]
        self.assertEqual(len(combatants), 3, "Should have 3 combatants in queue")
        self.assertIn(self.char1, combatants, "char1 should be in queue")
        self.assertIn(self.char2, combatants, "char2 should be in queue")
        self.assertIn(self.char3, combatants, "char3 should be in queue")
        
        # Direct check for 'player_1' string in various containers
        for instance in TurnQueue._instances:
            for attr_name in dir(instance):
                if attr_name.startswith('_') and not attr_name.startswith('__'):
                    attr = getattr(instance, attr_name, None)
                    
                    # Check lists for 'player_1'
                    if isinstance(attr, list):
                        for item in attr:
                            if isinstance(item, str) and 'player_1' in item:
                                self.fail(f"Found 'player_1' in {attr_name} list: {attr}")
                    
                    # Check dictionaries for 'player_1' in keys
                    if isinstance(attr, dict):
                        for key in attr.keys():
                            if isinstance(key, str) and 'player_1' in key:
                                self.fail(f"Found 'player_1' in {attr_name} dict keys: {attr.keys()}")
    
    def test_create_and_clear_multiple_queues(self):
        """
        Test creating multiple queues and clearing them.
        
        This checks if clearing multiple queues properly removes all references
        to combat entities.
        """
        # Create 3 queues with different combatants
        queue1 = TurnQueue()
        queue1.add_combatant(self.char1)
        
        queue2 = TurnQueue()
        queue2.add_combatant(self.char2)
        
        queue3 = TurnQueue()
        queue3.add_combatant(self.char3)
        
        # Verify each queue has the right combatant
        self.assertEqual(len(queue1.queue), 1)
        self.assertEqual(queue1.queue[0], self.char1)
        
        self.assertEqual(len(queue2.queue), 1)
        self.assertEqual(queue2.queue[0], self.char2)
        
        self.assertEqual(len(queue3.queue), 1)
        self.assertEqual(queue3.queue[0], self.char3)
        
        # Now clear all instances
        instance_count = len(TurnQueue._instances)
        TurnQueue.clear_all_instances()
        
        # Check that all queues are now empty
        self.assertEqual(len(queue1.queue), 0, "queue1 should be empty after clear")
        self.assertEqual(len(queue2.queue), 0, "queue2 should be empty after clear")
        self.assertEqual(len(queue3.queue), 0, "queue3 should be empty after clear")

        # Check current_combatant is None for all queues
        self.assertIsNone(queue1.current_combatant, "queue1 current_combatant should be None")
        self.assertIsNone(queue2.current_combatant, "queue2 current_combatant should be None")
        self.assertIsNone(queue3.current_combatant, "queue3 current_combatant should be None")

    def test_add_player1_string_directly(self):
        """
        Test adding 'player_1' string directly to queue and then clearing it.
        
        This checks if our clearing mechanism properly handles string IDs.
        """
        # Add a string ID directly to test cleaning
        self.queue._queue.append('player_1')
        self.queue._initiative_order['player_1'] = 20
        
        # Verify it's there
        self.assertIn('player_1', self.queue.queue)
        self.assertIn('player_1', self.queue._initiative_order)
        
        # Clear all instances
        TurnQueue.clear_all_instances()
        
        # Verify it's gone
        self.assertNotIn('player_1', self.queue.queue, "player_1 should be removed from queue")
        self.assertNotIn('player_1', self.queue._initiative_order, "player_1 should be removed from initiative_order")

    def test_multiple_test_modules_clearing(self):
        """Test that clearing works properly when called from different test modules."""
        # Simulate player_1 being added from a different module
        test_module_name = 'backend.tests.backend.systems.combat.tests.test_combat_state_management'
        if test_module_name not in sys.modules:
            # Create a mock module if not already present
            module = type('MockModule', (), {})
            sys.modules[test_module_name] = module
        
        # Add 'player_1' to queue
        self.queue._queue.append('player_1')
        self.queue._initiative_order['player_1'] = 20
        
        # Call the clear method
        TurnQueue.clear_all_instances()
        
        # Check that player_1 is gone
        self.assertNotIn('player_1', self.queue.queue)
        self.assertNotIn('player_1', self.queue._initiative_order)


if __name__ == '__main__':
    unittest.main() 