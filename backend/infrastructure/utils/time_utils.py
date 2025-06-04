"""
Time system - Time Utils.

Utility functions for time calculations, conversions, and common operations.
"""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from backend.systems.game_time.models.time_model import GameTime, Season, TimeUnit


def game_time_to_datetime(game_time: GameTime) -> datetime:
    """
    Convert a GameTime object to a standard datetime object.
    
    Args:
        game_time: The GameTime object to convert
        
    Returns:
        datetime: A datetime representation of the game time
    """
    return datetime(
        year=game_time.year,
        month=game_time.month,
        day=game_time.day,
        hour=game_time.hour,
        minute=game_time.minute,
        second=game_time.second
    )


def datetime_to_game_time(dt: datetime, existing_game_time: Optional[GameTime] = None) -> GameTime:
    """
    Convert a datetime object to a GameTime object.
    
    Args:
        dt: The datetime to convert
        existing_game_time: Optional existing GameTime to copy settings from
        
    Returns:
        GameTime: A GameTime representation of the datetime
    """
    if existing_game_time:
        # Preserve settings from existing GameTime
        return GameTime(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            tick=existing_game_time.tick,
            time_scale=existing_game_time.time_scale,
            is_paused=existing_game_time.is_paused,
            total_game_seconds=existing_game_time.total_game_seconds,
            season=existing_game_time.season,
            current_datetime=existing_game_time.current_datetime
        )
    else:
        return GameTime(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second
        )


def calculate_time_difference(time1: GameTime, time2: GameTime) -> Dict[str, int]:
    """
    Calculate the difference between two GameTime objects.
    
    Args:
        time1: First time (later time)
        time2: Second time (earlier time)
        
    Returns:
        Dict containing the difference in various units
    """
    dt1 = game_time_to_datetime(time1)
    dt2 = game_time_to_datetime(time2)
    
    diff = dt1 - dt2
    total_seconds = int(diff.total_seconds())
    
    return {
        "total_seconds": total_seconds,
        "total_minutes": total_seconds // 60,
        "total_hours": total_seconds // 3600,
        "total_days": total_seconds // 86400,
        "days": diff.days,
        "hours": (total_seconds % 86400) // 3600,
        "minutes": (total_seconds % 3600) // 60,
        "seconds": total_seconds % 60
    }


def add_time_to_game_time(game_time: GameTime, amount: int, unit: TimeUnit) -> GameTime:
    """
    Add a specific amount of time to a GameTime object.
    
    Args:
        game_time: The base GameTime
        amount: Amount to add
        unit: Unit of time to add
        
    Returns:
        GameTime: New GameTime with added time
    """
    dt = game_time_to_datetime(game_time)
    
    if unit == TimeUnit.SECONDS:
        dt += timedelta(seconds=amount)
    elif unit == TimeUnit.MINUTES:
        dt += timedelta(minutes=amount)
    elif unit == TimeUnit.HOURS:
        dt += timedelta(hours=amount)
    elif unit == TimeUnit.DAYS:
        dt += timedelta(days=amount)
    elif unit == TimeUnit.WEEKS:
        dt += timedelta(weeks=amount)
    elif unit == TimeUnit.MONTHS:
        # Approximate: add 30 days per month
        dt += timedelta(days=amount * 30)
    elif unit == TimeUnit.YEARS:
        # Approximate: add 365 days per year
        dt += timedelta(days=amount * 365)
    else:
        raise ValueError(f"Unsupported time unit: {unit}")
    
    return datetime_to_game_time(dt, game_time)


def format_game_time(game_time: GameTime, include_date: bool = True, include_time: bool = True, include_season: bool = False) -> str:
    """
    Format a GameTime object as a human-readable string.
    
    Args:
        game_time: The GameTime to format
        include_date: Whether to include the date
        include_time: Whether to include the time
        include_season: Whether to include the season
        
    Returns:
        str: Formatted time string
    """
    parts = []
    
    if include_date:
        parts.append(f"Year {game_time.year}, Month {game_time.month}, Day {game_time.day}")
    
    if include_time:
        parts.append(f"{game_time.hour:02d}:{game_time.minute:02d}:{game_time.second:02d}")
    
    if include_season:
        parts.append(f"Season: {game_time.season.value.title()}")
    
    return " - ".join(parts)


