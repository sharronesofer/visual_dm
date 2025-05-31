"""
Core event system components.

This package contains the fundamental building blocks of the event system:
- EventBase: Base class for all events
- EventDispatcher: Singleton event bus
"""

from .event_base import EventBase
from ..services.event_dispatcher import EventDispatcher

__all__ = [
    'EventBase',
    'EventDispatcher',
]
