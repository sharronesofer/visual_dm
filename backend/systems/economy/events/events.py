"""
Economy Event System - Event definitions and integration for the economy system.

This module provides event definitions, event publishing, and event handling
for economy-related events that can be consumed by other systems.
"""

import logging
from typing import Dict, Any, List, Optional, Callable, Union
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import json

# Set up logging
logger = logging.getLogger(__name__)

class EconomyEventType(Enum):
    """Economy event types."""
    # Resource events
    RESOURCE_CREATED = "economy.resource.created"
    RESOURCE_UPDATED = "economy.resource.updated"
    RESOURCE_DELETED = "economy.resource.deleted"
    RESOURCE_AMOUNT_CHANGED = "economy.resource.amount_changed"
    RESOURCE_TRANSFERRED = "economy.resource.transferred"
    
    # Market events
    MARKET_CREATED = "economy.market.created"
    MARKET_UPDATED = "economy.market.updated"
    MARKET_DELETED = "economy.market.deleted"
    MARKET_CONDITIONS_CHANGED = "economy.market.conditions_changed"
    PRICE_UPDATED = "economy.market.price_updated"
    
    # Trade events
    TRADE_ROUTE_CREATED = "economy.trade.route_created"
    TRADE_ROUTE_UPDATED = "economy.trade.route_updated"
    TRADE_ROUTE_DELETED = "economy.trade.route_deleted"
    TRADE_EXECUTED = "economy.trade.executed"
    TRADE_FAILED = "economy.trade.failed"
    
    # Transaction events
    TRANSACTION_COMPLETED = "economy.transaction.completed"
    TRANSACTION_FAILED = "economy.transaction.failed"
    
    # Economic events
    ECONOMIC_TICK_PROCESSED = "economy.tick.processed"
    POPULATION_IMPACT_CALCULATED = "economy.population.impact_calculated"
    ECONOMIC_ANALYTICS_UPDATED = "economy.analytics.updated"
    ECONOMIC_FORECAST_GENERATED = "economy.forecast.generated"
    
    # System events
    ECONOMY_INITIALIZED = "economy.system.initialized"
    ECONOMY_SHUTDOWN = "economy.system.shutdown"
    ECONOMY_ERROR = "economy.system.error"

