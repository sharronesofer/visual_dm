"""
Event integration for the DM system.

This module integrates the DM system with the central event dispatcher,
implementing the event-driven architecture described in the Development Bible.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from firebase_admin import db
from pydantic import BaseModel, Field

# Define Event Types

class EventBase(BaseModel):
    """Base class for all events in the system."""
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_id: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True


class MemoryEvent(EventBase):
    """Event emitted when memory-related activities occur."""
    entity_id: str
    memory_id: str
    operation: str  # created, reinforced, recalled, forgotten
    memory_data: Optional[Dict[str, Any]] = None
    importance: Optional[float] = None
    tags: List[str] = []


class RumorEvent(EventBase):
    """Event emitted when rumors are created or spread."""
    rumor_id: str
    source_entity_id: str
    target_entity_ids: List[str] = []
    rumor_type: str  # scandal, secret, etc.
    rumor_data: Optional[Dict[str, Any]] = None
    mutated: bool = False


class MotifEvent(EventBase):
    """Event emitted when motifs are created or detected."""
    motif_id: str
    motif_name: str
    motif_category: str
    entity_id: Optional[str] = None
    region_id: Optional[str] = None
    occurrence_id: Optional[str] = None
    strength: Optional[float] = None


class FactionEvent(EventBase):
    """Event emitted for faction-related activities."""
    faction_id: str
    faction_name: Optional[str] = None
    faction_type: Optional[str] = None
    target_faction_id: Optional[str] = None
    reputation: Optional[float] = None
    influence: Optional[float] = None
    is_public: Optional[bool] = None
    goal_id: Optional[str] = None
    goal_title: Optional[str] = None
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    resource_type: Optional[str] = None
    importance: Optional[int] = None


class EventDispatcher:
    """
    Singleton event dispatcher following the publisher-subscriber pattern.
    
    Acts as the central hub for all events in the system, allowing components
    to emit events and subscribe to events from other components.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the EventDispatcher."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the event dispatcher."""
        if EventDispatcher._instance is not None:
            raise Exception("This class is a singleton. Use get_instance() instead.")
        
        EventDispatcher._instance = self
        self.subscribers = {}
        self.logger = logging.getLogger(__name__)
    
    def subscribe(self, event_type: str, callback):
        """
        Subscribe to an event type.
        
        Args:
            event_type: The type of event to subscribe to (use '*' for all events)
            callback: Function to call when event occurs
        """
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        
        self.subscribers[event_type].append(callback)
        self.logger.debug(f"Subscribed to {event_type} events")
    
    def publish(self, event: EventBase):
        """
        Publish an event to all subscribers.
        
        Args:
            event: The event to publish
        """
        # Store event in Firebase for history/auditing
        self._store_event(event)
        
        # Get specific subscribers and wildcard subscribers
        specific_subscribers = self.subscribers.get(event.event_type, [])
        wildcard_subscribers = self.subscribers.get('*', [])
        
        # Combine both subscriber lists
        all_subscribers = specific_subscribers + wildcard_subscribers
        
        if not all_subscribers:
            self.logger.debug(f"No subscribers for event type {event.event_type}")
            return
        
        # Notify all subscribers
        for callback in all_subscribers:
            try:
                callback(event)
            except Exception as e:
                self.logger.error(f"Error in event subscriber: {e}")
    
    def _store_event(self, event: EventBase):
        """
        Store an event in Firebase for history/auditing.
        
        Args:
            event: The event to store
        """
        try:
            # Convert to dict
            event_dict = event.dict()
            
            # Convert datetime to string for Firebase
            event_dict["timestamp"] = event_dict["timestamp"].isoformat()
            
            # Store in Firebase
            events_ref = db.reference("/events")
            new_event_ref = events_ref.push()
            new_event_ref.set(event_dict)
        except Exception as e:
            self.logger.error(f"Error storing event: {e}")


# Initialize the event dispatcher
event_dispatcher = EventDispatcher.get_instance()

class MotifChangedEvent(EventBase):
    """Event emitted when a global or regional motif changes."""
    region_id: Optional[str] = None  # None for global motif
    old_motif: Optional[Dict[str, Any]] = None
    new_motif: Dict[str, Any]
    intensity: int


class POIStateChangedEvent(EventBase):
    """Event emitted when a POI changes state."""
    region_id: str
    poi_id: str
    old_state: str
    new_state: str
    reason: Optional[str] = None