def get_season_from_day_of_year(day_of_year: int, total_days: int = 365) -> Season:
    """
    Calculate the season based on day of year.
    
    Args:
        day_of_year: Current day of the year (1-365/366)
        total_days: Total days in the year
        
    Returns:
        Season: The calculated season
    """
    # Divide year into 4 equal seasons
    season_length = total_days / 4
    
    if day_of_year <= season_length:
        return Season.WINTER
    elif day_of_year <= season_length * 2:
        return Season.SPRING
    elif day_of_year <= season_length * 3:
        return Season.SUMMER
    else:
        return Season.AUTUMN


def calculate_day_of_year(month: int, day: int, days_per_month: int = 30) -> int:
    """
    Calculate the day of year from month and day.
    
    Args:
        month: Month (1-12)
        day: Day of month (1-31)
        days_per_month: Days per month (simplified calendar)
        
    Returns:
        int: Day of year (1-365/366)
    """
    return ((month - 1) * days_per_month) + day


def is_leap_year(year: int, leap_interval: int = 4) -> bool:
    """
    Check if a year is a leap year.
    
    Args:
        year: The year to check
        leap_interval: Interval for leap years
        
    Returns:
        bool: True if it's a leap year
    """
    return year % leap_interval == 0


def validate_game_time(game_time: GameTime, calendar_config: Optional[Dict[str, Any]] = None) -> bool:
    """
    Validate that a GameTime object has valid values.
    
    Args:
        game_time: The GameTime to validate
        calendar_config: Optional calendar configuration for validation
        
    Returns:
        bool: True if valid, False otherwise
    """
    # Basic validation
    if game_time.month < 1 or game_time.month > 12:
        return False
    
    if game_time.day < 1 or game_time.day > 31:
        return False
    
    if game_time.hour < 0 or game_time.hour > 23:
        return False
    
    if game_time.minute < 0 or game_time.minute > 59:
        return False
    
    if game_time.second < 0 or game_time.second > 59:
        return False
    
    if game_time.tick < 0:
        return False
    
    # Advanced validation with calendar config
    if calendar_config:
        max_month = calendar_config.get("months_per_year", 12)
        max_day = calendar_config.get("days_per_month", 30)
        
        if game_time.month > max_month:
            return False
        
        if game_time.day > max_day:
            return False
    
    return True


def get_time_until_next_season(game_time: GameTime, days_per_month: int = 30, months_per_year: int = 12) -> Dict[str, int]:
    """
    Calculate time until the next season change.
    
    Args:
        game_time: Current game time
        days_per_month: Days per month in the calendar
        months_per_year: Months per year in the calendar
        
    Returns:
        Dict containing days, hours, minutes until next season
    """
    total_days_in_year = days_per_month * months_per_year
    current_day_of_year = calculate_day_of_year(game_time.month, game_time.day, days_per_month)
    
    # Calculate next season boundary
    season_length = total_days_in_year // 4
    current_season_start = ((current_day_of_year - 1) // season_length) * season_length
    next_season_start = current_season_start + season_length
    
    if next_season_start > total_days_in_year:
        next_season_start = total_days_in_year
    
    days_until_next_season = next_season_start - current_day_of_year
    
    # Convert to time units
    total_seconds_until = (days_until_next_season * 24 * 60 * 60) - (game_time.hour * 3600) - (game_time.minute * 60) - game_time.second
    
    return {
        "days": total_seconds_until // 86400,
        "hours": (total_seconds_until % 86400) // 3600,
        "minutes": (total_seconds_until % 3600) // 60,
        "seconds": total_seconds_until % 60,
        "total_seconds": total_seconds_until
    }


def convert_real_time_to_game_time(real_seconds: float, time_scale: float = 1.0, real_seconds_per_game_hour: float = 60.0) -> Dict[str, int]:
    """
    Convert real-world elapsed time to game time units.
    
    Args:
        real_seconds: Real seconds elapsed
        time_scale: Time scale multiplier
        real_seconds_per_game_hour: How many real seconds equal one game hour
        
    Returns:
        Dict containing game time units
    """
    # Calculate game seconds elapsed
    game_seconds = real_seconds * time_scale * (3600 / real_seconds_per_game_hour)
    
    return {
        "seconds": int(game_seconds % 60),
        "minutes": int((game_seconds // 60) % 60),
        "hours": int((game_seconds // 3600) % 24),
        "days": int(game_seconds // 86400),
        "total_game_seconds": int(game_seconds)
    }
