"""
Religion Event Infrastructure

Event handling and publishing for religion system.
"""

from .event_publisher import ReligionEventPublisher, get_religion_event_publisher
from . import religion_events

__all__ = [
    "ReligionEventPublisher",
    "get_religion_event_publisher", 
    "religion_events",
]

