"""Shared utils.time.py module."""

from datetime import datetime, timezone


def get_current_time() -> datetime:
    """Get the current UTC time."""
    return datetime.now(timezone.utc)


def get_current_timestamp() -> float:
    """Get the current timestamp as a float."""
    return datetime.now(timezone.utc).timestamp()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object to string."""
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse a datetime string to datetime object."""
    return datetime.strptime(dt_str, format_str)
