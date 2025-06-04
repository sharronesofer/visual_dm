"""
Time system - Time Model.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of time events."""
    SEASONAL = "seasonal"
    CALENDAR = "calendar"
    CUSTOM = "custom"
    ONE_TIME = "one_time"
    RECURRING_DAILY = "recurring_daily"
    RECURRING_WEEKLY = "recurring_weekly"
    RECURRING_MONTHLY = "recurring_monthly"
    RECURRING_YEARLY = "recurring_yearly"
    SEASON_CHANGE = "season_change"
    WEATHER_CHANGE = "weather_change"


class Season(str, Enum):
    """Seasons in the game calendar."""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    FALL = "autumn"  # Alias for AUTUMN to maintain compatibility
    WINTER = "winter"


class TimeUnit(str, Enum):
    """Time units for measurement."""
    TICK = "tick"
    SECONDS = "seconds"
    MINUTES = "minutes"
    HOURS = "hours"
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


class GameTime(BaseModel):
    """Represents the current game time."""
    # Individual time components for easy access
    year: int = Field(default=1, description="Current game year")
    month: int = Field(default=1, ge=1, le=12, description="Current game month (1-12)")
    day: int = Field(default=1, ge=1, le=31, description="Current game day (1-31)")
    hour: int = Field(default=0, ge=0, le=23, description="Current game hour (0-23)")
    minute: int = Field(default=0, ge=0, le=59, description="Current game minute (0-59)")
    second: int = Field(default=0, ge=0, le=59, description="Current game second (0-59)")
    tick: int = Field(default=0, ge=0, description="Sub-second ticks")
    
    # Time progression settings
    time_scale: float = Field(default=1.0, description="Time scale multiplier")
    is_paused: bool = Field(default=False, description="Whether time progression is paused")
    total_game_seconds: int = Field(default=0, description="Total elapsed game seconds")
    
    # Current season
    season: Season = Field(default=Season.SPRING, description="Current season")
    
    # Real-world tracking
    current_datetime: datetime = Field(default_factory=datetime.now, description="Real-world timestamp")
    
    class Config:
        arbitrary_types_allowed = True


class Calendar(BaseModel):
    """Calendar configuration for the game world."""
    days_per_month: int = Field(default=30, description="Number of days in each month")
    months_per_year: int = Field(default=12, description="Number of months in a year")
    hours_per_day: int = Field(default=24, description="Number of hours in a day")
    minutes_per_hour: int = Field(default=60, description="Number of minutes in an hour")
    
    # Leap year configuration
    has_leap_year: bool = Field(default=True, description="Whether this calendar has leap years")
    leap_year_interval: int = Field(default=4, description="Interval for leap years")
    
    # Current tracking
    current_season: Season = Field(default=Season.SPRING, description="Current season")
    current_day_of_year: int = Field(default=1, description="Current day of the year (1-365/366)")
    
    # Important dates
    important_dates: Dict[str, List[Dict[str, int]]] = Field(
        default_factory=dict, 
        description="Important dates in the calendar"
    )
    
    class Config:
        arbitrary_types_allowed = True


class TimeConfig(BaseModel):
    """Configuration settings for the time system."""
    # Time progression
    real_seconds_per_game_hour: float = Field(default=60.0, description="Real seconds per game hour")
    ticks_per_second: int = Field(default=10, description="Number of ticks per second")
    time_scale: float = Field(default=1.0, description="Global time scale multiplier")
    is_paused: bool = Field(default=False, description="Whether time is globally paused")
    
    # Features
    enable_seasonal_events: bool = Field(default=True, description="Enable seasonal events")
    
    # System settings
    auto_save_interval: int = Field(default=300, description="Auto-save interval in seconds")
    
    class Config:
        arbitrary_types_allowed = True


class TimeEvent(BaseModel):
    """Represents a time-based event."""
    event_id: str = Field(description="Unique event identifier")
    event_type: EventType = Field(description="Type of event")
    name: str = Field(description="Event name")
    description: Optional[str] = Field(default=None, description="Event description")
    
    # Timing
    next_trigger_time: datetime = Field(description="When the event should next trigger")
    created_at: datetime = Field(description="When the event was created")
    recurrence_interval: Optional[timedelta] = Field(default=None, description="Recurrence interval for repeating events")
    
    # Event execution
    callback_name: str = Field(description="Name of the callback function to execute")
    callback_data: Dict[str, Any] = Field(default_factory=dict, description="Data to pass to the callback")
    priority: int = Field(default=0, description="Event priority (higher executes first)")
    
    # Status
    is_active: bool = Field(default=True, description="Whether the event is active")
    
    # Legacy field for backward compatibility
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    class Config:
        arbitrary_types_allowed = True


def placeholder_function():
    """Placeholder function."""
    pass