@dataclass
class EconomyEvent:
    """Base class for all economy events."""
    event_type: EconomyEventType
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = "economy_system"
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization."""
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "data": self.data,
            "metadata": self.metadata
        }
    
    def to_json(self) -> str:
        """Convert event to JSON string."""
        return json.dumps(self.to_dict(), default=str)

@dataclass
class ResourceEvent(EconomyEvent):
    """Event for resource-related operations."""
    resource_id: str = ""
    region_id: int = 0
    resource_type: str = ""
    amount: float = 0.0
    
    def __post_init__(self):
        """Update data with resource-specific information."""
        self.data.update({
            "resource_id": self.resource_id,
            "region_id": self.region_id,
            "resource_type": self.resource_type,
            "amount": self.amount
        })

@dataclass
class MarketEvent(EconomyEvent):
    """Event for market-related operations."""
    market_id: int = 0
    region_id: int = 0
    market_type: str = ""
    
    def __post_init__(self):
        """Update data with market-specific information."""
        self.data.update({
            "market_id": self.market_id,
            "region_id": self.region_id,
            "market_type": self.market_type
        })

@dataclass
class PriceEvent(EconomyEvent):
    """Event for price-related operations."""
    resource_id: str = ""
    market_id: int = 0
    old_price: float = 0.0
    new_price: float = 0.0
    price_modifier: float = 1.0
    
    def __post_init__(self):
        """Update data with price-specific information."""
        self.data.update({
            "resource_id": self.resource_id,
            "market_id": self.market_id,
            "old_price": self.old_price,
            "new_price": self.new_price,
            "price_modifier": self.price_modifier,
            "price_change": self.new_price - self.old_price,
            "price_change_percent": ((self.new_price - self.old_price) / max(self.old_price, 0.01)) * 100
        })

@dataclass
class TradeEvent(EconomyEvent):
    """Event for trade-related operations."""
    trade_route_id: int = 0
    origin_region_id: int = 0
    destination_region_id: int = 0
    resource_ids: List[str] = field(default_factory=list)
    volume: float = 0.0
    profit: float = 0.0
    
    def __post_init__(self):
        """Update data with trade-specific information."""
        self.data.update({
            "trade_route_id": self.trade_route_id,
            "origin_region_id": self.origin_region_id,
            "destination_region_id": self.destination_region_id,
            "resource_ids": self.resource_ids,
            "volume": self.volume,
            "profit": self.profit
        })

@dataclass
class TransactionEvent(EconomyEvent):
    """Event for transaction operations."""
    transaction_id: str = ""
    buyer_id: str = ""
    seller_id: str = ""
    resource_id: str = ""
    quantity: float = 0.0
    unit_price: float = 0.0
    total_value: float = 0.0
    
    def __post_init__(self):
        """Update data with transaction-specific information."""
        self.data.update({
            "transaction_id": self.transaction_id,
            "buyer_id": self.buyer_id,
            "seller_id": self.seller_id,
            "resource_id": self.resource_id,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "total_value": self.total_value
        })

class EconomyEventBus:
    """
    Event bus for economy system events.
    
    Provides publish/subscribe functionality for economy events with support
    for synchronous and asynchronous event handling.
    """
    
    def __init__(self):
        """Initialize the event bus."""
        self._subscribers: Dict[EconomyEventType, List[Callable]] = {}
        self._async_subscribers: Dict[EconomyEventType, List[Callable]] = {}
        self._global_subscribers: List[Callable] = []
        self._async_global_subscribers: List[Callable] = []
        self._event_history: List[EconomyEvent] = []
        self._max_history_size = 1000
        
    def subscribe(self, event_type: EconomyEventType, handler: Callable[[EconomyEvent], None]):
        """
        Subscribe to a specific event type.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Function to call when event is published
        """
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(handler)
        logger.debug(f"Subscribed to {event_type.value}")
    
    def subscribe_async(self, event_type: EconomyEventType, handler: Callable[[EconomyEvent], None]):
        """
        Subscribe to a specific event type with async handler.
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async function to call when event is published
        """
        if event_type not in self._async_subscribers:
            self._async_subscribers[event_type] = []
        self._async_subscribers[event_type].append(handler)
        logger.debug(f"Subscribed async to {event_type.value}")
    
    def subscribe_all(self, handler: Callable[[EconomyEvent], None]):
        """
        Subscribe to all economy events.
        
        Args:
            handler: Function to call for any economy event
        """
        self._global_subscribers.append(handler)
        logger.debug("Subscribed to all economy events")
    
    def subscribe_all_async(self, handler: Callable[[EconomyEvent], None]):
        """
        Subscribe to all economy events with async handler.
        
        Args:
            handler: Async function to call for any economy event
        """
        self._async_global_subscribers.append(handler)
        logger.debug("Subscribed async to all economy events")
    
    def unsubscribe(self, event_type: EconomyEventType, handler: Callable[[EconomyEvent], None]):
        """
        Unsubscribe from a specific event type.
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Handler function to remove
        """
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(handler)
                logger.debug(f"Unsubscribed from {event_type.value}")
            except ValueError:
                logger.warning(f"Handler not found for {event_type.value}")
    
    def unsubscribe_async(self, event_type: EconomyEventType, handler: Callable[[EconomyEvent], None]):
        """
        Unsubscribe from a specific event type (async).
        
        Args:
            event_type: Type of event to unsubscribe from
            handler: Async handler function to remove
        """
        if event_type in self._async_subscribers:
            try:
                self._async_subscribers[event_type].remove(handler)
                logger.debug(f"Unsubscribed async from {event_type.value}")
            except ValueError:
                logger.warning(f"Async handler not found for {event_type.value}")
    
    def publish(self, event: EconomyEvent):
        """
        Publish an event to all subscribers.
        
        Args:
            event: Event to publish
        """
        try:
            # Add to history
            self._add_to_history(event)
            
            # Call specific event type subscribers
            if event.event_type in self._subscribers:
                for handler in self._subscribers[event.event_type]:
                    try:
                        handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler for {event.event_type.value}: {e}")
            
            # Call global subscribers
            for handler in self._global_subscribers:
                try:
                    handler(event)
                except Exception as e:
                    logger.error(f"Error in global event handler: {e}")
            
            logger.debug(f"Published event: {event.event_type.value}")
            
        except Exception as e:
            logger.error(f"Error publishing event {event.event_type.value}: {e}")
    
    async def publish_async(self, event: EconomyEvent):
        """
        Publish an event to all async subscribers.
        
        Args:
            event: Event to publish
        """
        try:
            # Add to history
            self._add_to_history(event)
            
            # Collect all async tasks
            tasks = []
            
            # Add specific event type async subscribers
            if event.event_type in self._async_subscribers:
                for handler in self._async_subscribers[event.event_type]:
                    tasks.append(self._safe_async_call(handler, event))
            
            # Add global async subscribers
            for handler in self._async_global_subscribers:
                tasks.append(self._safe_async_call(handler, event))
            
            # Execute all async handlers concurrently
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.debug(f"Published async event: {event.event_type.value}")
            
        except Exception as e:
            logger.error(f"Error publishing async event {event.event_type.value}: {e}")
    
    async def _safe_async_call(self, handler: Callable, event: EconomyEvent):
        """Safely call an async handler with error handling."""
        try:
            await handler(event)
        except Exception as e:
            logger.error(f"Error in async event handler: {e}")
    
    def _add_to_history(self, event: EconomyEvent):
        """Add event to history with size limit."""
        self._event_history.append(event)
        if len(self._event_history) > self._max_history_size:
            self._event_history.pop(0)
    
    def get_event_history(self, event_type: Optional[EconomyEventType] = None, 
                         limit: int = 100) -> List[EconomyEvent]:
        """
        Get event history.
        
        Args:
            event_type: Optional filter by event type
            limit: Maximum number of events to return
            
        Returns:
            List of events from history
        """
        events = self._event_history
        
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        
        return events[-limit:] if limit else events
    
    def clear_history(self):
        """Clear event history."""
        self._event_history.clear()
        logger.info("Event history cleared")
    
    def get_subscriber_count(self, event_type: Optional[EconomyEventType] = None) -> int:
        """
        Get number of subscribers for an event type.
        
        Args:
            event_type: Event type to check, or None for total
            
        Returns:
            Number of subscribers
        """
        if event_type:
            sync_count = len(self._subscribers.get(event_type, []))
            async_count = len(self._async_subscribers.get(event_type, []))
            return sync_count + async_count
        else:
            total = len(self._global_subscribers) + len(self._async_global_subscribers)
            for handlers in self._subscribers.values():
                total += len(handlers)
            for handlers in self._async_subscribers.values():
                total += len(handlers)
            return total
    
    def get_stats(self) -> Dict[str, Any]:
        """Get event bus statistics."""
        return {
            "total_subscribers": self.get_subscriber_count(),
            "event_types_with_subscribers": len(self._subscribers) + len(self._async_subscribers),
            "global_subscribers": len(self._global_subscribers) + len(self._async_global_subscribers),
            "events_in_history": len(self._event_history),
            "max_history_size": self._max_history_size
        }

# Global event bus instance
_event_bus: Optional[EconomyEventBus] = None

def get_event_bus() -> EconomyEventBus:
    """Get the global economy event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EconomyEventBus()
    return _event_bus

