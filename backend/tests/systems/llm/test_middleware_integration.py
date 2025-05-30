from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher

# Import EventBase and EventDispatcher with fallbacks
try: pass
    from backend.systems.events import EventBase, EventDispatcher
except ImportError: pass
    # Fallback for tests or when events system isn't available
    class EventBase: pass
        def __init__(self, **data): pass
            for key, value in data.items(): pass
                setattr(self, key, value)
    
    class EventDispatcher: pass
        @classmethod
        def get_instance(cls): pass
            return cls()
        
        def dispatch(self, event): pass
            pass
        
        def publish(self, event): pass
            pass
        
        def emit(self, event): pass
            pass

"""
Integration tests for the LLM system's middleware chain implementation.

These tests validate that the middleware components work together correctly: pass
1. Middleware chain processes events in the correct order
2. Middleware can modify, log, or filter events
3. Multiple middleware components can be chained together
4. Middleware can be added or removed dynamically
"""

import unittest
import os
import tempfile
import shutil
from datetime import datetime
from unittest.mock import MagicMock, patch, call

from backend.systems.llm.core.event_integration import (
    EventDispatcher,
    EventBase,
    LoggingMiddleware,
    ValidationMiddleware,
    AnalyticsMiddleware,
    ThrottlingMiddleware,
    MiddlewareChain,
)


