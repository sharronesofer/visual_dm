import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError
from typing import Any, Type, List, Dict, Optional, Union

from backend.systems.time.models.time_model import (
    TimeUnit,
    Season,
    WeatherCondition,
    EventType,
    TimeEvent,
    GameTime,
    TimeConfig,
    WorldTime,
)
from backend.systems.time.models.calendar_model import CalendarData
from backend.systems.time.models.event_model import CalendarEvent


class TestTimeEnums:
    """Tests for enumeration types in the time model."""

    def test_time_unit_enum(self):
        """Test TimeUnit enumeration values."""
        assert TimeUnit.TICK == "tick"
        assert TimeUnit.SECOND == "second"
        assert TimeUnit.MINUTE == "minute"
        assert TimeUnit.HOUR == "hour"
        assert TimeUnit.DAY == "day"
        assert TimeUnit.MONTH == "month"
        assert TimeUnit.YEAR == "year"
        assert TimeUnit.SEASON == "season"

    def test_season_enum(self):
        """Test Season enumeration values."""
        assert Season.SPRING == "spring"
        assert Season.SUMMER == "summer"
        assert Season.AUTUMN == "autumn"
        assert Season.WINTER == "winter"

    def test_weather_condition_enum(self):
        """Test WeatherCondition enumeration values."""
        assert WeatherCondition.CLEAR == "clear"
        assert WeatherCondition.PARTLY_CLOUDY == "partly_cloudy"
        assert WeatherCondition.OVERCAST == "overcast"
        assert WeatherCondition.LIGHT_RAIN == "light_rain"
        assert WeatherCondition.HEAVY_RAIN == "heavy_rain"
        assert WeatherCondition.STORM == "storm"
        assert WeatherCondition.SNOW == "snow"
        assert WeatherCondition.BLIZZARD == "blizzard"
        assert WeatherCondition.FOG == "fog"
        assert WeatherCondition.WINDY == "windy"

    def test_event_type_enum(self):
        """Test EventType enumeration values."""
        assert EventType.ONE_TIME == "one_time"
        assert EventType.RECURRING_DAILY == "recurring_daily"
        assert EventType.RECURRING_WEEKLY == "recurring_weekly"
        assert EventType.RECURRING_MONTHLY == "recurring_monthly"
        assert EventType.RECURRING_YEARLY == "recurring_yearly"
        assert EventType.SEASON_CHANGE == "season_change"
        assert EventType.SPECIAL_DATE == "special_date"


class TestTimeEvent:
    """Tests for the TimeEvent model."""

    def test_time_event_creation(self):
        """Test creating a TimeEvent with required fields."""
        event = TimeEvent(
            event_type=EventType.ONE_TIME,
            callback_name="test_callback",
            trigger_time=datetime.utcnow(),
        )

        assert event.id is not None
        assert event.event_type == EventType.ONE_TIME
        assert event.callback_name == "test_callback"
        assert event.callback_data == {}
        assert event.repeating is False
        assert event.repeat_interval is None
        assert event.cancelled is False
        assert event.executions == []
        assert event.priority == 0

    def test_time_event_with_all_fields(self):
        """Test creating a TimeEvent with all fields specified."""
        trigger_time = datetime.utcnow()
        repeat_interval = timedelta(days=1)

        event = TimeEvent(
            id="test-id-12345",
            event_type=EventType.RECURRING_DAILY,
            callback_name="test_callback",
            callback_data={"test": "data"},
            trigger_time=trigger_time,
            created_at=trigger_time,
            repeating=True,
            repeat_interval=repeat_interval,
            cancelled=False,
            executions=[],
            priority=5,
        )

        assert event.id == "test-id-12345"
        assert event.event_type == EventType.RECURRING_DAILY
        assert event.callback_name == "test_callback"
        assert event.callback_data == {"test": "data"}
        assert event.trigger_time == trigger_time
        assert event.created_at == trigger_time
        assert event.repeating is True
        assert event.repeat_interval == repeat_interval
        assert event.cancelled is False
        assert event.executions == []
        assert event.priority == 5

    def test_is_due_method(self):
        """Test is_due method for determining if an event is due."""
        # Event in the past
        past_time = datetime.utcnow() - timedelta(minutes=5)
        past_event = TimeEvent(
            event_type=EventType.ONE_TIME, callback_name="test", trigger_time=past_time
        )
        assert past_event.is_due() is True

        # Event in the future
        future_time = datetime.utcnow() + timedelta(minutes=5)
        future_event = TimeEvent(
            event_type=EventType.ONE_TIME,
            callback_name="test",
            trigger_time=future_time,
        )
        assert future_event.is_due() is False

        # Cancelled event
        cancelled_event = TimeEvent(
            event_type=EventType.ONE_TIME,
            callback_name="test",
            trigger_time=past_time,
            cancelled=True,
        )
        assert cancelled_event.is_due() is False

    def test_get_remaining_time_method(self):
        """Test get_remaining_time method for calculating time until event."""
        now = datetime.utcnow()

        # Event in the past
        past_time = now - timedelta(minutes=5)
        past_event = TimeEvent(
            event_type=EventType.ONE_TIME, callback_name="test", trigger_time=past_time
        )
        remaining = past_event.get_remaining_time(now)
        assert remaining.total_seconds() < 0

        # Event in the future
        future_time = now + timedelta(minutes=5)
        future_event = TimeEvent(
            event_type=EventType.ONE_TIME,
            callback_name="test",
            trigger_time=future_time,
        )
        remaining = future_event.get_remaining_time(now)
        assert remaining.total_seconds() > 0
        assert abs(remaining.total_seconds() - 300) < 1  # ~300 seconds (5 minutes)

    def test_get_next_trigger_time_method(self):
        """Test get_next_trigger_time method."""
        trigger_time = datetime.utcnow()

        # Normal event
        event = TimeEvent(
            event_type=EventType.ONE_TIME,
            callback_name="test",
            trigger_time=trigger_time,
        )
        assert event.get_next_trigger_time() == trigger_time

        # Cancelled event
        cancelled_event = TimeEvent(
            event_type=EventType.ONE_TIME,
            callback_name="test",
            trigger_time=trigger_time,
            cancelled=True,
        )
        assert cancelled_event.get_next_trigger_time() is None


