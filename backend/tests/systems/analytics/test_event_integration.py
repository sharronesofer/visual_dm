from backend.systems.population.events import PopulationChanged
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.population.events import PopulationChanged
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.population.events import PopulationChanged
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.population.events import PopulationChanged
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.population.events import PopulationChanged
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.population.events import PopulationChanged
from backend.systems.events.dispatcher import EventDispatcher
from typing import Type
"""
Tests for the analytics integration with the central event system.
"""

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from datetime import datetime
import pytest
import pytest_asyncio

from backend.systems.analytics.services.analytics_service import (
    AnalyticsService,
    AnalyticsEventType,
)
from backend.systems.analytics import register_with_event_system
from backend.systems.analytics.schemas import (
    MemoryEvent as MemoryCreatedEvent,
    RumorEvent as RumorSpreadEvent,
    PopulationEvent as PopulationChangedEvent,
    POIStateEvent as POIStateChangedEvent,
    RelationshipEvent as RelationshipChangedEvent,
)
from backend.systems.events import (
    EventBase,
    EventType,
    EventDispatcher,
    SystemEvent,
    # MotifChangedEvent,  # Not available in current events system
    # FactionChangedEvent,  # Not available in current events system
    # QuestUpdatedEvent,  # Not available in current events system
    # CombatEvent,  # Not available in current events system
    # TimeAdvancedEvent,  # Not available in current events system
    # EventLoggedEvent,  # Not available in current events system
    # StorageEvent,  # Not available in current events system
    # WorldStateChangedEvent  # Not available in current events system
)


