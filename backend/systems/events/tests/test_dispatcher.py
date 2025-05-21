"""
Tests for the EventDispatcher class.

This module contains unit tests for the EventDispatcher class,
verifying its subscription, publishing, and middleware functionality.
"""
import asyncio
import pytest
import time
from typing import List, Dict, Any

from ..base import EventBase
from ..dispatcher import EventDispatcher
from ..middleware.logging import logging_middleware
from ..middleware.error_handler import error_handling_middleware

# Test events
class TestEvent(EventBase):
    """Simple test event for unit testing."""
    event_type: str
    data: str = "test"

class DerivedTestEvent(TestEvent):
    """Derived test event for inheritance testing."""
    nested_data: str = "derived"

class SpecialTestEvent(EventBase):
    """Special test event for filtering tests."""
    event_type: str
    special: bool = True

# Test fixtures
@pytest.fixture
def dispatcher():
    """Create a fresh EventDispatcher for each test."""
    # Reset the singleton instance for each test
    EventDispatcher._instance = None
    return EventDispatcher.get_instance()

@pytest.fixture
def event():
    """Create a test event."""
    return TestEvent(event_type="test:basic")

@pytest.fixture
def derived_event():
    """Create a derived test event."""
    return DerivedTestEvent(event_type="test:derived", data="parent", nested_data="child")

@pytest.fixture
def special_event():
    """Create a special test event."""
    return SpecialTestEvent(event_type="test:special", special=True)

# Test synchronous event handling
def test_subscribe_and_publish_sync(dispatcher, event):
    """Test basic subscription and synchronous publishing."""
    # Setup
    received_events = []
    
    def handler(evt):
        received_events.append(evt)
        return "handled"
    
    # Subscribe
    dispatcher.subscribe(TestEvent, handler)
    
    # Publish
    results = dispatcher.publish_sync(event)
    
    # Assertions
    assert len(received_events) == 1
    assert received_events[0] == event
    assert results == ["handled"]

# Test asynchronous event handling
@pytest.mark.asyncio
async def test_subscribe_and_publish_async(dispatcher, event):
    """Test basic subscription and asynchronous publishing."""
    # Setup
    received_events = []
    
    async def async_handler(evt):
        received_events.append(evt)
        return "async_handled"
    
    # Subscribe
    dispatcher.subscribe(TestEvent, async_handler)
    
    # Publish
    results = await dispatcher.publish(event)
    
    # Assertions
    assert len(received_events) == 1
    assert received_events[0] == event
    assert results == ["async_handled"]

# Test multiple handlers
@pytest.mark.asyncio
async def test_multiple_handlers(dispatcher, event):
    """Test multiple handlers for the same event type."""
    # Setup
    handler1_called = False
    handler2_called = False
    
    def handler1(evt):
        nonlocal handler1_called
        handler1_called = True
        return "handler1"
    
    def handler2(evt):
        nonlocal handler2_called
        handler2_called = True
        return "handler2"
    
    # Subscribe
    dispatcher.subscribe(TestEvent, handler1)
    dispatcher.subscribe(TestEvent, handler2)
    
    # Publish
    results = await dispatcher.publish(event)
    
    # Assertions
    assert handler1_called
    assert handler2_called
    assert set(results) == {"handler1", "handler2"}

# Test handler priority
@pytest.mark.asyncio
async def test_handler_priority(dispatcher, event):
    """Test that handlers execute in priority order."""
    # Setup
    execution_order = []
    
    def handler1(evt):
        execution_order.append("handler1")
        return "handler1"
    
    def handler2(evt):
        execution_order.append("handler2")
        return "handler2"
    
    def handler3(evt):
        execution_order.append("handler3")
        return "handler3"
    
    # Subscribe with priorities
    dispatcher.subscribe(TestEvent, handler1, priority=1)  # Medium
    dispatcher.subscribe(TestEvent, handler2, priority=2)  # High
    dispatcher.subscribe(TestEvent, handler3, priority=0)  # Low
    
    # Publish
    await dispatcher.publish(event)
    
    # Assertions - higher priority first
    assert execution_order == ["handler2", "handler1", "handler3"]

# Test inheritance handling
@pytest.mark.asyncio
async def test_inheritance_handling(dispatcher, event, derived_event):
    """Test that handlers receive events from derived classes."""
    # Setup
    base_events = []
    derived_events = []
    
    def base_handler(evt):
        base_events.append(evt)
        return "base"
    
    def derived_handler(evt):
        derived_events.append(evt)
        return "derived"
    
    # Subscribe
    dispatcher.subscribe(TestEvent, base_handler)
    dispatcher.subscribe(DerivedTestEvent, derived_handler)
    
    # Publish base event
    await dispatcher.publish(event)
    
    # Assertions for base event
    assert len(base_events) == 1
    assert len(derived_events) == 0
    
    # Publish derived event
    base_events.clear()
    derived_events.clear()
    await dispatcher.publish(derived_event)
    
    # Assertions for derived event - both handlers should receive it
    assert len(base_events) == 1
    assert len(derived_events) == 1
    assert base_events[0] == derived_event
    assert derived_events[0] == derived_event

