"""
Base event classes for the event system.
"""

from dataclasses import dataclass
from typing import Any, Dict
from datetime import datetime
import uuid

@dataclass
class Event:
    """Base event class for all system events."""
    
    event_type: str
    data: Dict[str, Any]
    timestamp: datetime = None
    event_id: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.event_id is None:
            self.event_id = str(uuid.uuid4())
