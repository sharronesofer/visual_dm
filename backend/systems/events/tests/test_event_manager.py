"""
Tests for the EventManager utility class.

This module contains tests for the EventManager utility, which provides
a convenient interface for working with the event system.
"""
import pytest
import asyncio
from typing import List, Dict, Any

from backend.systems.events.core.event_base import EventBase
from backend.systems.events.utils.event_utils import EventManager

# Test event class
class TestEvent(EventBase):
    """Test event for unit testing."""
    event_type: str
    data: str

@pytest.fixture
def event_manager():
    """
    Fixture that provides a fresh EventManager instance for each test.
    """
    manager = EventManager()
    yield manager
    manager.cleanup()  # Clean up subscriptions after each test

def test_subscribe_and_publish(event_manager):
    """Test basic subscription and publication using EventManager."""
    # Track received events
    received_events = []
    
    # Define a handler
    def test_handler(event: TestEvent) -> None:
        received_events.append(event)
    
    # Subscribe to events
    event_manager.subscribe(TestEvent, test_handler)
    
    # Publish an event
    event = TestEvent(event_type="test:event", data="test_data")
    event_manager.publish(event)
    
    # Verify handler was called
    assert len(received_events) == 1
    assert received_events[0].data == "test_data"

def test_event_type_filtering(event_manager):
    """Test filtering events based on event_type."""
    # Track received events
    received_events = []
    
    # Define a handler that filters on event_type
    def test_handler(event: TestEvent) -> None:
        # Only handle specific event types
        if event.event_type == "test:specific":
            received_events.append(event)
    
    # Subscribe to TestEvent
    event_manager.subscribe(TestEvent, test_handler)
    
    # Publish events with different types
    event1 = TestEvent(event_type="test:specific", data="matching")
    event2 = TestEvent(event_type="test:other", data="non-matching")
    
    event_manager.publish(event1)
    event_manager.publish(event2)
    
    # Verify only matching event triggered handler
    assert len(received_events) == 1
    assert received_events[0].data == "matching"

def test_unsubscribe(event_manager):
    """Test unsubscribing from events with EventManager."""
    # Track handler calls
    call_count = 0
    
    # Define a handler
    def test_handler(event: TestEvent) -> None:
        nonlocal call_count
        call_count += 1
    
    # Subscribe
    event_manager.subscribe(TestEvent, test_handler)
    
    # Publish an event
    event = TestEvent(event_type="test:event", data="test_data")
    event_manager.publish(event)
    assert call_count == 1
    
    # Unsubscribe
    event_manager.unsubscribe(TestEvent, test_handler)
    
    # Publish again - should not increase call count
    event_manager.publish(event)
    assert call_count == 1

@pytest.mark.asyncio
async def test_async_publish(event_manager):
    """Test asynchronous event publishing with EventManager."""
    # Track received events
    received_events = []
    
    # Define an async handler
    async def async_handler(event: TestEvent) -> str:
        received_events.append(event)
        # Simulate async work
        await asyncio.sleep(0.01)
        return f"Processed {event.data}"
    
    # Subscribe
    event_manager.subscribe(TestEvent, async_handler)
    
    # Publish asynchronously
    event = TestEvent(event_type="test:async", data="async_data")
    results = await event_manager.publish_async(event)
    
    # Verify handler was called
    assert len(received_events) == 1
    assert received_events[0].data == "async_data"
    
    # Verify result was returned
    assert len(results) == 1
    assert results[0] == "Processed async_data"

def test_priority_subscription(event_manager):
    """Test that handlers with higher priority are called first."""
    # Track execution order
    execution_order = []
    
    # Define handlers with different priorities
    def low_priority_handler(event: TestEvent) -> None:
        execution_order.append("low")
    
    def high_priority_handler(event: TestEvent) -> None:
        execution_order.append("high")
    
    # Subscribe with different priorities
    event_manager.subscribe(TestEvent, low_priority_handler, priority=0)
    event_manager.subscribe(TestEvent, high_priority_handler, priority=10)
    
    # Publish an event
    event = TestEvent(event_type="test:priority", data="priority_test")
    event_manager.publish(event)
    
    # Verify execution order
    assert execution_order == ["high", "low"]

