"""
Tests for the EventBus implementation.
"""

import asyncio
import unittest
from unittest.mock import Mock, patch
from pydantic import BaseModel

from backend.core.events.event_bus import EventBus, EventPriority, event_bus

class TestEvent(BaseModel):
    """Test event class for type checking."""
    name: str
    value: int

class TestEventBus(unittest.TestCase):
    """Test cases for the EventBus implementation."""
    
    def setUp(self):
        """Set up test cases."""
        # Create a fresh EventBus for each test
        self.event_bus = EventBus()
        
    def test_subscribe_and_emit(self):
        """Test basic subscribe and emit functionality."""
        # Create a mock handler
        handler = Mock()
        
        # Subscribe to an event
        self.event_bus.subscribe("test_event", handler)
        
        # Emit the event
        test_payload = {"test": "data"}
        self.event_bus.emit("test_event", test_payload)
        
        # Verify handler was called with correct payload
        handler.assert_called_once_with(test_payload)
        
    def test_unsubscribe(self):
        """Test unsubscribing from events."""
        # Create a mock handler
        handler = Mock()
        
        # Subscribe and then unsubscribe
        self.event_bus.subscribe("test_event", handler)
        result = self.event_bus.unsubscribe("test_event", handler)
        
        # Verify unsubscribe returned True (successful)
        self.assertTrue(result)
        
        # Emit an event and verify handler was not called
        self.event_bus.emit("test_event", {"test": "data"})
        handler.assert_not_called()
        
    def test_multiple_handlers(self):
        """Test multiple handlers for the same event."""
        # Create mock handlers
        handler1 = Mock()
        handler2 = Mock()
        
        # Subscribe both handlers
        self.event_bus.subscribe("multi_event", handler1)
        self.event_bus.subscribe("multi_event", handler2)
        
        # Emit the event
        test_payload = {"multi": "data"}
        self.event_bus.emit("multi_event", test_payload)
        
        # Verify both handlers were called
        handler1.assert_called_once_with(test_payload)
        handler2.assert_called_once_with(test_payload)
        
    def test_error_handling(self):
        """Test that errors in handlers are caught and don't affect other handlers."""
        # Create a handler that raises an exception
        error_handler = Mock(side_effect=Exception("Test exception"))
        normal_handler = Mock()
        
        # Subscribe both handlers
        self.event_bus.subscribe("error_event", error_handler)
        self.event_bus.subscribe("error_event", normal_handler)
        
        # Emit the event - this should not raise an exception
        test_payload = {"error": "test"}
        self.event_bus.emit("error_event", test_payload)
        
        # Verify both handlers were called
        error_handler.assert_called_once_with(test_payload)
        normal_handler.assert_called_once_with(test_payload)
        
    def test_handler_priority(self):
        """Test that handlers are called in priority order."""
        # Create a list to track execution order
        execution_order = []
        
        # Create handlers with different priorities
        def high_priority_handler(payload):
            execution_order.append("high")
            
        def normal_priority_handler(payload):
            execution_order.append("normal")
            
        def low_priority_handler(payload):
            execution_order.append("low")
            
        # Subscribe handlers with different priorities
        self.event_bus.subscribe("priority_event", low_priority_handler, EventPriority.LOW)
        self.event_bus.subscribe("priority_event", normal_priority_handler, EventPriority.NORMAL)
        self.event_bus.subscribe("priority_event", high_priority_handler, EventPriority.HIGH)
        
        # Emit the event
        self.event_bus.emit("priority_event", {})
        
        # Verify execution order
        self.assertEqual(execution_order, ["high", "normal", "low"])
        
    def test_event_filtering(self):
        """Test event filtering functionality."""
        # Create a mock handler
        handler = Mock()
        
        # Create a filter function
        def filter_func(event):
            return event.get("pass_filter", False)
            
        # Subscribe with filter
        self.event_bus.subscribe("filter_event", handler, filter_func=filter_func)
        
        # Emit events - one that passes the filter, one that doesn't
        self.event_bus.emit("filter_event", {"pass_filter": True, "data": "pass"})
        self.event_bus.emit("filter_event", {"pass_filter": False, "data": "fail"})
        
        # Verify handler was only called for the event that passed the filter
        self.assertEqual(handler.call_count, 1)
        handler.assert_called_once_with({"pass_filter": True, "data": "pass"})
        
    def test_typed_events(self):
        """Test using typed events with Pydantic models."""
        # Create a mock handler
        handler = Mock()
        
        # Subscribe to event with specific type
        self.event_bus.subscribe(TestEvent, handler)
        
        # Create a test event
        test_event = TestEvent(name="test", value=42)
        
        # Emit the event
        self.event_bus.emit(TestEvent, test_event)
        
        # Verify handler was called with correct payload
        handler.assert_called_once_with(test_event)
        
    async def async_test_async_handlers(self):
        """Test async event handlers."""
        # Create a mock for tracking async calls
        result_tracker = {"called": False}
        
        # Create an async handler
        async def async_handler(payload):
            await asyncio.sleep(0.1)  # Simulate async work
            result_tracker["called"] = True
            result_tracker["payload"] = payload
            
        # Subscribe async handler
        self.event_bus.subscribe_async("async_event", async_handler)
        
        # Emit and wait for async processing
        await self.event_bus.emit_async("async_event", {"async": "data"})
        
        # Verify handler was called with correct payload
        self.assertTrue(result_tracker["called"])
        self.assertEqual(result_tracker["payload"], {"async": "data"})
        
    def test_async_handlers(self):
        """Run the async test using an event loop."""
        asyncio.run(self.async_test_async_handlers())
        
    def test_singleton_instance(self):
        """Test that the singleton instance works correctly."""
        # Get the singleton instance and verify it's the same instance
        instance1 = EventBus.get_instance()
        instance2 = EventBus.get_instance()
        
        self.assertIs(instance1, instance2)
        self.assertIs(event_bus, instance1)
        
        # Test with the singleton instance
        handler = Mock()
        event_bus.subscribe("singleton_test", handler)
        event_bus.emit("singleton_test", {"singleton": True})
        
        handler.assert_called_once_with({"singleton": True})
        
if __name__ == "__main__":
    unittest.main() 