# Convenience functions for common operations
def publish_resource_event(event_type: EconomyEventType, resource_id: str, 
                          region_id: int, **kwargs) -> None:
    """Publish a resource-related event."""
    event = ResourceEvent(
        event_type=event_type,
        resource_id=resource_id,
        region_id=region_id,
        **kwargs
    )
    get_event_bus().publish(event)

def publish_market_event(event_type: EconomyEventType, market_id: int, 
                        region_id: int, **kwargs) -> None:
    """Publish a market-related event."""
    event = MarketEvent(
        event_type=event_type,
        market_id=market_id,
        region_id=region_id,
        **kwargs
    )
    get_event_bus().publish(event)

def publish_price_event(resource_id: str, market_id: int, old_price: float, 
                       new_price: float, **kwargs) -> None:
    """Publish a price update event."""
    event = PriceEvent(
        event_type=EconomyEventType.PRICE_UPDATED,
        resource_id=resource_id,
        market_id=market_id,
        old_price=old_price,
        new_price=new_price,
        **kwargs
    )
    get_event_bus().publish(event)

def publish_trade_event(event_type: EconomyEventType, trade_route_id: int, 
                       origin_region_id: int, destination_region_id: int, **kwargs) -> None:
    """Publish a trade-related event."""
    event = TradeEvent(
        event_type=event_type,
        trade_route_id=trade_route_id,
        origin_region_id=origin_region_id,
        destination_region_id=destination_region_id,
        **kwargs
    )
    get_event_bus().publish(event)

def publish_transaction_event(event_type: EconomyEventType, transaction_id: str, 
                             buyer_id: str, seller_id: str, **kwargs) -> None:
    """Publish a transaction-related event."""
    event = TransactionEvent(
        event_type=event_type,
        transaction_id=transaction_id,
        buyer_id=buyer_id,
        seller_id=seller_id,
        **kwargs
    )
    get_event_bus().publish(event)

def publish_system_event(event_type: EconomyEventType, **kwargs) -> None:
    """Publish a system-level event."""
    event = EconomyEvent(
        event_type=event_type,
        **kwargs
    )
    get_event_bus().publish(event)

# Event handler decorators for easy subscription
def on_economy_event(event_type: EconomyEventType):
    """Decorator for subscribing to economy events."""
    def decorator(func):
        get_event_bus().subscribe(event_type, func)
        return func
    return decorator

def on_economy_event_async(event_type: EconomyEventType):
    """Decorator for subscribing to economy events with async handler."""
    def decorator(func):
        get_event_bus().subscribe_async(event_type, func)
        return func
    return decorator 