class QuestUpdatedEvent(EventBase):
    """Event emitted when a quest status or progress changes."""
    quest_id: str
    character_id: str
    old_status: Optional[str] = None
    new_status: str
    progress: float


class CombatEvent(EventBase):
    """Event emitted for combat-related activities."""
    combat_id: str
    action_type: str  # start, end, attack, effect
    actor_id: Optional[str] = None
    target_id: Optional[str] = None
    details: Dict[str, Any]


class TimeAdvancedEvent(EventBase):
    """Event emitted when in-game time advances."""
    old_time: Dict[str, Any]
    new_time: Dict[str, Any]
    units_advanced: Dict[str, int]  # e.g., {"days": 1, "hours": 0}


class EventDispatcher:
    """
    Singleton event dispatcher implementing the Event Bus pattern.
    
    This follows the publish-subscribe model for loose coupling between components.
    """
    _instance = None
    
    @classmethod
    def get_instance(cls):
        """Get the singleton instance of the EventDispatcher."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self):
        """Initialize the event dispatcher."""
        if EventDispatcher._instance is not None:
            raise Exception("This class is a singleton. Use get_instance() instead.")
        
        EventDispatcher._instance = self
        self.subscribers = {}
        self.middlewares = []
    
    def subscribe(self, event_type, handler):
        """
        Subscribe a handler to a specific event type.
        
        Args:
            event_type: The event class or type to subscribe to
            handler: The function to call when an event of this type is published
        """
        event_name = event_type.__name__ if hasattr(event_type, '__name__') else str(event_type)
        
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        
        self.subscribers[event_name].append(handler)
        return self  # For method chaining
    
    def unsubscribe(self, event_type, handler):
        """
        Unsubscribe a handler from a specific event type.
        
        Args:
            event_type: The event class or type to unsubscribe from
            handler: The handler function to remove
        """
        event_name = event_type.__name__ if hasattr(event_type, '__name__') else str(event_type)
        
        if event_name in self.subscribers:
            if handler in self.subscribers[event_name]:
                self.subscribers[event_name].remove(handler)
        
        return self  # For method chaining
    
    def add_middleware(self, middleware):
        """
        Add middleware to the event processing pipeline.
        
        Middleware can intercept, log, or modify events.
        
        Args:
            middleware: A function that takes an event and returns a modified event
        """
        self.middlewares.append(middleware)
        return self  # For method chaining
    
    def publish(self, event):
        """
        Publish an event to all subscribers.
        
        This processes the event through all middleware and delivers it to subscribers.
        
        Args:
            event: The event to publish
        """
        # Apply middleware
        processed_event = event
        for middleware in self.middlewares:
            processed_event = middleware(processed_event)
            if not processed_event:
                # Middleware can cancel event propagation by returning None
                return
        
        # Find event type
        event_name = processed_event.__class__.__name__
        
        # Deliver to subscribers
        if event_name in self.subscribers:
            for handler in self.subscribers[event_name]:
                try:
                    handler(processed_event)
                except Exception as e:
                    logging.error(f"Error in event handler for {event_name}: {e}")
        
        # Log event to Firebase for analytics
        try:
            self._log_event(processed_event)
        except Exception as e:
            logging.error(f"Error logging event to Firebase: {e}")
    
    def publish_sync(self, event):
        """
        Synchronous version of publish.
        
        Args:
            event: The event to publish
        """
        self.publish(event)
    
    def _log_event(self, event):
        """
        Log an event to Firebase for analytics.
        
        Args:
            event: The event to log
        """
        event_dict = event.dict()
        # Convert datetime to ISO format for Firebase
        if "timestamp" in event_dict:
            event_dict["timestamp"] = event_dict["timestamp"].isoformat()
        
        event_type = event.__class__.__name__
        log_ref = db.reference(f"/event_log/{event_type}")
        log_ref.push(event_dict)


# Example middleware functions

def logging_middleware(event):
    """Middleware that logs all events."""
    logging.info(f"Event dispatched: {event.__class__.__name__}")
    return event

def analytics_middleware(event):
    """Middleware that sends event data to analytics."""
    # Here you would implement any analytics-specific processing
    return event

def filtering_middleware(event):
    """Middleware that can filter or modify events."""
    # Here you can implement logic to filter or modify events
    return event


# Initialize the event dispatcher
dispatcher = EventDispatcher.get_instance()

# Add middleware
dispatcher.add_middleware(logging_middleware)
dispatcher.add_middleware(analytics_middleware)
dispatcher.add_middleware(filtering_middleware) 