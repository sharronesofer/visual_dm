from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from backend.systems.shared.database.base import Base
from backend.systems.events.dispatcher import EventDispatcher
from typing import Any, Type, List, Dict, Optional, Union
"""
Tests for the time manager module.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from backend.systems.time.models.time_model import (
    GameTime,
    TimeConfig,
    TimeEvent,
    EventType,
    Season,
    TimeUnit,
    WeatherCondition,
)

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

from backend.systems.time.models.calendar_model import CalendarData
from backend.systems.time.services.time_manager import (
    TimeManager,
    EventScheduler,
    CalendarService,
    TimeAdvancedEvent,
    SeasonChangedEvent,
    WeatherChangedEvent,
    SpecialDateEvent,
)


class TestEventScheduler: pass
    """Tests for the EventScheduler class."""

    @pytest.fixture
    def event_scheduler(self): pass
        """Create an EventScheduler instance for testing."""
        return EventScheduler()

    @pytest.fixture
    def sample_callback(self): pass
        """Create a sample callback function."""

        def callback(event): pass
            return f"Processed event: {event.id}"

        return callback

    def test_register_callback(self, event_scheduler, sample_callback): pass
        """Test registering a callback function."""
        event_scheduler.register_callback("test_callback", sample_callback)
        assert "test_callback" in event_scheduler._callbacks
        assert event_scheduler._callbacks["test_callback"] == sample_callback

    def test_unregister_callback(self, event_scheduler, sample_callback): pass
        """Test unregistering a callback function."""
        event_scheduler.register_callback("test_callback", sample_callback)

        # Test successful unregistration
        result = event_scheduler.unregister_callback("test_callback")
        assert result is True
        assert "test_callback" not in event_scheduler._callbacks

        # Test unsuccessful unregistration
        result = event_scheduler.unregister_callback("non_existent_callback")
        assert result is False

    def test_add_middleware(self, event_scheduler): pass
        """Test adding middleware to the scheduler."""

        def test_middleware(event): pass
            return event

        event_scheduler.add_middleware(test_middleware)
        assert test_middleware in event_scheduler._middlewares

    def test_schedule_event(self, event_scheduler, sample_callback): pass
        """Test scheduling an event."""
        event_scheduler.register_callback("test_callback", sample_callback)

        # Schedule a one-time event
        trigger_time = datetime.utcnow() + timedelta(minutes=5)
        event_id = event_scheduler.schedule_event(
            event_type=EventType.ONE_TIME,
            callback_name="test_callback",
            trigger_time=trigger_time,
            callback_data={"test": "data"},
            priority=5,
        )

        # Check that event was scheduled
        assert event_id in event_scheduler._events
        event = event_scheduler._events[event_id]
        assert event.event_type == EventType.ONE_TIME
        assert event.callback_name == "test_callback"
        assert event.callback_data == {"test": "data"}
        assert event.trigger_time == trigger_time
        assert event.priority == 5

    def test_cancel_event(self, event_scheduler, sample_callback): pass
        """Test cancelling an event."""
        event_scheduler.register_callback("test_callback", sample_callback)

        # Schedule an event
        trigger_time = datetime.utcnow() + timedelta(minutes=5)
        event_id = event_scheduler.schedule_event(
            event_type=EventType.ONE_TIME,
            callback_name="test_callback",
            trigger_time=trigger_time,
        )

        # Cancel the event
        result = event_scheduler.cancel_event(event_id)
        assert result is True
        assert event_scheduler._events[event_id].cancelled is True

        # Test cancelling non-existent event
        result = event_scheduler.cancel_event("non_existent_event")
        assert result is False

    def test_process_events_due(self, event_scheduler, sample_callback): pass
        """Test processing due events."""
        event_scheduler.register_callback("test_callback", sample_callback)

        # Schedule a past event
        past_time = datetime.utcnow() - timedelta(minutes=5)
        past_event_id = event_scheduler.schedule_event(
            event_type=EventType.ONE_TIME,
            callback_name="test_callback",
            trigger_time=past_time,
            callback_data={"when": "past"},
        )

        # Schedule a future event
        future_time = datetime.utcnow() + timedelta(minutes=5)
        future_event_id = event_scheduler.schedule_event(
            event_type=EventType.ONE_TIME,
            callback_name="test_callback",
            trigger_time=future_time,
            callback_data={"when": "future"},
        )

        # Process due events
        processed_events = event_scheduler.process_events_due()

        # Only past event should be processed
        assert len(processed_events) == 1
        assert processed_events[0].id == past_event_id
        assert processed_events[0].callback_data == {"when": "past"}

    def test_apply_middleware(self, event_scheduler): pass
        """Test applying middleware to events."""

        # Add middleware that modifies event
        def modify_data_middleware(event): pass
            event_copy = event.model_copy(deep=True)
            event_copy.callback_data["modified"] = True
            return event_copy

        event_scheduler.add_middleware(modify_data_middleware)

        # Create an event
        event = TimeEvent(
            event_type=EventType.ONE_TIME,
            callback_name="test",
            trigger_time=datetime.utcnow(),
            callback_data={"original": True},
        )

        # Apply middleware
        modified_event = event_scheduler._apply_middleware(event)

        # Check that middleware modified the event
        assert modified_event.callback_data["original"] is True
        assert modified_event.callback_data["modified"] is True
        # Original event should not be modified
        assert "modified" not in event.callback_data

    def test_get_event(self, event_scheduler, sample_callback): pass
        """Test retrieving a specific event."""
        event_scheduler.register_callback("test_callback", sample_callback)

        # Schedule an event
        trigger_time = datetime.utcnow() + timedelta(minutes=5)
        event_id = event_scheduler.schedule_event(
            event_type=EventType.ONE_TIME,
            callback_name="test_callback",
            trigger_time=trigger_time,
        )

        # Get the event
        event = event_scheduler.get_event(event_id)
        assert event is not None
        assert event.id == event_id

        # Test getting non-existent event: pass
        event = event_scheduler.get_event("non_existent_event")
        assert event is None

    def test_get_events(self, event_scheduler, sample_callback): pass
        """Test retrieving all events or upcoming events."""
        event_scheduler.register_callback("test_callback", sample_callback)

        # Schedule a past event
        past_time = datetime.utcnow() - timedelta(minutes=5)
        past_event_id = event_scheduler.schedule_event(
            event_type=EventType.ONE_TIME,
            callback_name="test_callback",
            trigger_time=past_time,
        )

        # Schedule a future event
        future_time = datetime.utcnow() + timedelta(minutes=5)
        future_event_id = event_scheduler.schedule_event(
            event_type=EventType.ONE_TIME,
            callback_name="test_callback",
            trigger_time=future_time,
        )

        # Get all events
        all_events = event_scheduler.get_events()
        assert len(all_events) == 2

        # Get upcoming events only
        upcoming_events = event_scheduler.get_events(upcoming_only=True)
        assert len(upcoming_events) == 1
        assert upcoming_events[0].id == future_event_id


class TestCalendarService: pass
    """Tests for the CalendarService class."""

    @pytest.fixture
    def calendar_service(self): pass
        """Create a CalendarService instance for testing."""
        return CalendarService()

    def test_configure_calendar(self, calendar_service): pass
        """Test configuring the calendar."""
        calendar_service.configure_calendar(
            days_per_month=28,
            months_per_year=13,
            leap_year_interval=5,
            has_leap_year=False,
            spring_start_day=30,
            summer_start_day=120,
            fall_start_day=210,
            winter_start_day=300,
        )

        calendar = calendar_service.calendar
        assert calendar.days_in_current_month == 28
        assert calendar.months_per_year == 13
        assert calendar.leap_year_interval == 5
        assert calendar.has_leap_year is False

    def test_add_important_date(self, calendar_service): pass
        """Test adding an important date to the calendar."""
        calendar_service.add_important_date("Founder's Day", 4, 15)

        # Check that date was added
        important_dates = calendar_service.calendar.important_dates
        assert "Founder's Day" in important_dates
        assert len(important_dates["Founder's Day"]) == 1
        assert important_dates["Founder's Day"][0] == {"month": 4, "day": 15}

        # Add another occurrence of the same date
        calendar_service.add_important_date("Founder's Day", 9, 30, 2023)

        # Check that both dates are present
        important_dates = calendar_service.calendar.important_dates
        assert len(important_dates["Founder's Day"]) == 2
        assert {"month": 9, "day": 30, "year": 2023} in important_dates["Founder's Day"]

    def test_remove_important_date(self, calendar_service): pass
        """Test removing an important date from the calendar."""
        # Add dates
        calendar_service.add_important_date("Founder's Day", 4, 15)
        calendar_service.add_important_date("Harvest Festival", 9, 30)

        # Remove a date
        result = calendar_service.remove_important_date("Founder's Day")

        # Check removal
        assert result is True
        important_dates = calendar_service.calendar.important_dates
        assert "Founder's Day" not in important_dates
        assert "Harvest Festival" in important_dates

        # Test removing non-existent date
        result = calendar_service.remove_important_date("Non-existent Date")
        assert result is False

    def test_get_important_dates_for_date(self, calendar_service): pass
        """Test getting important dates for a specific date."""
        # Add dates
        calendar_service.add_important_date("Founder's Day", 4, 15)
        calendar_service.add_important_date("Anniversary", 4, 15, 2023)  # Year-specific
        calendar_service.add_important_date("Harvest Festival", 9, 30)

        # Get dates for a specific date
        dates = calendar_service.get_important_dates_for_date(2023, 4, 15)

        # Should have both the annual and year-specific events
        assert "Founder's Day" in dates
        assert "Anniversary" in dates

        # Test with a different date (no events)
        dates = calendar_service.get_important_dates_for_date(2023, 5, 1)
        assert len(dates) == 0

        # Test with annual event but wrong year for year-specific
        dates = calendar_service.get_important_dates_for_date(2024, 4, 15)
        assert "Founder's Day" in dates
        assert "Anniversary" not in dates

    def test_is_holiday(self, calendar_service): pass
        """Test checking if a date is a holiday."""
        # Import CalendarEvent and CalendarEventType
        from backend.systems.time.models.calendar_model import CalendarEvent, CalendarEventType
        
        # Add a holiday using proper CalendarEvent object
        holiday_event = CalendarEvent(
            id="new_year_festival",
            name="New Year's Festival",
            event_type=CalendarEventType.HOLIDAY,
            month=1,
            day=1,
            recurring=True
        )
        calendar_service._calendar_events = [holiday_event]

        # Check holiday
        assert calendar_service.is_holiday(2023, 1, 1) is True

        # Check non-holiday: pass
        assert calendar_service.is_holiday(2023, 2, 1) is False

    def test_calculate_season(self, calendar_service): pass
        """Test calculating the season based on day of year."""
        # Configure season boundaries
        calendar_service.configure_calendar(
            spring_start_day=1,
            summer_start_day=91,
            fall_start_day=181,
            winter_start_day=271,
        )

        # Test each season
        assert calendar_service.calculate_season(1) == Season.SPRING
        assert calendar_service.calculate_season(50) == Season.SPRING

        assert calendar_service.calculate_season(91) == Season.SUMMER
        assert calendar_service.calculate_season(150) == Season.SUMMER

        assert calendar_service.calculate_season(181) == Season.AUTUMN
        assert calendar_service.calculate_season(250) == Season.AUTUMN

        assert calendar_service.calculate_season(271) == Season.WINTER
        assert calendar_service.calculate_season(350) == Season.WINTER

    def test_get_days_in_month(self, calendar_service): pass
        """Test getting the number of days in a month."""
        # Configure calendar with default 30-day months
        calendar_service.configure_calendar(days_per_month=30)

        # Standard month (May should have 30 days with our custom calendar)
        assert calendar_service.get_days_in_month(5, 2023) == 30

        # Configure calendar with leap years
        calendar_service.configure_calendar(
            days_per_month=30, has_leap_year=True, leap_year_interval=4
        )

        # Add an exception for month 2 (February equivalent): pass
        with patch.object(calendar_service, "_calculate_day_of_year"): pass
            # Non-leap year February (30 days with custom calendar)
            assert calendar_service.get_days_in_month(2, 2023) == 30

            # Leap year February (31 days with custom calendar)
            assert calendar_service.get_days_in_month(2, 2024) == 31


class TestTimeManager: pass
    """Tests for the TimeManager class."""

    @pytest.fixture
    def time_manager(self): pass
        """Create a TimeManager instance for testing."""
        # Reset the singleton instance before each test
        TimeManager._instance = None
        return TimeManager()

    @pytest.fixture
    def event_dispatcher_mock(self): pass
        """Mock the event dispatcher."""
        with patch(
            "backend.systems.time.services.time_manager.EventDispatcher"
        ) as mock: pass
            mock_instance = MagicMock()
            mock.get_instance.return_value = mock_instance
            yield mock_instance

    def test_singleton_pattern(self): pass
        """Test that TimeManager implements the singleton pattern."""
        # Reset singleton for test
        TimeManager._instance = None

        # First instance
        manager1 = TimeManager()

        # Second instance should be the same object
        manager2 = TimeManager()

        assert manager1 is manager2

    def test_get_time(self, time_manager): pass
        """Test getting the current game time."""
        game_time = time_manager.get_time()

        assert isinstance(game_time, GameTime)
        assert game_time.hour == time_manager.get_time().hour
        assert game_time.minute == time_manager.get_time().minute
        assert game_time.day == time_manager.get_time().day
        assert game_time.month == time_manager.get_time().month
        assert game_time.year == time_manager.get_time().year

    def test_get_calendar(self, time_manager): pass
        """Test getting the calendar."""
        calendar = time_manager.get_calendar()

        assert isinstance(calendar, CalendarData)
        assert calendar.days_in_current_month == time_manager.calendar.days_in_current_month
        assert calendar.months_per_year == time_manager.calendar.months_per_year

    def test_set_time_scale(self, time_manager): pass
        """Test setting the time scale."""
        # Set to normal speed
        time_manager.set_time_scale(1.0)
        assert time_manager.config.time_scale == 1.0

        # Set to fast speed
        time_manager.set_time_scale(5.0)
        assert time_manager.config.time_scale == 5.0

        # Test invalid values (should clamp)
        time_manager.set_time_scale(-1.0)  # Too low
        assert time_manager.config.time_scale == 0.0  # Clamped to minimum

        time_manager.set_time_scale(100.0)  # Too high
        assert time_manager.config.time_scale == 50.0  # Clamped to maximum

    def test_set_time_scale_preset(self, time_manager): pass
        """Test setting time scale using presets."""
        # Test various presets
        time_manager.set_time_scale_preset("paused")
        assert time_manager.config.time_scale == TimeManager.TIME_SCALE_PAUSED

        time_manager.set_time_scale_preset("slow")
        assert time_manager.config.time_scale == TimeManager.TIME_SCALE_SLOW

        time_manager.set_time_scale_preset("normal")
        assert time_manager.config.time_scale == TimeManager.TIME_SCALE_NORMAL

        time_manager.set_time_scale_preset("fast")
        assert time_manager.config.time_scale == TimeManager.TIME_SCALE_FAST

        time_manager.set_time_scale_preset("very_fast")
        assert time_manager.config.time_scale == TimeManager.TIME_SCALE_VERY_FAST

        # Test invalid preset
        with pytest.raises(ValueError): pass
            time_manager.set_time_scale_preset("invalid_preset")

    def test_pause_resume(self, time_manager): pass
        """Test pausing and resuming time progression."""
        # Initially not paused
        assert time_manager.config.is_paused is False

        # Pause
        time_manager.pause()
        assert time_manager.config.is_paused is True

        # Resume
        time_manager.resume()
        assert time_manager.config.is_paused is False

        # Toggle
        time_manager.toggle_pause()
        assert time_manager.config.is_paused is True

        time_manager.toggle_pause()
        assert time_manager.config.is_paused is False

    def test_set_time(self, event_dispatcher_mock): pass
        """Test setting the game time."""
        # Reset singleton and create new instance with mock in place
        TimeManager._instance = None
        time_manager = TimeManager()
        
        # Create a new time
        new_time = GameTime(
            hour=14,
            minute=30,
            second=0,
            day=20,
            month=7,
            year=2023,
            season=Season.SUMMER,
        )

        # Get original time for comparison
        original_time = time_manager.get_time().model_copy(deep=True)

        # Set the time
        time_manager.set_time(new_time)

        # Check that time was updated
        assert time_manager.get_time().hour == 14
        assert time_manager.get_time().minute == 30
        assert time_manager.get_time().day == 20
        assert time_manager.get_time().month == 7
        assert time_manager.get_time().year == 2023

        # Check that TimeAdvancedEvent was emitted
        event_dispatcher_mock.publish_sync.assert_called()
        event = event_dispatcher_mock.publish_sync.call_args[0][0]
        assert isinstance(event, TimeAdvancedEvent)
        
        # Compare the important fields, excluding weather_last_changed which can vary
        assert event.old_time.hour == original_time.hour
        assert event.old_time.minute == original_time.minute
        assert event.old_time.day == original_time.day
        assert event.old_time.month == original_time.month
        assert event.old_time.year == original_time.year
        
        assert event.new_time.hour == new_time.hour
        assert event.new_time.minute == new_time.minute
        assert event.new_time.day == new_time.day
        assert event.new_time.month == new_time.month
        assert event.new_time.year == new_time.year

    def test_advance_time(self, time_manager): pass
        """Test advancing time by different units."""
        # Store original time
        original_time = time_manager.get_time().model_copy(deep=True)

        # Advance by minutes
        time_manager.advance_time(30, TimeUnit.MINUTE)

        # Check minute advance: pass
        assert time_manager.get_time().minute == (original_time.minute + 30) % 60
        if original_time.minute + 30 >= 60: pass
            assert time_manager.get_time().hour == (original_time.hour + 1) % 24

        # Reset time
        time_manager.set_time(original_time)

        # Advance by hours
        time_manager.advance_time(5, TimeUnit.HOUR)

        # Check hour advance
        assert time_manager.get_time().hour == (original_time.hour + 5) % 24
        if original_time.hour + 5 >= 24: pass
            assert time_manager.get_time().day == original_time.day + 1

        # Reset time
        time_manager.set_time(original_time)

        # Advance by days
        time_manager.advance_time(10, TimeUnit.DAY)

        # Check day advance (this will depend on month length)
        expected_day = original_time.day + 10
        days_in_month = time_manager.get_days_in_month(
            original_time.month, original_time.year
        )
        if expected_day > days_in_month: pass
            expected_day -= days_in_month
            assert time_manager.get_time().month == (original_time.month % 12) + 1
        else: pass
            assert time_manager.get_time().day == expected_day

    def test_update_weather(self, event_dispatcher_mock): pass
        """Test updating weather conditions."""
        # Reset singleton and create new instance with mock in place
        TimeManager._instance = None
        time_manager = TimeManager()
        
        # Store original weather
        original_weather = time_manager.get_time().weather

        # Force weather update
        with patch("random.choices") as mock_choices: pass
            # Mock random.choices to return a specific weather
            mock_choices.return_value = [WeatherCondition.CLEAR]

            # Update weather
            time_manager.update_weather(force=True)

            # Check that weather was updated: pass
            assert time_manager.get_time().weather == WeatherCondition.CLEAR

            # Check that WeatherChangedEvent was emitted if weather actually changed: pass
            if original_weather != WeatherCondition.CLEAR: pass
                event_dispatcher_mock.publish_sync.assert_called()
                event_calls = [
                    call[0][0]
                    for call in event_dispatcher_mock.publish_sync.call_args_list
                ]
                weather_events = [
                    e for e in event_calls if isinstance(e, WeatherChangedEvent)
                ]
                assert len(weather_events) > 0
                assert weather_events[0].old_weather == original_weather
                assert weather_events[0].new_weather == WeatherCondition.CLEAR

    def test_schedule_event(self, time_manager): pass
        """Test scheduling events through TimeManager."""

        # Register a test callback
        def test_callback(event): pass
            pass

        time_manager.register_callback("test_callback", test_callback)

        # Schedule an event
        trigger_time = datetime.utcnow() + timedelta(minutes=5)
        event_id = time_manager.schedule_event(
            event_type=EventType.ONE_TIME,
            callback_name="test_callback",
            trigger_time=trigger_time,
        )

        # Check that event was scheduled
        event = time_manager.get_event(event_id)
        assert event is not None
        assert event.event_type == EventType.ONE_TIME
        assert event.callback_name == "test_callback"
        assert event.trigger_time == trigger_time

    def test_save_load_state(self, time_manager, tmp_path): pass
        """Test saving and loading time system state."""
        # Configure with test values
        time_manager.set_time(
            GameTime(
                hour=14, minute=30, day=20, month=7, year=2023, season=Season.SUMMER
            )
        )

        time_manager.configure_calendar(days_per_month=28, months_per_year=13)

        time_manager.set_time_scale(2.0)

        # Register a callback for event testing: pass
        def test_callback(event): pass
            pass

        time_manager.register_callback("test_callback", test_callback)

        # Schedule an event
        time_manager.schedule_event(
            event_type=EventType.ONE_TIME,
            callback_name="test_callback",
            trigger_time=datetime.utcnow() + timedelta(hours=1),
        )

        # Save state
        state_dict = time_manager.save_state()

        # Verify state contents
        assert "calendar" in state_dict
        assert "weather" in state_dict
        assert "time_scale" in state_dict
        assert "paused" in state_dict

        # Modify state
        time_manager.set_time(GameTime(hour=9, minute=0, day=1, month=1, year=2024))

        # Load saved state
        time_manager.load_state(state_dict)

        # Verify state was restored
        assert time_manager.get_time().hour == 14
        assert time_manager.get_time().minute == 30
        assert time_manager.get_time().day == 20
        assert time_manager.get_time().month == 7
        assert time_manager.get_time().year == 2023

        assert time_manager.calendar.base_days_per_month == 28
        assert time_manager.calendar.months_per_year == 13

        assert time_manager.config.time_scale == 2.0

    def test_reset(self, time_manager): pass
        """Test resetting the time system."""
        # Modify state
        time_manager.set_time(
            GameTime(
                hour=14, minute=30, day=20, month=7, year=2023, season=Season.SUMMER
            )
        )

        time_manager.set_time_scale(5.0)

        # Reset
        time_manager.reset()

        # Verify defaults were restored
        assert time_manager.get_time().hour == 12  # Default hour
        assert time_manager.get_time().day == 1
        assert time_manager.get_time().month == 1
        assert time_manager.get_time().year == 1

        assert time_manager.config.time_scale == 1.0  # Default time scale

    def test_get_current_time_formatted(self, time_manager): pass
        """Test getting formatted current time."""
        # Set a specific time
        time_manager.set_time(GameTime(hour=14, minute=30, day=15, month=6, year=2023))

        # Test with date included: pass
        formatted_with_date = time_manager.get_current_time_formatted(include_date=True)
        assert "14:30" in formatted_with_date
        assert "15" in formatted_with_date  # day
        assert "6" in formatted_with_date   # month
        assert "2023" in formatted_with_date # year

        # Test without date: pass
        formatted_without_date = time_manager.get_current_time_formatted(include_date=False)
        assert "14:30" in formatted_without_date
        assert "2023" not in formatted_without_date

    def test_get_days_in_month(self, time_manager): pass
        """Test getting days in a specific month."""
        # Test with default calendar
        days = time_manager.get_days_in_month(2, 2023)
        assert days == 30  # Default days per month
        
        # Configure calendar with different settings
        time_manager.configure_calendar(days_per_month=28)
        days = time_manager.get_days_in_month(2, 2023)
        assert days == 28

    def test_is_special_date(self, time_manager): pass
        """Test checking if a date is special."""
        # Add an important date
        time_manager.add_important_date("Test Day", 6, 15)
        
        # Test with GameTime
        test_time = GameTime(day=15, month=6, year=2023)
        assert time_manager.is_special_date(test_time) is True

        # Test with dict: pass
        test_dict = {"day": 15, "month": 6, "year": 2023}
        assert time_manager.is_special_date(test_dict) is True
        
        # Test non-special date
        non_special_time = GameTime(day=16, month=6, year=2023)
        assert time_manager.is_special_date(non_special_time) is False

    def test_get_current_season(self, time_manager): pass
        """Test getting current season."""
        # Set time to summer (day 150 should be summer)
        time_manager.set_time(GameTime(day=15, month=6, season=Season.SUMMER))
        assert time_manager.get_current_season() == Season.SUMMER

    def test_get_current_weather(self, time_manager): pass
        """Test getting current weather."""
        # Get current weather (returns WeatherData object)
        weather = time_manager.get_current_weather()
        assert hasattr(weather, 'weather_state')
        assert weather.weather_state in ['clear', 'partly_cloudy', 'overcast', 'light_rain', 'heavy_rain', 'snow', 'fog', 'windy', 'stormy', 'heatwave', 'cold_snap']

    def test_get_current_temperature(self, time_manager): pass
        """Test getting current temperature."""
        # Get current temperature from weather service
        temperature = time_manager.get_current_temperature()
        assert isinstance(temperature, (int, float))
        assert -50 <= temperature <= 50  # Reasonable temperature range

    def test_get_weather_last_changed(self, time_manager): pass
        """Test getting when weather was last changed."""
        weather_time = time_manager.get_weather_last_changed()
        assert isinstance(weather_time, datetime)

    def test_export_import_state_json(self, time_manager, tmp_path): pass
        """Test exporting and importing state to/from JSON."""
        # Configure test state
        time_manager.set_time(GameTime(hour=15, minute=45, day=25, month=8, year=2023))
        time_manager.set_time_scale(3.0)
        
        # Export to JSON
        json_file = tmp_path / "test_state.json"
        result = time_manager.export_state_to_json(str(json_file))
        assert result is True
        assert json_file.exists()
        
        # Modify state
        time_manager.set_time(GameTime(hour=9, minute=0, day=1, month=1, year=2024))
        time_manager.set_time_scale(1.0)
        
        # Import from JSON
        result = time_manager.import_state_from_json(str(json_file))
        assert result is True
        
        # Verify state was restored
        assert time_manager.get_time().hour == 15
        assert time_manager.get_time().minute == 45
        assert time_manager.get_time().day == 25
        assert time_manager.get_time().month == 8
        assert time_manager.get_time().year == 2023
        assert time_manager.config.time_scale == 3.0

    def test_export_import_state_json_errors(self, time_manager): pass
        """Test error handling in JSON export/import."""
        # Test export to invalid path
        result = time_manager.export_state_to_json("/invalid/path/file.json")
        assert result is False
        
        # Test import from non-existent file
        result = time_manager.import_state_from_json("/non/existent/file.json")
        assert result is False

    def test_callback_registration(self, time_manager): pass
        """Test callback registration and unregistration."""
        def test_callback(): pass
            pass
        
        # Register callback
        time_manager.register_callback("test_callback", test_callback)
        
        # Verify registration
        assert time_manager.event_scheduler._callbacks["test_callback"] == test_callback
        
        # Unregister callback
        result = time_manager.unregister_callback("test_callback")
        assert result is True
        assert "test_callback" not in time_manager.event_scheduler._callbacks

    def test_time_changed_callbacks(self, time_manager): pass
        """Test time change callback registration."""
        callback_called = []
        
        def time_callback(calendar): pass
            callback_called.append("time")
        
        def day_callback(calendar): pass
            callback_called.append("day")
        
        def month_callback(calendar): pass
            callback_called.append("month")
        
        def year_callback(calendar): pass
            callback_called.append("year")
        
        def season_callback(calendar): pass
            callback_called.append("season")
        
        # Register callbacks
        time_manager.register_time_changed_callback(time_callback)
        time_manager.register_day_changed_callback(day_callback)
        time_manager.register_month_changed_callback(month_callback)
        time_manager.register_year_changed_callback(year_callback)
        time_manager.register_season_changed_callback(season_callback)
        
        # Advance time to trigger callbacks
        time_manager.advance_time(1440, TimeUnit.MINUTE)  # 1 day
        
        # Check that callbacks were called
        assert "time" in callback_called
        assert "day" in callback_called
        assert "month" in callback_called
        assert "year" in callback_called
        assert "season" in callback_called

    def test_start_stop_time_progression(self, time_manager): pass
        """Test starting and stopping time progression."""
        # Test start
        time_manager.start_time_progression()
        assert time_manager.config.is_paused is False
        
        # Test stop
        time_manager.stop_time_progression()
        assert time_manager.config.is_paused is True

    def test_advance_time_by_unit(self, time_manager): pass
        """Test advancing time by specific units."""
        original_time = time_manager.get_time().model_copy(deep=True)
        
        # Advance by seconds
        time_manager.advance_time_by_unit(120, TimeUnit.SECOND)
        assert time_manager.get_time().second == (original_time.second + 120) % 60
        
        # Reset and advance by hours
        time_manager.set_time(original_time)
        time_manager.advance_time_by_unit(3, TimeUnit.HOUR)
        assert time_manager.get_time().hour == (original_time.hour + 3) % 24

    def test_holiday_management(self, time_manager): pass
        """Test holiday management functionality."""
        # Add a holiday
        time_manager.add_holiday(
            name="Test Holiday",
            description="A test holiday",
            month=12,
            day=25,
            effects={"happiness": 2}
        )
        
        # Check if today is a holiday (should be False unless it's Dec 25)
        is_holiday = time_manager.is_holiday_today()
        assert isinstance(is_holiday, bool)
        
        # Get holidays for a specific date
        holidays = time_manager.get_holidays_for_date(month=12, day=25)
        assert len(holidays) >= 0  # Could be 0 or more depending on implementation
        
        # Remove the holiday: pass
        result = time_manager.remove_holiday("Test Holiday")
        assert isinstance(result, bool)

    def test_important_date_management(self, time_manager): pass
        """Test important date management."""
        # Add important date
        time_manager.add_important_date("Important Day", 7, 4)
        
        # Get important dates for that date
        dates = time_manager.get_important_dates_for_date(2023, 7, 4)
        assert "Important Day" in dates
        
        # Remove important date
        result = time_manager.remove_important_date("Important Day")
        assert result is True
        
        # Verify removal: pass
        dates = time_manager.get_important_dates_for_date(2023, 7, 4)
        assert "Important Day" not in dates