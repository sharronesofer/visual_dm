from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union, Any

from backend.systems.time.models.time_model import GameTime, Season, TimeUnit

# Import TimeManager but don't reference it directly in functions
# This avoids circular import issues while maintaining access to the singleton
from backend.systems.time.services.time_manager import TimeManager


def get_current_time() -> GameTime:
    """
    Get the current game time.
    
    Returns:
        GameTime: The current game time
    """
    return TimeManager().game_time


def get_current_season() -> Season:
    """
    Get the current game season.
    
    Returns:
        Season: The current season
    """
    return TimeManager().game_time.season


def get_formatted_time(include_date: bool = True) -> str:
    """
    Get a formatted string representation of the current game time.
    
    Args:
        include_date: Whether to include the date in the formatted string
        
    Returns:
        str: Formatted time string
    """
    return TimeManager().get_current_time_formatted(include_date)


def get_time_of_day() -> str:
    """
    Get a string representation of the time of day.
    
    Returns:
        str: "morning", "afternoon", "evening", or "night"
    """
    hour = TimeManager().game_time.hour
    
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def is_daytime() -> bool:
    """
    Check if it's currently daytime.
    
    Returns:
        bool: True if it's daytime (6:00-18:00), False otherwise
    """
    hour = TimeManager().game_time.hour
    return 6 <= hour < 18


def time_since(reference_time: GameTime) -> Dict[str, int]:
    """
    Calculate the time elapsed since a reference game time.
    
    Args:
        reference_time: The reference game time
        
    Returns:
        Dict[str, int]: Time components (years, months, days, hours, minutes, seconds) since the reference time
    """
    current = TimeManager().game_time
    
    # Convert both times to days for easier calculation
    days_current = (
        current.year * 360 +  # Simplified 30-day months
        current.month * 30 +
        current.day
    )
    
    days_reference = (
        reference_time.year * 360 +
        reference_time.month * 30 +
        reference_time.day
    )
    
    # Calculate days difference
    days_diff = days_current - days_reference
    
    # Extract years, months, days
    years = days_diff // 360
    days_diff %= 360
    
    months = days_diff // 30
    days = days_diff % 30
    
    # Calculate hours, minutes, seconds
    seconds_current = current.hour * 3600 + current.minute * 60 + current.second
    seconds_reference = reference_time.hour * 3600 + reference_time.minute * 60 + reference_time.second
    
    seconds_diff = seconds_current - seconds_reference
    
    # Handle negative time (reference is later in the day)
    if seconds_diff < 0 and days > 0:
        seconds_diff += 86400  # Add one day worth of seconds
        days -= 1
    
    hours = seconds_diff // 3600
    seconds_diff %= 3600
    
    minutes = seconds_diff // 60
    seconds = seconds_diff % 60
    
    return {
        "years": years,
        "months": months,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds
    }


def format_time_since(reference_time: GameTime) -> str:
    """
    Format the time elapsed since a reference game time as a human-readable string.
    
    Args:
        reference_time: The reference game time
        
    Returns:
        str: Human-readable time elapsed (e.g., "2 years, 3 months", "5 hours ago")
    """
    time_diff = time_since(reference_time)
    
    if time_diff["years"] > 0:
        if time_diff["months"] > 0:
            return f"{time_diff['years']} {'year' if time_diff['years'] == 1 else 'years'}, {time_diff['months']} {'month' if time_diff['months'] == 1 else 'months'} ago"
        return f"{time_diff['years']} {'year' if time_diff['years'] == 1 else 'years'} ago"
    
    if time_diff["months"] > 0:
        if time_diff["days"] > 0:
            return f"{time_diff['months']} {'month' if time_diff['months'] == 1 else 'months'}, {time_diff['days']} {'day' if time_diff['days'] == 1 else 'days'} ago"
        return f"{time_diff['months']} {'month' if time_diff['months'] == 1 else 'months'} ago"
    
    if time_diff["days"] > 0:
        if time_diff["hours"] > 0:
            return f"{time_diff['days']} {'day' if time_diff['days'] == 1 else 'days'}, {time_diff['hours']} {'hour' if time_diff['hours'] == 1 else 'hours'} ago"
        return f"{time_diff['days']} {'day' if time_diff['days'] == 1 else 'days'} ago"
    
    if time_diff["hours"] > 0:
        if time_diff["minutes"] > 0:
            return f"{time_diff['hours']} {'hour' if time_diff['hours'] == 1 else 'hours'}, {time_diff['minutes']} {'minute' if time_diff['minutes'] == 1 else 'minutes'} ago"
        return f"{time_diff['hours']} {'hour' if time_diff['hours'] == 1 else 'hours'} ago"
    
    if time_diff["minutes"] > 0:
        return f"{time_diff['minutes']} {'minute' if time_diff['minutes'] == 1 else 'minutes'} ago"
    
    return "just now"


