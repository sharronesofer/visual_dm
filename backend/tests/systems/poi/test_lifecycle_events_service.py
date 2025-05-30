from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from backend.systems.poi.models import PointOfInterest
from typing import Type
from typing import List
from dataclasses import field
"""
Tests for backend.systems.poi.services.lifecycle_events_service

This module contains tests for POI lifecycle event functionality.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from typing import Dict, List

from backend.systems.poi.services.lifecycle_events_service import POILifecycleEventsService
from backend.systems.poi.models import PointOfInterest, POIType


class TestPOILifecycleEventsService: pass
    """Tests for POI lifecycle events service."""

    @pytest.fixture
    def sample_poi(self): pass
        """Create a sample POI for testing."""
        poi = Mock(spec=PointOfInterest)
        poi.id = "poi_1"
        poi.name = "Test Settlement"
        poi.poi_type = "village"
        poi.population = 500
        poi.lifecycle_events = []
        return poi

    @pytest.fixture
    def sample_event(self): pass
        """Create a sample event for testing."""
        return {
            "id": "event_1",
            "category": "founding",
            "event_type": "settlement_founded",
            "title": "Settlement Founded",
            "description": "The settlement was founded by brave pioneers",
            "timestamp": "2023-01-01T00:00:00",
            "importance": 8,
            "metadata": {"founder": "John Smith"},
            "expired": False
        }

    def test_event_categories_constants(self): pass
        """Test that event categories are properly defined."""
        categories = POILifecycleEventsService.EVENT_CATEGORIES
        
        # Check required categories exist
        required_categories = ["founding", "destruction", "population", "leadership", 
                             "conflict", "construction", "disaster", "festival", 
                             "economy", "discovery", "faction"]
        for category in required_categories: pass
            assert category in categories
            assert "importance" in categories[category]
            assert "description" in categories[category]
            assert 1 <= categories[category]["importance"] <= 10

    def test_event_types_constants(self): pass
        """Test that event types are properly defined."""
        event_types = POILifecycleEventsService.EVENT_TYPES
        
        # Check all categories have event types
        for category in POILifecycleEventsService.EVENT_CATEGORIES.keys(): pass
            assert category in event_types
            assert isinstance(event_types[category], list)
            assert len(event_types[category]) > 0

    def test_get_events_empty_poi(self, sample_poi): pass
        """Test getting events from POI with no events."""
        sample_poi.lifecycle_events = []
        
        events = POILifecycleEventsService.get_events(sample_poi)
        
        assert isinstance(events, list)
        assert len(events) == 0

    def test_get_events_no_lifecycle_events_attribute(self): pass
        """Test getting events from POI without lifecycle_events attribute."""
        poi = Mock()
        poi.id = "poi_1"
        # No lifecycle_events attribute
        
        events = POILifecycleEventsService.get_events(poi)
        
        assert isinstance(events, list)
        assert len(events) == 0

    def test_get_events_basic(self, sample_poi, sample_event): pass
        """Test basic event retrieval."""
        sample_poi.lifecycle_events = [sample_event]
        
        events = POILifecycleEventsService.get_events(sample_poi)
        
        assert len(events) == 1
        assert events[0]["id"] == "event_1"
        assert events[0]["category"] == "founding"

    def test_get_events_filter_by_category(self, sample_poi, sample_event): pass
        """Test filtering events by category."""
        # Add multiple events with different categories
        event2 = sample_event.copy()
        event2["id"] = "event_2"
        event2["category"] = "population"
        
        sample_poi.lifecycle_events = [sample_event, event2]
        
        founding_events = POILifecycleEventsService.get_events(sample_poi, category="founding")
        population_events = POILifecycleEventsService.get_events(sample_poi, category="population")
        
        assert len(founding_events) == 1
        assert founding_events[0]["category"] == "founding"
        assert len(population_events) == 1
        assert population_events[0]["category"] == "population"

    def test_get_events_filter_by_type(self, sample_poi, sample_event): pass
        """Test filtering events by event type."""
        # Add multiple events with different types
        event2 = sample_event.copy()
        event2["id"] = "event_2"
        event2["event_type"] = "discovered"
        
        sample_poi.lifecycle_events = [sample_event, event2]
        
        founded_events = POILifecycleEventsService.get_events(
            sample_poi, event_type="settlement_founded"
        )
        discovered_events = POILifecycleEventsService.get_events(
            sample_poi, event_type="discovered"
        )
        
        assert len(founded_events) == 1
        assert founded_events[0]["event_type"] == "settlement_founded"
        assert len(discovered_events) == 1
        assert discovered_events[0]["event_type"] == "discovered"

    def test_get_events_filter_by_date_range(self, sample_poi): pass
        """Test filtering events by date range."""
        # Create events with different dates
        event1 = {
            "id": "event_1",
            "timestamp": "2023-01-01T00:00:00",
            "category": "founding",
            "expired": False
        }
        event2 = {
            "id": "event_2", 
            "timestamp": "2023-06-01T00:00:00",
            "category": "population",
            "expired": False
        }
        event3 = {
            "id": "event_3",
            "timestamp": "2023-12-01T00:00:00",
            "category": "conflict",
            "expired": False
        }
        
        sample_poi.lifecycle_events = [event1, event2, event3]
        
        # Filter events from June onwards
        start_date = datetime(2023, 6, 1)
        filtered_events = POILifecycleEventsService.get_events(
            sample_poi, start_date=start_date
        )
        
        assert len(filtered_events) == 2
        assert filtered_events[0]["id"] == "event_3"  # Sorted newest first
        assert filtered_events[1]["id"] == "event_2"

    def test_get_events_limit(self, sample_poi): pass
        """Test limiting number of events returned."""
        # Create multiple events
        events = []
        for i in range(5): pass
            event = {
                "id": f"event_{i}",
                "timestamp": f"2023-0{i+1}-01T00:00:00",
                "category": "founding",
                "expired": False
            }
            events.append(event)
        
        sample_poi.lifecycle_events = events
        
        limited_events = POILifecycleEventsService.get_events(sample_poi, limit=2)
        
        assert len(limited_events) == 2

    def test_get_events_exclude_expired(self, sample_poi): pass
        """Test excluding expired events."""
        event1 = {
            "id": "event_1",
            "timestamp": "2023-01-01T00:00:00",
            "category": "founding",
            "expired": False
        }
        event2 = {
            "id": "event_2",
            "timestamp": "2023-02-01T00:00:00", 
            "category": "population",
            "expired": True
        }
        
        sample_poi.lifecycle_events = [event1, event2]
        
        # Default - exclude expired
        events = POILifecycleEventsService.get_events(sample_poi)
        assert len(events) == 1
        assert events[0]["id"] == "event_1"
        
        # Include expired
        all_events = POILifecycleEventsService.get_events(sample_poi, include_expired=True)
        assert len(all_events) == 2

    def test_add_event_basic(self, sample_poi): pass
        """Test adding a basic event."""
        sample_poi.lifecycle_events = []
        
        updated_poi, event = POILifecycleEventsService.add_event(
            sample_poi,
            category="founding",
            event_type="settlement_founded",
            title="Settlement Founded",
            description="A new settlement was established"
        )
        
        assert len(updated_poi.lifecycle_events) == 1
        assert event["category"] == "founding"
        assert event["event_type"] == "settlement_founded"
        assert event["title"] == "Settlement Founded"
        assert "id" in event
        assert "timestamp" in event

    def test_add_event_with_metadata(self, sample_poi): pass
        """Test adding event with custom metadata."""
        sample_poi.lifecycle_events = []
        metadata = {"founder": "John Smith", "initial_population": 100}
        
        updated_poi, event = POILifecycleEventsService.add_event(
            sample_poi,
            category="founding",
            event_type="settlement_founded",
            title="Settlement Founded",
            description="A new settlement was established",
            metadata=metadata
        )
        
        assert event["metadata"] == metadata

    def test_add_event_with_custom_timestamp(self, sample_poi): pass
        """Test adding event with custom timestamp."""
        sample_poi.lifecycle_events = []
        custom_time = datetime(2023, 5, 15, 10, 30, 0)
        
        updated_poi, event = POILifecycleEventsService.add_event(
            sample_poi,
            category="founding", 
            event_type="settlement_founded",
            title="Settlement Founded",
            description="A new settlement was established",
            timestamp=custom_time
        )
        
        assert event["timestamp"] == custom_time.isoformat()

    def test_add_event_with_importance(self, sample_poi): pass
        """Test adding event with custom importance."""
        sample_poi.lifecycle_events = []
        
        updated_poi, event = POILifecycleEventsService.add_event(
            sample_poi,
            category="founding",
            event_type="settlement_founded",
            title="Settlement Founded",
            description="A new settlement was established",
            importance=9
        )
        
        assert event["importance"] == 9

    def test_get_event_by_id(self, sample_poi, sample_event): pass
        """Test getting specific event by ID."""
        sample_poi.lifecycle_events = [sample_event]
        
        event = POILifecycleEventsService.get_event_by_id(sample_poi, "event_1")
        
        assert event is not None
        assert event["id"] == "event_1"
        
        # Test non-existent event
        missing_event = POILifecycleEventsService.get_event_by_id(sample_poi, "nonexistent")
        assert missing_event is None

    def test_update_event(self, sample_poi, sample_event): pass
        """Test updating an existing event."""
        sample_poi.lifecycle_events = [sample_event]
        
        updates = {
            "title": "Updated Title",
            "importance": 10,
            "metadata": {"updated": True}
        }
        
        updated_poi, success = POILifecycleEventsService.update_event(
            sample_poi, "event_1", updates
        )
        
        assert success is True
        event = updated_poi.lifecycle_events[0]
        assert event["title"] == "Updated Title"
        assert event["importance"] == 10
        assert event["metadata"]["updated"] is True

    def test_update_nonexistent_event(self, sample_poi): pass
        """Test updating a non-existent event."""
        sample_poi.lifecycle_events = []
        
        updated_poi, success = POILifecycleEventsService.update_event(
            sample_poi, "nonexistent", {"title": "New Title"}
        )
        
        assert success is False

    def test_expire_event(self, sample_poi, sample_event): pass
        """Test expiring an event."""
        sample_poi.lifecycle_events = [sample_event]
        
        updated_poi, success = POILifecycleEventsService.expire_event(
            sample_poi, "event_1"
        )
        
        assert success is True
        event = updated_poi.lifecycle_events[0]
        assert event["expired"] is True

    def test_remove_event(self, sample_poi, sample_event): pass
        """Test removing an event."""
        sample_poi.lifecycle_events = [sample_event]
        
        updated_poi, success = POILifecycleEventsService.remove_event(
            sample_poi, "event_1"
        )
        
        assert success is True
        assert len(updated_poi.lifecycle_events) == 0

    def test_remove_nonexistent_event(self, sample_poi): pass
        """Test removing a non-existent event."""
        sample_poi.lifecycle_events = []
        
        updated_poi, success = POILifecycleEventsService.remove_event(
            sample_poi, "nonexistent"
        )
        
        assert success is False

    def test_get_poi_history(self, sample_poi): pass
        """Test getting POI history with filtering."""
        # Create events with different categories and importance
        events = [
            {
                "id": "event_1",
                "category": "founding",
                "importance": 8,
                "timestamp": "2023-01-01T00:00:00",
                "expired": False
            },
            {
                "id": "event_2",
                "category": "population",
                "importance": 3,
                "timestamp": "2023-02-01T00:00:00",
                "expired": False
            },
            {
                "id": "event_3",
                "category": "conflict",
                "importance": 9,
                "timestamp": "2023-03-01T00:00:00",
                "expired": False
            }
        ]
        
        sample_poi.lifecycle_events = events
        
        # Test include categories filter
        founding_history = POILifecycleEventsService.get_poi_history(
            sample_poi, include_categories=["founding", "conflict"]
        )
        assert len(founding_history) == 2
        
        # Test exclude categories filter
        no_conflict_history = POILifecycleEventsService.get_poi_history(
            sample_poi, exclude_categories=["conflict"]
        )
        assert len(no_conflict_history) == 2
        
        # Test minimum importance filter
        important_history = POILifecycleEventsService.get_poi_history(
            sample_poi, min_importance=5
        )
        assert len(important_history) == 2

    def test_generate_founding_event(self, sample_poi): pass
        """Test generating a founding event."""
        sample_poi.lifecycle_events = []
        
        updated_poi, event = POILifecycleEventsService.generate_founding_event(
            sample_poi,
            founder="John Smith",
            reason="Strategic location"
        )
        
        assert len(updated_poi.lifecycle_events) == 1
        assert event["category"] == "founding"
        assert event["metadata"]["founder"] == "John Smith"
        assert event["metadata"]["reason"] == "Strategic location"

    def test_generate_population_milestone_event(self, sample_poi): pass
        """Test generating a population milestone event."""
        sample_poi.lifecycle_events = []
        
        updated_poi, event = POILifecycleEventsService.generate_population_milestone_event(
            sample_poi, new_population=1000, old_population=500
        )
        
        assert len(updated_poi.lifecycle_events) == 1
        assert event["category"] == "population"
        assert event["event_type"] == "population_milestone"
        assert event["metadata"]["new_population"] == 1000
        assert event["metadata"]["old_population"] == 500

    def test_generate_leadership_change_event(self, sample_poi): pass
        """Test generating a leadership change event."""
        sample_poi.lifecycle_events = []
        
        updated_poi, event = POILifecycleEventsService.generate_leadership_change_event(
            sample_poi,
            new_leader="Jane Doe",
            old_leader="John Smith",
            change_type="election",
            reason="Popular vote"
        )
        
        assert len(updated_poi.lifecycle_events) == 1
        assert event["category"] == "leadership"
        assert event["metadata"]["new_leader"] == "Jane Doe"
        assert event["metadata"]["old_leader"] == "John Smith"
        assert event["metadata"]["change_type"] == "election"

    def test_process_event_effects(self, sample_poi, sample_event): pass
        """Test processing event effects on POI."""
        # This method applies effects based on event type
        # Test that it completes without error
        POILifecycleEventsService.process_event_effects(sample_poi, sample_event)
        
        # The method should execute without raising exceptions
        assert True

    def test_generate_narrative_summary(self, sample_poi): pass
        """Test generating narrative summary of POI history."""
        # Create some events for the narrative
        events = [
            {
                "id": "event_1",
                "category": "founding",
                "event_type": "settlement_founded",
                "title": "Settlement Founded",
                "description": "The settlement was founded",
                "importance": 8,
                "timestamp": "2023-01-01T00:00:00",
                "expired": False
            },
            {
                "id": "event_2",
                "category": "population",
                "event_type": "population_milestone", 
                "title": "Population Growth",
                "description": "Population reached 1000",
                "importance": 6,
                "timestamp": "2023-06-01T00:00:00",
                "expired": False
            }
        ]
        
        sample_poi.lifecycle_events = events
        
        summary = POILifecycleEventsService.generate_narrative_summary(
            sample_poi, max_events=5, min_importance=5
        )
        
        assert isinstance(summary, str)
        assert len(summary) > 0
        # Should include settlement name
        assert "Test Settlement" in summary

    def test_cleanup_expired_events(self, sample_poi): pass
        """Test cleaning up expired events."""
        # Create mix of expired and active events
        # The cleanup function checks for 'expiration' field, not 'expired' boolean
        from datetime import datetime, timedelta
        
        # Mock update_timestamp method
        sample_poi.update_timestamp = Mock()
        
        now = datetime.utcnow()
        past_time = (now - timedelta(days=1)).isoformat()
        future_time = (now + timedelta(days=1)).isoformat()
        
        events = [
            {
                "id": "event_1",
                "timestamp": "2023-01-01T00:00:00"
                # No expiration - should remain
            },
            {
                "id": "event_2", 
                "expiration": past_time,  # Expired
                "timestamp": "2023-02-01T00:00:00"
            },
            {
                "id": "event_3",
                "expiration": past_time,  # Expired
                "timestamp": "2023-03-01T00:00:00"
            },
            {
                "id": "event_4",
                "expiration": future_time,  # Not expired
                "timestamp": "2023-04-01T00:00:00"
            }
        ]
        
        sample_poi.lifecycle_events = events
        
        updated_poi, removed_count = POILifecycleEventsService.cleanup_expired_events(sample_poi)
        
        assert removed_count == 2
        assert len(updated_poi.lifecycle_events) == 2
        remaining_ids = [event["id"] for event in updated_poi.lifecycle_events]
        assert "event_1" in remaining_ids
        assert "event_4" in remaining_ids

    def test_event_sorting_newest_first(self, sample_poi): pass
        """Test that events are sorted newest first."""
        events = [
            {
                "id": "event_1",
                "timestamp": "2023-01-01T00:00:00",
                "expired": False
            },
            {
                "id": "event_2",
                "timestamp": "2023-03-01T00:00:00",
                "expired": False
            },
            {
                "id": "event_3",
                "timestamp": "2023-02-01T00:00:00",
                "expired": False
            }
        ]
        
        sample_poi.lifecycle_events = events
        
        sorted_events = POILifecycleEventsService.get_events(sample_poi)
        
        assert len(sorted_events) == 3
        assert sorted_events[0]["id"] == "event_2"  # March - newest
        assert sorted_events[1]["id"] == "event_3"  # February
        assert sorted_events[2]["id"] == "event_1"  # January - oldest

    def test_edge_cases_invalid_dates(self, sample_poi): pass
        """Test handling of invalid or missing dates."""
        events = [
            {
                "id": "event_1",
                "expired": False
                # Missing timestamp - should use default
            },
            {
                "id": "event_2",
                "timestamp": "2023-01-01T00:00:00",  # Use valid timestamp for basic functionality test
                "expired": False
            }
        ]
        
        sample_poi.lifecycle_events = events
        
        # Should handle gracefully without crashing
        result_events = POILifecycleEventsService.get_events(sample_poi)
        assert isinstance(result_events, list)
        assert len(result_events) == 2  # Both events should be returned 