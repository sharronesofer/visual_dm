from datetime import date
from datetime import datetime
"""
Tests for dialogue time integration module.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from backend.systems.dialogue.time_integration import DialogueTimeIntegration, CalendarManagerStub


class TestCalendarManagerStub:
    """Test suite for CalendarManagerStub class."""

    @pytest.fixture
    def calendar_stub(self):
        """Create a calendar manager stub."""
        return CalendarManagerStub()

    def test_get_instance(self, calendar_stub):
        """Test getting calendar manager instance."""
        result = calendar_stub.get_instance()
        assert result == calendar_stub

    def test_get_event_returns_none(self, calendar_stub):
        """Test getting event returns None (stub implementation)."""
        result = calendar_stub.get_event("event_1", "location_1")
        assert result is None

    def test_get_current_season(self, calendar_stub):
        """Test getting current season information."""
        current_time = {"hour": 12, "day": 1}
        result = calendar_stub.get_current_season(current_time)
        
        assert result["name"] == "spring"
        assert "description" in result
        assert "progress" in result
        assert "weather_tendencies" in result
        assert "typical_activities" in result
        assert "seasonal_foods" in result

    def test_get_events_in_range_returns_empty(self, calendar_stub):
        """Test getting events in range returns empty list (stub implementation)."""
        start_time = {"hour": 12, "day": 1}
        end_time = {"hour": 12, "day": 8}
        result = calendar_stub.get_events_in_range(start_time, end_time, "location_1")
        assert result == []

    def test_get_current_events_returns_empty(self, calendar_stub):
        """Test getting current events returns empty list (stub implementation)."""
        current_time = {"hour": 12, "day": 1}
        result = calendar_stub.get_current_events(current_time, "location_1", ["festival"])
        assert result == []


class TestDialogueTimeIntegration:
    """Test suite for DialogueTimeIntegration class."""

    @pytest.fixture
    def mock_time_manager(self):
        """Create a mock time manager."""
        manager = Mock()
        manager.get_current_time.return_value = {
            "date": "2024-01-15",
            "day_number": 15,
            "day_name": "Monday",
            "month_number": 1,
            "month_name": "January",
            "year": 2024,
            "hour": 10,
            "minute": 30
        }
        manager.add_days.return_value = {
            "date": "2024-01-22",
            "day_number": 22,
            "day_name": "Monday",
            "month_number": 1,
            "month_name": "January",
            "year": 2024,
            "hour": 10,
            "minute": 30
        }
        manager.get_days_between.return_value = 3
        return manager

    @pytest.fixture
    def mock_calendar_manager(self):
        """Create a mock calendar manager."""
        manager = Mock()
        manager.get_event.return_value = {
            "id": "event_1",
            "name": "Test Festival",
            "description": "A test festival",
            "start_time": {"date": "2024-01-18"},
            "end_time": {"date": "2024-01-20"},
            "location": "Test Town",
            "recurring": True,
            "importance": "high",
            "tags": ["festival"],
            "participants": ["character_1"]
        }
        manager.get_current_season.return_value = {
            "name": "winter",
            "description": "A cold winter season",
            "progress": 0.75,
            "weather_tendencies": ["cold", "snowy"],
            "typical_activities": ["indoor work", "firewood gathering"],
            "seasonal_foods": ["preserved meats", "root vegetables"]
        }
        manager.get_events_in_range.return_value = [
            {
                "id": "event_1",
                "name": "Test Festival",
                "description": "A test festival",
                "start_time": {"date": "2024-01-18"},
                "location": "Test Town",
                "importance": "high"
            }
        ]
        manager.get_current_events.return_value = [
            {
                "id": "festival_1",
                "name": "Winter Festival",
                "description": "A winter celebration",
                "end_time": {"date": "2024-01-16"},
                "location": "Test Town",
                "importance": 5,
                "activities": ["dancing", "feasting"],
                "significance": "Celebrates the winter solstice"
            }
        ]
        return manager

    @pytest.fixture
    def integration(self, mock_calendar_manager, mock_time_manager):
        """Create a dialogue time integration instance with mocks."""
        return DialogueTimeIntegration(
            calendar_manager=mock_calendar_manager,
            time_manager=mock_time_manager
        )

    def test_init_with_managers(self, mock_calendar_manager, mock_time_manager):
        """Test initialization with provided managers."""
        integration = DialogueTimeIntegration(
            calendar_manager=mock_calendar_manager,
            time_manager=mock_time_manager
        )
        assert integration.calendar_manager == mock_calendar_manager
        assert integration.time_manager == mock_time_manager

    @patch('backend.systems.dialogue.time_integration.TimeManager')
    def test_init_with_defaults(self, mock_time_manager_class):
        """Test initialization with default managers."""
        mock_time_manager_class.get_instance.return_value = Mock()
        integration = DialogueTimeIntegration()
        assert isinstance(integration.calendar_manager, CalendarManagerStub)
        assert integration.time_manager is not None

    def test_add_time_context_to_dialogue_full(self, integration):
        """Test adding comprehensive time context to dialogue."""
        context = {"existing": "data"}
        
        result = integration.add_time_context_to_dialogue(
            context=context,
            location_id="location_1",
            include_events=True,
            events_lookahead_days=10,
            include_season=True
        )
        
        assert "existing" in result
        assert "time" in result
        assert "current_date" in result["time"]
        assert "time_of_day" in result["time"]
        assert "season" in result["time"]
        assert "upcoming_events" in result["time"]

    def test_add_time_context_to_dialogue_minimal(self, integration):
        """Test adding minimal time context to dialogue."""
        context = {}
        
        result = integration.add_time_context_to_dialogue(
            context=context,
            include_events=False,
            include_season=False
        )
        
        assert "time" in result
        assert "current_date" in result["time"]
        assert "season" not in result["time"]
        assert "upcoming_events" not in result["time"]

    def test_add_time_context_existing_time_context(self, integration):
        """Test adding time context when time context already exists."""
        context = {"time": {"existing_time_data": "value"}}
        
        result = integration.add_time_context_to_dialogue(context)
        
        assert "existing_time_data" in result["time"]
        assert "current_date" in result["time"]

    def test_get_time_references_season(self, integration):
        """Test getting season time references."""
        result = integration.get_time_references_for_dialogue("season")
        
        assert "name" in result
        assert "description" in result
        assert "progress" in result
        assert result["name"] == "winter"

    def test_get_time_references_festival(self, integration):
        """Test getting festival time references."""
        result = integration.get_time_references_for_dialogue("festival", "location_1")
        
        assert "id" in result
        assert "name" in result
        assert "activities" in result

    def test_get_time_references_day_period(self, integration):
        """Test getting day period time references."""
        result = integration.get_time_references_for_dialogue("day_period")
        
        assert "name" in result
        assert "lighting" in result
        assert "is_day" in result
        assert "typical_activities" in result

    def test_get_time_references_weather(self, integration):
        """Test getting weather time references."""
        result = integration.get_time_references_for_dialogue("weather", "location_1")
        
        assert "condition" in result
        assert "temperature" in result
        assert "precipitation" in result

    def test_get_time_references_unknown_type(self, integration):
        """Test getting time references for unknown type."""
        result = integration.get_time_references_for_dialogue("unknown_type")
        assert result == {}

    @patch('backend.systems.dialogue.time_integration.logger')
    def test_get_time_references_exception_handling(self, mock_logger, integration):
        """Test exception handling in get_time_references_for_dialogue."""
        integration.time_manager.get_current_time.side_effect = Exception("Test error")
        
        result = integration.get_time_references_for_dialogue("day_period")
        
        assert result == {}
        mock_logger.error.assert_called()

    def test_get_event_dialogue_context_success(self, integration):
        """Test getting event dialogue context successfully."""
        result = integration.get_event_dialogue_context("event_1", "location_1")
        
        assert result["id"] == "event_1"
        assert result["name"] == "Test Festival"
        assert result["description"] == "A test festival"
        assert result["recurring"] is True
        assert result["importance"] == "high"

    def test_get_event_dialogue_context_not_found(self, integration):
        """Test getting event dialogue context when event not found."""
        integration.calendar_manager.get_event.return_value = None
        
        result = integration.get_event_dialogue_context("nonexistent", "location_1")
        assert result == {}

    @patch('backend.systems.dialogue.time_integration.logger')
    def test_get_event_dialogue_context_exception(self, mock_logger, integration):
        """Test exception handling in get_event_dialogue_context."""
        integration.calendar_manager.get_event.side_effect = Exception("Test error")
        
        result = integration.get_event_dialogue_context("event_1")
        
        assert result == {}
        mock_logger.error.assert_called()

    def test_get_time_sensitive_dialogue_options_morning(self, integration):
        """Test getting morning time-sensitive dialogue options."""
        integration.time_manager.get_current_time.return_value = {
            "hour": 8, "day_name": "Monday"
        }
        
        result = integration.get_time_sensitive_dialogue_options(
            character_id="char_1",
            dialogue_type="greeting"
        )
        
        assert len(result) >= 1
        morning_option = next((opt for opt in result if opt["time_relevance"] == "morning"), None)
        assert morning_option is not None
        assert "Good morning" in morning_option["text"]

    def test_get_time_sensitive_dialogue_options_afternoon(self, integration):
        """Test getting afternoon time-sensitive dialogue options."""
        integration.time_manager.get_current_time.return_value = {
            "hour": 14, "day_name": "Tuesday"
        }
        
        result = integration.get_time_sensitive_dialogue_options(
            character_id="char_1",
            dialogue_type="greeting"
        )
        
        afternoon_option = next((opt for opt in result if opt["time_relevance"] == "afternoon"), None)
        assert afternoon_option is not None
        assert "Good afternoon" in afternoon_option["text"]

    def test_get_time_sensitive_dialogue_options_evening(self, integration):
        """Test getting evening time-sensitive dialogue options."""
        integration.time_manager.get_current_time.return_value = {
            "hour": 19, "day_name": "Wednesday"
        }
        
        result = integration.get_time_sensitive_dialogue_options(
            character_id="char_1",
            dialogue_type="greeting"
        )
        
        evening_option = next((opt for opt in result if opt["time_relevance"] == "evening"), None)
        assert evening_option is not None
        assert "Good evening" in evening_option["text"]

    def test_get_time_sensitive_dialogue_options_night(self, integration):
        """Test getting night time-sensitive dialogue options."""
        integration.time_manager.get_current_time.return_value = {
            "hour": 23, "day_name": "Thursday"
        }
        
        result = integration.get_time_sensitive_dialogue_options(
            character_id="char_1",
            dialogue_type="greeting"
        )
        
        night_option = next((opt for opt in result if opt["time_relevance"] == "night"), None)
        assert night_option is not None
        assert "up late tonight" in night_option["text"]

    def test_get_time_sensitive_dialogue_options_with_season(self, integration):
        """Test getting dialogue options that include season references."""
        result = integration.get_time_sensitive_dialogue_options(
            character_id="char_1",
            dialogue_type="greeting"
        )
        
        # Should include season-specific option
        season_option = next((opt for opt in result if "season_" in opt["time_relevance"]), None)
        assert season_option is not None
        assert "winter weather" in season_option["text"]

    @patch('backend.systems.dialogue.time_integration.logger')
    def test_get_time_sensitive_dialogue_options_exception(self, mock_logger, integration):
        """Test exception handling in get_time_sensitive_dialogue_options."""
        integration.time_manager.get_current_time.side_effect = Exception("Test error")
        
        result = integration.get_time_sensitive_dialogue_options("char_1")
        
        assert result == []
        mock_logger.error.assert_called()

    def test_get_current_time_info_success(self, integration):
        """Test getting current time info successfully."""
        result = integration._get_current_time_info()
        
        assert result["current_date"] == "2024-01-15"
        assert result["day_number"] == 15
        assert result["day_name"] == "Monday"
        assert result["month_name"] == "January"
        assert result["year"] == 2024
        assert result["hour"] == 10
        assert result["minute"] == 30
        assert result["time_of_day"] == "morning"
        assert result["is_day"] is True

    @patch('backend.systems.dialogue.time_integration.logger')
    def test_get_current_time_info_exception(self, mock_logger, integration):
        """Test exception handling in _get_current_time_info."""
        integration.time_manager.get_current_time.side_effect = Exception("Test error")
        
        result = integration._get_current_time_info()
        
        assert result["current_date"] == "Unknown"
        assert result["time_of_day"] == "unknown"
        assert result["is_day"] is True
        mock_logger.error.assert_called()

    def test_get_season_info_success(self, integration):
        """Test getting season info successfully."""
        result = integration._get_season_info()
        
        assert result["name"] == "winter"
        assert result["description"] == "A cold winter season"
        assert result["progress"] == 0.75
        assert "cold" in result["weather_tendencies"]
        assert "indoor work" in result["typical_activities"]
        assert "preserved meats" in result["seasonal_foods"]

    @patch('backend.systems.dialogue.time_integration.logger')
    def test_get_season_info_exception(self, mock_logger, integration):
        """Test exception handling in _get_season_info."""
        integration.time_manager.get_current_time.side_effect = Exception("Test error")
        
        result = integration._get_season_info()
        
        assert result["name"] == "unknown"
        assert result["description"] == "The current season"
        mock_logger.error.assert_called()

    def test_get_upcoming_events_success(self, integration):
        """Test getting upcoming events successfully."""
        result = integration._get_upcoming_events("location_1", 7)
        
        assert len(result) == 1
        event = result[0]
        assert event["id"] == "event_1"
        assert event["name"] == "Test Festival"
        assert event["days_until"] == 3
        assert event["importance"] == "high"

    def test_get_upcoming_events_no_location(self, integration):
        """Test getting upcoming events without specific location."""
        result = integration._get_upcoming_events(days_ahead=14)
        
        assert len(result) == 1
        assert result[0]["name"] == "Test Festival"

    @patch('backend.systems.dialogue.time_integration.logger')
    def test_get_upcoming_events_exception(self, mock_logger, integration):
        """Test exception handling in _get_upcoming_events."""
        integration.time_manager.get_current_time.side_effect = Exception("Test error")
        
        result = integration._get_upcoming_events()
        
        assert result == []
        mock_logger.error.assert_called()

    def test_get_current_festival_info_success(self, integration):
        """Test getting current festival info successfully."""
        result = integration._get_current_festival_info("location_1")
        
        assert result["id"] == "festival_1"
        assert result["name"] == "Winter Festival"
        assert result["description"] == "A winter celebration"
        assert "dancing" in result["activities"]
        assert result["significance"] == "Celebrates the winter solstice"

    def test_get_current_festival_info_no_festivals(self, integration):
        """Test getting current festival info when no festivals are happening."""
        integration.calendar_manager.get_current_events.return_value = []
        
        result = integration._get_current_festival_info("location_1")
        assert result == {}

    def test_get_current_festival_info_multiple_festivals(self, integration):
        """Test getting current festival info with multiple festivals (returns most important)."""
        integration.calendar_manager.get_current_events.return_value = [
            {
                "id": "festival_1",
                "name": "Minor Festival",
                "importance": 3,
                "activities": [],
                "significance": ""
            },
            {
                "id": "festival_2", 
                "name": "Major Festival",
                "importance": 8,
                "activities": ["celebration"],
                "significance": "Very important"
            }
        ]
        
        result = integration._get_current_festival_info("location_1")
        assert result["id"] == "festival_2"
        assert result["name"] == "Major Festival"

    @patch('backend.systems.dialogue.time_integration.logger')
    def test_get_current_festival_info_exception(self, mock_logger, integration):
        """Test exception handling in _get_current_festival_info."""
        integration.time_manager.get_current_time.side_effect = Exception("Test error")
        
        result = integration._get_current_festival_info()
        
        assert result == {}
        mock_logger.error.assert_called()

    def test_get_day_period_info_morning(self, integration):
        """Test getting day period info for morning."""
        integration.time_manager.get_current_time.return_value = {"hour": 8}
        
        result = integration._get_day_period_info()
        
        assert result["name"] == "morning"
        assert result["lighting"] == "normal"
        assert result["is_day"] is True
        assert "breakfast" in result["typical_activities"]

    def test_get_day_period_info_bright_midday(self, integration):
        """Test getting day period info for bright midday."""
        integration.time_manager.get_current_time.return_value = {"hour": 12}
        
        result = integration._get_day_period_info()
        
        assert result["name"] == "afternoon"
        assert result["lighting"] == "bright"
        assert result["is_day"] is True

    def test_get_day_period_info_dim_twilight(self, integration):
        """Test getting day period info for dim twilight."""
        integration.time_manager.get_current_time.return_value = {"hour": 18}
        
        result = integration._get_day_period_info()
        
        assert result["name"] == "evening"
        assert result["lighting"] == "dim"
        assert result["is_day"] is True

    def test_get_day_period_info_night(self, integration):
        """Test getting day period info for night."""
        integration.time_manager.get_current_time.return_value = {"hour": 2}
        
        result = integration._get_day_period_info()
        
        assert result["name"] == "night"
        assert result["lighting"] == "dark"
        assert result["is_day"] is False
        assert "sleeping" in result["typical_activities"]

    @patch('backend.systems.dialogue.time_integration.logger')
    def test_get_day_period_info_exception(self, mock_logger, integration):
        """Test exception handling in _get_day_period_info."""
        integration.time_manager.get_current_time.side_effect = Exception("Test error")
        
        result = integration._get_day_period_info()
        
        assert result["name"] == "unknown"
        assert result["is_day"] is True
        mock_logger.error.assert_called()

    def test_get_weather_info_success(self, integration):
        """Test getting weather info successfully."""
        result = integration._get_weather_info("location_1")
        
        assert result["condition"] == "clear"
        assert result["temperature"] == "mild"
        assert result["precipitation"] == "none"
        assert result["wind"] == "light"
        assert result["affects_visibility"] is False
        assert result["affects_travel"] is False
        assert "pleasant" in result["description"]

    def test_get_weather_info_no_location(self, integration):
        """Test getting weather info without specific location."""
        result = integration._get_weather_info()
        
        assert "condition" in result
        assert "temperature" in result

    @patch('backend.systems.dialogue.time_integration.logger')
    def test_get_weather_info_exception(self, mock_logger, integration):
        """Test exception handling in _get_weather_info."""
        # Mock the time_manager to raise an exception
        integration.time_manager.get_current_time.side_effect = Exception("Test error")
        
        result = integration._get_weather_info()
        
        assert result["condition"] == "unknown"
        mock_logger.error.assert_called()

    def test_get_time_of_day_morning(self, integration):
        """Test determining time of day for morning hours."""
        assert integration._get_time_of_day(5) == "morning"
        assert integration._get_time_of_day(8) == "morning"
        assert integration._get_time_of_day(11) == "morning"

    def test_get_time_of_day_afternoon(self, integration):
        """Test determining time of day for afternoon hours."""
        assert integration._get_time_of_day(12) == "afternoon"
        assert integration._get_time_of_day(14) == "afternoon"
        assert integration._get_time_of_day(16) == "afternoon"

    def test_get_time_of_day_evening(self, integration):
        """Test determining time of day for evening hours."""
        assert integration._get_time_of_day(17) == "evening"
        assert integration._get_time_of_day(19) == "evening"
        assert integration._get_time_of_day(20) == "evening"

    def test_get_time_of_day_night(self, integration):
        """Test determining time of day for night hours."""
        assert integration._get_time_of_day(21) == "night"
        assert integration._get_time_of_day(0) == "night"
        assert integration._get_time_of_day(4) == "night"

    def test_is_daytime_true(self, integration):
        """Test daytime detection for day hours."""
        assert integration._is_daytime(6) is True
        assert integration._is_daytime(12) is True
        assert integration._is_daytime(19) is True

    def test_is_daytime_false(self, integration):
        """Test daytime detection for night hours."""
        assert integration._is_daytime(5) is False
        assert integration._is_daytime(20) is False
        assert integration._is_daytime(0) is False

    def test_get_typical_activities_for_time_morning(self, integration):
        """Test getting typical activities for morning."""
        activities = integration._get_typical_activities_for_time("morning")
        assert "breakfast" in activities
        assert "commuting" in activities
        assert "opening shops" in activities
        assert "morning chores" in activities

    def test_get_typical_activities_for_time_afternoon(self, integration):
        """Test getting typical activities for afternoon."""
        activities = integration._get_typical_activities_for_time("afternoon")
        assert "lunch" in activities
        assert "working" in activities
        assert "shopping" in activities
        assert "traveling" in activities

    def test_get_typical_activities_for_time_evening(self, integration):
        """Test getting typical activities for evening."""
        activities = integration._get_typical_activities_for_time("evening")
        assert "dinner" in activities
        assert "returning home" in activities
        assert "socializing" in activities
        assert "entertainment" in activities

    def test_get_typical_activities_for_time_night(self, integration):
        """Test getting typical activities for night."""
        activities = integration._get_typical_activities_for_time("night")
        assert "sleeping" in activities
        assert "guarding" in activities
        assert "night work" in activities
        assert "stargazing" in activities

    def test_get_typical_activities_for_time_unknown(self, integration):
        """Test getting typical activities for unknown time."""
        activities = integration._get_typical_activities_for_time("unknown")
        assert activities == [] 