"""
Game Time System Events

Standardized event classes for time system integration with EventDispatcher.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from backend.infrastructure.events.core.event_base import EventBase
from backend.systems.game_time.models.time_model import Season, GameTime


class TimeChangedEvent(EventBase):
    """Event emitted when game time advances."""
    
    def __init__(self, old_time: GameTime, new_time: GameTime, time_delta: Dict[str, int]):
        super().__init__(event_type="time.changed")
        self.old_time = old_time
        self.new_time = new_time
        self.time_delta = time_delta  # What changed: {"hours": 1, "minutes": 30}


class TimeAdvancedEvent(EventBase):
    """Event emitted for external systems like weather to react to time progression."""
    
    def __init__(self, game_time: GameTime, hours_elapsed: float, season: str):
        super().__init__(event_type="time_advanced")
        self.game_time = game_time
        self.hours_elapsed = hours_elapsed
        self.season = season


class SeasonChangedEvent(EventBase):
    """Event emitted when the season changes."""
    
    def __init__(self, old_season: Season, new_season: Season, game_time: GameTime):
        super().__init__(event_type="season_changed")
        self.old_season = old_season
        self.new_season = new_season.value  # Convert enum to string for external systems
        self.game_time = game_time


class TimeScaleChangedEvent(EventBase):
    """Event emitted when time scale is modified."""
    
    def __init__(self, old_scale: float, new_scale: float):
        super().__init__(event_type="time.scale_changed")
        self.old_scale = old_scale
        self.new_scale = new_scale


class TimePausedEvent(EventBase):
    """Event emitted when time progression is paused."""
    
    def __init__(self, game_time: GameTime):
        super().__init__(event_type="time.paused")
        self.game_time = game_time


class TimeResumedEvent(EventBase):
    """Event emitted when time progression is resumed."""
    
    def __init__(self, game_time: GameTime):
        super().__init__(event_type="time.resumed")
        self.game_time = game_time


class TimeEventScheduledEvent(EventBase):
    """Event emitted when a new time event is scheduled."""
    
    def __init__(self, event_id: str, event_type: str, trigger_time: datetime):
        super().__init__(event_type="time.event_scheduled")
        self.event_id = event_id
        self.scheduled_event_type = event_type  # Renamed to avoid conflict
        self.trigger_time = trigger_time


class TimeEventTriggeredEvent(EventBase):
    """Event emitted when a scheduled time event is triggered."""
    
    def __init__(self, event_id: str, event_type: str, callback_name: str, 
                 callback_data: Dict[str, Any]):
        super().__init__(event_type="time.event_triggered")
        self.event_id = event_id
        self.scheduled_event_type = event_type  # Renamed to avoid conflict
        self.callback_name = callback_name
        self.callback_data = callback_data


__all__ = [
    "TimeChangedEvent",
    "TimeAdvancedEvent",
    "SeasonChangedEvent", 
    "TimeScaleChangedEvent",
    "TimePausedEvent",
    "TimeResumedEvent",
    "TimeEventScheduledEvent",
    "TimeEventTriggeredEvent"
]