def schedule_one_time_event(
    callback_name: str,
    callback_data: Dict[str, Any] = None,
    trigger_time: Optional[datetime] = None,
    time_offset: Optional[timedelta] = None,
    priority: int = 0
) -> str:
    """
    Schedule a one-time event.
    
    Args:
        callback_name: Name of the registered callback to call
        callback_data: Data to pass to the callback
        trigger_time: Absolute time when event should trigger (or None for time_offset)
        time_offset: Relative time from now when event should trigger (ignored if trigger_time)
        priority: Priority of the event (higher priority events trigger first)
        
    Returns:
        str: The event ID
    """
    from backend.systems.time.models.time_model import EventType
    
    return TimeManager().schedule_event(
        event_type=EventType.ONE_TIME,
        callback_name=callback_name,
        callback_data=callback_data,
        trigger_time=trigger_time,
        time_offset=time_offset,
        priority=priority
    )


def schedule_recurring_event(
    recurrence_type: str,
    callback_name: str,
    callback_data: Dict[str, Any] = None,
    start_time: Optional[datetime] = None,
    start_offset: Optional[timedelta] = None,
    priority: int = 0
) -> str:
    """
    Schedule a recurring event.
    
    Args:
        recurrence_type: "daily", "weekly", "monthly", or "yearly"
        callback_name: Name of the registered callback to call
        callback_data: Data to pass to the callback
        start_time: When the recurrence should start (or None for start_offset)
        start_offset: Delay before first occurrence (ignored if start_time)
        priority: Priority of the event
        
    Returns:
        str: The event ID
    """
    from backend.systems.time.models.time_model import EventType
    
    # Convert recurrence_type to EventType
    recurrence_map = {
        "daily": EventType.RECURRING_DAILY,
        "weekly": EventType.RECURRING_WEEKLY,
        "monthly": EventType.RECURRING_MONTHLY,
        "yearly": EventType.RECURRING_YEARLY
    }
    
    if recurrence_type not in recurrence_map:
        raise ValueError(f"Unsupported recurrence type: {recurrence_type}")
    
    event_type = recurrence_map[recurrence_type]
    
    # Calculate recurrence interval
    interval_map = {
        "daily": timedelta(days=1),
        "weekly": timedelta(days=7),
        "monthly": timedelta(days=30),  # Simplified for game calendar
        "yearly": timedelta(days=360)   # Simplified for game calendar
    }
    
    return TimeManager().schedule_event(
        event_type=event_type,
        callback_name=callback_name,
        callback_data=callback_data,
        trigger_time=start_time,
        time_offset=start_offset,
        recurrence_interval=interval_map[recurrence_type],
        priority=priority
    )


def cancel_scheduled_event(event_id: str) -> bool:
    """
    Cancel a scheduled event.
    
    Args:
        event_id: The ID of the event to cancel
        
    Returns:
        bool: True if the event was found and cancelled, False otherwise
    """
    return TimeManager().cancel_event(event_id)


def register_event_callback(callback_name: str, callback_func: callable) -> None:
    """
    Register a callback function that can be used by time events.
    
    Args:
        callback_name: Name to register the callback under
        callback_func: Function to call when events with this callback name trigger
    """
    TimeManager().register_callback(callback_name, callback_func)


def advance_time(amount: int, unit: str) -> None:
    """
    Advance the game time by the specified amount and unit.
    
    Args:
        amount: The amount to advance by
        unit: The time unit to advance by ('tick', 'second', 'minute', 'hour', 'day', 'month', 'year')
    """
    # Convert string unit to TimeUnit enum
    unit_map = {
        "tick": TimeUnit.TICK,
        "second": TimeUnit.SECOND,
        "minute": TimeUnit.MINUTE,
        "hour": TimeUnit.HOUR,
        "day": TimeUnit.DAY,
        "month": TimeUnit.MONTH,
        "year": TimeUnit.YEAR
    }
    
    if unit not in unit_map:
        raise ValueError(f"Unsupported time unit: {unit}")
    
    TimeManager().advance_time(amount, unit_map[unit])