def test_cleanup(event_manager):
    """Test cleanup method unsubscribes all handlers."""
    # Track handler calls
    call_count = 0
    
    # Define a handler
    def test_handler(event: TestEvent) -> None:
        nonlocal call_count
        call_count += 1
    
    # Subscribe
    event_manager.subscribe(TestEvent, test_handler)
    
    # Verify handler works
    event = TestEvent(event_type="test:event", data="test_data")
    event_manager.publish(event)
    assert call_count == 1
    
    # Clean up
    event_manager.cleanup()
    
    # Verify handler no longer called
    event_manager.publish(event)
    assert call_count == 1  # Count should not increase

def test_batch_operations(event_manager):
    """Test batch subscription and publishing."""
    # Track event counts by type
    event_counts = {"type1": 0, "type2": 0, "type3": 0}
    
    # Define handlers
    def handler1(event: TestEvent) -> None:
        event_counts["type1"] += 1
    
    def handler2(event: TestEvent) -> None:
        event_counts["type2"] += 1
    
    def handler3(event: TestEvent) -> None:
        event_counts["type3"] += 1
    
    # Subscribe multiple handlers
    event_manager.subscribe_batch([
        (TestEvent, handler1, {"event_type": "test:type1"}),
        (TestEvent, handler2, {"event_type": "test:type2"}),
        (TestEvent, handler3, {"event_type": "test:type3"})
    ])
    
    # Publish multiple events
    events = [
        TestEvent(event_type="test:type1", data="data1"),
        TestEvent(event_type="test:type2", data="data2"),
        TestEvent(event_type="test:type3", data="data3"),
        TestEvent(event_type="test:type1", data="data1-2"),
    ]
    
    event_manager.publish_batch(events)
    
    # Verify correct counts
    assert event_counts["type1"] == 2
    assert event_counts["type2"] == 1
    assert event_counts["type3"] == 1

def test_multiple_managers():
    """Test that multiple managers can coexist."""
    # Create two managers
    manager1 = EventManager()
    manager2 = EventManager()
    
    # Set up test data
    manager1_received = False
    manager2_received = False
    
    def handler1(event):
        nonlocal manager1_received
        manager1_received = True
    
    def handler2(event):
        nonlocal manager2_received
        manager2_received = True
    
    # Subscribe each handler to its manager
    manager1.subscribe(TestEvent, handler1)
    manager2.subscribe(TestEvent, handler2)
    
    # Create and publish an event through manager1
    event = TestEvent(event_type="test.event", data="test_data")
    manager1.publish(event)
    
    # Verify both handlers were called (since they use the same dispatcher)
    assert manager1_received
    assert manager2_received
    
    # Clean up
    manager1.cleanup()
    manager2.cleanup()

def test_subscription_tracking(event_manager):
    """Test that subscriptions are properly tracked for cleanup."""
    # Set up test data
    handler1_called = False
    handler2_called = False
    
    def handler1(event):
        nonlocal handler1_called
        handler1_called = True
    
    def handler2(event):
        nonlocal handler2_called
        handler2_called = True
    
    # Subscribe handlers
    event_manager.subscribe(TestEvent, handler1)
    event_manager.subscribe(TestEvent, handler2)
    
    # Check internal tracking
    assert TestEvent in event_manager._subscriptions
    assert len(event_manager._subscriptions[TestEvent]) == 2
    
    # Unsubscribe one handler
    event_manager.unsubscribe(TestEvent, handler1)
    
    # Check internal tracking updated
    assert len(event_manager._subscriptions[TestEvent]) == 1
    
    # Create and publish an event
    event = TestEvent(event_type="test.event", data="test_data")
    event_manager.publish(event)
    
    # Verify only handler2 was called
    assert not handler1_called
    assert handler2_called 