class TestGameTime:
    """Tests for the GameTime model."""

    def test_game_time_default_values(self):
        """Test GameTime model with default values."""
        game_time = GameTime()

        assert game_time.tick == 0
        assert game_time.second == 0
        assert game_time.minute == 0
        assert game_time.hour == 0
        assert game_time.day == 1
        assert game_time.month == 1
        assert game_time.year == 1
        assert game_time.season == Season.SPRING
        assert game_time.weather == WeatherCondition.CLEAR
        assert game_time.temperature == 20.0
        assert game_time.weather_last_changed is not None

    def test_game_time_custom_values(self):
        """Test GameTime model with custom values."""
        game_time = GameTime(
            tick=10,
            second=30,
            minute=45,
            hour=12,
            day=15,
            month=6,
            year=2023,
            season=Season.SUMMER,
            weather=WeatherCondition.CLEAR,
            temperature=22.5,
            weather_last_changed=datetime(2023, 6, 15, 12, 0),
        )

        assert game_time.tick == 10
        assert game_time.second == 30
        assert game_time.minute == 45
        assert game_time.hour == 12
        assert game_time.day == 15
        assert game_time.month == 6
        assert game_time.year == 2023
        assert game_time.season == Season.SUMMER
        assert game_time.weather == WeatherCondition.CLEAR
        assert game_time.temperature == 22.5
        assert game_time.weather_last_changed == datetime(2023, 6, 15, 12, 0)


class TestCalendar:
    """Tests for the CalendarData model."""

    def test_calendar_default_values(self):
        """Test CalendarData model with default values."""
        calendar = CalendarData()

        assert calendar.days_in_current_month == 30
        assert calendar.months_per_year == 12
        assert calendar.current_day_of_year == 1
        assert calendar.leap_year_interval == 4
        assert calendar.has_leap_year is True
        assert calendar.important_dates == {}

    def test_calendar_custom_values(self):
        """Test CalendarData model with custom values."""
        important_dates = {
            "Founder's Day": [{"month": 4, "day": 15}],
            "Harvest Festival": [{"month": 9, "day": 30}],
        }

        calendar = CalendarData(
            base_days_per_month=28,
            months_per_year=13,
            leap_year_interval=5,
            has_leap_year=False,
            important_dates=important_dates,
        )

        assert calendar.days_in_current_month == 28
        assert calendar.months_per_year == 13
        assert calendar.current_day_of_year == 1  # Should be 1 since we're on day 1
        assert calendar.leap_year_interval == 5
        assert calendar.has_leap_year is False
        assert calendar.important_dates == important_dates