def is_leap_year(year: Optional[int] = None) -> bool:
    """
    Check if the specified year (or current year if None) is a leap year.
    
    Args:
        year: The year to check, or None for current year
        
    Returns:
        bool: True if the year is a leap year, False otherwise
    """
    time_manager = TimeManager()
    
    if year is None:
        year = time_manager.game_time.year
    
    return time_manager._is_leap_year(year)


def get_days_in_month(month: Optional[int] = None, year: Optional[int] = None) -> int:
    """
    Get the number of days in the specified month and year.
    
    Args:
        month: The month (1-12), or None for current month
        year: The year, or None for current year
        
    Returns:
        int: Number of days in the month
    """
    time_manager = TimeManager()
    
    if month is None:
        month = time_manager.game_time.month
    
    if year is None:
        year = time_manager.game_time.year
    
    return time_manager.get_days_in_month(month, year)


def add_important_date(name: str, month: int, day: int, year: Optional[int] = None) -> None:
    """
    Add an important date to the calendar (holiday, special occasion, etc.)
    
    Args:
        name: Name/identifier for the date
        month: Month (1-based)
        day: Day of month (1-based)
        year: Specific year, or None for yearly occurrence
    """
    TimeManager().add_important_date(name, month, day, year)


def is_important_date(month: Optional[int] = None, day: Optional[int] = None, year: Optional[int] = None) -> List[str]:
    """
    Check if the specified date (or current date if None) is an important date.
    
    Args:
        month: The month (1-12), or None for current month
        day: The day (1-31), or None for current day
        year: The year, or None for current year
        
    Returns:
        List[str]: Names of important dates on this day, or empty list if none
    """
    time_manager = TimeManager()
    
    if month is None:
        month = time_manager.game_time.month
    
    if day is None:
        day = time_manager.game_time.day
    
    if year is None:
        year = time_manager.game_time.year
    
    return time_manager.get_important_dates_for_date(year, month, day)


# ----------------
# FORMATTER UTILS
# ----------------

def format_time_difference(time_diff: Dict[str, int]) -> str:
    """
    Format a time difference dictionary as a human-readable string.
    
    Args:
        time_diff: Dictionary with time components (years, months, days, etc.)
        
    Returns:
        str: Human-readable time difference string
    """
    components = []
    
    if time_diff.get("years", 0) > 0:
        year_text = "year" if time_diff["years"] == 1 else "years"
        components.append(f"{time_diff['years']} {year_text}")
    
    if time_diff.get("months", 0) > 0:
        month_text = "month" if time_diff["months"] == 1 else "months"
        components.append(f"{time_diff['months']} {month_text}")
    
    if time_diff.get("days", 0) > 0:
        day_text = "day" if time_diff["days"] == 1 else "days"
        components.append(f"{time_diff['days']} {day_text}")
    
    if time_diff.get("hours", 0) > 0:
        hour_text = "hour" if time_diff["hours"] == 1 else "hours"
        components.append(f"{time_diff['hours']} {hour_text}")
    
    if time_diff.get("minutes", 0) > 0:
        minute_text = "minute" if time_diff["minutes"] == 1 else "minutes"
        components.append(f"{time_diff['minutes']} {minute_text}")
    
    if time_diff.get("seconds", 0) > 0:
        second_text = "second" if time_diff["seconds"] == 1 else "seconds"
        components.append(f"{time_diff['seconds']} {second_text}")
    
    if not components:
        return "just now"
    
    if len(components) == 1:
        return components[0]
    elif len(components) == 2:
        return f"{components[0]} and {components[1]}"
    else:
        return ", ".join(components[:-1]) + f", and {components[-1]}"


def time_to_string(game_time: GameTime, include_date: bool = True, 
                  include_time: bool = True, include_season: bool = False) -> str:
    """
    Convert a GameTime object to a human-readable string.
    
    Args:
        game_time: The game time to convert
        include_date: Whether to include the date part
        include_time: Whether to include the time part
        include_season: Whether to include the season
        
    Returns:
        str: Formatted time string
    """
    parts = []
    
    if include_date:
        date_str = f"Year {game_time.year}, Month {game_time.month}, Day {game_time.day}"
        parts.append(date_str)
    
    if include_time:
        time_str = f"{game_time.hour:02d}:{game_time.minute:02d}:{game_time.second:02d}"
        parts.append(time_str)
    
    if include_season and game_time.season:
        parts.append(f"({game_time.season.name.capitalize()})")
    
    return " - ".join(parts)


