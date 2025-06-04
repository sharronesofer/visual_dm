"""Events for world_state system"""

# HACK: Placeholder event classes to fix missing imports
# TODO: Implement proper event classes or restructure imports
from typing import Any, Optional
from enum import Enum

class StateChangeType(Enum):
    """Types of state changes"""
    CREATED = "created"
    UPDATED = "updated"
    DELETED = "deleted"
    CALCULATED = "calculated"

class WorldStateEvent:
    """Base world state event"""
    def __init__(self, state_key: str, change_type: StateChangeType, **kwargs):
        self.state_key = state_key
        self.change_type = change_type
        self.category = kwargs.get('category')
        self.region = kwargs.get('region')
        self.entity_id = kwargs.get('entity_id')

class WorldStateCreatedEvent(WorldStateEvent):
    """Event for state creation"""
    def __init__(self, state_key: str, new_value: Any, **kwargs):
        super().__init__(state_key, StateChangeType.CREATED, **kwargs)
        self.new_value = new_value

class WorldStateUpdatedEvent(WorldStateEvent):
    """Event for state updates"""
    def __init__(self, state_key: str, old_value: Any, new_value: Any, **kwargs):
        super().__init__(state_key, StateChangeType.UPDATED, **kwargs)
        self.old_value = old_value
        self.new_value = new_value

class WorldStateDeletedEvent(WorldStateEvent):
    """Event for state deletion"""
    def __init__(self, state_key: str, old_value: Any, **kwargs):
        super().__init__(state_key, StateChangeType.DELETED, **kwargs)
        self.old_value = old_value

class WorldStateCalculatedEvent(WorldStateEvent):
    """Event for calculated states"""
    def __init__(self, state_key: str, new_value: Any, **kwargs):
        super().__init__(state_key, StateChangeType.CALCULATED, **kwargs)
        self.new_value = new_value

# Import handlers after defining events to avoid circular imports
# from .handlers import *