class TestTimeConfig:
    """Tests for the TimeConfig model."""

    def test_time_config_default_values(self):
        """Test TimeConfig model with default values."""
        config = TimeConfig()

        assert config.ticks_per_second == 10
        assert config.time_scale == 1.0
        assert config.is_paused is False
        assert config.spring_start_day == 1
        assert config.summer_start_day == 91
        assert config.fall_start_day == 182
        assert config.winter_start_day == 273
        assert config.weather_change_chance_daily == 0.3
        assert config.weather_change_chance_seasonal == 0.7
        assert config.temperature_variation == 3.0
        assert config.weather_severity_by_season == {}

    def test_time_config_custom_values(self):
        """Test TimeConfig model with custom values."""
        weather_severity = {
            Season.WINTER: {"storm": 0.8, "blizzard": 0.5},
            Season.SUMMER: {"heatwave": 0.7},
        }

        config = TimeConfig(
            ticks_per_second=20,
            time_scale=2.0,
            is_paused=True,
            spring_start_day=30,
            summer_start_day=120,
            fall_start_day=210,
            winter_start_day=300,
            weather_change_chance_daily=0.5,
            weather_change_chance_seasonal=0.8,
            temperature_variation=5.0,
            weather_severity_by_season=weather_severity,
        )

        assert config.ticks_per_second == 20
        assert config.time_scale == 2.0
        assert config.is_paused is True
        assert config.spring_start_day == 30
        assert config.summer_start_day == 120
        assert config.fall_start_day == 210
        assert config.winter_start_day == 300
        assert config.weather_change_chance_daily == 0.5
        assert config.weather_change_chance_seasonal == 0.8
        assert config.temperature_variation == 5.0
        assert config.weather_severity_by_season == weather_severity


class TestCalendarEvent:
    """Tests for the CalendarEvent model."""

    def test_calendar_event_creation(self):
        """Test creating a CalendarEvent with required fields."""
        event = CalendarEvent(name="New Year's Festival", month=1, day=1)

        assert event.id is not None
        assert event.name == "New Year's Festival"
        assert event.description == ""
        assert event.month == 1
        assert event.day == 1
        assert event.year is None
        assert event.is_holiday is False
        assert event.is_recurring is True
        assert event.effects == {}
        assert event.start_time is None
        assert event.end_time is None

    def test_calendar_event_with_all_fields(self):
        """Test creating a CalendarEvent with all fields specified."""
        event = CalendarEvent(
            id="test-id-12345",
            name="Midsummer Feast",
            description="A celebration of the summer solstice",
            month=6,
            day=21,
            year=2023,
            is_holiday=True,
            is_recurring=False,
            effects={"happiness": 2, "productivity": -1},
            start_time="12:00",
            end_time="23:59",
        )

        assert event.id == "test-id-12345"
        assert event.name == "Midsummer Feast"
        assert event.description == "A celebration of the summer solstice"
        assert event.month == 6
        assert event.day == 21
        assert event.year == 2023
        assert event.is_holiday is True
        assert event.is_recurring is False
        assert event.effects == {"happiness": 2, "productivity": -1}
        assert event.start_time == "12:00"
        assert event.end_time == "23:59"

    def test_is_annual_property(self):
        """Test is_annual property."""
        # Annual event (no year specified)
        annual_event = CalendarEvent(name="Harvest Festival", month=9, day=30)
        assert annual_event.is_annual is True

        # One-time event (year specified)
        one_time_event = CalendarEvent(
            name="Special Festival", month=7, day=15, year=2023
        )
        assert one_time_event.is_annual is False


class TestWorldTime:
    """Tests for the WorldTime model."""

    def test_world_time_creation(self):
        """Test creating a WorldTime with required fields."""
        game_time = GameTime()
        calendar = CalendarData()
        config = TimeConfig()

        world_time = WorldTime(game_time=game_time, calendar=calendar, config=config)

        assert world_time.game_time == game_time
        assert world_time.calendar == calendar
        assert world_time.config == config
        assert world_time.events == []
        assert world_time.calendar_events == []
        assert world_time.important_dates == {}
        assert world_time.last_updated is not None

    def test_world_time_with_all_fields(self):
        """Test creating a WorldTime with all fields specified."""
        game_time = GameTime()
        calendar = CalendarData()
        config = TimeConfig()
        events = [
            TimeEvent(
                event_type=EventType.ONE_TIME,
                callback_name="test",
                trigger_time=datetime.utcnow(),
            )
        ]
        calendar_events = [CalendarEvent(id="new_year", name="New Year's Festival", month=1, day=1)]
        important_dates = {"Founder's Day": [{"month": 4, "day": 15}]}
        last_updated = datetime(2023, 6, 15, 12, 0)

        world_time = WorldTime(
            game_time=game_time,
            calendar=calendar,
            config=config,
            events=events,
            calendar_events=calendar_events,
            important_dates=important_dates,
            last_updated=last_updated,
        )

        assert world_time.game_time == game_time
        assert world_time.calendar == calendar
        assert world_time.config == config
        assert world_time.events == events
        assert world_time.calendar_events == calendar_events
        assert world_time.important_dates == important_dates
        assert world_time.last_updated == last_updated
