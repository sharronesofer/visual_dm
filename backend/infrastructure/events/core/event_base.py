"""
Base class for all events in the Visual DM system.

This module defines EventBase, the foundation for all events used throughout
the application. All event types must inherit from EventBase to ensure
consistent behavior and properties.
"""
from pydantic import BaseModel, Field, ConfigDict
import time
from typing import TypeVar

T = TypeVar('T', bound='EventBase')

class EventBase(BaseModel):
    """
    Base class for all event types in the system.
    
    All events must inherit from this class to ensure consistency and
    to provide common functionality across event types. This ensures
    all events have a type and timestamp at minimum.
    
    Attributes:
        event_type: String identifier for the event
        timestamp: Unix timestamp when the event was created
    """
    event_type: str
    timestamp: float = Field(default_factory=time.time)
    
    model_config = ConfigDict(arbitrary_types_allowed=True) 