import asyncio
import logging
import uuid
from datetime import datetime, timedelta
from heapq import heappush, heappop
from typing import Dict, List, Optional, Callable, Tuple, Any, Union

from backend.systems.time.models.time_model import (
    GameTime, Calendar, TimeConfig, TimeEvent, EventType, Season, TimeUnit
)

logger = logging.getLogger(__name__)

class EventScheduler:
    """
    Manages scheduling and processing of time-based events.
    """
    
    def __init__(self):
        # Event scheduling
        self._event_queue = []  # Priority queue: (timestamp, priority, event_id, event)
        self._events_by_id = {}  # Maps event_id to event for fast lookup/cancellation
        self._callback_registry = {}  # Maps callback_name to actual function
    
    def schedule_event(
        self, 
        event_type: EventType,
        callback_name: str,
        callback_data: Dict[str, Any] = None,
        trigger_time: Optional[datetime] = None,
        time_offset: Optional[timedelta] = None,
        recurrence_interval: Optional[timedelta] = None,
        priority: int = 0
    ) -> str:
        """
        Schedule an event to happen at a specific time or after a delay.
        
        Args:
            event_type: Type of event (one-time, recurring, etc.)
            callback_name: Name of the registered callback to call
            callback_data: Data to pass to the callback
            trigger_time: Absolute time when event should trigger (or None for time_offset)
            time_offset: Relative time from now when event should trigger (ignored if trigger_time)
            recurrence_interval: For recurring events, how often to recur
            priority: Priority of the event (higher priority events trigger first)
            
        Returns:
            str: The event ID for later reference/cancellation
        """
        if callback_name not in self._callback_registry:
            raise ValueError(f"Callback '{callback_name}' is not registered")
        
        if trigger_time is None and time_offset is None:
            raise ValueError("Either trigger_time or time_offset must be provided")
        
        # Calculate the trigger time
        if trigger_time is None:
            trigger_time = datetime.utcnow() + time_offset
        
        # Create event ID
        event_id = str(uuid.uuid4())
        
        # Create the event
        event = TimeEvent(
            event_id=event_id,
            event_type=event_type,
            callback_name=callback_name,
            callback_data=callback_data or {},
            next_trigger_time=trigger_time,
            recurrence_interval=recurrence_interval,
            priority=priority,
            created_at=datetime.utcnow(),
            is_active=True
        )
        
        # Add to the events dictionary
        self._events_by_id[event_id] = event
        
        # Add to the priority queue
        heappush(self._event_queue, (trigger_time, -priority, event_id))
        
        logger.info(f"Scheduled {event_type} event '{event_id}' at {trigger_time}")
        return event_id
    
    def cancel_event(self, event_id: str) -> bool:
        """Cancel a scheduled event by its ID."""
        if event_id in self._events_by_id:
            event = self._events_by_id[event_id]
            event.is_active = False
            logger.info(f"Cancelled event '{event_id}'")
            return True
        return False
    
    def register_callback(self, callback_name: str, callback_func: Callable) -> None:
        """Register a callback function that can be used by scheduled events."""
        self._callback_registry[callback_name] = callback_func
        logger.info(f"Registered callback '{callback_name}'")
    
    def unregister_callback(self, callback_name: str) -> bool:
        """Unregister a callback function."""
        if callback_name in self._callback_registry:
            del self._callback_registry[callback_name]
            logger.info(f"Unregistered callback '{callback_name}'")
            return True
        return False
    
    def get_event(self, event_id: str) -> Optional[TimeEvent]:
        """Get an event by its ID."""
        return self._events_by_id.get(event_id)
    
    def get_events(self, upcoming_only: bool = False) -> List[TimeEvent]:
        """Get all events or only upcoming ones."""
        if upcoming_only:
            current_time = datetime.utcnow()
            return [
                event for event in self._events_by_id.values()
                if event.is_active and event.next_trigger_time > current_time
            ]
        return list(self._events_by_id.values())
    
    def process_events_due(self, current_time: datetime = None) -> None:
        """
        Process all events that are due up to the current time.
        
        Args:
            current_time: The current time to process events up to (default: now)
        """
        if current_time is None:
            current_time = datetime.utcnow()
        
        # Process events until no more are due
        while self._event_queue and self._event_queue[0][0] <= current_time:
            _, _, event_id = heappop(self._event_queue)
            
            # Skip if event is cancelled
            if event_id not in self._events_by_id or not self._events_by_id[event_id].is_active:
                continue
            
            event = self._events_by_id[event_id]
            
            # Execute the callback
            self._execute_event_callback(event)
            
            # Re-schedule recurring events
            if event.event_type in [
                EventType.RECURRING_DAILY,
                EventType.RECURRING_WEEKLY,
                EventType.RECURRING_MONTHLY,
                EventType.RECURRING_YEARLY
            ] and event.recurrence_interval:
                # Calculate next trigger time
                next_time = event.next_trigger_time + event.recurrence_interval
                
                # Update the event
                event.next_trigger_time = next_time
                
                # Re-add to the queue
                heappush(self._event_queue, (next_time, -event.priority, event_id))
            else:
                # One-time event, mark as inactive
                event.is_active = False
    
    def _execute_event_callback(self, event: TimeEvent) -> None:
        """Execute the callback for a time event."""
        if event.callback_name in self._callback_registry:
            try:
                self._callback_registry[event.callback_name](event.callback_data)
                logger.info(f"Executed event '{event.event_id}' callback '{event.callback_name}'")
            except Exception as e:
                logger.error(f"Error executing event callback: {e}")
        else:
            logger.warning(f"Callback '{event.callback_name}' not found for event '{event.event_id}'")

