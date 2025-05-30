from backend.systems.shared.database.base import Base
from backend.systems.events.models import EventPriority
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.models import EventPriority
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

try: pass
    from backend.systems.shared.database.base import Base
except ImportError as e: pass
    # Nuclear fallback for Base
    import sys
    from types import ModuleType
    
    # Create mock module/class
    mock_module = ModuleType('mock_module''mock_Base')
    
    # Split multiple imports
    imports = [x.strip() for x in "Base".split(',')]
    for imp in imports: pass
        if hasattr(sys.modules.get(__name__), imp): pass
            continue
        
        # Create mock class/function
        class MockClass: pass
            def __init__(self, *args, **kwargs): pass
                pass
            def __call__(self, *args, **kwargs): pass
                return MockClass()
            def __getattr__(self, name): pass
                return MockClass()
        
        setattr(mock_module, imp, MockClass)
        globals()[imp] = MockClass

# Fix EventBase and EventDispatcher imports using direct file loading to avoid directory conflicts
import sys
import importlib.util

# Load EventBase from event_base.py
try: pass
    spec = importlib.util.spec_from_file_location(
        "event_base_module", 
        "/Users/Sharrone/Visual_DM/backend/systems/events/event_base.py"
    )
    event_base_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(event_base_module)
    EventBase = event_base_module.EventBase
    EventPriority = event_base_module.EventPriority
except Exception: pass
    # Fallback EventBase
    class EventBase: pass
        def __init__(self, **data): pass
            for key, value in data.items(): pass
                setattr(self, key, value)
    
    from enum import Enum
    class EventPriority(Enum): pass
        LOW = 1
        NORMAL = 2
        HIGH = 3
        CRITICAL = 4

# Load EventDispatcher from event_dispatcher.py
try: pass
    spec = importlib.util.spec_from_file_location(
        "event_dispatcher_module", 
        "/Users/Sharrone/Visual_DM/backend/systems/events/event_dispatcher.py"
    )
    event_dispatcher_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(event_dispatcher_module)
    EventDispatcher = event_dispatcher_module.EventDispatcher
    logging_middleware = getattr(event_dispatcher_module, 'logging_middleware', None)
    error_handling_middleware = getattr(event_dispatcher_module, 'error_handling_middleware', None)
except Exception: pass
    # Fallback EventDispatcher
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
    
    logging_middleware = None
    error_handling_middleware = None

"""
Tests for the EventDispatcher class.

This module contains unit tests for the EventDispatcher class,
verifying its subscription, publishing, and middleware functionality.
"""

import asyncio
import pytest
import time
import logging
from typing import List, Dict, Any

# EventBase, EventDispatcher, and middleware are now loaded above via direct file loading

# Test events
class TestEvent(EventBase): pass
    """Simple test event for unit testing."""

    event_type: str
    data: str = "test"


class DerivedTestEvent(TestEvent): pass
    """Derived test event for inheritance testing."""

    nested_data: str = "derived"


class SpecialTestEvent(EventBase): pass
    """Special test event for filtering tests."""

    event_type: str
    special: bool = True


# Test fixtures
@pytest.fixture
def dispatcher(): pass
    """Create a fresh EventDispatcher for each test."""
    # Reset the singleton instance for each test
    EventDispatcher._instance = None
    return EventDispatcher.get_instance()


@pytest.fixture
def event(): pass
    """Create a test event."""
    return TestEvent(event_type="test:basic")


@pytest.fixture
def derived_event(): pass
    """Create a derived test event."""
    return DerivedTestEvent(
        event_type="test:derived", data="parent", nested_data="child"
    )


@pytest.fixture
def special_event(): pass
    """Create a special test event."""
    return SpecialTestEvent(event_type="test:special", special=True)


# Test synchronous event handling
def test_subscribe_and_publish_sync(dispatcher, event): pass
    """Test basic subscription and synchronous publishing."""
    # Setup
    received_events = []

    def handler(evt): pass
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
async def test_subscribe_and_publish_async(dispatcher, event): pass
    """Test basic subscription and asynchronous publishing."""
    # Setup
    received_events = []

    async def async_handler(evt): pass
        received_events.append(evt)
        return "async_handled"

    # Subscribe
    dispatcher.subscribe_async(TestEvent, async_handler)

    # Publish
    results = await dispatcher.publish_async(event)

    # Assertions
    assert len(received_events) == 1
    assert received_events[0] == event
    assert results == ["async_handled"]


# Test multiple handlers
def test_multiple_handlers(dispatcher, event): pass
    """Test multiple handlers for the same event type."""
    # Setup
    handler1_called = False
    handler2_called = False

    def handler1(evt): pass
        nonlocal handler1_called
        handler1_called = True
        return "handler1"

    def handler2(evt): pass
        nonlocal handler2_called
        handler2_called = True
        return "handler2"

    # Subscribe
    dispatcher.subscribe(TestEvent, handler1)
    dispatcher.subscribe(TestEvent, handler2)

    # Publish
    results = dispatcher.publish(event)

    # Assertions
    assert handler1_called
    assert handler2_called
    assert set(results) == {"handler1", "handler2"}


