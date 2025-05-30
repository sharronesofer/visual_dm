from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.events.dispatcher import EventDispatcher
from typing import Type

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
Tests for the analytics schemas to ensure they match the Development Bible requirements.
"""

import unittest
from datetime import datetime
from pydantic import ValidationError

from backend.systems.analytics.schemas import (
    AnalyticsEventBase,
    GameStartEvent,
    GameEndEvent,
    MemoryEvent,
    RumorEvent,
    MotifEvent,
    PopulationEvent,
    POIStateEvent,
    FactionEvent,
    QuestEvent,
    CombatEvent,
    TimeEvent,
    StorageEvent,
    RelationshipEvent,
    WorldStateEvent,
    CustomEvent,
    EVENT_TYPE_MAPPING,
    get_event_model,
)


class TestAnalyticsSchemas(unittest.TestCase): pass
    """Test analytics schemas for compliance with Development Bible."""

    def test_event_type_mapping_completeness(self): pass
        """Test that EVENT_TYPE_MAPPING contains all 15 canonical event types."""
        expected_types = [
            "GameStart",
            "GameEnd",
            "MemoryEvent",
            "RumorEvent",
            "MotifEvent",
            "PopulationEvent",
            "POIStateEvent",
            "FactionEvent",
            "QuestEvent",
            "CombatEvent",
            "TimeEvent",
            "StorageEvent",
            "RelationshipEvent",
            "WorldStateEvent",
            "CustomEvent",
        ]

        self.assertEqual(
            len(expected_types),
            len(EVENT_TYPE_MAPPING),
            "EVENT_TYPE_MAPPING should contain exactly 15 canonical event types",
        )

        for event_type in expected_types: pass
            self.assertIn(
                event_type,
                EVENT_TYPE_MAPPING,
                f"EVENT_TYPE_MAPPING should contain {event_type}",
            )

    def test_get_event_model(self): pass
        """Test the get_event_model function."""
        # Test with known event type
        self.assertEqual(get_event_model("GameStart"), GameStartEvent)

        # Test with unknown event type - should return CustomEvent
        self.assertEqual(get_event_model("UnknownEventType"), CustomEvent)

    def test_base_event_model(self): pass
        """Test AnalyticsEventBase model validation."""
        # Valid event
        event = AnalyticsEventBase(event_type="TestEvent", entity_id="test_entity")
        self.assertEqual(event.event_type, "TestEvent")
        self.assertEqual(event.entity_id, "test_entity")
        self.assertIsInstance(event.timestamp, datetime)

        # Test required fields
        with self.assertRaises(ValidationError): pass
            AnalyticsEventBase()

    def test_game_start_event(self): pass
        """Test GameStartEvent model validation."""
        # Valid event
        event = GameStartEvent(
            session_id="test_session",
            user_id="test_user",
            client_info={"platform": "test", "version": "1.0"},
        )
        self.assertEqual(event.event_type, "GameStart")
        self.assertEqual(event.session_id, "test_session")
        self.assertEqual(event.user_id, "test_user")
        self.assertEqual(event.client_info["platform"], "test")

        # Test required fields
        with self.assertRaises(ValidationError): pass
            GameStartEvent(user_id="test_user")

    def test_game_end_event(self): pass
        """Test GameEndEvent model validation."""
        # Valid event
        event = GameEndEvent(
            session_id="test_session", session_duration=3600.5, reason="user_quit"
        )
        self.assertEqual(event.event_type, "GameEnd")
        self.assertEqual(event.session_id, "test_session")
        self.assertEqual(event.session_duration, 3600.5)
        self.assertEqual(event.reason, "user_quit")

        # Test required fields
        with self.assertRaises(ValidationError): pass
            GameEndEvent(session_id="test_session")

    def test_memory_event(self): pass
        """Test MemoryEvent model validation."""
        # Valid event
        event = MemoryEvent(
            memory_id="memory_123",
            action="created",
            memory_type="observation",
            relevance=0.8,
        )
        self.assertEqual(event.event_type, "MemoryEvent")
        self.assertEqual(event.memory_id, "memory_123")
        self.assertEqual(event.action, "created")
        self.assertEqual(event.memory_type, "observation")
        self.assertEqual(event.relevance, 0.8)

        # Test required fields
        with self.assertRaises(ValidationError): pass
            MemoryEvent(memory_id="memory_123", action="created")

    def test_event_serialization(self): pass
        """Test that events can be serialized to JSON."""
        event = GameStartEvent(
            session_id="test_session",
            user_id="test_user",
            client_info={"platform": "test", "version": "1.0"},
        )

        # Convert to dict/JSON and back
        event_dict = event.model_dump()
        self.assertEqual(event_dict["event_type"], "GameStart")
        self.assertEqual(event_dict["session_id"], "test_session")

        # Test JSON serialization
        event_json = event.model_dump_json()
        self.assertIsInstance(event_json, str)
        self.assertIn("GameStart", event_json)
        self.assertIn("test_session", event_json)

    def test_event_inheritance(self): pass
        """Test that all event models inherit from AnalyticsEventBase."""
        for event_class in EVENT_TYPE_MAPPING.values(): pass
            self.assertTrue(
                issubclass(event_class, AnalyticsEventBase),
                f"{event_class.__name__} should inherit from AnalyticsEventBase",
            )

    def test_custom_event(self): pass
        """Test CustomEvent model for arbitrary data."""
        # Test with simple data
        event = CustomEvent(
            custom_type="test_custom", data={"key1": "value1", "key2": 123}
        )
        self.assertEqual(event.event_type, "CustomEvent")
        self.assertEqual(event.custom_type, "test_custom")
        self.assertEqual(event.data["key1"], "value1")
        self.assertEqual(event.data["key2"], 123)

        # Test with nested data
        event = CustomEvent(
            custom_type="test_nested",
            data={"nested": {"key1": "value1", "key2": [1, 2, 3]}},
        )
        self.assertEqual(event.custom_type, "test_nested")
        self.assertEqual(event.data["nested"]["key1"], "value1")
        self.assertEqual(event.data["nested"]["key2"], [1, 2, 3])

        # Test required fields
        with self.assertRaises(ValidationError): pass
            CustomEvent(data={"key1": "value1"})


if __name__ == "__main__": pass
    unittest.main()