class CalendarService:
    """
    Manages calendar operations, seasons, and special dates.
    """
    
    def __init__(self):
        self._calendar = Calendar()
    
    @property
    def calendar(self) -> Calendar:
        """Get the calendar configuration."""
        return self._calendar
    
    def configure_calendar(
        self,
        days_per_month: int = None,
        months_per_year: int = None,
        leap_year_interval: int = None,
        has_leap_year: bool = None
    ) -> None:
        """Configure the calendar settings."""
        if days_per_month is not None:
            self._calendar.days_per_month = days_per_month
        
        if months_per_year is not None:
            self._calendar.months_per_year = months_per_year
        
        if leap_year_interval is not None:
            self._calendar.leap_year_interval = leap_year_interval
        
        if has_leap_year is not None:
            self._calendar.has_leap_year = has_leap_year
        
        logger.info(f"Calendar configured: {self._calendar}")
    
    def add_important_date(self, name: str, month: int, day: int, year: Optional[int] = None) -> None:
        """
        Add an important date to the calendar.
        
        Args:
            name: Name of the important date
            month: Month (1-based)
            day: Day (1-based)
            year: Year (optional, None for recurring)
        """
        if name not in self._calendar.important_dates:
            self._calendar.important_dates[name] = []
        
        date_info = {"month": month, "day": day}
        if year is not None:
            date_info["year"] = year
        
        self._calendar.important_dates[name].append(date_info)
        logger.info(f"Added important date '{name}' on {month}/{day}" + (f"/{year}" if year else ""))
    
    def remove_important_date(self, name: str) -> bool:
        """Remove an important date from the calendar."""
        if name in self._calendar.important_dates:
            del self._calendar.important_dates[name]
            logger.info(f"Removed important date '{name}'")
            return True
        return False
    
    def get_important_dates_for_date(self, year: int, month: int, day: int) -> List[str]:
        """Get all important dates for a specific date."""
        result = []
        
        for name, dates in self._calendar.important_dates.items():
            for date_info in dates:
                if date_info["month"] == month and date_info["day"] == day:
                    if "year" not in date_info or date_info["year"] == year:
                        result.append(name)
        
        return result
    
    def update_calendar_from_game_time(self, game_time: GameTime) -> None:
        """Update the calendar day of year based on game time."""
        self._calendar.current_day_of_year = ((game_time.month - 1) * self._calendar.days_per_month) + game_time.day
    
    def calculate_season(self, day_of_year: int) -> Season:
        """Calculate the season based on the day of year."""
        winter_end = 90
        spring_end = 180
        summer_end = 270
        
        if day_of_year <= winter_end:
            return Season.WINTER
        elif day_of_year <= spring_end:
            return Season.SPRING
        elif day_of_year <= summer_end:
            return Season.SUMMER
        else:
            return Season.FALL
    
    def get_days_in_month(self, month: int, year: int) -> int:
        """Get the number of days in a month."""
        # Special case for leap year February
        if month == 2 and self._is_leap_year(year) and self._calendar.has_leap_year:
            return 29
        return self._calendar.days_per_month
    
    def is_special_date(self, date: Union[datetime, Dict[str, int]]) -> bool:
        """Check if a date is a special date in the calendar."""
        if isinstance(date, datetime):
            return self.get_important_dates_for_date(date.year, date.month, date.day) != []
        else:
            return self.get_important_dates_for_date(date.get("year", 1), date.get("month", 1), date.get("day", 1)) != []
    
    def _is_leap_year(self, year: int) -> bool:
        """Check if a year is a leap year."""
        if not self._calendar.has_leap_year:
            return False
        return year % self._calendar.leap_year_interval == 0

