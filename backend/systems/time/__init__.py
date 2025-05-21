"""
Time System - Manages game time, calendar, seasons, and time-based events.

This module provides the time management functionality for the simulation, including
calendar operations, season progression, and scheduling time-based events.
"""

from backend.systems.time.models.time_model import (
    GameTime, Calendar, TimeConfig, TimeEvent, 
    EventType, Season, TimeUnit, WeatherCondition, 
    CalendarEvent, WorldTime
)
from backend.systems.time.utils.time_utils import (
    get_time_of_day_name, is_daytime, time_since, format_time_since,
    time_to_string, calculate_time_difference, format_time_difference,
    format_time_remaining, convert_time_units, parse_time_string,
    is_valid_date, get_date_string, is_same_day, is_same_month,
    time_in_range
)
from backend.systems.time.services.time_manager import (
    TimeManager, EventScheduler, CalendarService
)
from backend.systems.time.repositories.time_repository import TimeRepository

# Create default singleton instance
time_manager = TimeManager()

# Convenience exports
get_time = time_manager.get_time
advance_time = time_manager.advance_time
schedule_event = time_manager.schedule_event
get_calendar = time_manager.get_calendar 