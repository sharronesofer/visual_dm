"""
Event Factory for creating and publishing events.

This module provides factory functions for creating and publishing events
in a standardized way across the application.
"""
import logging
import time
import asyncio
from typing import Any, Dict, Optional, Type, TypeVar, Union, cast

from .event_dispatcher import EventBase, EventDispatcher
from .canonical_events import (
    SystemEvent, SystemEventType,
    MemoryEvent, MemoryEventType,
    RumorEvent, RumorEventType,
    MotifEvent, MotifEventType,
    PopulationEvent, PopulationEventType,
    POIEvent, POIEventType,
    FactionEvent, FactionEventType,
    QuestEvent, QuestEventType,
    CombatEvent, CombatEventType,
    TimeEvent, TimeEventType,
    RelationshipEvent, RelationshipEventType,
    StorageEvent, StorageEventType,
    WorldStateEvent, WorldStateEventType,
)

logger = logging.getLogger(__name__)

# Define a type variable for generic functions
T = TypeVar('T', bound=EventBase)


class EventFactory:
    """
    Factory for creating and publishing standard events.
    
    This class provides factory methods for all canonical event types
    to ensure consistent event creation and simplify dispatching.
    """
    
    def __init__(self, dispatcher: Optional[EventDispatcher] = None):
        """
        Initialize the event factory.
        
        Args:
            dispatcher: Event dispatcher to use, or None for the singleton instance
        """
        self.dispatcher = dispatcher or EventDispatcher.get_instance()
    
    def create_event(self, event_cls: Type[T], **kwargs) -> T:
        """
        Create an event of the specified type.
        
        Args:
            event_cls: Event class to instantiate
            **kwargs: Event properties
        
        Returns:
            Created event instance
        """
        # Add timestamp if not provided
        if 'timestamp' not in kwargs:
            kwargs['timestamp'] = time.time()
            
        return event_cls(**kwargs)
    
    async def publish_event(self, event: EventBase) -> None:
        """
        Publish an event using the dispatcher.
        
        Args:
            event: Event to publish
            
        Returns:
            None
        """
        await self.dispatcher.publish(event)
    
    def publish_event_sync(self, event: EventBase) -> None:
        """
        Publish an event synchronously.
        
        Args:
            event: Event to publish
            
        Returns:
            None
        """
        self.dispatcher.publish_sync(event)
    
    async def create_and_publish(self, event_cls: Type[T], **kwargs) -> T:
        """
        Create and publish an event in one step.
        
        Args:
            event_cls: Event class to instantiate
            **kwargs: Event properties
            
        Returns:
            The created and published event
        """
        event = self.create_event(event_cls, **kwargs)
        await self.publish_event(event)
        return event
    
    def create_and_publish_sync(self, event_cls: Type[T], **kwargs) -> T:
        """
        Create and publish an event synchronously.
        
        Args:
            event_cls: Event class to instantiate
            **kwargs: Event properties
            
        Returns:
            The created and published event
        """
        event = self.create_event(event_cls, **kwargs)
        self.publish_event_sync(event)
        return event
    
    # System Events
    async def system_event(self, 
                         event_type: Union[SystemEventType, str], 
                         component: str, 
                         details: Optional[Dict[str, Any]] = None) -> SystemEvent:
        """
        Create and publish a system event.
        
        Args:
            event_type: Type of system event
            component: Component that generated the event
            details: Additional event details
            
        Returns:
            The created and published event
        """
        if isinstance(event_type, SystemEventType):
            event_type_str = event_type.value
        else:
            event_type_str = event_type
            
        return await self.create_and_publish(
            SystemEvent,
            event_type=event_type_str,
            component=component,
            details=details or {}
        )
    
    # Memory Events
    async def memory_event(self,
                         event_type: Union[MemoryEventType, str],
                         entity_id: str,
                         memory_id: str,
                         memory_type: str,
                         **kwargs) -> MemoryEvent:
        """
        Create and publish a memory event.
        
        Args:
            event_type: Type of memory event
            entity_id: Entity ID associated with the memory
            memory_id: Unique ID of the memory
            memory_type: Type of memory
            **kwargs: Additional event properties
            
        Returns:
            The created and published event
        """
        if isinstance(event_type, MemoryEventType):
            event_type_str = event_type.value
        else:
            event_type_str = event_type
            
        return await self.create_and_publish(
            MemoryEvent,
            event_type=event_type_str,
            entity_id=entity_id,
            memory_id=memory_id,
            memory_type=memory_type,
            **kwargs
        )
    
    # Rumor Events
    async def rumor_event(self,
                        event_type: Union[RumorEventType, str],
                        rumor_id: str,
                        rumor_type: str,
                        **kwargs) -> RumorEvent:
        """
        Create and publish a rumor event.
        
        Args:
            event_type: Type of rumor event
            rumor_id: Unique ID of the rumor
            rumor_type: Type of rumor
            **kwargs: Additional event properties
            
        Returns:
            The created and published event
        """
        if isinstance(event_type, RumorEventType):
            event_type_str = event_type.value
        else:
            event_type_str = event_type
            
        return await self.create_and_publish(
            RumorEvent,
            event_type=event_type_str,
            rumor_id=rumor_id,
            rumor_type=rumor_type,
            **kwargs
        )
    
    # Add similar methods for other event types...
    
    # Time Events
    async def time_event(self,
                       event_type: Union[TimeEventType, str],
                       previous_time: Union[float, str],
                       current_time: Union[float, str],
                       **kwargs) -> TimeEvent:
        """
        Create and publish a time event.
        
        Args:
            event_type: Type of time event
            previous_time: Previous time value
            current_time: Current time value
            **kwargs: Additional event properties
            
        Returns:
            The created and published event
        """
        if isinstance(event_type, TimeEventType):
            event_type_str = event_type.value
        else:
            event_type_str = event_type
            
        return await self.create_and_publish(
            TimeEvent,
            event_type=event_type_str,
            previous_time=previous_time,
            current_time=current_time,
            **kwargs
        )
    
    # Synchronous versions for non-async contexts
    
    def system_event_sync(self, 
                        event_type: Union[SystemEventType, str], 
                        component: str, 
                        details: Optional[Dict[str, Any]] = None) -> SystemEvent:
        """Synchronous version of system_event."""
        if isinstance(event_type, SystemEventType):
            event_type_str = event_type.value
        else:
            event_type_str = event_type
            
        return self.create_and_publish_sync(
            SystemEvent,
            event_type=event_type_str,
            component=component,
            details=details or {}
        )
    
    def memory_event_sync(self,
                        event_type: Union[MemoryEventType, str],
                        entity_id: str,
                        memory_id: str,
                        memory_type: str,
                        **kwargs) -> MemoryEvent:
        """Synchronous version of memory_event."""
        if isinstance(event_type, MemoryEventType):
            event_type_str = event_type.value
        else:
            event_type_str = event_type
            
        return self.create_and_publish_sync(
            MemoryEvent,
            event_type=event_type_str,
            entity_id=entity_id,
            memory_id=memory_id,
            memory_type=memory_type,
            **kwargs
        )


# Singleton instance for convenience
_factory = None

def get_event_factory() -> EventFactory:
    """
    Get the singleton event factory instance.
    
    Returns:
        EventFactory: The singleton instance
    """
    global _factory
    if _factory is None:
        _factory = EventFactory()
    return _factory 
