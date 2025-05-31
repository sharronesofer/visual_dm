"""
Event logger for analytics infrastructure.

Provides centralized event logging functionality for tracking user actions,
system events, and analytics data across the Visual DM backend.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum

# Set up logger
logger = logging.getLogger(__name__)


class EventType(Enum):
    """Event type enumeration."""
    USER_ACTION = "user_action"
    SYSTEM_EVENT = "system_event"
    DIALOGUE_EVENT = "dialogue_event"
    CHARACTER_EVENT = "character_event"
    ANALYTICS_EVENT = "analytics_event"
    ERROR_EVENT = "error_event"


@dataclass
class Event:
    """Event data structure."""
    event_type: EventType
    event_name: str
    timestamp: datetime
    data: Dict[str, Any]
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        result = asdict(self)
        result['event_type'] = self.event_type.value
        result['timestamp'] = self.timestamp.isoformat()
        return result


class EventLogger:
    """
    Centralized event logger for analytics and monitoring.
    
    Provides singleton access to event logging functionality with
    support for different event types and filtering.
    """
    
    _instance: Optional['EventLogger'] = None
    
    def __init__(self):
        """Initialize event logger."""
        self.events: List[Event] = []
        self.max_events = 10000  # Maximum events to keep in memory
        
    @classmethod
    def get_instance(cls) -> 'EventLogger':
        """Get singleton instance of event logger."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def log_event(
        self,
        event_type: Union[EventType, str],
        event_name: str,
        data: Dict[str, Any],
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log an event.
        
        Args:
            event_type: Type of event
            event_name: Name/identifier of the event
            data: Event data
            user_id: Optional user ID
            session_id: Optional session ID
            metadata: Optional metadata
            
        Returns:
            bool: True if event was logged successfully
        """
        try:
            # Convert string to enum if needed
            if isinstance(event_type, str):
                try:
                    event_type = EventType(event_type)
                except ValueError:
                    event_type = EventType.SYSTEM_EVENT
            
            # Create event
            event = Event(
                event_type=event_type,
                event_name=event_name,
                timestamp=datetime.utcnow(),
                data=data or {},
                user_id=user_id,
                session_id=session_id,
                metadata=metadata or {}
            )
            
            # Add to events list
            self.events.append(event)
            
            # Trim events if we exceed max
            if len(self.events) > self.max_events:
                self.events = self.events[-self.max_events:]
            
            # Log to standard logger
            logger.info(f"Event logged: {event_name} ({event_type.value})")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to log event {event_name}: {e}")
            return False
    
    def query_events(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Event]:
        """
        Query events with optional filters.
        
        Args:
            filters: Optional filters to apply
            limit: Optional limit on number of results
            
        Returns:
            List of matching events
        """
        try:
            events = self.events.copy()
            
            # Apply filters if provided
            if filters:
                filtered_events = []
                for event in events:
                    match = True
                    
                    # Check event type filter
                    if 'event_type' in filters:
                        filter_type = filters['event_type']
                        if isinstance(filter_type, str):
                            filter_type = EventType(filter_type)
                        if event.event_type != filter_type:
                            match = False
                    
                    # Check event name filter
                    if 'event_name' in filters and event.event_name != filters['event_name']:
                        match = False
                    
                    # Check user ID filter
                    if 'user_id' in filters and event.user_id != filters['user_id']:
                        match = False
                    
                    # Check session ID filter
                    if 'session_id' in filters and event.session_id != filters['session_id']:
                        match = False
                    
                    # Check timestamp range filters
                    if 'start_time' in filters:
                        start_time = filters['start_time']
                        if isinstance(start_time, str):
                            start_time = datetime.fromisoformat(start_time)
                        if event.timestamp < start_time:
                            match = False
                    
                    if 'end_time' in filters:
                        end_time = filters['end_time']
                        if isinstance(end_time, str):
                            end_time = datetime.fromisoformat(end_time)
                        if event.timestamp > end_time:
                            match = False
                    
                    if match:
                        filtered_events.append(event)
                
                events = filtered_events
            
            # Apply limit if provided
            if limit and limit > 0:
                events = events[-limit:]
            
            return events
            
        except Exception as e:
            logger.error(f"Failed to query events: {e}")
            return []
    
    def get_event_count(self, event_type: Optional[Union[EventType, str]] = None) -> int:
        """
        Get count of events, optionally filtered by type.
        
        Args:
            event_type: Optional event type to filter by
            
        Returns:
            Number of matching events
        """
        if event_type is None:
            return len(self.events)
        
        if isinstance(event_type, str):
            try:
                event_type = EventType(event_type)
            except ValueError:
                return 0
        
        return len([e for e in self.events if e.event_type == event_type])
    
    def clear_events(self) -> None:
        """Clear all events."""
        self.events.clear()
        logger.info("All events cleared")
    
    def export_events(
        self,
        filters: Optional[Dict[str, Any]] = None,
        format: str = "json"
    ) -> str:
        """
        Export events to string format.
        
        Args:
            filters: Optional filters to apply
            format: Export format ("json" or "csv")
            
        Returns:
            Exported events as string
        """
        events = self.query_events(filters)
        
        if format.lower() == "json":
            return json.dumps([event.to_dict() for event in events], indent=2)
        elif format.lower() == "csv":
            if not events:
                return ""
            
            # Simple CSV export
            lines = ["timestamp,event_type,event_name,user_id,session_id,data"]
            for event in events:
                data_str = json.dumps(event.data).replace('"', '""')
                line = f"{event.timestamp.isoformat()},{event.event_type.value},{event.event_name},{event.user_id or ''},{event.session_id or ''},\"{data_str}\""
                lines.append(line)
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")


# Convenience functions for common event types
def log_user_action(
    action_name: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> bool:
    """Log a user action event."""
    logger_instance = EventLogger.get_instance()
    return logger_instance.log_event(
        EventType.USER_ACTION,
        action_name,
        data,
        user_id,
        session_id
    )


def log_system_event(
    event_name: str,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Log a system event."""
    logger_instance = EventLogger.get_instance()
    return logger_instance.log_event(
        EventType.SYSTEM_EVENT,
        event_name,
        data,
        metadata=metadata
    )


def log_dialogue_event(
    event_name: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> bool:
    """Log a dialogue event."""
    logger_instance = EventLogger.get_instance()
    return logger_instance.log_event(
        EventType.DIALOGUE_EVENT,
        event_name,
        data,
        user_id,
        session_id
    )


def log_character_event(
    event_name: str,
    data: Dict[str, Any],
    user_id: Optional[str] = None,
    session_id: Optional[str] = None
) -> bool:
    """Log a character event."""
    logger_instance = EventLogger.get_instance()
    return logger_instance.log_event(
        EventType.CHARACTER_EVENT,
        event_name,
        data,
        user_id,
        session_id
    )


def log_error_event(
    error_name: str,
    error_data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> bool:
    """Log an error event."""
    logger_instance = EventLogger.get_instance()
    return logger_instance.log_event(
        EventType.ERROR_EVENT,
        error_name,
        error_data,
        metadata=metadata
    ) 