class TimeManager:
    """
    Central manager for game time, calendar operations, and event scheduling.
    
    Implements a singleton pattern to ensure a single source of truth for game time.
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TimeManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        # Core time state
        self._game_time = GameTime()
        self._config = TimeConfig()
        
        # Sub-services
        self._calendar_service = CalendarService()
        self._event_scheduler = EventScheduler()
        
        # Tick management
        self._last_tick_time = datetime.utcnow()
        self._tick_task = None
        
        self._initialized = True
    
    @property
    def game_time(self) -> GameTime:
        """Get the current game time."""
        return self._game_time
    
    def get_time(self) -> GameTime:
        """Get the current game time (alias for game_time)."""
        return self._game_time
    
    @property
    def calendar(self) -> Calendar:
        """Get the calendar configuration."""
        return self._calendar_service.calendar
    
    def get_calendar(self) -> Calendar:
        """Get the calendar configuration (alias for calendar)."""
        return self._calendar_service.calendar
    
    @property
    def config(self) -> TimeConfig:
        """Get the time system configuration."""
        return self._config
    
    def start_time_progression(self) -> None:
        """Start automatic time progression based on configured tick rate."""
        if self._tick_task is None or self._tick_task.done():
            self._last_tick_time = datetime.utcnow()
            self._tick_task = asyncio.create_task(self._tick_loop())
            logger.info("Time progression started")
    
    def stop_time_progression(self) -> None:
        """Stop automatic time progression."""
        if self._tick_task and not self._tick_task.done():
            self._tick_task.cancel()
            logger.info("Time progression stopped")
    
    def set_time_scale(self, scale: float) -> None:
        """Set the time scale (1.0 = real-time, 2.0 = 2x speed, etc.)"""
        if scale < 0:
            raise ValueError("Time scale cannot be negative")
        self._config.time_scale = scale
        logger.info(f"Time scale set to {scale}")
    
    def pause(self) -> None:
        """Pause time progression."""
        self._config.is_paused = True
        logger.info("Time progression paused")
    
    def resume(self) -> None:
        """Resume time progression."""
        self._config.is_paused = False
        self._last_tick_time = datetime.utcnow()  # Reset last tick time
        logger.info("Time progression resumed")
    
    def set_time(self, game_time: GameTime) -> None:
        """Set the game time directly."""
        old_time = self._game_time
        self._game_time = game_time
        
        # Update calendar day of year
        self._calendar_service.update_calendar_from_game_time(game_time)
        
        # Update season if day of year changed
        if old_time.day != game_time.day or old_time.month != game_time.month:
            self._update_season()
        
        logger.info(f"Game time set to {game_time}")
        
        # Process scheduled events that should have happened with this time change
        self._event_scheduler.process_events_due()
    
    def advance_time(self, amount: int, unit: TimeUnit) -> None:
        """
        Advance the game time by the specified amount and unit.
        
        Args:
            amount: The amount to advance by
            unit: The time unit to advance by (e.g., TimeUnit.HOUR)
        """
        # Store old values for comparison
        old_day = self._game_time.day
        old_month = self._game_time.month
        old_year = self._game_time.year
        
        # Handle different units
        if unit == TimeUnit.TICK:
            self._advance_ticks(amount)
        elif unit == TimeUnit.SECOND:
            self._advance_seconds(amount)
        elif unit == TimeUnit.MINUTE:
            self._advance_minutes(amount)
        elif unit == TimeUnit.HOUR:
            self._advance_hours(amount)
        elif unit == TimeUnit.DAY:
            self._advance_days(amount)
        elif unit == TimeUnit.MONTH:
            self._advance_months(amount)
        elif unit == TimeUnit.YEAR:
            self._advance_years(amount)
        else:
            raise ValueError(f"Unsupported time unit: {unit}")
        
        # Update the calendar
        self._calendar_service.update_calendar_from_game_time(self._game_time)
        
        # Check if we need to update the season (day or month changed)
        if (old_day != self._game_time.day or 
            old_month != self._game_time.month or 
            old_year != self._game_time.year):
            self._update_season()
        
        # Process scheduled events that should happen with this time change
        self._event_scheduler.process_events_due()
    
    # Event scheduling methods delegate to EventScheduler
    def schedule_event(self, **kwargs) -> str:
        """Schedule a time event. See EventScheduler.schedule_event for details."""
        return self._event_scheduler.schedule_event(**kwargs)
    
    def cancel_event(self, event_id: str) -> bool:
        """Cancel a scheduled event."""
        return self._event_scheduler.cancel_event(event_id)
    
    def register_callback(self, callback_name: str, callback_func: Callable) -> None:
        """Register a callback function for event scheduling."""
        self._event_scheduler.register_callback(callback_name, callback_func)
    
    def unregister_callback(self, callback_name: str) -> bool:
        """Unregister a callback function."""
        return self._event_scheduler.unregister_callback(callback_name)
    
    def get_event(self, event_id: str) -> Optional[TimeEvent]:
        """Get an event by its ID."""
        return self._event_scheduler.get_event(event_id)
    
    def get_events(self, upcoming_only: bool = False) -> List[TimeEvent]:
        """Get all events or only upcoming ones."""
        return self._event_scheduler.get_events(upcoming_only)
    
    # Calendar methods delegate to CalendarService
    def configure_calendar(self, **kwargs) -> None:
        """Configure the calendar settings."""
        self._calendar_service.configure_calendar(**kwargs)
    
    def add_important_date(self, name: str, month: int, day: int, year: Optional[int] = None) -> None:
        """Add an important date to the calendar."""
        self._calendar_service.add_important_date(name, month, day, year)
    
    def remove_important_date(self, name: str) -> bool:
        """Remove an important date from the calendar."""
        return self._calendar_service.remove_important_date(name)
    
    def get_important_dates_for_date(self, year: int, month: int, day: int) -> List[str]:
        """Get all important dates for a specific date."""
        return self._calendar_service.get_important_dates_for_date(year, month, day)
    
    def get_current_time_formatted(self, include_date: bool = True) -> str:
        """Get a formatted string representation of the current game time."""
        if include_date:
            return f"Year {self._game_time.year}, Month {self._game_time.month}, Day {self._game_time.day} - {self._game_time.hour:02d}:{self._game_time.minute:02d}:{self._game_time.second:02d}"
        else:
            return f"{self._game_time.hour:02d}:{self._game_time.minute:02d}:{self._game_time.second:02d}"
    
    def get_days_in_month(self, month: int, year: int) -> int:
        """Get the number of days in a month."""
        return self._calendar_service.get_days_in_month(month, year)
    
    def is_special_date(self, date: Union[datetime, Dict[str, int]]) -> bool:
        """Check if a date is a special date in the calendar."""
        return self._calendar_service.is_special_date(date)
    
    def get_current_season(self) -> Season:
        """Get the current game season."""
        return self._game_time.season
    
    def get_current_weather(self) -> str:
        """Get the current weather condition string."""
        # Weather simulation placeholder
        return "clear"
    
    def get_current_temperature(self) -> float:
        """Get the current temperature."""
        # Temperature simulation placeholder
        return 72.0
    
    def get_weather_last_changed(self) -> Optional[datetime]:
        """Get when the weather last changed."""
        # Weather simulation placeholder
        return None
    
    def save_state(self) -> None:
        """
        Save the current time system state.
        This is a placeholder - implementation would depend on storage system.
        """
        logger.info("Time system state saved")
    
    def reset(self) -> None:
        """Reset the time system to default state."""
        self._game_time = GameTime()
        self._calendar_service = CalendarService()
        self._config = TimeConfig()
        logger.info("Time system reset to defaults")
    
    async def _tick_loop(self) -> None:
        """Background task that advances time based on real-time elapsed."""
        try:
            while True:
                now = datetime.utcnow()
                elapsed = (now - self._last_tick_time).total_seconds()
                self._last_tick_time = now
                
                # Skip if paused
                if self._config.is_paused:
                    await asyncio.sleep(0.1)
                    continue
                
                # Calculate ticks to advance based on elapsed time
                ticks_to_advance = int(elapsed * self._config.ticks_per_second * self._config.time_scale)
                
                if ticks_to_advance > 0:
                    self._advance_ticks(ticks_to_advance)
                    
                    # Update calendar and process events
                    self._calendar_service.update_calendar_from_game_time(self._game_time)
                    self._event_scheduler.process_events_due()
                
                # Sleep a bit to avoid hammering the CPU
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            logger.info("Tick loop cancelled")
        except Exception as e:
            logger.error(f"Error in tick loop: {e}")
    
    def _advance_ticks(self, ticks: int) -> None:
        """Advance the game time by a number of ticks."""
        self._game_time.tick += ticks
        
        # Handle tick overflow
        if self._game_time.tick >= self._config.ticks_per_second:
            seconds = self._game_time.tick // self._config.ticks_per_second
            self._game_time.tick %= self._config.ticks_per_second
            self._advance_seconds(seconds)
    
    def _advance_seconds(self, seconds: int) -> None:
        """Advance the game time by a number of seconds."""
        self._game_time.second += seconds
        
        # Handle second overflow
        if self._game_time.second >= 60:
            minutes = self._game_time.second // 60
            self._game_time.second %= 60
            self._advance_minutes(minutes)
    
    def _advance_minutes(self, minutes: int) -> None:
        """Advance the game time by a number of minutes."""
        self._game_time.minute += minutes
        
        # Handle minute overflow
        if self._game_time.minute >= 60:
            hours = self._game_time.minute // 60
            self._game_time.minute %= 60
            self._advance_hours(hours)
    
    def _advance_hours(self, hours: int) -> None:
        """Advance the game time by a number of hours."""
        self._game_time.hour += hours
        
        # Handle hour overflow
        if self._game_time.hour >= 24:
            days = self._game_time.hour // 24
            self._game_time.hour %= 24
            self._advance_days(days)
    
    def _advance_days(self, days: int) -> None:
        """Advance the game time by a number of days."""
        for _ in range(days):
            # Increment day
            self._game_time.day += 1
            
            # Check if we need to advance to the next month
            if self._game_time.day > self.get_days_in_month(self._game_time.month, self._game_time.year):
                self._game_time.day = 1
                self._advance_months(1)
    
    def _advance_months(self, months: int) -> None:
        """Advance the game time by a number of months."""
        self._game_time.month += months
        
        # Handle month overflow
        if self._game_time.month > self._calendar_service.calendar.months_per_year:
            years = (self._game_time.month - 1) // self._calendar_service.calendar.months_per_year
            self._game_time.month = ((self._game_time.month - 1) % self._calendar_service.calendar.months_per_year) + 1
            self._advance_years(years)
    
    def _advance_years(self, years: int) -> None:
        """Advance the game time by a number of years."""
        self._game_time.year += years
    
    def _update_season(self) -> None:
        """Update the season based on the day of year in the calendar."""
        old_season = self._game_time.season
        new_season = self._calendar_service.calculate_season(self._calendar_service.calendar.current_day_of_year)
        
        if new_season != old_season:
            self._game_time.season = new_season
            self._emit_season_changed()
    
    def _emit_season_changed(self) -> None:
        """Emit a season changed event."""
        # Event emission placeholder - implementation would depend on event system
        season_data = {
            "old_season": self._game_time.season,
            "new_season": self._game_time.season,
            "day_of_year": self._calendar_service.calendar.current_day_of_year,
            "year": self._game_time.year
        }
        
        logger.info(f"Season changed to {self._game_time.season}")
        
        # Schedule a season change event
        self._event_scheduler.schedule_event(
            event_type=EventType.SEASON_CHANGE,
            callback_name="handle_season_change",
            callback_data=season_data,
            trigger_time=datetime.utcnow()
        ) 