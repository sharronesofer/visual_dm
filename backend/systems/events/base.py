"""
Base class for all events in the Visual DM system.

This module defines EventBase, the foundation for all events used throughout
the application. All event types must inherit from EventBase to ensure
consistent behavior and properties.
"""
from datetime import datetime
from pydantic import BaseModel, Field
import time
from typing import TypeVar, Any, Dict, Optional

T = TypeVar('T', bound='EventBase')

class EventBase(BaseModel):
    """
    Base class for all event types in the system.
    
    All events must inherit from this class to ensure consistency and
    to provide common functionality across event types. This ensures
    all events have a type and timestamp at minimum.
    
    Attributes:
        event_type: String identifier for the event
        timestamp: Time when the event was created (unix timestamp float or datetime)
    """
    event_type: str
    timestamp: Any = Field(default_factory=time.time)
    
    class Config:
        arbitrary_types_allowed = True
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary format."""
        return self.dict()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EventBase':
        """Create event from dictionary data."""
        return cls(**data)
        
    def __str__(self) -> str:
        """String representation of the event."""
        return f"{self.__class__.__name__}(event_type={self.event_type}, timestamp={self.timestamp})" 