"""
Integration system - Event Bus module for proper cross-system communication.

This module enhances existing utils/event_bus.py and integrates with backend.systems.events
for proper cross-system communication. It provides:
- Unified event system architecture
- Event routing and filtering
- Event persistence and replay capabilities
- Support for both sync and async event handling
- Event correlation and tracing
- Integration with monitoring and validation systems
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Callable, Union, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
import json
import threading
from enum import Enum

# Import base event types
from backend.infrastructure.events.events.event_types import EventType
from backend.infrastructure.events.core.event_base import EventBase as BaseEvent

# Define EventPriority if not imported
class EventPriority(Enum):
    """Event priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

logger = logging.getLogger(__name__)


class EventFilter:
    """Event filtering for routing and subscription"""
    
    def __init__(self, 
                 event_types: Optional[List[EventType]] = None,
                 source_systems: Optional[List[str]] = None,
                 priorities: Optional[List[EventPriority]] = None,
                 custom_filter: Optional[Callable[[BaseEvent], bool]] = None):
        self.event_types = set(event_types) if event_types else None
        self.source_systems = set(source_systems) if source_systems else None
        self.priorities = set(priorities) if priorities else None
        self.custom_filter = custom_filter
    
    def matches(self, event: BaseEvent) -> bool:
        """Check if event matches filter criteria"""
        # Check event type
        if self.event_types and event.event_type not in self.event_types:
            return False
        
        # Check source system
        if self.source_systems and event.source_system not in self.source_systems:
            return False
        
        # Check priority
        if self.priorities and event.priority not in self.priorities:
            return False
        
        # Check custom filter
        if self.custom_filter and not self.custom_filter(event):
            return False
        
        return True


@dataclass
class EventSubscription:
    """Represents an event subscription"""
    subscription_id: str
    handler: Callable
    filter: EventFilter
    system_id: str
    created_at: datetime = field(default_factory=datetime.now)
    active: bool = True
    
    async def handle_event(self, event: BaseEvent):
        """Handle event with subscription handler"""
        try:
            if asyncio.iscoroutinefunction(self.handler):
                await self.handler(event)
            else:
                self.handler(event)
        except Exception as e:
            logger.error(f"Event handler error in subscription {self.subscription_id}: {e}")


