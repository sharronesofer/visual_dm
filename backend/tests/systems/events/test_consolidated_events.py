from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from typing import Type
"""
Tests for the consolidated event system.

This test suite verifies that the event system consolidation was successful
and that both old and new import paths work correctly.
"""

import unittest
from unittest.mock import MagicMock, patch
import warnings

class TestConsolidatedEvents(unittest.TestCase): pass
    """Test cases for the consolidated event system."""
    
    def setUp(self): pass
        # Clear any prior warning filters
        warnings.resetwarnings()
        
        # Store any captured warnings
        self.captured_warnings = []
        
        # Setup warning capture
        warnings.simplefilter("always")
        self._original_showwarning = warnings.showwarning
        warnings.showwarning = self._collect_warning
    
    def tearDown(self): pass
        # Restore original warning behavior
        warnings.showwarning = self._original_showwarning
    
    def _collect_warning(self, message, category, filename, lineno, file=None, line=None): pass
        """Collect warnings for inspection."""
        self.captured_warnings.append((message, category))
    
    def test_old_event_import_path_works_with_warning(self): pass
        """Test that the old import path works but shows a deprecation warning."""
        with patch.dict('sys.modules', {'backend.systems.events': MagicMock()}): pass
            # This should trigger a deprecation warning
            import backend.systems.event
            
            # Verify a deprecation warning was issued
            self.assertTrue(any(issubclass(cat, DeprecationWarning) for _, cat in self.captured_warnings))
            self.assertTrue(any('deprecated' in str(msg).lower() for msg, _ in self.captured_warnings))
    
    def test_new_imports(self): pass
        """Test that the new import paths work correctly."""
        # Direct imports from the events package
        from backend.systems.events import EventBase, EventDispatcher, get_dispatcher
        from backend.systems.events import MemoryCreated, RumorCreated
        
        # Test event creation
        memory_event = MemoryCreated(
            entity_id="character-123",
            memory_id="memory-456",
            memory_type="observation",
            content={"text": "Test memory"},
            importance=0.8
        )
        
        # Verify the event was created correctly
        self.assertEqual(memory_event.entity_id, "character-123")
        self.assertEqual(memory_event.memory_id, "memory-456")
        self.assertEqual(memory_event.memory_type, "observation")
        self.assertEqual(memory_event.importance, 0.8)
        
        # Check dispatcher singleton
        dispatcher1 = get_dispatcher()
        dispatcher2 = EventDispatcher.get_instance()
        self.assertIs(dispatcher1, dispatcher2, "Both dispatcher references should point to the same instance")
    
    def test_legacy_event_types(self): pass
        """Test that the legacy event types still work."""
        from backend.systems.events import MemoryEvent, MemoryEventType
        
        # Create a memory event using the legacy class
        event = MemoryEvent(
            memory_type=MemoryEventType.CREATED,
            entity_id="character-123",
            memory_id="memory-456",
            content={"text": "Test memory"}
        )
        
        # Verify the event was created correctly
        self.assertEqual(event.entity_id, "character-123")
        self.assertEqual(event.memory_id, "memory-456")
        self.assertEqual(event.memory_type, MemoryEventType.CREATED)
    
    def test_subscribe_and_publish(self): pass
        """Test that subscribing to and publishing events works correctly."""
        from backend.systems.events import EventDispatcher, MemoryCreated, get_dispatcher
        
        # Get the singleton dispatcher
        dispatcher = get_dispatcher()
        
        # Create a mock handler
        mock_handler = MagicMock()
        
        # Subscribe the handler to MemoryCreated events
        dispatcher.subscribe(MemoryCreated, mock_handler)
        
        # Create and publish an event
        event = MemoryCreated(
            entity_id="character-123",
            memory_id="memory-456",
            memory_type="observation",
            content={"text": "Test memory"},
            importance=0.8
        )
        dispatcher.publish(event)
        
        # Verify the handler was called with the event
        mock_handler.assert_called_once()
        args, _ = mock_handler.call_args
        received_event = args[0]
        self.assertIsInstance(received_event, MemoryCreated)
        self.assertEqual(received_event.entity_id, "character-123")
        self.assertEqual(received_event.memory_id, "memory-456")
        
        # Unsubscribe and verify handler doesn't get called again
        dispatcher.unsubscribe(MemoryCreated, mock_handler)
        mock_handler.reset_mock()
        dispatcher.publish(event)
        mock_handler.assert_not_called()
        
        # Cleanup: Remove all subscribers to avoid affecting other tests
        dispatcher._subscribers = {}

if __name__ == '__main__': pass
    unittest.main() 