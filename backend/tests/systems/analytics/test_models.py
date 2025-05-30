from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher

# Import EventBase and EventDispatcher with fallbacks
try:
    from backend.systems.events import EventBase, EventDispatcher
except ImportError:
    # Fallback for tests or when events system isn't available
    class EventBase:
        def __init__(self, **data):
            for key, value in data.items():
                setattr(self, key, value)
    
    class EventDispatcher:
        @classmethod
        def get_instance(cls):
            return cls()
        
        def dispatch(self, event):
            pass
        
        def publish(self, event):
            pass
        
        def emit(self, event):
            pass

"""
Tests for mock models in the analytics system.
"""
import pytest
from backend.systems.analytics.models import EventBase


def test_event_base_init():
    """Test EventBase initialization."""
    # Test with entity_id
    event = EventBase(entity_id="test_entity")
    assert event.entity_id == "test_entity"
    
    # Test with additional kwargs
    event = EventBase(entity_id="test_entity", name="Test Event", value=42)
    assert event.entity_id == "test_entity"
    assert event.name == "Test Event"
    assert event.value == 42


def test_event_base_model_dump():
    """Test the model_dump method in EventBase."""
    # Create an event with some attributes
    event = EventBase(entity_id="test_entity", name="Test Event", value=42)
    
    # Call model_dump and verify the result
    result = event.model_dump()
    
    # Check it returns a dictionary with all attributes
    assert isinstance(result, dict)
    assert result["entity_id"] == "test_entity"
    assert result["name"] == "Test Event"
    assert result["value"] == 42 