from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum
from app.core.enums import TimeOfDay
from app.utils.constants import (
    SECONDS_PER_ROUND,
    ROUNDS_PER_MINUTE,
    MINUTES_PER_HOUR,
    HOURS_PER_DAY,
    DAYS_PER_WEEK
)

@dataclass
class TimeEvent:
    """Represents a time-based event in the game."""
    id: str
    type: str
    trigger_time: datetime
    duration: Optional[timedelta] = None
    data: Optional[Dict] = None
    recurring: bool = False
    recurrence_interval: Optional[timedelta] = None
    last_triggered: Optional[datetime] = None

class TimeScale(Enum):
    """Different time scales for game time progression."""
    REALTIME = "realtime"  # 1 second real = 1 second game
    ACCELERATED = "accelerated"  # 1 second real = 1 minute game
    FAST = "fast"  # 1 second real = 1 hour game
    SUPER_FAST = "super_fast"  # 1 second real = 1 day game

class TimeSystem:
    """Manages game time progression and time-based events."""
    
    def __init__(self):
        self.current_time = datetime.now()
        self.time_scale = TimeScale.ACCELERATED
        self.paused = False
        self.events: List[TimeEvent] = []
        self.last_update = datetime.now()
        self._time_multipliers = {
            TimeScale.REALTIME: 1,
            TimeScale.ACCELERATED: 60,  # 1 real second = 1 game minute
            TimeScale.FAST: 3600,  # 1 real second = 1 game hour
            TimeScale.SUPER_FAST: 86400  # 1 real second = 1 game day
        }
        
    def update(self, real_time_delta: float) -> List[TimeEvent]:
        """Update game time based on real time passed.
        
        Args:
            real_time_delta: Real time passed in seconds
            
        Returns:
            List of triggered time events
        """
        if self.paused:
            return []
            
        # Calculate game time progression
        game_time_delta = timedelta(
            seconds=real_time_delta * self._time_multipliers[self.time_scale]
        )
        self.current_time += game_time_delta
        
        # Process events
        triggered_events = self._process_events()
        self.last_update = datetime.now()
        
        return triggered_events
        
    def _process_events(self) -> List[TimeEvent]:
        """Process all registered time events.
        
        Returns:
            List of triggered events
        """
        triggered = []
        remaining = []
        
        for event in self.events:
            if event.trigger_time <= self.current_time:
                triggered.append(event)
                
                # Handle recurring events
                if event.recurring and event.recurrence_interval:
                    # Calculate next trigger time
                    while event.trigger_time <= self.current_time:
                        event.trigger_time += event.recurrence_interval
                    event.last_triggered = self.current_time
                    remaining.append(event)
            else:
                remaining.append(event)
                
        self.events = remaining
        return triggered
        
    def add_event(self, event: TimeEvent) -> None:
        """Add a new time event to the system."""
        self.events.append(event)
        
    def remove_event(self, event_id: str) -> None:
        """Remove a time event by ID."""
        self.events = [e for e in events if e.id != event_id]
        
    def set_time_scale(self, scale: TimeScale) -> None:
        """Set the time progression scale."""
        self.time_scale = scale
        
    def pause(self) -> None:
        """Pause time progression."""
        self.paused = True
        
    def resume(self) -> None:
        """Resume time progression."""
        self.paused = False
        
    def get_time_of_day(self) -> TimeOfDay:
        """Get the current time of day."""
        hour = self.current_time.hour
        
        if 5 <= hour < 8:
            return TimeOfDay.DAWN
        elif 8 <= hour < 12:
            return TimeOfDay.MORNING
        elif 12 <= hour < 14:
            return TimeOfDay.NOON
        elif 14 <= hour < 17:
            return TimeOfDay.AFTERNOON
        elif 17 <= hour < 20:
            return TimeOfDay.DUSK
        elif 20 <= hour < 24 or 0 <= hour < 5:
            return TimeOfDay.NIGHT
            
    def format_time(self, include_seconds: bool = False) -> str:
        """Format the current time as a string."""
        if include_seconds:
            return self.current_time.strftime("%Y-%m-%d %H:%M:%S")
        return self.current_time.strftime("%Y-%m-%d %H:%M")
        
    def advance_time(self, 
                    days: int = 0, 
                    hours: int = 0, 
                    minutes: int = 0,
                    seconds: int = 0) -> List[TimeEvent]:
        """Advance time by a specific amount.
        
        Args:
            days: Number of days to advance
            hours: Number of hours to advance
            minutes: Number of minutes to advance
            seconds: Number of seconds to advance
            
        Returns:
            List of triggered time events
        """
        delta = timedelta(
            days=days,
            hours=hours,
            minutes=minutes,
            seconds=seconds
        )
        self.current_time += delta
        return self._process_events() 