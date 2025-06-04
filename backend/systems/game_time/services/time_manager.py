import asyncio
import uuid
from datetime import datetime, timedelta
from heapq import heappush, heappop
from typing import Dict, List, Optional, Callable, Tuple, Any, Union

from backend.systems.game_time.models.time_model import (
    GameTime, Calendar, TimeConfig, TimeEvent, EventType, Season, TimeUnit
)
from backend.infrastructure.logging_adapters.game_time_logger import get_time_manager_logger

logger = get_time_manager_logger()

# Event system integration
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
from backend.systems.game_time.events import (
    TimeChangedEvent, TimeAdvancedEvent, SeasonChangedEvent, 
    TimeScaleChangedEvent, TimePausedEvent, TimeResumedEvent,
    TimeEventScheduledEvent, TimeEventTriggeredEvent
)

class EventScheduler:
    """
    Handles scheduling and execution of time-based events.
    """
    
    def __init__(self, event_dispatcher: EventDispatcher):
        # Event scheduling
        self._event_queue = []  # heap: [(trigger_time, -priority, event_id)]
        self._events_by_id = {}  # event_id -> TimeEvent
        self._callback_registry = {}  # callback_name -> callback_function
        self._event_dispatcher = event_dispatcher

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
        Schedule a time-based event.
        
        Args:
            event_type: Type of event to schedule
            callback_name: Name of the callback function to execute
            callback_data: Data to pass to the callback
            trigger_time: Specific time to trigger (optional)
            time_offset: Offset from current time (optional)
            recurrence_interval: Interval for recurring events (optional)
            priority: Priority of event (higher = more important)
        
        Returns:
            Event ID for the scheduled event
        """
        import uuid
        
        event_id = str(uuid.uuid4())
        
        # Calculate trigger time
        if trigger_time is not None:
            calculated_trigger_time = trigger_time
        elif time_offset is not None:
            calculated_trigger_time = datetime.utcnow() + time_offset
        else:
            calculated_trigger_time = datetime.utcnow()
        
        # Create the event
        event = TimeEvent(
            event_id=event_id,
            event_type=event_type,
            callback_name=callback_name,
            callback_data=callback_data or {},
            trigger_time=calculated_trigger_time,
            next_trigger_time=calculated_trigger_time,
            recurrence_interval=recurrence_interval,
            priority=priority,
            is_active=True
        )
        
        # Store the event
        self._events_by_id[event_id] = event
        
        # Add to the priority queue
        heappush(self._event_queue, (calculated_trigger_time, -priority, event_id))
        
        # Emit event scheduled notification
        self._event_dispatcher.publish_sync(
            TimeEventScheduledEvent(event_id, event_type.value, calculated_trigger_time)
        )
        
        logger.info(f"Scheduled event '{event_id}' of type {event_type} for {calculated_trigger_time}")
        
        return event_id

    def cancel_event(self, event_id: str) -> bool:
        """Cancel a scheduled event."""
        if event_id in self._events_by_id:
            self._events_by_id[event_id].is_active = False
            logger.info(f"Cancelled event '{event_id}'")
            return True
        return False

    def register_callback(self, callback_name: str, callback_func: Callable) -> None:
        """Register a callback function for event execution."""
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
        # Emit event triggered notification first
        self._event_dispatcher.publish_sync(
            TimeEventTriggeredEvent(
                event.event_id, 
                event.event_type.value, 
                event.callback_name, 
                event.callback_data
            )
        )
        
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
        if not hasattr(self, '_initialized') or not self._initialized:
            # Core time management
            self._game_time = GameTime()
            self._config = TimeConfig()
            self._is_running = False
            self._time_scale = 1.0
            self._is_paused = False
            self._tick_task = None
            
            # Services
            self._event_dispatcher = EventDispatcher.get_instance()
            self._event_scheduler = EventScheduler(self._event_dispatcher)
            self._calendar_service = CalendarService()
            
            # Load configuration
            self._load_configuration()
            
            self._initialized = True
        
        if hasattr(self, '_initialized'):
            return
        
        # Initialize base configuration first
        self._config = TimeConfig()
        
        # Load configuration from JSON file per Development Bible requirements
        self._load_configuration()
        
        self._game_time = GameTime()
        self._calendar_service = CalendarService()
        self._event_scheduler = EventScheduler()
        
        # Apply calendar configuration if loaded
        if hasattr(self, '_pending_calendar_config'):
            cal_cfg = self._pending_calendar_config
            self._calendar_service.configure_calendar(
                days_per_month=cal_cfg.get('days_per_month'),
                months_per_year=cal_cfg.get('months_per_year'),
                leap_year_interval=cal_cfg.get('leap_year_interval'),
                has_leap_year=cal_cfg.get('has_leap_year')
            )
            # Add important dates if specified
            if 'important_dates' in cal_cfg:
                for date_info in cal_cfg['important_dates']:
                    self._calendar_service.add_important_date(
                        name=date_info['name'],
                        month=date_info['month'],
                        day=date_info['day'],
                        year=date_info.get('year')
                    )
            delattr(self, '_pending_calendar_config')
        
        # Initialize persistence service
        from backend.infrastructure.persistence.game_time_persistence import PersistenceService
        self._persistence_service = PersistenceService()
        
        # Time progression tracking
        self._last_tick_time = datetime.utcnow()
        self._tick_task: Optional[asyncio.Task] = None
        self._last_save_time = datetime.utcnow()
        
        logger.info("TimeManager initialized")
        
        # Try to load existing state
        self._load_state()
    
    def _load_configuration(self) -> None:
        """Load configuration from time_system_config.json file."""
        import json
        import os
        
        # Initialize pending calendar config
        self._pending_calendar_config = None
        
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'data', 'systems', 'game_time', 'time_system_config.json'
        )
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                
                # Apply configuration values to TimeConfig
                if 'time_progression' in config_data:
                    time_prog = config_data['time_progression']
                    self._config.time_scale = time_prog.get('default_time_scale', self._config.time_scale)
                    self._config.auto_save_interval = time_prog.get('auto_save_interval_minutes', 5) * 60  # Convert to seconds
                
                if 'calendar' in config_data:
                    calendar_cfg = config_data['calendar']
                    # Store calendar config for later application
                    self._pending_calendar_config = calendar_cfg
                
                logger.info(f"Configuration loaded from {config_path}")
            else:
                logger.warning(f"Configuration file not found at {config_path}, using defaults")
                
        except Exception as e:
            logger.error(f"Failed to load configuration from {config_path}: {e}")
            logger.info("Using default configuration values")
    
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
        """Set the time scale for time progression."""
        if scale < 0:
            raise ValueError("Time scale cannot be negative")
        
        old_scale = self._time_scale
        self._time_scale = scale
        
        # Emit scale changed event
        self._event_dispatcher.publish_sync(
            TimeScaleChangedEvent(old_scale, scale)
        )
        
        logger.info(f"Time scale changed from {old_scale}x to {scale}x")
    
    def pause(self) -> None:
        """Pause time progression."""
        self._is_paused = True
        
        # Emit pause event
        self._event_dispatcher.publish_sync(
            TimePausedEvent(self._game_time)
        )
        
        logger.info("Time progression paused")
    
    def resume(self) -> None:
        """Resume time progression."""
        if self._is_paused:
            self._is_paused = False
            
            # Emit resume event
            self._event_dispatcher.publish_sync(
                TimeResumedEvent(self._game_time)
            )
            
            logger.info("Time progression resumed")
    
    def set_time(self, game_time: GameTime) -> None:
        """Set the current game time."""
        old_time = GameTime(
            year=self._game_time.year,
            month=self._game_time.month,
            day=self._game_time.day,
            hour=self._game_time.hour,
            minute=self._game_time.minute,
            second=self._game_time.second
        )
        
        self._game_time = game_time
        self._calendar_service.update_calendar_from_game_time(game_time)
        self._update_season()
        
        # Calculate time delta for event
        time_delta = {
            "years": game_time.year - old_time.year,
            "months": game_time.month - old_time.month,
            "days": game_time.day - old_time.day,
            "hours": game_time.hour - old_time.hour,
            "minutes": game_time.minute - old_time.minute,
            "seconds": game_time.second - old_time.second
        }
        
        # Emit time changed event
        self._event_dispatcher.publish_sync(
            TimeChangedEvent(old_time, game_time, time_delta)
        )
        
        logger.info(f"Time set to {game_time}")
    
    def advance_time(self, amount: int, unit: TimeUnit) -> None:
        """Advance time by a specific amount."""
        old_time = GameTime(
            year=self._game_time.year,
            month=self._game_time.month,
            day=self._game_time.day,
            hour=self._game_time.hour,
            minute=self._game_time.minute,
            second=self._game_time.second
        )
        
        if unit == TimeUnit.SECONDS:
            self._advance_seconds(amount)
        elif unit == TimeUnit.MINUTES:
            self._advance_minutes(amount)
        elif unit == TimeUnit.HOURS:
            self._advance_hours(amount)
        elif unit == TimeUnit.DAYS:
            self._advance_days(amount)
        elif unit == TimeUnit.MONTHS:
            self._advance_months(amount)
        elif unit == TimeUnit.YEARS:
            self._advance_years(amount)
        else:
            raise ValueError(f"Unknown time unit: {unit}")
        
        # Update calendar and season
        self._calendar_service.update_calendar_from_game_time(self._game_time)
        self._update_season()
        
        # Calculate time delta for event
        time_delta = {
            "years": self._game_time.year - old_time.year,
            "months": self._game_time.month - old_time.month,
            "days": self._game_time.day - old_time.day,
            "hours": self._game_time.hour - old_time.hour,
            "minutes": self._game_time.minute - old_time.minute,
            "seconds": self._game_time.second - old_time.second
        }
        
        # Emit time changed event
        self._event_dispatcher.publish_sync(
            TimeChangedEvent(old_time, self._game_time, time_delta)
        )
        
        # Emit time advanced event for external systems like weather
        hours_elapsed = 0
        if unit == TimeUnit.HOURS:
            hours_elapsed = amount
        elif unit == TimeUnit.MINUTES:
            hours_elapsed = amount / 60.0
        elif unit == TimeUnit.SECONDS:
            hours_elapsed = amount / 3600.0
        elif unit == TimeUnit.DAYS:
            hours_elapsed = amount * 24
        elif unit == TimeUnit.MONTHS:
            hours_elapsed = amount * 24 * 30  # Approximate
        elif unit == TimeUnit.YEARS:
            hours_elapsed = amount * 24 * 365  # Approximate
            
        self._event_dispatcher.publish_sync(
            TimeAdvancedEvent(
                game_time=self._game_time,
                hours_elapsed=hours_elapsed,
                season=self._game_time.season.value
            )
        )
        
        # Process any events that may now be due
        self._event_scheduler.process_events_due()
        
        logger.info(f"Advanced time by {amount} {unit.value}(s) to {self._game_time}")
    
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
        return "clear"
    
    def get_current_temperature(self) -> float:
        """Get the current temperature."""
        return 65.0
    
    def get_weather_last_changed(self) -> Optional[datetime]:
        """Get when the weather last changed."""
        return None
    
    def get_current_weather_details(self) -> Optional[object]:
        """Get detailed weather information."""
        return None
    
    def set_weather(self, weather: object) -> None:
        """Manually set the weather conditions."""
        pass
    
    def get_weather_forecast(self, hours_ahead: int) -> List[object]:
        """Get weather forecast for the specified number of hours."""
        return []
    
    def save_state(self) -> bool:
        """
        Save the current time system state to persistent storage.
        
        Returns:
            bool: True if save was successful
        """
        try:
            # Create backup before saving
            self._persistence_service.backup_saves()
            
            # Save all components
            success = self._persistence_service.save_all(
                game_time=self._game_time,
                calendar=self._calendar_service.calendar,
                config=self._config
            )
            
            if success:
                self._last_save_time = datetime.utcnow()
                logger.info("Time system state saved successfully")
            else:
                logger.error("Failed to save time system state")
            
            return success
            
        except Exception as e:
            logger.error(f"Error saving time system state: {e}")
            return False
    
    def load_state(self) -> bool:
        """
        Load time system state from persistent storage.
        
        Returns:
            bool: True if load was successful
        """
        return self._load_state()
    
    def _load_state(self) -> bool:
        """
        Internal method to load time system state.
        
        Returns:
            bool: True if load was successful
        """
        try:
            loaded_data = self._persistence_service.load_all()
            
            # Load game time
            if loaded_data["game_time"]:
                self._game_time = loaded_data["game_time"]
                logger.info("Game time loaded from file")
            
            # Load calendar
            if loaded_data["calendar"]:
                self._calendar_service._calendar = loaded_data["calendar"]
                logger.info("Calendar loaded from file")
            
            # Load config
            if loaded_data["config"]:
                self._config = loaded_data["config"]
                logger.info("Configuration loaded from file")
            
            # Update calendar state from loaded game time
            self._calendar_service.update_calendar_from_game_time(self._game_time)
            
            return True
            
        except Exception as e:
            logger.warning(f"Could not load time system state, using defaults: {e}")
            return False
    
    def get_save_info(self) -> Dict[str, Any]:
        """
        Get information about save files.
        
        Returns:
            Dictionary with save file information
        """
        return self._persistence_service.get_save_info()
    
    def export_state(self, export_path: str) -> bool:
        """
        Export the entire time system state to a directory.
        
        Args:
            export_path: Directory to export to
            
        Returns:
            bool: True if successful
        """
        try:
            # Import here to avoid circular imports
            from backend.infrastructure.persistence.game_time_persistence import PersistenceService
            export_service = PersistenceService(export_path)
            
            success = export_service.save_all(
                self._game_time,
                self._calendar_service.calendar,
                self._config
            )
            
            if success:
                logger.info(f"Time system state exported to {export_path}")
            else:
                logger.error(f"Failed to export time system state to {export_path}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error exporting time system state: {e}")
            return False
    
    def import_state(self, import_path: str) -> bool:
        """
        Import time system state from a directory.
        
        Args:
            import_path: Directory to import from
            
        Returns:
            bool: True if successful
        """
        try:
            # Import here to avoid circular imports
            from backend.infrastructure.persistence.game_time_persistence import PersistenceService
            import_service = PersistenceService(import_path)
            
            loaded_data = import_service.load_all()
            
            # Apply loaded data if available
            if loaded_data["game_time"]:
                self._game_time = loaded_data["game_time"]
            if loaded_data["calendar"]:
                self._calendar_service._calendar = loaded_data["calendar"]
            if loaded_data["config"]:
                self._config = loaded_data["config"]
            
            # Update calendar state
            self._calendar_service.update_calendar_from_game_time(self._game_time)
            
            logger.info(f"Time system state imported from {import_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import time system state: {e}")
            return False
    
    def reset(self) -> None:
        """Reset the time system to default state."""
        self._game_time = GameTime()
        self._calendar_service = CalendarService()
        self._config = TimeConfig()
        self._last_save_time = datetime.utcnow()
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
                    
                    # Emit time advanced event for other systems (like weather)
                    ticks_to_hours = ticks_to_advance / (self._config.ticks_per_second * 3600)
                    time_event = TimeAdvancedEvent(
                        game_time=self._game_time,
                        hours_elapsed=ticks_to_hours,
                        season=self._game_time.season.value
                    )
                    self._event_dispatcher.publish_sync(time_event)
                
                # Check for auto-save
                time_since_save = (now - self._last_save_time).total_seconds()
                if time_since_save >= self._config.auto_save_interval:
                    self.save_state()
                
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
        """Update the current season based on the day of year."""
        current_day_of_year = self._calendar_service.calendar.current_day_of_year
        new_season = self._calendar_service.calculate_season(current_day_of_year)
        
        if new_season != self._game_time.season:
            old_season = self._game_time.season
            self._game_time.season = new_season
            
            # Emit season changed event
            self._event_dispatcher.publish_sync(
                SeasonChangedEvent(old_season, new_season, self._game_time)
            )
            
            logger.info(f"Season changed from {old_season} to {new_season}") 