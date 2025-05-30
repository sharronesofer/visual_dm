from dataclasses import field
"""
Tests for backend.systems.world_state.utils.newspaper_system

Comprehensive tests for the newspaper system functionality.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Import the module being tested
try:
    from backend.systems.world_state.utils.newspaper_system import Newspaper
except ImportError as e:
    pytest.skip(f"Could not import backend.systems.world_state.utils.newspaper_system: {e}", allow_module_level=True)


class TestNewspaperInitialization:
    """Test Newspaper class initialization."""

    def test_init_without_region(self):
        """Test newspaper initialization without region."""
        newspaper = Newspaper()
        
        assert newspaper.region is None
        assert newspaper.articles == []

    def test_init_with_region(self):
        """Test newspaper initialization with region."""
        region = "test_region"
        newspaper = Newspaper(region=region)
        
        assert newspaper.region == region
        assert newspaper.articles == []


class TestFetchRecentEvents:
    """Test fetch_recent_events method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.newspaper = Newspaper()
        self.mock_events = {
            "event1": {
                "type": "war",
                "region_id": "region1",
                "severity": 5,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": "War breaks out",
                "details": "A major conflict has begun"
            },
            "event2": {
                "type": "trade",
                "region_id": "region2", 
                "severity": 2,
                "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                "summary": "Trade agreement signed",
                "details": "New trade routes established"
            },
            "event3": {
                "type": "festival",
                "region_id": "region1",
                "severity": 3,
                "timestamp": (datetime.utcnow() - timedelta(hours=12)).isoformat(),
                "summary": "Festival celebration",
                "details": "Annual harvest festival"
            }
        }

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_fetch_recent_events_all_events(self, mock_db):
        """Test fetching all recent events without filters."""
        mock_db.reference.return_value.get.return_value = self.mock_events
        
        events = self.newspaper.fetch_recent_events()
        
        # Should return events from the last day
        assert len(events) == 2  # event1 and event3 (event2 is 2 days old)
        mock_db.reference.assert_called_with("/global_state/world_log")

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_fetch_recent_events_with_region_filter(self, mock_db):
        """Test fetching events filtered by region."""
        mock_db.reference.return_value.get.return_value = self.mock_events
        
        newspaper = Newspaper(region="region1")
        events = newspaper.fetch_recent_events()
        
        # Should only return events from region1
        assert len(events) == 2  # event1 and event3
        for event in events:
            assert event["region_id"] == "region1"

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_fetch_recent_events_with_severity_filter(self, mock_db):
        """Test fetching events filtered by minimum severity."""
        mock_db.reference.return_value.get.return_value = self.mock_events
        
        events = self.newspaper.fetch_recent_events(severity_min=4)
        
        # Should only return events with severity >= 4
        assert len(events) == 1  # Only event1 has severity 5
        assert events[0]["severity"] == 5

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_fetch_recent_events_with_type_filter(self, mock_db):
        """Test fetching events filtered by event type."""
        mock_db.reference.return_value.get.return_value = self.mock_events
        
        events = self.newspaper.fetch_recent_events(event_type="war")
        
        # Should only return war events
        assert len(events) == 1
        assert events[0]["type"] == "war"

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_fetch_recent_events_with_days_filter(self, mock_db):
        """Test fetching events filtered by number of days."""
        mock_db.reference.return_value.get.return_value = self.mock_events
        
        events = self.newspaper.fetch_recent_events(days=3)
        
        # Should return all events within 3 days
        assert len(events) == 3

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_fetch_recent_events_combined_filters(self, mock_db):
        """Test fetching events with multiple filters combined."""
        mock_db.reference.return_value.get.return_value = self.mock_events
        
        newspaper = Newspaper(region="region1")
        events = newspaper.fetch_recent_events(severity_min=4, event_type="war")
        
        # Should return events matching all criteria
        assert len(events) == 1
        assert events[0]["type"] == "war"
        assert events[0]["region_id"] == "region1"
        assert events[0]["severity"] == 5

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_fetch_recent_events_no_events(self, mock_db):
        """Test fetching events when no events exist."""
        mock_db.reference.return_value.get.return_value = None
        
        events = self.newspaper.fetch_recent_events()
        
        assert events == []

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_fetch_recent_events_empty_events(self, mock_db):
        """Test fetching events when events dict is empty."""
        mock_db.reference.return_value.get.return_value = {}
        
        events = self.newspaper.fetch_recent_events()
        
        assert events == []

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_fetch_recent_events_missing_timestamp(self, mock_db):
        """Test fetching events when some events lack timestamps."""
        events_without_timestamp = {
            "event1": {
                "type": "war",
                "region_id": "region1",
                "severity": 5,
                "summary": "War breaks out"
                # No timestamp
            }
        }
        mock_db.reference.return_value.get.return_value = events_without_timestamp
        
        events = self.newspaper.fetch_recent_events()
        
        # Events without timestamps should be included
        assert len(events) == 1

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_fetch_recent_events_invalid_timestamp(self, mock_db):
        """Test fetching events with invalid timestamp format."""
        events_invalid_timestamp = {
            "event1": {
                "type": "war",
                "region_id": "region1", 
                "severity": 5,
                "timestamp": "invalid-timestamp",
                "summary": "War breaks out"
            }
        }
        mock_db.reference.return_value.get.return_value = events_invalid_timestamp
        
        # Should handle invalid timestamps gracefully
        events = self.newspaper.fetch_recent_events()
        
        # Event should still be included if timestamp parsing fails
        assert len(events) == 1


