"""
Event system package for event-driven architecture.

This package provides a robust event system for communication between components,
with a focus on scene management integration.
"""

from .scene_events import SceneEvent, SceneEventType, create_event
from .event_bus import EventBus, EventPriority
from .scene_event_system import SceneEventSystem, DependencyType

__all__ = [
    'SceneEvent',
    'SceneEventType',
    'create_event',
    'EventBus',
    'EventPriority',
    'SceneEventSystem',
    'DependencyType'
] 