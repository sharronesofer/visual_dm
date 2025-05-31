"""
Event Service

Service layer for chaos event management.
Provides high-level interface for event operations and queries.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from backend.systems.chaos.services.event_manager import EventManager
from backend.systems.chaos.core.config import ChaosConfig
from backend.systems.chaos.models.chaos_events import ChaosEvent, ChaosEventType

logger = logging.getLogger(__name__)

class EventService:
    """
    Service for managing chaos events and their lifecycle.
    
    This service provides a high-level interface for triggering,
    managing, and monitoring chaos events in the game world.
    """
    
    def __init__(self, config: Optional[ChaosConfig] = None):
        """Initialize the event service."""
        self.config = config or ChaosConfig()
        self.event_manager = EventManager(self.config)
        
    async def initialize(self) -> None:
        """Initialize the event service."""
        try:
            await self.event_manager.initialize()
            logger.info("Event Service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Event Service: {e}")
            raise
    
    def get_active_events(self) -> List[ChaosEvent]:
        """Get all currently active chaos events."""
        return self.event_manager.get_active_events()
    
    def get_event_by_id(self, event_id: str) -> Optional[ChaosEvent]:
        """Get a specific event by its ID."""
        return self.event_manager.get_event_by_id(event_id)
    
    def get_events_by_type(self, event_type: ChaosEventType) -> List[ChaosEvent]:
        """Get all events of a specific type."""
        return self.event_manager.get_events_by_type(event_type)
    
    def get_events_in_region(self, region_id: str) -> List[ChaosEvent]:
        """Get all events affecting a specific region."""
        return self.event_manager.get_events_in_region(region_id)
    
    async def trigger_event(
        self,
        event_type: str,
        severity: str = "moderate",
        regions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[ChaosEvent]:
        """
        Manually trigger a chaos event.
        
        Args:
            event_type: Type of event to trigger
            severity: Severity level of the event
            regions: Regions to affect (None for global)
            metadata: Additional event metadata
            
        Returns:
            The triggered event or None if triggering failed
        """
        return await self.event_manager.trigger_event(
            event_type=event_type,
            severity=severity,
            regions=regions,
            metadata=metadata
        )
    
    async def resolve_event(
        self,
        event_id: str,
        resolution_type: str = "natural",
        resolution_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Resolve/end a chaos event.
        
        Args:
            event_id: ID of the event to resolve
            resolution_type: How the event was resolved
            resolution_data: Additional resolution data
            
        Returns:
            True if event was resolved successfully
        """
        return await self.event_manager.resolve_event(
            event_id=event_id,
            resolution_type=resolution_type,
            resolution_data=resolution_data
        )
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about chaos events.
        
        Returns:
            Dict containing event statistics
        """
        return self.event_manager.get_event_statistics()
    
    def get_event_history(
        self,
        hours: int = 24,
        event_type: Optional[str] = None,
        region_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get historical event data.
        
        Args:
            hours: Number of hours of history to retrieve
            event_type: Optional event type to filter by
            region_id: Optional region to filter by
            
        Returns:
            List of historical event data
        """
        return self.event_manager.get_event_history(
            hours=hours,
            event_type=event_type,
            region_id=region_id
        )
    
    def get_event_cooldowns(self) -> Dict[str, datetime]:
        """Get current event cooldown status."""
        return self.event_manager.get_event_cooldowns()
    
    def set_event_cooldown(
        self,
        event_type: str,
        cooldown_minutes: int
    ) -> None:
        """
        Set a cooldown for a specific event type.
        
        Args:
            event_type: Type of event to set cooldown for
            cooldown_minutes: Cooldown duration in minutes
        """
        self.event_manager.set_event_cooldown(event_type, cooldown_minutes)
    
    def clear_event_cooldown(self, event_type: str) -> None:
        """Clear the cooldown for a specific event type."""
        self.event_manager.clear_event_cooldown(event_type)
    
    def register_event_handler(
        self,
        event_type: str,
        handler_func
    ) -> None:
        """
        Register a handler for a specific event type.
        
        Args:
            event_type: Type of event to handle
            handler_func: Function to handle the event
        """
        self.event_manager.register_event_handler(event_type, handler_func)
    
    def unregister_event_handler(
        self,
        event_type: str,
        handler_func
    ) -> None:
        """
        Unregister an event handler.
        
        Args:
            event_type: Type of event
            handler_func: Handler function to remove
        """
        self.event_manager.unregister_event_handler(event_type, handler_func)
    
    async def stop(self) -> None:
        """Stop the event service."""
        await self.event_manager.stop() 