import pytest
import os
import json
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Type, List, Dict, Optional, Union

from backend.systems.time.models.time_model import (
    GameTime,
    Calendar,
    TimeConfig,
    TimeEvent,
    EventType,
    Season,
    WeatherCondition,
)
from backend.systems.time.repositories.time_repository import TimeRepository


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def repository(temp_data_dir):
    """Create a repository instance with a temporary data directory."""
    return TimeRepository(data_dir=temp_data_dir)


@pytest.fixture
def game_time():
    """Create a sample GameTime object for testing."""
    return GameTime(
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


@pytest.fixture
def calendar():
    """Create a sample Calendar object for testing."""
    important_dates = {
        "Founder's Day": [{"month": 4, "day": 15}],
        "Harvest Festival": [{"month": 9, "day": 30}],
    }

    return Calendar(
        days_per_month=30,
        months_per_year=12,
        current_day_of_year=166,
        leap_year_interval=4,
        has_leap_year=True,
        important_dates=important_dates,
    )


@pytest.fixture
def time_config():
    """Create a sample TimeConfig object for testing."""
    return TimeConfig(
        ticks_per_second=10,
        time_scale=1.0,
        is_paused=False,
        spring_start_day=1,
        summer_start_day=91,
        fall_start_day=182,
        winter_start_day=273,
    )


@pytest.fixture
def time_events():
    """Create a list of sample TimeEvent objects for testing."""
    now = datetime.utcnow()

    return [
        TimeEvent(
            event_type=EventType.ONE_TIME,
            callback_name="test_callback_1",
            trigger_time=now + timedelta(hours=1),
            callback_data={"message": "Test event 1"},
        ),
        TimeEvent(
            event_type=EventType.RECURRING_DAILY,
            callback_name="test_callback_2",
            trigger_time=now + timedelta(days=1),
            callback_data={"message": "Test event 2"},
            repeating=True,
            repeat_interval=timedelta(days=1),
        ),
    ]


class TestTimeRepository:
    """Tests for the TimeRepository class."""

    def test_init_creates_directories(self, temp_data_dir):
        """Test that the repository creates the data directory on initialization."""
        # Create a new path
        data_dir = Path(temp_data_dir) / "nested/time"
        repo = TimeRepository(data_dir=str(data_dir))

        # Check that directory was created
        assert data_dir.exists()
        assert data_dir.is_dir()

    def test_save_load_game_time(self, repository, game_time):
        """Test saving and loading GameTime objects."""
        # Save the game time
        repository.save_game_time(game_time)

        # Check that file was created
        assert repository.game_time_path.exists()

        # Load the game time
        loaded_game_time = repository.load_game_time()

        # Check that loaded data matches original
        assert loaded_game_time.tick == game_time.tick
        assert loaded_game_time.second == game_time.second
        assert loaded_game_time.minute == game_time.minute
        assert loaded_game_time.hour == game_time.hour
        assert loaded_game_time.day == game_time.day
        assert loaded_game_time.month == game_time.month
        assert loaded_game_time.year == game_time.year
        assert loaded_game_time.season == game_time.season
        assert loaded_game_time.weather == game_time.weather
        assert loaded_game_time.temperature == game_time.temperature
        # Datetime serialization might change format, so compare string representation
        assert (
            loaded_game_time.weather_last_changed.isoformat()[:19]
            == game_time.weather_last_changed.isoformat()[:19]
        )

    def test_save_load_calendar(self, repository, calendar):
        """Test saving and loading Calendar objects."""
        # Save the calendar
        repository.save_calendar(calendar)

        # Check that file was created
        assert repository.calendar_path.exists()

        # Load the calendar
        loaded_calendar = repository.load_calendar()

        # Check that loaded data matches original
        assert loaded_calendar.days_in_current_month == calendar.days_in_current_month
        assert loaded_calendar.months_per_year == calendar.months_per_year
        assert loaded_calendar.current_day_of_year == calendar.current_day_of_year
        assert loaded_calendar.leap_year_interval == calendar.leap_year_interval
        assert loaded_calendar.has_leap_year == calendar.has_leap_year
        assert loaded_calendar.important_dates == calendar.important_dates

    def test_save_load_config(self, repository, time_config):
        """Test saving and loading TimeConfig objects."""
        # Save the config
        repository.save_config(time_config)

        # Check that file was created
        assert repository.config_path.exists()

        # Load the config
        loaded_config = repository.load_config()

        # Check that loaded data matches original
        assert loaded_config.ticks_per_second == time_config.ticks_per_second
        assert loaded_config.time_scale == time_config.time_scale
        assert loaded_config.is_paused == time_config.is_paused
        assert loaded_config.spring_start_day == time_config.spring_start_day
        assert loaded_config.summer_start_day == time_config.summer_start_day
        assert loaded_config.fall_start_day == time_config.fall_start_day
        assert loaded_config.winter_start_day == time_config.winter_start_day

    def test_save_load_events(self, repository, time_events):
        """Test saving and loading TimeEvent objects."""
        # Save the events
        repository.save_events(time_events)

        # Check that file was created
        assert repository.events_path.exists()

        # Load the events
        loaded_events = repository.load_events()

        # Check that loaded data matches original
        assert len(loaded_events) == len(time_events)

        # Check first event
        assert loaded_events[0].event_type == time_events[0].event_type
        assert loaded_events[0].callback_name == time_events[0].callback_name
        assert loaded_events[0].callback_data == time_events[0].callback_data
        assert loaded_events[0].repeating == time_events[0].repeating

        # Check second event (with repeating interval)
        assert loaded_events[1].event_type == time_events[1].event_type
        assert loaded_events[1].callback_name == time_events[1].callback_name
        assert loaded_events[1].callback_data == time_events[1].callback_data
        assert loaded_events[1].repeating == time_events[1].repeating
        # Check that repeat_interval was preserved through serialization
        assert (
            loaded_events[1].repeat_interval.total_seconds()
            == time_events[1].repeat_interval.total_seconds()
        )

    def test_save_load_all(
        self, repository, game_time, calendar, time_config, time_events
    ):
        """Test saving and loading all time system state."""
        # Save all state
        repository.save_all(game_time, calendar, time_config, time_events)

        # Check that all files were created
        assert repository.game_time_path.exists()
        assert repository.calendar_path.exists()
        assert repository.config_path.exists()
        assert repository.events_path.exists()

        # Load all state
        state_dict = repository.load_all()

        # Check that all components are present
        assert "game_time" in state_dict
        assert "calendar" in state_dict
        assert "config" in state_dict
        assert "events" in state_dict

        # Check that loaded data matches original
        loaded_game_time = state_dict["game_time"]
        loaded_calendar = state_dict["calendar"]
        loaded_config = state_dict["config"]
        loaded_events = state_dict["events"]

        assert loaded_game_time.year == game_time.year
        assert loaded_game_time.month == game_time.month
        assert loaded_game_time.day == game_time.day

        assert loaded_calendar.days_in_current_month == calendar.days_in_current_month
        assert loaded_calendar.months_per_year == calendar.months_per_year

        assert loaded_config.time_scale == time_config.time_scale

        assert len(loaded_events) == len(time_events)
        assert loaded_events[0].callback_name == time_events[0].callback_name

    def test_file_not_found_returns_none(self, repository):
        """Test that loading from non-existent files returns None."""
        # Load from non-existent files
        assert repository.load_game_time() is None
        assert repository.load_calendar() is None
        assert repository.load_config() is None
        assert repository.load_events() == []

    def test_create_restore_backup(
        self, repository, game_time, calendar, time_config, time_events
    ):
        """Test creating and restoring backups."""
        # Save all state
        repository.save_all(game_time, calendar, time_config, time_events)

        # Create a backup
        backup_name = repository.create_backup()
        assert backup_name is not None

        # Modify the state
        modified_game_time = GameTime(year=2024, month=1, day=1)
        repository.save_game_time(modified_game_time)

        # Check that the state was modified
        assert repository.load_game_time().year == 2024

        # Restore the backup
        success = repository.restore_backup(backup_name)
        assert success is True

        # Check that the original state was restored
        assert repository.load_game_time().year == 2023
        assert repository.load_game_time().month == 6
        assert repository.load_game_time().day == 15

    def test_get_available_backups(self, repository):
        """Test getting available backups."""
        # Create some backups
        backup1 = repository.create_backup("backup1")
        backup2 = repository.create_backup("backup2")

        # Get available backups
        backups = repository.get_available_backups()

        # Check that both backups are in the list
        assert backup1 in backups
        assert backup2 in backups