def get_time_of_day_name(hour: Optional[int] = None) -> str:
    """
    Get a descriptive name for the time of day.
    
    Args:
        hour: The hour to get the name for, or None for current hour
        
    Returns:
        str: Name of the time of day (e.g., "morning", "afternoon")
    """
    if hour is None:
        hour = TimeManager().game_time.hour
    
    if 5 <= hour < 8:
        return "early morning"
    elif 8 <= hour < 12:
        return "morning"
    elif 12 <= hour < 14:
        return "midday"
    elif 14 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def is_daytime(hour: Optional[int] = None) -> bool:
    """
    Check if the specified hour is during daytime.
    
    Args:
        hour: The hour to check, or None for current hour
        
    Returns:
        bool: True if it's daytime, False otherwise
    """
    if hour is None:
        hour = TimeManager().game_time.hour
    
    return 6 <= hour < 18


# ----------------
# TIME CALCULATION UTILS
# ----------------

def calculate_time_difference(earlier: GameTime, later: GameTime) -> Dict[str, int]:
    """
    Calculate the time difference between two game times.
    
    Args:
        earlier: The earlier game time
        later: The later game time
        
    Returns:
        Dict[str, int]: Dictionary with time difference components
    """
    # Convert both times to seconds for easier calculation
    seconds_earlier = (
        (earlier.year * 360 + earlier.month * 30 + earlier.day) * 86400 +
        earlier.hour * 3600 + earlier.minute * 60 + earlier.second
    )
    
    seconds_later = (
        (later.year * 360 + later.month * 30 + later.day) * 86400 +
        later.hour * 3600 + later.minute * 60 + later.second
    )
    
    # Calculate total seconds difference
    seconds_diff = seconds_later - seconds_earlier
    
    if seconds_diff < 0:
        raise ValueError("Later time must be after earlier time")
    
    # Extract time components
    days_diff = seconds_diff // 86400
    seconds_diff %= 86400
    
    years = days_diff // 360
    days_diff %= 360
    
    months = days_diff // 30
    days = days_diff % 30
    
    hours = seconds_diff // 3600
    seconds_diff %= 3600
    
    minutes = seconds_diff // 60
    seconds = seconds_diff % 60
    
    return {
        "years": years,
        "months": months,
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds
    }


def time_since(reference_time: GameTime) -> Dict[str, int]:
    """
    Calculate the time elapsed since a reference game time.
    
    Args:
        reference_time: The reference game time
        
    Returns:
        Dict[str, int]: Time components since the reference time
    """
    current_time = TimeManager().game_time
    try:
        return calculate_time_difference(reference_time, current_time)
    except ValueError:
        # Handle case where reference_time is in the future
        return calculate_time_difference(current_time, reference_time)


def format_time_since(reference_time: GameTime) -> str:
    """
    Format the time elapsed since a reference game time as a human-readable string.
    
    Args:
        reference_time: The reference game time
        
    Returns:
        str: Human-readable time elapsed
    """
    try:
        time_diff = time_since(reference_time)
        return format_time_difference(time_diff) + " ago"
    except ValueError:
        # Handle case where reference_time is in the future
        current_time = TimeManager().game_time
        time_diff = calculate_time_difference(current_time, reference_time)
        return "in " + format_time_difference(time_diff)


def format_time_remaining(target_time: GameTime) -> str:
    """
    Format the time remaining until a target game time.
    
    Args:
        target_time: The target game time
        
    Returns:
        str: Human-readable time remaining
    """
    current_time = TimeManager().game_time
    try:
        time_diff = calculate_time_difference(current_time, target_time)
        return format_time_difference(time_diff)
    except ValueError:
        return "already passed"


def convert_time_units(amount: float, from_unit: TimeUnit, to_unit: TimeUnit) -> float:
    """
    Convert an amount from one time unit to another.
    
    Args:
        amount: The amount to convert
        from_unit: The source time unit
        to_unit: The target time unit
        
    Returns:
        float: The converted amount
    """
    # Define time unit conversion factors
    unit_to_seconds = {
        TimeUnit.TICK: 1 / TimeManager().config.ticks_per_second,
        TimeUnit.SECOND: 1,
        TimeUnit.MINUTE: 60,
        TimeUnit.HOUR: 3600,
        TimeUnit.DAY: 86400,
        TimeUnit.MONTH: 86400 * 30,  # Simplified 30-day months
        TimeUnit.YEAR: 86400 * 360,  # Simplified 360-day years
    }
    
    # Convert to seconds first, then to target unit
    seconds = amount * unit_to_seconds[from_unit]
    return seconds / unit_to_seconds[to_unit]


