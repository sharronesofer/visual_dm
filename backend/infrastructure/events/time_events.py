"""
Time System Events - Canonical event definitions for game time system.

These events are emitted by the TimeManager when significant time-related
changes occur in the game world.
"""

from typing import Optional
from datetime import datetime
from backend.infrastructure.events.services.event_dispatcher import EventBase


class SeasonChangedEvent(EventBase):
    """Event emitted when the game season changes."""
    
    event_type: str = "season_changed"
    old_season: str
    new_season: str
    day_of_year: int
    year: int
    game_time: object  # GameTime object
    
    def __init__(self, old_season, new_season, day_of_year, year, game_time, **kwargs):
        super().__init__(
            event_type="season_changed",
            old_season=str(old_season),
            new_season=str(new_season),
            day_of_year=day_of_year,
            year=year,
            game_time=game_time,
            **kwargs
        )


class WeatherChangedEvent(EventBase):
    """Event emitted when weather conditions change."""
    
    event_type: str = "weather_changed"
    condition: str
    temperature: float
    humidity: float
    wind_speed: float
    changed_at: Optional[datetime]
    season: str
    game_time: object  # GameTime object
    
    def __init__(self, condition, temperature, humidity, wind_speed, changed_at, season, game_time, **kwargs):
        super().__init__(
            event_type="weather_changed",
            condition=condition,
            temperature=temperature,
            humidity=humidity,
            wind_speed=wind_speed,
            changed_at=changed_at,
            season=season,
            game_time=game_time,
            **kwargs
        )


class TimeAdvancedEvent(EventBase):
    """Event emitted when game time is advanced."""
    
    event_type: str = "time_advanced"
    old_time: object  # GameTime object
    new_time: object  # GameTime object
    amount: int
    unit: str
    
    def __init__(self, old_time, new_time, amount, unit, **kwargs):
        super().__init__(
            event_type="time_advanced",
            old_time=old_time,
            new_time=new_time,
            amount=amount,
            unit=unit,
            **kwargs
        )


class TimeSystemPausedEvent(EventBase):
    """Event emitted when time progression is paused."""
    
    event_type: str = "time_system_paused"
    game_time: object  # GameTime object
    
    def __init__(self, game_time, **kwargs):
        super().__init__(
            event_type="time_system_paused",
            game_time=game_time,
            **kwargs
        )


class TimeSystemResumedEvent(EventBase):
    """Event emitted when time progression is resumed."""
    
    event_type: str = "time_system_resumed"
    game_time: object  # GameTime object
    
    def __init__(self, game_time, **kwargs):
        super().__init__(
            event_type="time_system_resumed",
            game_time=game_time,
            **kwargs
        ) 