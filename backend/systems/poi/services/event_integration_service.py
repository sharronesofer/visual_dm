"""
Event Integration Service for POI System

Handles integration between POI events and other game systems,
managing cross-system event propagation and state synchronization.
"""

from typing import Dict, List, Optional, Any, Callable, Set
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
import logging
from datetime import datetime, timedelta
import asyncio
from functools import wraps

from backend.infrastructure.systems.poi.models import PoiEntity, POIType, POIState
from backend.infrastructure.database import get_db_session
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class POIEventType(str, Enum):
    """Types of POI-related events"""
    # POI Lifecycle Events
    POI_CREATED = "poi_created"
    POI_UPDATED = "poi_updated"
    POI_DELETED = "poi_deleted"
    POI_STATE_CHANGED = "poi_state_changed"
    
    # Population Events
    POPULATION_CHANGED = "population_changed"
    MIGRATION_STARTED = "migration_started"
    MIGRATION_COMPLETED = "migration_completed"
    
    # Resource Events
    RESOURCE_PRODUCTION = "resource_production"
    RESOURCE_CONSUMPTION = "resource_consumption"
    TRADE_OFFER_CREATED = "trade_offer_created"
    TRADE_COMPLETED = "trade_completed"
    
    # Metropolitan Events
    METROPOLITAN_EXPANSION = "metropolitan_expansion"
    URBAN_GROWTH = "urban_growth"
    HEX_CLAIMED = "hex_claimed"
    
    # Lifecycle Events
    LIFECYCLE_STAGE_CHANGED = "lifecycle_stage_changed"
    RANDOM_EVENT_OCCURRED = "random_event_occurred"
    DISASTER_EVENT = "disaster_event"
    
    # Faction Events
    INFLUENCE_CHANGED = "influence_changed"
    FACTION_CONTROL_GAINED = "faction_control_gained"
    FACTION_CONTROL_LOST = "faction_control_lost"
    FACTION_ACTION_EXECUTED = "faction_action_executed"
    
    # Landmark Events
    LANDMARK_DISCOVERED = "landmark_discovered"
    LANDMARK_EFFECT_ACTIVATED = "landmark_effect_activated"
    LANDMARK_QUEST_STARTED = "landmark_quest_started"
    
    # Generation Events
    POI_GENERATED = "poi_generated"
    REGION_GENERATED = "region_generated"
    WORLD_GENERATION_COMPLETE = "world_generation_complete"
    
    # Cross-System Events
    ECONOMY_UPDATE = "economy_update"
    DIPLOMACY_UPDATE = "diplomacy_update"
    QUEST_UPDATE = "quest_update"