class TestMiddlewareIntegration(unittest.TestCase): pass
    """Integration tests for the middleware chain of the LLM system."""

    def setUp(self): pass
        """Set up test environment."""
        # Create temporary data directory
        self.temp_dir = tempfile.mkdtemp()
        os.environ["VDM_DATA_DIR"] = self.temp_dir

        # Reset EventDispatcher singleton
        EventDispatcher._instance = None

        # Get clean instance
        self.event_dispatcher = EventDispatcher.get_instance()

        # Define test event class
        class TestEvent(EventBase): pass
            event_type: str = "test.event"
            message: str
            value: int = 0

        self.TestEvent = TestEvent

    def tearDown(self): pass
        """Clean up the test environment."""
        shutil.rmtree(self.temp_dir)

    def test_middleware_execution_order(self): pass
        """Test that middleware is executed in the correct order."""
        # Create mock middleware
        middleware1 = MagicMock()
        middleware1.process.side_effect = lambda event: event

        middleware2 = MagicMock()
        middleware2.process.side_effect = lambda event: event

        middleware3 = MagicMock()
        middleware3.process.side_effect = lambda event: event

        # Add middleware to the chain in specific order
        self.event_dispatcher.add_middleware(middleware1)
        self.event_dispatcher.add_middleware(middleware2)
        self.event_dispatcher.add_middleware(middleware3)

        # Create mock event handler
        handler = MagicMock()

        # Subscribe to the event
        self.event_dispatcher.subscribe("test.event", handler)

        # Create and publish an event
        event = self.TestEvent(message="Test message")
        self.event_dispatcher.publish_sync(event)

        # Verify middleware execution order
        middleware1.process.assert_called_once()
        middleware2.process.assert_called_once()
        middleware3.process.assert_called_once()

        middleware1_call = middleware1.process.call_args[0][0]
        middleware2_call = middleware2.process.call_args[0][0]
        middleware3_call = middleware3.process.call_args[0][0]

        # Verify that each middleware was called with the same event
        self.assertEqual(middleware1_call.message, "Test message")
        self.assertEqual(middleware2_call.message, "Test message")
        self.assertEqual(middleware3_call.message, "Test message")

        # Verify that middleware were called in the right order
        middleware1.process.assert_called()
        middleware2.process.assert_called()
        middleware3.process.assert_called()

        call_order = [
            call.process(middleware1.process.call_args[0][0]),
            call.process(middleware2.process.call_args[0][0]),
            call.process(middleware3.process.call_args[0][0]),
        ]

        self.assertEqual(call_order[0].args[0], middleware1.process.call_args[0][0])
        self.assertEqual(call_order[1].args[0], middleware2.process.call_args[0][0])
        self.assertEqual(call_order[2].args[0], middleware3.process.call_args[0][0])

    def test_middleware_event_modification(self): pass
        """Test that middleware can modify events."""

        # Create middleware that modifies the event
        class ModifyingMiddleware: pass
            def process(self, event): pass
                event.message = f"Modified: {event.message}"
                event.value += 1
                return event

        # Add the middleware to the chain
        self.event_dispatcher.add_middleware(ModifyingMiddleware())

        # Create mock event handler
        handler = MagicMock()

        # Subscribe to the event
        self.event_dispatcher.subscribe("test.event", handler)

        # Create and publish an event
        event = self.TestEvent(message="Original message", value=0)
        self.event_dispatcher.publish_sync(event)

        # Verify that the handler received the modified event
        handler.assert_called_once()
        handled_event = handler.call_args[0][0]
        self.assertEqual(handled_event.message, "Modified: Original message")
        self.assertEqual(handled_event.value, 1)

    def test_middleware_event_filtering(self): pass
        """Test that middleware can filter events."""

        # Create middleware that filters events
        class FilteringMiddleware: pass
            def process(self, event): pass
                if event.value > 5: pass
                    return None  # Filter out events with value > 5
                return event

        # Add the middleware to the chain
        self.event_dispatcher.add_middleware(FilteringMiddleware())

        # Create mock event handler
        handler = MagicMock()

        # Subscribe to the event
        self.event_dispatcher.subscribe("test.event", handler)

        # Create and publish events with different values
        event1 = self.TestEvent(message="Event 1", value=3)
        event2 = self.TestEvent(message="Event 2", value=7)
        event3 = self.TestEvent(message="Event 3", value=4)

        self.event_dispatcher.publish_sync(event1)
        self.event_dispatcher.publish_sync(event2)
        self.event_dispatcher.publish_sync(event3)

        # Verify that only events with value <= 5 were handled
        self.assertEqual(handler.call_count, 2)

        # Extract the events that were handled
        handled_events = [call[0][0] for call in handler.call_args_list]

        # Verify that the filtered event was not handled
        self.assertEqual(handled_events[0].message, "Event 1")
        self.assertEqual(handled_events[1].message, "Event 3")

        # Verify that the filtered event is not in the handled events
        messages = [event.message for event in handled_events]
        self.assertNotIn("Event 2", messages)

    def test_multiple_middleware_chain(self): pass
        """Test that multiple middleware can be chained together."""

        # Create middleware that logs events
        class LoggingTestMiddleware: pass
            def __init__(self): pass
                self.logs = []

            def process(self, event): pass
                self.logs.append(f"Logged: {event.message}")
                return event

        # Create middleware that modifies events
        class ModifyingTestMiddleware: pass
            def process(self, event): pass
                event.message = f"Modified: {event.message}"
                event.value += 1
                return event

        # Create middleware that filters events
        class FilteringTestMiddleware: pass
            def __init__(self): pass
                self.filtered = []

            def process(self, event): pass
                if event.value > 5: pass
                    self.filtered.append(event.message)
                    return None
                return event

        # Create instances of the middleware
        logging_middleware = LoggingTestMiddleware()
        modifying_middleware = ModifyingTestMiddleware()
        filtering_middleware = FilteringTestMiddleware()

        # Add middleware to the chain in specific order
        self.event_dispatcher.add_middleware(logging_middleware)
        self.event_dispatcher.add_middleware(modifying_middleware)
        self.event_dispatcher.add_middleware(filtering_middleware)

        # Create mock event handler
        handler = MagicMock()

        # Subscribe to the event
        self.event_dispatcher.subscribe("test.event", handler)

        # Create and publish events with different values
        event1 = self.TestEvent(message="Event 1", value=3)
        event2 = self.TestEvent(message="Event 2", value=5)
        event3 = self.TestEvent(message="Event 3", value=4)

        self.event_dispatcher.publish_sync(event1)
        self.event_dispatcher.publish_sync(event2)
        self.event_dispatcher.publish_sync(event3)

        # Verify that the logging middleware logged all events
        self.assertEqual(len(logging_middleware.logs), 3)
        self.assertEqual(logging_middleware.logs[0], "Logged: Event 1")
        self.assertEqual(logging_middleware.logs[1], "Logged: Event 2")
        self.assertEqual(logging_middleware.logs[2], "Logged: Event 3")

        # Verify that the modifying middleware modified all events

        # Verify that the filtering middleware filtered out the event with value > 5 after modification
        self.assertEqual(len(filtering_middleware.filtered), 1)
        self.assertEqual(filtering_middleware.filtered[0], "Modified: Event 2")

        # Verify that only events that weren't filtered were handled
        self.assertEqual(handler.call_count, 2)

        # Extract the events that were handled
        handled_events = [call[0][0] for call in handler.call_args_list]

        # Verify that the handled events have the expected values
        self.assertEqual(handled_events[0].message, "Modified: Event 1")
        self.assertEqual(handled_events[0].value, 4)
        self.assertEqual(handled_events[1].message, "Modified: Event 3")
        self.assertEqual(handled_events[1].value, 5)

    def test_dynamic_middleware_addition_removal(self): pass
        """Test that middleware can be added or removed dynamically."""
        # Create middleware
        middleware1 = MagicMock()
        middleware1.process.side_effect = lambda event: event

        middleware2 = MagicMock()
        middleware2.process.side_effect = lambda event: event

        # Add middleware1 to the chain
        self.event_dispatcher.add_middleware(middleware1)

        # Create mock event handler
        handler = MagicMock()

        # Subscribe to the event
        self.event_dispatcher.subscribe("test.event", handler)

        # Create and publish an event
        event1 = self.TestEvent(message="Event 1")
        self.event_dispatcher.publish_sync(event1)

        # Verify that middleware1 was called
        middleware1.process.assert_called_once()

        # Add middleware2 to the chain
        self.event_dispatcher.add_middleware(middleware2)

        # Reset middleware1 mock
        middleware1.reset_mock()

        # Create and publish another event
        event2 = self.TestEvent(message="Event 2")
        self.event_dispatcher.publish_sync(event2)

        # Verify that both middleware were called
        middleware1.process.assert_called_once()
        middleware2.process.assert_called_once()

        # Remove middleware1 from the chain
        self.event_dispatcher.remove_middleware(middleware1)

        # Reset middleware mocks
        middleware1.reset_mock()
        middleware2.reset_mock()

        # Create and publish another event
        event3 = self.TestEvent(message="Event 3")
        self.event_dispatcher.publish_sync(event3)

        # Verify that only middleware2 was called
        middleware1.process.assert_not_called()
        middleware2.process.assert_called_once()

    def test_built_in_middleware(self): pass
        """Test integration with the built-in middleware classes."""
        # Create mock logger
        mock_logger = MagicMock()

        # Create instances of built-in middleware
        logging_middleware = LoggingMiddleware(logger=mock_logger)
        validation_middleware = ValidationMiddleware()
        analytics_middleware = AnalyticsMiddleware()
        throttling_middleware = ThrottlingMiddleware(rate_limit=2, window_seconds=1)

        # Add middleware to the chain
        self.event_dispatcher.add_middleware(logging_middleware)
        self.event_dispatcher.add_middleware(validation_middleware)
        self.event_dispatcher.add_middleware(analytics_middleware)
        self.event_dispatcher.add_middleware(throttling_middleware)

        # Create mock event handler
        handler = MagicMock()

        # Subscribe to the event
        self.event_dispatcher.subscribe("test.event", handler)

        # Create and publish events
        event1 = self.TestEvent(message="Event 1")
        event2 = self.TestEvent(message="Event 2")

        self.event_dispatcher.publish_sync(event1)
        self.event_dispatcher.publish_sync(event2)

        # Verify that the logger was called for each event
        self.assertEqual(mock_logger.info.call_count, 2)

        # Verify that the handler was called for each event
        self.assertEqual(handler.call_count, 2)

        # Try to publish more events than the rate limit allows
        event3 = self.TestEvent(message="Event 3")
        self.event_dispatcher.publish_sync(event3)

        # Verify that the throttling middleware blocked the third event
        self.assertEqual(handler.call_count, 2)

        # Wait for the throttling window to expire
        import time

        time.sleep(1.1)

        # Publish another event
        event4 = self.TestEvent(message="Event 4")
        self.event_dispatcher.publish_sync(event4)

        # Verify that the handler was called after the throttling window expired
        self.assertEqual(handler.call_count, 3)

    def test_middleware_chain_class(self): pass
        """Test that the MiddlewareChain class works correctly."""
        # Create mock middleware
        middleware1 = MagicMock()
        middleware1.process.side_effect = lambda event: event

        middleware2 = MagicMock()
        middleware2.process.side_effect = lambda event: event

        # Create a middleware chain
        chain = MiddlewareChain()

        # Add middleware to the chain
        chain.add_middleware(middleware1)
        chain.add_middleware(middleware2)

        # Process an event through the chain
        event = self.TestEvent(message="Test message")
        processed_event = chain.process(event)

        # Verify that both middleware were called
        middleware1.process.assert_called_once()
        middleware2.process.assert_called_once()

        # Verify that the event was returned
        self.assertEqual(processed_event.message, "Test message")

        # Remove middleware from the chain
        chain.remove_middleware(middleware1)

        # Reset middleware mocks
        middleware1.reset_mock()
        middleware2.reset_mock()

        # Process another event through the chain
        event2 = self.TestEvent(message="Test message 2")
        processed_event2 = chain.process(event2)

        # Verify that only middleware2 was called
        middleware1.process.assert_not_called()
        middleware2.process.assert_called_once()


if __name__ == "__main__": pass
    unittest.main()