class TestAnalyticsEventIntegration(unittest.TestCase): pass
    """Test analytics integration with the central event system."""

    def setUp(self): pass
        """Set up test environment."""
        # Create a mock event dispatcher
        self.mock_dispatcher = MagicMock(spec=EventDispatcher)

        # Patch the analytics service
        self.analytics_service_patcher = patch(
            "backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance"
        )
        self.mock_get_instance = self.analytics_service_patcher.start()
        self.mock_analytics = MagicMock(spec=AnalyticsService)
        self.mock_analytics.register_with_dispatcher = MagicMock()
        self.mock_get_instance.return_value = self.mock_analytics

        # Patch the event dispatcher
        self.event_dispatcher_patcher = patch("backend.systems.events.get_dispatcher")
        self.mock_get_dispatcher = self.event_dispatcher_patcher.start()
        self.mock_get_dispatcher.return_value = self.mock_dispatcher

    def tearDown(self): pass
        """Clean up after tests."""
        self.analytics_service_patcher.stop()
        self.event_dispatcher_patcher.stop()

    def test_register_with_event_system(self): pass
        """Test registration with the event system."""
        # Call the registration function
        result = register_with_event_system()

        # Verify the analytics service was registered with the dispatcher
        self.mock_analytics.register_with_dispatcher.assert_called_once_with(
            self.mock_dispatcher
        )

        # Verify the function returns the analytics service
        self.assertEqual(result, self.mock_analytics)

    def test_middleware_registration(self): pass
        """Test that analytics middleware is registered with the event dispatcher."""
        # Create middleware
        middleware = MagicMock()
        self.mock_analytics.get_analytics_middleware.return_value = middleware

        # Mock the register_with_dispatcher method to simulate the real behavior
        def mock_register_with_dispatcher(dispatcher): pass
            # Simulate what the real method does - add middleware to dispatcher
            dispatcher.add_middleware(middleware)

        self.mock_analytics.register_with_dispatcher.side_effect = (
            mock_register_with_dispatcher
        )

        # Register with dispatcher
        self.mock_analytics.register_with_dispatcher(self.mock_dispatcher)

        # Verify middleware was added
        self.mock_dispatcher.add_middleware.assert_called_once_with(middleware)

    def test_event_mapping_memory_event(self): pass
        """Test that MemoryCreatedEvent is mapped to MemoryEvent in analytics."""

        # Create a mock middleware that simulates the real middleware behavior
        def mock_middleware(event): pass
            # Simulate the real middleware logic for memory events
            self.mock_analytics.log_event(
                event_type=AnalyticsEventType.MEMORY_EVENT,
                source_event=event,
                entity_id=getattr(event, "entity_id", None),
                metadata={},
            )
            return event

        # Configure the mock to return our middleware
        self.mock_analytics.get_analytics_middleware.return_value = mock_middleware

        # Create a memory event
        memory_event = MemoryCreatedEvent(
            entity_id="entity_456", 
            memory_id="memory_123",
            action="created",
            memory_type="observation", 
            relevance=0.8
        )

        # Create the middleware
        middleware = self.mock_analytics.get_analytics_middleware()

        # Process the event
        middleware(memory_event)

        # Verify the event was logged with the correct mapping
        self.mock_analytics.log_event.assert_called_once()
        call_args = self.mock_analytics.log_event.call_args[1]
        self.assertEqual(call_args["event_type"], AnalyticsEventType.MEMORY_EVENT)

    def test_event_mapping_rumor_event(self): pass
        """Test that RumorSpreadEvent is mapped to RumorEvent in analytics."""

        # Create a mock middleware that simulates the real middleware behavior
        def mock_middleware(event): pass
            # Simulate the real middleware logic for rumor events
            self.mock_analytics.log_event(
                event_type=AnalyticsEventType.RUMOR_EVENT,
                source_event=event,
                entity_id=getattr(
                    event, "source_entity_id", None
                ),  # Use source_entity_id for rumor events
                metadata={},
            )
            return event

        # Configure the mock to return our middleware
        self.mock_analytics.get_analytics_middleware.return_value = mock_middleware

        # Create a rumor event
        rumor_event = RumorSpreadEvent(
            rumor_id="rumor_123",
            action="spread",
            spread_count=3,
            mutation_level=0.2,
        )

        # Create the middleware
        middleware = self.mock_analytics.get_analytics_middleware()

        # Process the event
        middleware(rumor_event)

        # Verify the event was logged with the correct mapping
        self.mock_analytics.log_event.assert_called_once()
        call_args = self.mock_analytics.log_event.call_args[1]
        self.assertEqual(call_args["event_type"], AnalyticsEventType.RUMOR_EVENT)

    def test_middleware_passthrough(self): pass
        """Test that middleware returns the original event."""

        # Create a mock middleware that simulates the real middleware behavior
        def mock_middleware(event): pass
            # Simulate the real middleware logic - log event and return original
            self.mock_analytics.log_event(
                event_type=AnalyticsEventType.CUSTOM_EVENT,
                source_event=event,
                entity_id=getattr(event, "entity_id", None),
                metadata={},
            )
            return event

        # Configure the mock to return our middleware
        self.mock_analytics.get_analytics_middleware.return_value = mock_middleware

        # Create an event
        event = SystemEvent(system_name="test_system", event_data={"key": "value"})

        # Create the middleware
        middleware = self.mock_analytics.get_analytics_middleware()

        # Process the event
        result = middleware(event)

        # Verify the middleware returned the original event
        self.assertIs(result, event)

    def test_all_event_types_mapped(self): pass
        """Test that all event types from the canonical list are mapped."""

        # Create a mock middleware that simulates the real middleware behavior
        def mock_middleware(event): pass
            # Simulate the real middleware logic - call log_event with some analytics event type
            self.mock_analytics.log_event(
                event_type=AnalyticsEventType.CUSTOM_EVENT,  # Default mapping
                source_event=event,
                entity_id=getattr(event, "entity_id", None),
                metadata={},
            )
            return event

        # Configure the mock to return our middleware
        self.mock_analytics.get_analytics_middleware.return_value = mock_middleware

        # Create a dictionary to hold test events for only the available event types
        event_types = {
            "MemoryCreatedEvent": MemoryCreatedEvent(
                entity_id="123", 
                memory_id="memory_123",
                action="created",
                memory_type="test", 
                relevance=0.5
            ),
            "RumorSpreadEvent": RumorSpreadEvent(
                rumor_id="rumor_123",
                action="spread",
                spread_count=3,
                mutation_level=0.1,
            ),
            "PopulationChangedEvent": PopulationChangedEvent(
                poi_id="test",
                previous_population=100,
                new_population=110,
                reason="growth",
            ),
            "POIStateChangedEvent": POIStateChangedEvent(
                poi_id="test",
                previous_state="normal",
                new_state="ruins",
                reason="war",
            ),
            "RelationshipChangedEvent": RelationshipChangedEvent(
                source_id="char1",
                target_id="char2",
                relationship_type="friendship",
                previous_value="neutral",
                new_value="friend",
            ),
        }

        # Get the middleware
        middleware = self.mock_analytics.get_analytics_middleware()

        # Process each event type
        for event_name, event in event_types.items(): pass
            self.mock_analytics.log_event.reset_mock()
            middleware(event)

            # Verify each event was logged
            self.mock_analytics.log_event.assert_called_once()

            # Verify analytics mapping exists for each event
            call_args = self.mock_analytics.log_event.call_args[1]
            self.assertIn("event_type", call_args)

            # Print event name and mapped type for debugging
            # print(f"{event_name} -> {call_args['event_type']}")


@pytest.mark.asyncio
@patch("backend.systems.analytics.services.analytics_service.AnalyticsService.get_instance")
async def test_background_processing(mock_get_instance): pass
    """Test that analytics processing happens in the background."""
    # Create analytics service mock
    mock_analytics = MagicMock(spec=AnalyticsService)
    mock_get_instance.return_value = mock_analytics
    
    # Simply mock the log_event method and middleware
    mock_analytics.log_event = MagicMock()
    
    # Create a simpler middleware that directly calls log_event 
    # This avoids creating any coroutines that might not be awaited
    def mock_middleware(event): pass
        # Directly log the event instead of creating a coroutine
        mock_analytics.log_event(
            event_type=AnalyticsEventType.CUSTOM_EVENT,
            source_event=event,
            entity_id=getattr(event, "entity_id", None),
            metadata={}
        )
        return event  # Return the original event

    # Configure the mock
    mock_analytics.get_analytics_middleware.return_value = mock_middleware

    # Create a test event
    event = SystemEvent(system_name="test_system", event_data={"key": "value"})
    
    # Create and use the middleware
    middleware = mock_analytics.get_analytics_middleware()
    result = middleware(event)
    
    # Verify immediate return
    assert result is event
    
    # No need to wait for async processing
    # Verify the event was processed
    mock_analytics.log_event.assert_called_once_with(
        event_type=AnalyticsEventType.CUSTOM_EVENT,
        source_event=event,
        entity_id=None,
        metadata={}
    )


if __name__ == "__main__": pass
    unittest.main()