class TestFormatArticle:
    """Test format_article method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.newspaper = Newspaper()

    def test_format_article_complete_event(self):
        """Test formatting an event with all fields."""
        event = {
            "type": "war",
            "region_id": "region1",
            "summary": "Major battle erupts",
            "details": "A fierce battle has broken out between two factions",
            "byline": "War Correspondent",
            "timestamp": "2023-01-01T12:00:00"
        }
        
        article = self.newspaper.format_article(event)
        
        assert article["headline"] == "Major battle erupts"
        assert article["body"] == "A fierce battle has broken out between two factions"
        assert article["byline"] == "War Correspondent"
        assert article["date"] == "2023-01-01T12:00:00"

    def test_format_article_minimal_event(self):
        """Test formatting an event with minimal fields."""
        event = {
            "type": "trade",
            "region_id": "region2"
        }
        
        article = self.newspaper.format_article(event)
        
        assert article["headline"] == "Trade in region2!"
        assert article["body"] == "Details are scarce at this time."
        assert article["byline"] == "Staff Reporter"
        assert "date" in article  # Should have a default timestamp

    def test_format_article_no_summary_no_type(self):
        """Test formatting an event without summary or type."""
        event = {
            "region_id": "region3"
        }
        
        article = self.newspaper.format_article(event)
        
        assert article["headline"] == "Event in region3!"
        assert article["body"] == "Details are scarce at this time."
        assert article["byline"] == "Staff Reporter"

    def test_format_article_no_region(self):
        """Test formatting an event without region."""
        event = {
            "type": "festival",
            "summary": "Celebration begins"
        }
        
        article = self.newspaper.format_article(event)
        
        assert article["headline"] == "Celebration begins"

    def test_format_article_empty_event(self):
        """Test formatting an empty event."""
        event = {}
        
        article = self.newspaper.format_article(event)
        
        assert article["headline"] == "Event in the world!"
        assert article["body"] == "Details are scarce at this time."
        assert article["byline"] == "Staff Reporter"
        assert "date" in article

    def test_format_article_custom_fields(self):
        """Test formatting an event with custom field values."""
        event = {
            "summary": "Custom headline",
            "details": "Custom body content",
            "byline": "Custom Reporter",
            "timestamp": "2023-12-25T00:00:00"
        }
        
        article = self.newspaper.format_article(event)
        
        assert article["headline"] == "Custom headline"
        assert article["body"] == "Custom body content"
        assert article["byline"] == "Custom Reporter"
        assert article["date"] == "2023-12-25T00:00:00"


class TestPublishLatestEdition:
    """Test publish_latest_edition method."""

    def setup_method(self):
        """Set up test fixtures."""
        self.newspaper = Newspaper()
        self.mock_events = {
            "event1": {
                "type": "war",
                "region_id": "region1",
                "severity": 5,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": "War breaks out",
                "details": "A major conflict has begun"
            },
            "event2": {
                "type": "festival",
                "region_id": "region1",
                "severity": 3,
                "timestamp": (datetime.utcnow() - timedelta(hours=12)).isoformat(),
                "summary": "Festival celebration",
                "details": "Annual harvest festival"
            }
        }

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_publish_latest_edition_success(self, mock_db):
        """Test successful publication of latest edition."""
        mock_db.reference.return_value.get.return_value = self.mock_events
        
        articles = self.newspaper.publish_latest_edition()
        
        assert len(articles) == 2
        assert self.newspaper.articles == articles
        
        # Verify articles are properly formatted
        for article in articles:
            assert "headline" in article
            assert "body" in article
            assert "byline" in article
            assert "date" in article

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_publish_latest_edition_with_filters(self, mock_db):
        """Test publication with filters applied."""
        mock_db.reference.return_value.get.return_value = self.mock_events
        
        articles = self.newspaper.publish_latest_edition(severity_min=4)
        
        # Should only include high-severity events
        assert len(articles) == 1
        assert self.newspaper.articles == articles

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_publish_latest_edition_no_events(self, mock_db):
        """Test publication when no events are available."""
        mock_db.reference.return_value.get.return_value = {}
        
        articles = self.newspaper.publish_latest_edition()
        
        assert articles == []
        assert self.newspaper.articles == []

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_publish_latest_edition_multiple_calls(self, mock_db):
        """Test multiple calls to publish_latest_edition."""
        mock_db.reference.return_value.get.return_value = self.mock_events
        
        # First publication
        articles1 = self.newspaper.publish_latest_edition()
        
        # Second publication should replace the first
        articles2 = self.newspaper.publish_latest_edition(severity_min=5)
        
        assert len(articles1) == 2
        assert len(articles2) == 1
        assert self.newspaper.articles == articles2  # Should be the latest


class TestNewspaperIntegration:
    """Test integration scenarios for the Newspaper class."""

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_regional_newspaper_workflow(self, mock_db):
        """Test complete workflow for a regional newspaper."""
        # Setup regional events
        regional_events = {
            "event1": {
                "type": "war",
                "region_id": "kingdom_north",
                "severity": 8,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": "Northern Border Conflict Escalates",
                "details": "Tensions rise as border disputes turn violent",
                "byline": "Northern Correspondent"
            },
            "event2": {
                "type": "trade",
                "region_id": "kingdom_south",
                "severity": 3,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": "Southern Trade Routes Expand",
                "details": "New merchant agreements boost economy"
            },
            "event3": {
                "type": "festival",
                "region_id": "kingdom_north",
                "severity": 2,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": "Harvest Festival Cancelled",
                "details": "Due to ongoing conflicts, celebrations postponed"
            }
        }
        
        mock_db.reference.return_value.get.return_value = regional_events
        
        # Create regional newspaper
        northern_paper = Newspaper(region="kingdom_north")
        
        # Publish edition focusing on high-severity events
        articles = northern_paper.publish_latest_edition(severity_min=5)
        
        # Should only include the war event from the north
        assert len(articles) == 1
        assert articles[0]["headline"] == "Northern Border Conflict Escalates"
        assert "Northern Correspondent" in articles[0]["byline"]

    @patch('backend.systems.world_state.utils.newspaper_system.db')
    def test_global_newspaper_workflow(self, mock_db):
        """Test complete workflow for a global newspaper."""
        global_events = {
            "event1": {
                "type": "diplomatic",
                "region_id": "capital",
                "severity": 7,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": "Peace Treaty Signed",
                "details": "Historic agreement ends decade-long conflict"
            },
            "event2": {
                "type": "calamity",
                "region_id": "eastern_provinces",
                "severity": 9,
                "timestamp": datetime.utcnow().isoformat(),
                "summary": "Earthquake Devastates Eastern Provinces",
                "details": "Massive earthquake causes widespread destruction"
            }
        }
        
        mock_db.reference.return_value.get.return_value = global_events
        
        # Create global newspaper (no region filter)
        global_paper = Newspaper()
        
        # Publish comprehensive edition
        articles = global_paper.publish_latest_edition()
        
        # Should include all events
        assert len(articles) == 2
        headlines = [article["headline"] for article in articles]
        assert "Peace Treaty Signed" in headlines
        assert "Earthquake Devastates Eastern Provinces" in headlines


def test_module_imports():
    """Test that the module can be imported without errors."""
    from backend.systems.world_state.utils.newspaper_system import Newspaper
    assert Newspaper is not None