def parse_time_string(time_str: str) -> Optional[GameTime]:
    """
    Parse a time string into a GameTime object.
    
    Supported formats:
    - "YYYY-MM-DD HH:MM:SS"
    - "MM-DD HH:MM"
    - "HH:MM:SS"
    - "HH:MM"
    
    Args:
        time_str: The time string to parse
        
    Returns:
        Optional[GameTime]: Parsed game time or None if parsing failed
    """
    try:
        current_time = TimeManager().game_time
        result = GameTime(
            year=current_time.year,
            month=current_time.month,
            day=current_time.day,
            hour=0,
            minute=0,
            second=0
        )
        
        # Try different formats
        parts = time_str.split()
        
        if len(parts) == 2:  # Date and time
            date_part, time_part = parts
            
            # Parse date
            date_elements = date_part.split('-')
            if len(date_elements) == 3:  # YYYY-MM-DD
                result.year = int(date_elements[0])
                result.month = int(date_elements[1])
                result.day = int(date_elements[2])
            elif len(date_elements) == 2:  # MM-DD
                result.month = int(date_elements[0])
                result.day = int(date_elements[1])
            
            # Parse time
            time_elements = time_part.split(':')
            result.hour = int(time_elements[0])
            if len(time_elements) > 1:
                result.minute = int(time_elements[1])
            if len(time_elements) > 2:
                result.second = int(time_elements[2])
            
        elif len(parts) == 1:  # Only time
            time_elements = parts[0].split(':')
            result.hour = int(time_elements[0])
            if len(time_elements) > 1:
                result.minute = int(time_elements[1])
            if len(time_elements) > 2:
                result.second = int(time_elements[2])
        
        return result
    
    except Exception:
        return None


# ----------------
# DATE VALIDATION UTILS
# ----------------

def is_valid_date(year: int, month: int, day: int) -> bool:
    """
    Check if a date is valid according to the game calendar.
    
    Args:
        year: Year
        month: Month (1-12)
        day: Day
        
    Returns:
        bool: True if the date is valid, False otherwise
    """
    time_manager = TimeManager()
    calendar = time_manager.calendar
    
    if month < 1 or month > calendar.months_per_year:
        return False
    
    days_in_month = time_manager.get_days_in_month(month, year)
    return 1 <= day <= days_in_month


def get_date_string(date: Union[Dict[str, int], GameTime], format_str: str = "full") -> str:
    """
    Format a date as a string according to the specified format.
    
    Args:
        date: Dictionary with year, month, day or GameTime object
        format_str: Format string ("full", "short", "medium")
        
    Returns:
        str: Formatted date string
    """
    if isinstance(date, GameTime):
        year, month, day = date.year, date.month, date.day
    else:
        year = date.get("year", 1)
        month = date.get("month", 1)
        day = date.get("day", 1)
    
    if format_str == "short":
        return f"{month}/{day}"
    elif format_str == "medium":
        return f"{month}/{day}/{year}"
    else:  # "full"
        return f"Year {year}, Month {month}, Day {day}"


# ----------------
# TIME COMPARISON UTILS
# ----------------

def is_same_day(time1: GameTime, time2: GameTime) -> bool:
    """
    Check if two game times are on the same day.
    
    Args:
        time1: First game time
        time2: Second game time
        
    Returns:
        bool: True if the times are on the same day
    """
    return (
        time1.year == time2.year and
        time1.month == time2.month and
        time1.day == time2.day
    )


def is_same_month(time1: GameTime, time2: GameTime) -> bool:
    """
    Check if two game times are in the same month.
    
    Args:
        time1: First game time
        time2: Second game time
        
    Returns:
        bool: True if the times are in the same month
    """
    return time1.year == time2.year and time1.month == time2.month


def time_in_range(time: GameTime, start: GameTime, end: GameTime) -> bool:
    """
    Check if a game time is within a range (inclusive).
    
    Args:
        time: The time to check
        start: Start of the range
        end: End of the range
        
    Returns:
        bool: True if the time is within the range
    """
    # Convert all times to a comparable format (total seconds)
    def time_to_seconds(t: GameTime) -> int:
        return (
            (t.year * 360 + t.month * 30 + t.day) * 86400 +
            t.hour * 3600 + t.minute * 60 + t.second
        )
    
    time_seconds = time_to_seconds(time)
    start_seconds = time_to_seconds(start)
    end_seconds = time_to_seconds(end)
    
    return start_seconds <= time_seconds <= end_seconds 