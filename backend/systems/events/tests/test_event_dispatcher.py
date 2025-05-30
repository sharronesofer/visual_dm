"""
Tests for the EventDispatcher class.

This module contains tests for the core event dispatcher functionality,
including subscription, publication, and middleware handling.
"""
import pytest
import asyncio
from typing import List, Dict, Any

from backend.systems.events.core.event_base import EventBase
from backend.systems.events.core.event_dispatcher import EventDispatcher
from backend.systems.events.middleware.logging_middleware import logging_middleware

# Test event classes
class TestEvent(EventBase):
    """Test event for unit testing."""
    event_type: str
    data: str

class SpecialTestEvent(TestEvent):
    """Special test event for inheritance testing."""
    priority: int = 0

# Fixture to ensure each test has a clean dispatcher
@pytest.fixture
def event_dispatcher():
    """
    Fixture that provides a fresh EventDispatcher instance for each test.
    """
    # Reset the singleton before each test
    EventDispatcher._instance = None
    dispatcher = EventDispatcher.get_instance()
    yield dispatcher
    # No need to explicitly clean up subscriptions - they'll be reset on the next test
    # by resetting the singleton

def test_singleton_pattern():
    """Test that EventDispatcher follows the singleton pattern."""
    # Reset for this test
    EventDispatcher._instance = None
    
    # First instance
    dispatcher1 = EventDispatcher.get_instance()
    
    # Second instance should be the same object
    dispatcher2 = EventDispatcher.get_instance()
    
    assert dispatcher1 is dispatcher2
    assert id(dispatcher1) == id(dispatcher2)

def test_subscribe_and_publish_sync(event_dispatcher):
    """Test basic synchronous subscription and publication."""
    # Track received events
    received_events = []
    
    # Define a handler
    def test_handler(event: TestEvent) -> str:
        received_events.append(event)
        return f"Processed {event.data}"
    
    # Subscribe to events
    event_dispatcher.subscribe(TestEvent, test_handler)
    
    # Publish an event
    event = TestEvent(event_type="test:event", data="test_data")
    results = event_dispatcher.publish_sync(event)
    
    # Verify handler was called
    assert len(received_events) == 1
    assert received_events[0].data == "test_data"
    
    # Verify results were collected
    assert len(results) == 1
    assert results[0] == "Processed test_data"

def test_event_inheritance(event_dispatcher):
    """Test that handlers receive events of subclasses."""
    # Track received events
    received_events = []
    
    # Define a handler for the base class
    def base_handler(event: TestEvent) -> None:
        received_events.append(("base", event))
    
    # Define a handler for the specific class
    def specific_handler(event: SpecialTestEvent) -> None:
        received_events.append(("specific", event))
    
    # Subscribe both handlers
    event_dispatcher.subscribe(TestEvent, base_handler)
    event_dispatcher.subscribe(SpecialTestEvent, specific_handler)
    
    # Publish base event - should only trigger base handler
    base_event = TestEvent(event_type="test:event", data="base_data")
    event_dispatcher.publish_sync(base_event)
    
    # Publish special event - should trigger both handlers
    special_event = SpecialTestEvent(event_type="test:special", data="special_data", priority=1)
    event_dispatcher.publish_sync(special_event)
    
    # Verify handler calls - we need 3 calls total
    assert len(received_events) == 3
    
    # Verify base event was processed by base handler
    assert received_events[0] == ("base", base_event)
    
    # The order of handling special_event might vary based on implementation,
    # so we just check that both handlers were called with it
    special_handlers = [
        item for item in received_events 
        if item[1].event_type == "test:special"
    ]
    assert len(special_handlers) == 2
    
    # Make sure both specific and base handlers were called for the special event
    assert any(handler[0] == "base" for handler in special_handlers)
    assert any(handler[0] == "specific" for handler in special_handlers)

def test_unsubscribe(event_dispatcher):
    """Test unsubscribing from events."""
    # Track handler calls
    call_count = 0
    
    # Define a handler
    def test_handler(event: TestEvent) -> None:
        nonlocal call_count
        call_count += 1
    
    # Subscribe
    event_dispatcher.subscribe(TestEvent, test_handler)
    
    # Publish an event
    event = TestEvent(event_type="test:event", data="test_data")
    event_dispatcher.publish_sync(event)
    assert call_count == 1
    
    # Unsubscribe
    event_dispatcher.unsubscribe(TestEvent, test_handler)
    
    # Publish again - should not increase call count
    event_dispatcher.publish_sync(event)
    assert call_count == 1

def test_middleware(event_dispatcher):
    """Test middleware in the event pipeline."""
    # Track events
    received_events = []
    middleware_events = []
    
    # Define a handler
    def test_handler(event: TestEvent) -> None:
        received_events.append(event)
    
    # Define middleware
    def test_middleware(event: EventBase, next_middleware):
        middleware_events.append(event)
        # Modify event before passing it on
        if isinstance(event, TestEvent):
            event.data = f"Modified: {event.data}"
        return next_middleware(event)
    
    # Add middleware and subscribe
    event_dispatcher.add_middleware(test_middleware)
    event_dispatcher.subscribe(TestEvent, test_handler)
    
    # Publish an event
    event = TestEvent(event_type="test:event", data="original_data")
    event_dispatcher.publish_sync(event)
    
    # Verify middleware was called
    assert len(middleware_events) == 1
    assert middleware_events[0] is event
    
    # Verify handler received modified event
    assert len(received_events) == 1
    assert received_events[0].data == "Modified: original_data"

# Asynchronous tests
@pytest.mark.asyncio
async def test_async_publish(event_dispatcher):
    """Test asynchronous event publication and handling."""
    # Track received events
    received_events = []
    
    # Define an async handler
    async def async_handler(event: TestEvent) -> str:
        received_events.append(event)
        # Simulate async work
        await asyncio.sleep(0.01)
        return f"Processed {event.data} async"
    
    # Define a sync handler
    def sync_handler(event: TestEvent) -> str:
        received_events.append(event)
        return f"Processed {event.data} sync"
    
    # Subscribe both handlers
    event_dispatcher.subscribe(TestEvent, async_handler)
    event_dispatcher.subscribe(TestEvent, sync_handler)
    
    # Publish an event async
    event = TestEvent(event_type="test:async", data="async_data")
    results = await event_dispatcher.publish(event)
    
    # Verify both handlers were called
    assert len(received_events) == 2
    
    # Verify results were collected
    assert len(results) == 2
    assert "Processed async_data async" in results
    assert "Processed async_data sync" in results 