# Test middleware
@pytest.mark.asyncio
async def test_middleware(dispatcher, event):
    """Test middleware chain execution."""
    # Setup
    middleware_chain = []
    
    async def test_middleware1(evt, next_middleware):
        middleware_chain.append("middleware1_before")
        result = await next_middleware(evt)
        middleware_chain.append("middleware1_after")
        return result
    
    async def test_middleware2(evt, next_middleware):
        middleware_chain.append("middleware2_before")
        result = await next_middleware(evt)
        middleware_chain.append("middleware2_after")
        return result
    
    def handler(evt):
        middleware_chain.append("handler")
        return "handled"
    
    # Add middleware and handler
    dispatcher.add_middleware(test_middleware1)
    dispatcher.add_middleware(test_middleware2)
    dispatcher.subscribe(TestEvent, handler)
    
    # Publish
    await dispatcher.publish(event)
    
    # Assertions - middleware should wrap in order
    assert middleware_chain == [
        "middleware1_before",
        "middleware2_before",
        "handler",
        "middleware2_after",
        "middleware1_after"
    ]

# Test middleware filtering
@pytest.mark.asyncio
async def test_middleware_filtering(dispatcher, event):
    """Test that middleware can filter events."""
    # Setup
    handler_called = False
    
    async def filtering_middleware(evt, next_middleware):
        # Filter out the event - return None
        return None
    
    def handler(evt):
        nonlocal handler_called
        handler_called = True
        return "handled"
    
    # Add middleware and handler
    dispatcher.add_middleware(filtering_middleware)
    dispatcher.subscribe(TestEvent, handler)
    
    # Publish
    await dispatcher.publish(event)
    
    # Assertions - handler should not be called
    assert not handler_called

# Test error handling in handlers
@pytest.mark.asyncio
async def test_error_handling_middleware(dispatcher, event):
    """Test that error handling middleware catches errors."""
    # Setup
    error_caught = False
    
    async def error_middleware(evt, next_middleware):
        nonlocal error_caught
        try:
            return await next_middleware(evt)
        except Exception:
            error_caught = True
            return None
    
    def handler_with_error(evt):
        raise ValueError("Test error")
    
    # Add middleware and handler
    dispatcher.add_middleware(error_middleware)
    dispatcher.subscribe(TestEvent, handler_with_error)
    
    # Publish
    await dispatcher.publish(event)
    
    # Assertions - error should be caught
    assert error_caught

# Test unsubscribe
@pytest.mark.asyncio
async def test_unsubscribe(dispatcher, event):
    """Test that handlers can be unsubscribed."""
    # Setup
    handler_called = False
    
    def handler(evt):
        nonlocal handler_called
        handler_called = True
        return "handled"
    
    # Subscribe
    dispatcher.subscribe(TestEvent, handler)
    
    # Unsubscribe
    result = dispatcher.unsubscribe(TestEvent, handler)
    
    # Publish
    await dispatcher.publish(event)
    
    # Assertions
    assert result  # Unsubscribe should return True
    assert not handler_called  # Handler should not be called

# Test singleton pattern
def test_singleton_pattern():
    """Test that EventDispatcher follows the singleton pattern."""
    # Get two instances
    dispatcher1 = EventDispatcher.get_instance()
    dispatcher2 = EventDispatcher.get_instance()
    
    # They should be the same object
    assert dispatcher1 is dispatcher2
    
    # Both should have empty subscribers and middlewares
    assert dispatcher1._subscribers is dispatcher2._subscribers
    assert dispatcher1._middlewares is dispatcher2._middlewares

# Test built-in middlewares
@pytest.mark.asyncio
async def test_built_in_middlewares(dispatcher, event, caplog):
    """Test the built-in logging and error handling middlewares."""
    # Setup - add built-in middlewares
    dispatcher.add_middleware(logging_middleware)
    dispatcher.add_middleware(error_handling_middleware)
    
    # Handler that works
    def good_handler(evt):
        return "good"
    
    # Handler that raises an error
    def bad_handler(evt):
        raise ValueError("Test error")
    
    # Subscribe both handlers
    dispatcher.subscribe(TestEvent, good_handler)
    dispatcher.subscribe(TestEvent, bad_handler)
    
    # Publish - should not crash due to error_handling_middleware
    results = await dispatcher.publish(event)
    
    # Assertions
    assert "good" in results
    # Check that logging middleware logged the event
    assert any("Event dispatched" in record.message for record in caplog.records)
    # Check that error handling middleware logged the error
    assert any("Test error" in record.message for record in caplog.records) 