class EventPriority(str, Enum):
    """Event priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class POIEvent:
    """Represents a POI-related event"""
    event_id: UUID = field(default_factory=uuid4)
    event_type: POIEventType = POIEventType.POI_UPDATED
    priority: EventPriority = EventPriority.MEDIUM
    poi_id: Optional[UUID] = None
    poi_type: Optional[POIType] = None
    source_service: str = "unknown"
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    tags: Set[str] = field(default_factory=set)
    
    def add_tag(self, tag: str):
        """Add a tag to the event"""
        self.tags.add(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if event has a specific tag"""
        return tag in self.tags
    
    def is_expired(self) -> bool:
        """Check if the event has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'event_id': str(self.event_id),
            'event_type': self.event_type.value,
            'priority': self.priority.value,
            'poi_id': str(self.poi_id) if self.poi_id else None,
            'poi_type': self.poi_type.value if self.poi_type else None,
            'source_service': self.source_service,
            'data': self.data,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'tags': list(self.tags)
        }


@dataclass
class EventSubscription:
    """Represents an event subscription"""
    subscription_id: UUID = field(default_factory=uuid4)
    service_name: str = ""
    event_types: Set[POIEventType] = field(default_factory=set)
    poi_types: Set[POIType] = field(default_factory=set)
    callback: Optional[Callable[[POIEvent], None]] = None
    filter_func: Optional[Callable[[POIEvent], bool]] = None
    priority_threshold: EventPriority = EventPriority.LOW
    active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def matches_event(self, event: POIEvent) -> bool:
        """Check if subscription matches an event"""
        if not self.active:
            return False
        
        # Check event type filter
        if self.event_types and event.event_type not in self.event_types:
            return False
        
        # Check POI type filter
        if self.poi_types and event.poi_type and event.poi_type not in self.poi_types:
            return False
        
        # Check priority threshold
        priority_order = [EventPriority.LOW, EventPriority.MEDIUM, EventPriority.HIGH, EventPriority.CRITICAL]
        if priority_order.index(event.priority) < priority_order.index(self.priority_threshold):
            return False
        
        # Apply custom filter
        if self.filter_func and not self.filter_func(event):
            return False
        
        return True


class EventIntegrationService:
    """Service for POI system event integration and management"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session or get_db_session()
        self.event_dispatcher = EventDispatcher()
        
        # Event management
        self.subscriptions: Dict[UUID, EventSubscription] = {}
        self.event_history: List[POIEvent] = []
        self.max_history_size = 10000
        
        # Performance tracking
        self.events_published = 0
        self.events_processed = 0
        self.processing_times: List[float] = []
        
        # Async processing
        self.event_queue: asyncio.Queue = asyncio.Queue()
        self.processing_active = False
        
        # Initialize core event handlers
        self._initialize_core_handlers()
    
    def _initialize_core_handlers(self):
        """Initialize core event handlers for POI system"""
        # Subscribe to all POI events for logging
        self.subscribe_to_events(
            service_name="event_logger",
            event_types={event_type for event_type in POIEventType},
            callback=self._log_event
        )
        
        # Subscribe to critical events for immediate processing
        self.subscribe_to_events(
            service_name="critical_handler",
            event_types={
                POIEventType.DISASTER_EVENT,
                POIEventType.FACTION_CONTROL_LOST,
                POIEventType.POI_DELETED
            },
            priority_threshold=EventPriority.CRITICAL,
            callback=self._handle_critical_event
        )
    
    def publish_event(self, event: POIEvent) -> bool:
        """Publish an event to all subscribers"""
        try:
            # Add to history
            self._add_to_history(event)
            
            # Find matching subscriptions
            matching_subscriptions = [
                sub for sub in self.subscriptions.values()
                if sub.matches_event(event)
            ]
            
            # Publish to event dispatcher
            self.event_dispatcher.publish(event.to_dict())
            
            # Call subscription callbacks
            for subscription in matching_subscriptions:
                if subscription.callback:
                    try:
                        subscription.callback(event)
                    except Exception as e:
                        logger.error(f"Error in event callback for {subscription.service_name}: {e}")
            
            self.events_published += 1
            logger.debug(f"Published event {event.event_type} to {len(matching_subscriptions)} subscribers")
            
            return True
            
        except Exception as e:
            logger.error(f"Error publishing event: {e}")
            return False
    
    def subscribe_to_events(self, service_name: str,
                           event_types: Set[POIEventType] = None,
                           poi_types: Set[POIType] = None,
                           callback: Callable[[POIEvent], None] = None,
                           filter_func: Callable[[POIEvent], bool] = None,
                           priority_threshold: EventPriority = EventPriority.LOW) -> UUID:
        """Subscribe to POI events"""
        subscription = EventSubscription(
            service_name=service_name,
            event_types=event_types or set(),
            poi_types=poi_types or set(),
            callback=callback,
            filter_func=filter_func,
            priority_threshold=priority_threshold
        )
        
        self.subscriptions[subscription.subscription_id] = subscription
        logger.info(f"Service '{service_name}' subscribed to events")
        
        return subscription.subscription_id
    
    def unsubscribe(self, subscription_id: UUID) -> bool:
        """Unsubscribe from events"""
        if subscription_id in self.subscriptions:
            subscription = self.subscriptions.pop(subscription_id)
            logger.info(f"Service '{subscription.service_name}' unsubscribed from events")
            return True
        return False
    
    def create_poi_event(self, event_type: POIEventType,
                        poi_id: UUID = None,
                        poi_type: POIType = None,
                        source_service: str = "unknown",
                        data: Dict[str, Any] = None,
                        priority: EventPriority = EventPriority.MEDIUM,
                        tags: Set[str] = None) -> POIEvent:
        """Create a POI event"""
        event = POIEvent(
            event_type=event_type,
            poi_id=poi_id,
            poi_type=poi_type,
            source_service=source_service,
            data=data or {},
            priority=priority,
            tags=tags or set()
        )
        
        return event
    
    def publish_poi_created(self, poi: PoiEntity, source_service: str = "poi_service") -> bool:
        """Publish POI created event"""
        event = self.create_poi_event(
            event_type=POIEventType.POI_CREATED,
            poi_id=poi.id,
            poi_type=POIType(poi.poi_type),
            source_service=source_service,
            data={
                'name': poi.name,
                'location_x': poi.location_x,
                'location_y': poi.location_y,
                'population': poi.population,
                'state': poi.state
            },
            priority=EventPriority.MEDIUM
        )
        
        return self.publish_event(event)
    
    def publish_poi_updated(self, poi: PoiEntity, changed_fields: List[str],
                           source_service: str = "poi_service") -> bool:
        """Publish POI updated event"""
        event = self.create_poi_event(
            event_type=POIEventType.POI_UPDATED,
            poi_id=poi.id,
            poi_type=POIType(poi.poi_type),
            source_service=source_service,
            data={
                'name': poi.name,
                'changed_fields': changed_fields,
                'population': poi.population,
                'state': poi.state
            },
            priority=EventPriority.LOW
        )
        
        return self.publish_event(event)
    
    def publish_state_change(self, poi: PoiEntity, old_state: POIState, new_state: POIState,
                           source_service: str = "poi_state_service") -> bool:
        """Publish POI state change event"""
        event = self.create_poi_event(
            event_type=POIEventType.POI_STATE_CHANGED,
            poi_id=poi.id,
            poi_type=POIType(poi.poi_type),
            source_service=source_service,
            data={
                'old_state': old_state.value,
                'new_state': new_state.value,
                'name': poi.name
            },
            priority=EventPriority.MEDIUM
        )
        
        return self.publish_event(event)
    
    def publish_population_change(self, poi: PoiEntity, old_population: int, new_population: int,
                                 change_reason: str = "", source_service: str = "migration_service") -> bool:
        """Publish population change event"""
        change_amount = new_population - old_population
        change_percentage = (change_amount / old_population * 100) if old_population > 0 else 0
        
        event = self.create_poi_event(
            event_type=POIEventType.POPULATION_CHANGED,
            poi_id=poi.id,
            poi_type=POIType(poi.poi_type),
            source_service=source_service,
            data={
                'old_population': old_population,
                'new_population': new_population,
                'change_amount': change_amount,
                'change_percentage': change_percentage,
                'change_reason': change_reason,
                'name': poi.name
            },
            priority=EventPriority.MEDIUM if abs(change_percentage) > 10 else EventPriority.LOW
        )
        
        return self.publish_event(event)
    
    def publish_resource_event(self, poi_id: UUID, resource_type: str, action: str,
                              amount: int, source_service: str = "resource_service") -> bool:
        """Publish resource-related event"""
        event_type = POIEventType.RESOURCE_PRODUCTION if action == "produce" else POIEventType.RESOURCE_CONSUMPTION
        
        event = self.create_poi_event(
            event_type=event_type,
            poi_id=poi_id,
            source_service=source_service,
            data={
                'resource_type': resource_type,
                'amount': amount,
                'action': action
            },
            priority=EventPriority.LOW
        )
        
        return self.publish_event(event)
    
    def publish_trade_event(self, buyer_poi_id: UUID, seller_poi_id: UUID,
                           resource_type: str, amount: int, price: float,
                           source_service: str = "resource_service") -> bool:
        """Publish trade completion event"""
        event = self.create_poi_event(
            event_type=POIEventType.TRADE_COMPLETED,
            poi_id=buyer_poi_id,
            source_service=source_service,
            data={
                'buyer_poi_id': str(buyer_poi_id),
                'seller_poi_id': str(seller_poi_id),
                'resource_type': resource_type,
                'amount': amount,
                'price': price
            },
            priority=EventPriority.MEDIUM
        )
        
        return self.publish_event(event)
    
    def publish_influence_change(self, poi_id: UUID, faction_id: str, influence_type: str,
                               old_value: float, new_value: float,
                               source_service: str = "faction_influence_service") -> bool:
        """Publish faction influence change event"""
        change_amount = new_value - old_value
        
        event = self.create_poi_event(
            event_type=POIEventType.INFLUENCE_CHANGED,
            poi_id=poi_id,
            source_service=source_service,
            data={
                'faction_id': faction_id,
                'influence_type': influence_type,
                'old_value': old_value,
                'new_value': new_value,
                'change_amount': change_amount
            },
            priority=EventPriority.MEDIUM if abs(change_amount) > 0.2 else EventPriority.LOW
        )
        
        return self.publish_event(event)
    
    def publish_disaster_event(self, poi_id: UUID, disaster_type: str, severity: float,
                              effects: Dict[str, Any], source_service: str = "lifecycle_events_service") -> bool:
        """Publish disaster event"""
        event = self.create_poi_event(
            event_type=POIEventType.DISASTER_EVENT,
            poi_id=poi_id,
            source_service=source_service,
            data={
                'disaster_type': disaster_type,
                'severity': severity,
                'effects': effects
            },
            priority=EventPriority.CRITICAL if severity > 0.7 else EventPriority.HIGH
        )
        
        return self.publish_event(event)
    
    def publish_landmark_discovery(self, poi_id: UUID, landmark_type: str,
                                  discovery_data: Dict[str, Any],
                                  source_service: str = "landmark_service") -> bool:
        """Publish landmark discovery event"""
        event = self.create_poi_event(
            event_type=POIEventType.LANDMARK_DISCOVERED,
            poi_id=poi_id,
            source_service=source_service,
            data={
                'landmark_type': landmark_type,
                'discovery_data': discovery_data
            },
            priority=EventPriority.HIGH
        )
        
        return self.publish_event(event)
    
    def get_events_by_poi(self, poi_id: UUID, limit: int = 100) -> List[POIEvent]:
        """Get events related to a specific POI"""
        poi_events = [
            event for event in self.event_history
            if event.poi_id == poi_id
        ]
        
        # Sort by timestamp, most recent first
        poi_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return poi_events[:limit]
    
    def get_events_by_type(self, event_type: POIEventType, limit: int = 100) -> List[POIEvent]:
        """Get events of a specific type"""
        type_events = [
            event for event in self.event_history
            if event.event_type == event_type
        ]
        
        # Sort by timestamp, most recent first
        type_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return type_events[:limit]
    
    def get_recent_events(self, hours: int = 24, limit: int = 100) -> List[POIEvent]:
        """Get recent events within specified time window"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_events = [
            event for event in self.event_history
            if event.timestamp >= cutoff_time
        ]
        
        # Sort by timestamp, most recent first
        recent_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return recent_events[:limit]
    
    def get_critical_events(self, limit: int = 50) -> List[POIEvent]:
        """Get critical priority events"""
        critical_events = [
            event for event in self.event_history
            if event.priority == EventPriority.CRITICAL
        ]
        
        # Sort by timestamp, most recent first
        critical_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        return critical_events[:limit]
    
    def cleanup_expired_events(self) -> int:
        """Remove expired events from history"""
        initial_count = len(self.event_history)
        
        self.event_history = [
            event for event in self.event_history
            if not event.is_expired()
        ]
        
        removed_count = initial_count - len(self.event_history)
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} expired events")
        
        return removed_count
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get event system statistics"""
        recent_events = self.get_recent_events(hours=24)
        
        # Count events by type
        type_counts = {}
        for event in recent_events:
            type_counts[event.event_type.value] = type_counts.get(event.event_type.value, 0) + 1
        
        # Count events by priority
        priority_counts = {}
        for event in recent_events:
            priority_counts[event.priority.value] = priority_counts.get(event.priority.value, 0) + 1
        
        return {
            'total_events_published': self.events_published,
            'total_events_processed': self.events_processed,
            'events_in_history': len(self.event_history),
            'active_subscriptions': len([s for s in self.subscriptions.values() if s.active]),
            'recent_events_24h': len(recent_events),
            'events_by_type': type_counts,
            'events_by_priority': priority_counts,
            'average_processing_time': sum(self.processing_times) / len(self.processing_times) if self.processing_times else 0
        }
    
    def _add_to_history(self, event: POIEvent):
        """Add event to history with size management"""
        self.event_history.append(event)
        
        # Maintain maximum history size
        if len(self.event_history) > self.max_history_size:
            # Remove oldest events
            self.event_history = self.event_history[-self.max_history_size:]
    
    def _log_event(self, event: POIEvent):
        """Log an event (core handler)"""
        log_level = {
            EventPriority.LOW: logging.DEBUG,
            EventPriority.MEDIUM: logging.INFO,
            EventPriority.HIGH: logging.WARNING,
            EventPriority.CRITICAL: logging.ERROR
        }.get(event.priority, logging.INFO)
        
        logger.log(log_level, f"POI Event: {event.event_type.value} - POI: {event.poi_id} - Source: {event.source_service}")
    
    def _handle_critical_event(self, event: POIEvent):
        """Handle critical events (core handler)"""
        logger.critical(f"CRITICAL POI EVENT: {event.event_type.value} - {event.data}")
        
        # Could trigger alerts, notifications, emergency responses, etc.
        if event.event_type == POIEventType.DISASTER_EVENT:
            self._handle_disaster_response(event)
        elif event.event_type == POIEventType.POI_DELETED:
            self._handle_poi_deletion_cleanup(event)
    
    def _handle_disaster_response(self, event: POIEvent):
        """Handle disaster event response"""
        disaster_type = event.data.get('disaster_type', 'unknown')
        severity = event.data.get('severity', 0.0)
        
        logger.critical(f"Disaster response triggered: {disaster_type} (severity: {severity}) at POI {event.poi_id}")
        
        # Could trigger:
        # - Emergency resource allocation
        # - Refugee migration
        # - Military response
        # - Economic impact calculations
    
    def _handle_poi_deletion_cleanup(self, event: POIEvent):
        """Handle cleanup when a POI is deleted"""
        poi_id = event.poi_id
        
        # Clean up POI-related events from history
        initial_count = len(self.event_history)
        self.event_history = [
            e for e in self.event_history
            if e.poi_id != poi_id
        ]
        
        cleaned_count = initial_count - len(self.event_history)
        logger.info(f"Cleaned up {cleaned_count} events for deleted POI {poi_id}")


# Decorator for automatic event publishing
def publish_event_on_method(event_type: POIEventType, 
                           source_service: str = "",
                           priority: EventPriority = EventPriority.MEDIUM):
    """Decorator to automatically publish events when methods are called"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Execute the original method
            result = func(self, *args, **kwargs)
            
            # Get event integration service
            event_service = getattr(self, 'event_integration', None)
            if not event_service:
                return result
            
            # Extract POI information from result or arguments
            poi_id = None
            poi_type = None
            
            if hasattr(result, 'id'):
                poi_id = result.id
            if hasattr(result, 'poi_type'):
                poi_type = POIType(result.poi_type)
            
            # Create and publish event
            event = event_service.create_poi_event(
                event_type=event_type,
                poi_id=poi_id,
                poi_type=poi_type,
                source_service=source_service or self.__class__.__name__,
                priority=priority,
                data={'method': func.__name__, 'args': str(args), 'result': str(result)}
            )
            
            event_service.publish_event(event)
            
            return result
        return wrapper
    return decorator


# Factory function for dependency injection
def get_event_integration_service(db_session: Optional[Session] = None) -> EventIntegrationService:
    """Factory function to create EventIntegrationService instance"""
    return EventIntegrationService(db_session) 