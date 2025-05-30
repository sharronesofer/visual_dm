from backend.systems.shared.database.base import Base
from backend.systems.shared.database.base import Base
from typing import Type
"""
Tests for the event mapping functionality in the analytics service.
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from backend.systems.analytics.services.analytics_service import (
    AnalyticsService,
    AnalyticsEventType,
)
from backend.systems.events import (
    EventBase,
    EventType,
    SystemEvent,
    GameEvent,
    MemoryEvent,
    RumorEvent,
    FactionEvent,
    CharacterEvent,
    NarrativeEvent,
)


class TestAnalyticsEventMapping: pass
    """Test the analytics event mapping functionality."""

    def test_map_event_to_analytics_type_specific_types(self): pass
        """Test mapping specific event types to analytics types."""
        # Create an analytics service
        service = AnalyticsService()
        
        # Define test cases with event classes and expected mappings
        test_cases = {
            "GameInitialized": AnalyticsEventType.GAME_START,
            "GameEnded": AnalyticsEventType.GAME_END,
            "MemoryCreated": AnalyticsEventType.MEMORY_EVENT,
            "MemoryUpdated": AnalyticsEventType.MEMORY_EVENT,
            "MemoryDeleted": AnalyticsEventType.MEMORY_EVENT,
            "MemoryRecalled": AnalyticsEventType.MEMORY_EVENT,
            "RumorCreated": AnalyticsEventType.RUMOR_EVENT,
            "RumorSpread": AnalyticsEventType.RUMOR_EVENT,
            "RumorUpdated": AnalyticsEventType.RUMOR_EVENT,
            "NarrativeMotifIntroduced": AnalyticsEventType.MOTIF_EVENT,
            "FactionCreated": AnalyticsEventType.FACTION_EVENT,
            "FactionUpdated": AnalyticsEventType.FACTION_EVENT,
            "FactionRelationshipChanged": AnalyticsEventType.FACTION_EVENT,
            "CharacterRelationshipChanged": AnalyticsEventType.RELATIONSHIP_EVENT,
            "GameSaved": AnalyticsEventType.STORAGE_EVENT,
            "GameLoaded": AnalyticsEventType.STORAGE_EVENT,
        }
        
        # Test each case
        for event_type_name, expected_analytics_type in test_cases.items(): pass
            # Create a mock event with the specific class name
            event = MagicMock()
            type(event).__name__ = event_type_name
            
            # Map the event and check the result
            result = service._map_event_to_analytics_type(event)
            assert result == expected_analytics_type, f"Failed for {event_type_name}"
    
    def test_map_event_to_analytics_type_base_classes(self): pass
        """Test mapping events based on their base class."""
        # Create an analytics service
        service = AnalyticsService()
        
        # Test MemoryEvent mapping
        memory_event = MagicMock(spec=MemoryEvent)
        type(memory_event).__name__ = "CustomMemoryEvent"
        assert service._map_event_to_analytics_type(memory_event) == AnalyticsEventType.MEMORY_EVENT
        
        # Test RumorEvent mapping
        rumor_event = MagicMock(spec=RumorEvent)
        type(rumor_event).__name__ = "CustomRumorEvent"
        assert service._map_event_to_analytics_type(rumor_event) == AnalyticsEventType.RUMOR_EVENT
        
        # Test FactionEvent mapping
        faction_event = MagicMock(spec=FactionEvent)
        type(faction_event).__name__ = "CustomFactionEvent"
        assert service._map_event_to_analytics_type(faction_event) == AnalyticsEventType.FACTION_EVENT
        
        # Test CharacterEvent with relationship
        character_event = MagicMock(spec=CharacterEvent)
        type(character_event).__name__ = "CustomCharacterEvent"
        character_event.relationship = "friend"
        assert service._map_event_to_analytics_type(character_event) == AnalyticsEventType.RELATIONSHIP_EVENT
        
        # Test CharacterEvent without relationship
        character_event = MagicMock(spec=CharacterEvent)
        type(character_event).__name__ = "CustomCharacterEvent"
        # No relationship attribute
        assert service._map_event_to_analytics_type(character_event) == AnalyticsEventType.CUSTOM_EVENT
        
        # Test GameEvent
        game_event = MagicMock(spec=GameEvent)
        type(game_event).__name__ = "CustomGameEvent"
        assert service._map_event_to_analytics_type(game_event) == AnalyticsEventType.CUSTOM_EVENT
        
        # Test SystemEvent
        system_event = MagicMock(spec=SystemEvent)
        type(system_event).__name__ = "CustomSystemEvent"
        assert service._map_event_to_analytics_type(system_event) == AnalyticsEventType.CUSTOM_EVENT
    
    def test_map_event_to_analytics_type_narrative_events(self): pass
        """Test mapping narrative events based on their name."""
        # Create an analytics service
        service = AnalyticsService()
        
        # Test NarrativeEvent with motif in name
        motif_event = MagicMock(spec=NarrativeEvent)
        type(motif_event).__name__ = "CustomMotifEvent"
        # Add a property that explicitly identifies this as a motif event
        motif_event.is_motif_event = True
        assert service._map_event_to_analytics_type(motif_event) == AnalyticsEventType.MOTIF_EVENT
        
        # Test NarrativeEvent with quest in name
        quest_event = MagicMock(spec=NarrativeEvent)
        type(quest_event).__name__ = "CustomQuestEvent"
        quest_event.is_quest_event = True
        assert service._map_event_to_analytics_type(quest_event) == AnalyticsEventType.QUEST_EVENT
        
        # Test other NarrativeEvent
        other_narrative_event = MagicMock(spec=NarrativeEvent)
        type(other_narrative_event).__name__ = "CustomNarrativeEvent"
        assert service._map_event_to_analytics_type(other_narrative_event) == AnalyticsEventType.CUSTOM_EVENT
    
    def test_map_event_to_analytics_type_default_fallback(self): pass
        """Test the default fallback for unknown event types."""
        # Create an analytics service
        service = AnalyticsService()
        
        # Create a completely custom event that doesn't match any specific type
        custom_event = MagicMock()
        type(custom_event).__name__ = "TotallyCustomEvent"
        
        # Map the event and check the result
        result = service._map_event_to_analytics_type(custom_event)
        assert result == AnalyticsEventType.CUSTOM_EVENT
        
    def test_non_canonical_event_type_warning(self): pass
        """Test that non-canonical event types generate a warning."""
        # Create an analytics service
        service = AnalyticsService()
        
        # Test with canonical event type (should not warn)
        with patch("backend.systems.analytics.services.analytics_service.logger.warning") as mock_warning: pass
            service.log_event(
                event_type=AnalyticsEventType.GAME_START,
                entity_id="test_entity",
                metadata={"test": "data"}
            )
            mock_warning.assert_not_called()
        
        # Test with non-canonical event type (should warn)
        with patch("backend.systems.analytics.services.analytics_service.logger.warning") as mock_warning: pass
            service.log_event(
                event_type="NonCanonicalType",
                entity_id="test_entity",
                metadata={"test": "data"}
            )
            mock_warning.assert_called_once()
            
        # Test with Custom_ prefix (should not warn)
        with patch("backend.systems.analytics.services.analytics_service.logger.warning") as mock_warning: pass
            service.log_event(
                event_type="Custom_TestType",
                entity_id="test_entity",
                metadata={"test": "data"}
            )
            mock_warning.assert_not_called() 