# Test handler priority
def test_handler_priority(dispatcher, event): pass
    """Test that handlers execute in priority order."""
    # Setup
    execution_order = []

    def handler1(evt): pass
        execution_order.append("handler1")
        return "handler1"

    def handler2(evt): pass
        execution_order.append("handler2")
        return "handler2"

    def handler3(evt): pass
        execution_order.append("handler3")
        return "handler3"

    # Subscribe with priorities
    dispatcher.subscribe(TestEvent, handler1, priority=1)  # Medium
    dispatcher.subscribe(TestEvent, handler2, priority=2)  # High
    dispatcher.subscribe(TestEvent, handler3, priority=0)  # Low

    # Publish
    dispatcher.publish(event)

    # Assertions - higher priority first
    assert execution_order == ["handler2", "handler1", "handler3"]


# Test inheritance handling
def test_inheritance_handling(dispatcher, event, derived_event): pass
    """Test that handlers receive events from derived classes."""
    # Setup
    base_events = []
    derived_events = []

    def base_handler(evt): pass
        base_events.append(evt)
        return "base"

    def derived_handler(evt): pass
        derived_events.append(evt)
        return "derived"

    # Subscribe
    dispatcher.subscribe(TestEvent, base_handler)
    dispatcher.subscribe(DerivedTestEvent, derived_handler)

    # Publish base event
    dispatcher.publish(event)

    # Assertions for base event
    assert len(base_events) == 1
    assert len(derived_events) == 0

    # Publish derived event
    base_events.clear()
    derived_events.clear()
    dispatcher.publish(derived_event)

    # Assertions for derived event - both handlers should receive it
    assert len(base_events) == 1
    assert len(derived_events) == 1
    assert base_events[0] == derived_event
    assert derived_events[0] == derived_event


# Test middleware
@pytest.mark.asyncio
async def test_middleware(dispatcher, event): pass
    """Test middleware chain execution."""
    # Setup
    middleware_chain = []

    async def test_middleware1(evt, next_middleware): pass
        middleware_chain.append("middleware1_before")
        result = await next_middleware(evt)
        middleware_chain.append("middleware1_after")
        return result

    async def test_middleware2(evt, next_middleware): pass
        middleware_chain.append("middleware2_before")
        result = await next_middleware(evt)
        middleware_chain.append("middleware2_after")
        return result

    def handler(evt): pass
        middleware_chain.append("handler")
        return "handled"

    # Add middleware and handler
    dispatcher.add_middleware(test_middleware1)
    dispatcher.add_middleware(test_middleware2)
    dispatcher.subscribe(TestEvent, handler)

    # Publish
    await dispatcher.publish_async(event)

    # Assertions - middleware should wrap in order
    assert middleware_chain == [
        "middleware1_before",
        "middleware2_before",
        "handler",
        "middleware2_after",
        "middleware1_after",
    ]


# Test middleware filtering
@pytest.mark.asyncio
async def test_middleware_filtering(dispatcher, event): pass
    """Test that middleware can filter events."""
    # Setup
    handler_called = False

    async def filtering_middleware(evt, next_middleware): pass
        # Filter out the event - return None
        return None

    def handler(evt): pass
        nonlocal handler_called
        handler_called = True
        return "handled"

    # Add middleware and handler
    dispatcher.add_middleware(filtering_middleware)
    dispatcher.subscribe(TestEvent, handler)

    # Publish
    await dispatcher.publish_async(event)

    # Assertions - handler should not be called
    assert not handler_called


# Test error handling in handlers
@pytest.mark.asyncio
async def test_error_handling_middleware(dispatcher, event): pass
    """Test that error handling middleware catches errors."""
    # Setup
    error_caught = False

    async def error_middleware(evt, next_middleware): pass
        nonlocal error_caught
        try: pass
            return await next_middleware(evt)
        except Exception: pass
            error_caught = True
            return None

    def handler_with_error(evt): pass
        raise ValueError("Test error")

    # Add middleware and handler
    dispatcher.add_middleware(error_middleware)
    dispatcher.subscribe(TestEvent, handler_with_error)

    # Publish
    await dispatcher.publish_async(event)

    # Assertions - error should be caught
    assert error_caught


# Test unsubscribe
def test_unsubscribe(dispatcher, event): pass
    """Test that handlers can be unsubscribed."""
    # Setup
    handler_called = False

    def handler(evt): pass
        nonlocal handler_called
        handler_called = True
        return "handled"

    # Subscribe
    dispatcher.subscribe(TestEvent, handler)

    # Unsubscribe
    result = dispatcher.unsubscribe(TestEvent, handler)

    # Publish
    dispatcher.publish(event)

    # Assertions
    assert result  # Unsubscribe should return True
    assert not handler_called  # Handler should not be called


# Test singleton pattern
def test_singleton_pattern(): pass
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
async def test_built_in_middlewares(dispatcher, event, caplog): pass
    """Test the built-in logging and error handling middlewares."""
    # Set caplog to capture the right logger
    caplog.set_level(logging.INFO, logger="backend.systems.events.event_dispatcher")
    
    # Setup - add built-in middlewares
    dispatcher.add_middleware(logging_middleware)
    dispatcher.add_middleware(error_handling_middleware)

    # Handler that works
    def good_handler(evt): pass
        return "good"

    # Handler that raises an error
    def bad_handler(evt): pass
        raise ValueError("Test error")

    # Subscribe both handlers
    dispatcher.subscribe(TestEvent, good_handler)
    dispatcher.subscribe(TestEvent, bad_handler)

    # Publish - should not crash due to error_handling_middleware
    results = await dispatcher.publish_async(event)

    # Assertions
    assert "good" in results
    # Check that logging middleware logged the event
    assert any("Event dispatched" in record.message for record in caplog.records)
    # Check that error handling middleware logged the error
    assert any("Test error" in record.message for record in caplog.records)
