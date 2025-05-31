"""
Core event system components.

This package contains the fundamental building blocks of the event system:
- EventBase: Base class for all events
- EventDispatcher: Core event dispatch functionality
"""

from .event_base import *
from ..services.event_dispatcher import EventDispatcher

__all__ = ['EventDispatcher']