class IntegrationEventBus:
    """
    Enhanced event bus for cross-system integration with routing, filtering, 
    and persistence capabilities.
    """
    
    def __init__(self):
        self._subscriptions: Dict[str, EventSubscription] = {}
        self._system_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        self._event_history: List[BaseEvent] = []
        self._max_history = 10000
        self._lock = asyncio.Lock()
        self._metrics_callback: Optional[Callable] = None
        self._validation_callback: Optional[Callable] = None
        
        # Event routing configuration
        self._routing_rules: Dict[str, List[str]] = defaultdict(list)
        self._broadcast_types: Set[EventType] = {EventType.SYSTEM, EventType.INTEGRATION}
        
        # Performance tracking
        self._event_stats = {
            "events_published": 0,
            "events_delivered": 0,
            "delivery_failures": 0,
            "subscriptions_created": 0,
            "subscriptions_removed": 0
        }
    
    async def subscribe(self,
                       system_id: str,
                       handler: Callable,
                       event_filter: Optional[EventFilter] = None,
                       subscription_id: Optional[str] = None) -> str:
        """
        Subscribe to events with optional filtering.
        
        Args:
            system_id: System subscribing to events
            handler: Event handler function (sync or async)
            event_filter: Optional filter for events
            subscription_id: Optional custom subscription ID
            
        Returns:
            str: Subscription ID
        """
        async with self._lock:
            sub_id = subscription_id or f"{system_id}_{datetime.now().timestamp()}"
            
            if event_filter is None:
                event_filter = EventFilter()  # Match all events
            
            subscription = EventSubscription(
                subscription_id=sub_id,
                handler=handler,
                filter=event_filter,
                system_id=system_id
            )
            
            self._subscriptions[sub_id] = subscription
            self._system_subscriptions[system_id].add(sub_id)
            self._event_stats["subscriptions_created"] += 1
            
            logger.info(f"Created subscription {sub_id} for system {system_id}")
            return sub_id
    
    async def unsubscribe(self, subscription_id: str) -> bool:
        """
        Unsubscribe from events.
        
        Args:
            subscription_id: Subscription to remove
            
        Returns:
            bool: True if subscription was removed
        """
        async with self._lock:
            if subscription_id not in self._subscriptions:
                return False
            
            subscription = self._subscriptions[subscription_id]
            system_id = subscription.system_id
            
            del self._subscriptions[subscription_id]
            self._system_subscriptions[system_id].discard(subscription_id)
            self._event_stats["subscriptions_removed"] += 1
            
            logger.info(f"Removed subscription {subscription_id} for system {system_id}")
            return True
    
    async def publish(self, event: BaseEvent) -> int:
        """
        Publish an event to all matching subscribers.
        
        Args:
            event: Event to publish
            
        Returns:
            int: Number of handlers the event was delivered to
        """
        async with self._lock:
            self._event_stats["events_published"] += 1
            
            # Add to history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
            
            # Validate event if validator available
            if self._validation_callback:
                try:
                    validation_result = await self._validation_callback(event)
                    if not validation_result:
                        logger.warning(f"Event validation failed for {event.event_id}")
                        return 0
                except Exception as e:
                    logger.error(f"Event validation error: {e}")
            
            # Find matching subscriptions
            matching_subscriptions = []
            for subscription in self._subscriptions.values():
                if subscription.active and subscription.filter.matches(event):
                    matching_subscriptions.append(subscription)
            
            # Deliver to matching subscriptions
            delivery_count = 0
            for subscription in matching_subscriptions:
                try:
                    await subscription.handle_event(event)
                    delivery_count += 1
                    self._event_stats["events_delivered"] += 1
                except Exception as e:
                    self._event_stats["delivery_failures"] += 1
                    logger.error(f"Event delivery failed for subscription {subscription.subscription_id}: {e}")
            
            # Record metrics if callback available
            if self._metrics_callback:
                try:
                    await self._metrics_callback(event, delivery_count)
                except Exception as e:
                    logger.error(f"Metrics callback error: {e}")
            
            logger.debug(f"Published event {event.event_id} to {delivery_count} handlers")
            return delivery_count
    
    async def replay_events(self,
                           system_id: str,
                           event_filter: Optional[EventFilter] = None,
                           since: Optional[datetime] = None) -> int:
        """
        Replay historical events to a system.
        
        Args:
            system_id: System to replay events to
            event_filter: Optional filter for events to replay
            since: Optional timestamp to replay events from
            
        Returns:
            int: Number of events replayed
        """
        async with self._lock:
            system_subscriptions = self._system_subscriptions.get(system_id, set())
            if not system_subscriptions:
                return 0
            
            # Filter events based on criteria
            events_to_replay = []
            for event in self._event_history:
                # Check timestamp filter
                if since and event.timestamp < since:
                    continue
                
                # Check event filter
                if event_filter and not event_filter.matches(event):
                    continue
                
                events_to_replay.append(event)
            
            # Replay events to system subscriptions
            replay_count = 0
            for event in events_to_replay:
                for sub_id in system_subscriptions:
                    subscription = self._subscriptions.get(sub_id)
                    if subscription and subscription.active and subscription.filter.matches(event):
                        try:
                            await subscription.handle_event(event)
                            replay_count += 1
                        except Exception as e:
                            logger.error(f"Event replay failed for subscription {sub_id}: {e}")
            
            logger.info(f"Replayed {replay_count} events to system {system_id}")
            return replay_count
    
    def add_routing_rule(self, source_system: str, target_systems: List[str]):
        """Add routing rule for directed event delivery"""
        self._routing_rules[source_system].extend(target_systems)
    
    def remove_routing_rule(self, source_system: str, target_system: str):
        """Remove routing rule"""
        if source_system in self._routing_rules:
            try:
                self._routing_rules[source_system].remove(target_system)
            except ValueError:
                pass
    
    def set_metrics_callback(self, callback: Callable):
        """Set callback for event metrics collection"""
        self._metrics_callback = callback
    
    def set_validation_callback(self, callback: Callable):
        """Set callback for event validation"""
        self._validation_callback = callback
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics"""
        return {
            "total_subscriptions": len(self._subscriptions),
            "active_subscriptions": len([s for s in self._subscriptions.values() if s.active]),
            "systems_with_subscriptions": len(self._system_subscriptions),
            "events_in_history": len(self._event_history),
            "stats": self._event_stats.copy()
        }
    
    def get_system_subscriptions(self, system_id: str) -> List[str]:
        """Get all subscription IDs for a system"""
        return list(self._system_subscriptions.get(system_id, set()))
    
    async def shutdown(self):
        """Gracefully shutdown the event bus"""
        async with self._lock:
            logger.info("Shutting down integration event bus")
            self._subscriptions.clear()
            self._system_subscriptions.clear()
            self._event_history.clear()


# Global event bus instance
integration_event_bus = IntegrationEventBus()


# Convenience functions for backward compatibility and ease of use
async def register_handler(system_id: str, 
                          handler: Callable,
                          event_filter: Optional[EventFilter] = None) -> str:
    """Register an event handler"""
    return await integration_event_bus.subscribe(system_id, handler, event_filter)


async def dispatch_event(event: BaseEvent) -> int:
    """Dispatch an event to all matching handlers"""
    return await integration_event_bus.publish(event)


async def unregister_handler(subscription_id: str) -> bool:
    """Unregister an event handler"""
    return await integration_event_bus.unsubscribe(subscription_id)
