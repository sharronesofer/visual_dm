"""
Event handlers for world state events.

This module provides handlers for various world state events.
"""
import logging
from typing import Dict, Any, Optional, List

from backend.systems.world_state.events import WorldStateEvent
from backend.systems.world_state.utils.world_event_utils import create_world_event
from backend.systems.world_state.world_types import StateCategory, WorldRegion

logger = logging.getLogger(__name__)


class WorldStateEventHandler:
    """Base handler for all world state events."""
    
    def __init__(self):
        self.handled_event_types = [WorldStateEvent]
    
    async def handle_event(self, event: WorldStateEvent) -> None:
        """
        General handler for world state events.
        
        Args:
            event: The world state event to handle
        """
        logger.info(f"Handling world state event: {event.event_type}")
        
        # Log the event for analytics
        self._log_to_analytics(event)
        
        # Handle based on event type
        if event.event_type == "state_created":
            await self._handle_created_event(event)
        elif event.event_type == "state_updated":
            await self._handle_updated_event(event)
        elif event.event_type == "state_deleted":
            await self._handle_deleted_event(event)
        elif event.event_type == "state_calculated":
            await self._handle_calculated_event(event)
    
    async def _handle_created_event(self, event: WorldStateEvent) -> None:
        """Handle state created events."""
        logger.debug(f"State created event: {event.event_type}")
        
        # Create a world event for significant state creations
        state_key = event.data.get('state_key', '')
        if self._is_significant_state(state_key):
            await self._create_world_event(
                event_type="state_created",
                description=f"New state created: {state_key}",
                metadata=event.data
            )
    
    async def _handle_updated_event(self, event: WorldStateEvent) -> None:
        """Handle state updated events."""
        logger.debug(f"State updated event: {event.event_type}")
        
        # Check for significant changes
        if await self._is_significant_change(event):
            await self._create_world_event(
                event_type="state_changed",
                description=f"State changed: {event.data.get('state_key', '')}",
                metadata=event.data
            )
    
    async def _handle_deleted_event(self, event: WorldStateEvent) -> None:
        """Handle state deleted events."""
        logger.debug(f"State deleted event: {event.event_type}")
        
        state_key = event.data.get('state_key', '')
        if self._is_significant_state(state_key):
            await self._create_world_event(
                event_type="state_deleted",
                description=f"State removed: {state_key}",
                metadata=event.data
            )
    
    async def _handle_calculated_event(self, event: WorldStateEvent) -> None:
        """Handle state calculated events."""
        logger.debug(f"State calculated event: {event.event_type}")
        
        await self._create_world_event(
            event_type="state_calculated",
            description=f"Calculated state: {event.data.get('state_key', '')}",
            metadata=event.data
        )
    
    def _log_to_analytics(self, event: WorldStateEvent) -> None:
        """Log event to analytics system."""
        # Placeholder for analytics logging
        logger.info(f"Analytics: {event.event_type} at {event.timestamp}")
    
    def _is_significant_state(self, state_key: str) -> bool:
        """Determine if a state change is significant enough to create an event."""
        # Business rules for significance
        significant_patterns = [
            'faction_power',
            'population_count',
            'economic_status',
            'military_strength',
            'diplomatic_relations'
        ]
        
        return any(pattern in state_key for pattern in significant_patterns)
    
    async def _is_significant_change(self, event: WorldStateEvent) -> bool:
        """Check if a state change is significant."""
        old_value = event.data.get('old_value')
        new_value = event.data.get('new_value')
        
        if old_value is None or new_value is None:
            return True  # New or deleted values are significant
        
        # Check for numeric changes above threshold
        if isinstance(old_value, (int, float)) and isinstance(new_value, (int, float)):
            change_percent = abs(new_value - old_value) / max(abs(old_value), 1)
            return change_percent > 0.1  # 10% change threshold
        
        # String changes are significant if different
        return old_value != new_value
    
    async def _create_world_event(self, 
                                 event_type: str, 
                                 description: str, 
                                 category: Optional[StateCategory] = None,
                                 region: Optional[WorldRegion] = None,
                                 entity_id: Optional[str] = None,
                                 metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a world event from a state change."""
        return create_world_event(
            event_type=event_type,
            description=description,
            category=category,
            region=region,
            entity_id=entity_id,
            metadata=metadata or {}
        ) 