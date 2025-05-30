from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field


class TimeUnit(str, Enum):
    """Enumeration of time units supported by the system."""
    TICK = "tick"
    SECOND = "second"
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    MONTH = "month"
    YEAR = "year"
    SEASON = "season"


class Season(str, Enum):
    """Enumeration of seasons in the game world."""
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"  
    WINTER = "winter"


class EventType(str, Enum):
    """Enumeration of event types in the time system."""
    ONE_TIME = "one_time"
    RECURRING_DAILY = "recurring_daily"
    RECURRING_WEEKLY = "recurring_weekly"
    RECURRING_MONTHLY = "recurring_monthly"
    RECURRING_YEARLY = "recurring_yearly"
    SEASON_CHANGE = "season_change"
    SPECIAL_DATE = "special_date"


class TimeEvent(BaseModel):
    """Model for time-related events."""
    event_id: str
    event_type: EventType
    callback_name: str
    callback_data: Dict[str, Any] = Field(default_factory=dict)
    next_trigger_time: datetime
    recurrence_interval: Optional[timedelta] = None
    priority: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True


class GameTime(BaseModel):
    """Model representing the current game time."""
    tick: int = 0
    second: int = 0
    minute: int = 0
    hour: int = 0
    day: int = 1
    month: int = 1
    year: int = 1
    season: Season = Season.SPRING
    

class Calendar(BaseModel):
    """Model for the game calendar configuration."""
    days_per_month: int = 30
    months_per_year: int = 12
    current_day_of_year: int = 1
    leap_year_interval: int = 4
    has_leap_year: bool = True
    important_dates: Dict[str, List[Dict[str, int]]] = Field(default_factory=dict)
    

class TimeConfig(BaseModel):
    """Configuration for the time system."""
    ticks_per_second: int = 10
    time_scale: float = 1.0  # 1.0 = real-time, 2.0 = 2x speed, etc.
    is_paused: bool = False
    day_duration_seconds: int = 1440  # 24 minutes real-time = 1 day in-game
    auto_save_interval: timedelta = timedelta(minutes=5)
    
    # Season configuration
    spring_start_day: int = 1  # Day of year
    summer_start_day: int = 91
    fall_start_day: int = 181
    winter_start_day: int = 271 