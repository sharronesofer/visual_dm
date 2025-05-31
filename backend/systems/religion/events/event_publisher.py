"""
Religion Event Publisher - Central event publishing for religion system.

This module provides a centralized event publisher for all religion-related events,
ensuring consistent event dispatching and integration with both the event system
and WebSocket broadcasting for real-time updates.
"""

import logging
from typing import Dict, Any, List, Optional, Union
from uuid import UUID
import asyncio

# Try to import from main event dispatcher, fall back to local if needed
try:
    from backend.infrastructure.events import get_dispatcher
    HAS_EVENT_DISPATCHER = True
except ImportError:
    HAS_EVENT_DISPATCHER = False
    logging.warning("Main event dispatcher not available, using local fallback")

from backend.systems.religion.events.religion_events import (
    # Core events
    ReligionCreatedEvent, ReligionUpdatedEvent, ReligionDeletedEvent,
    # Membership events
    MembershipCreatedEvent, MembershipUpdatedEvent, MembershipDeletedEvent, ConversionEvent,
    # Devotion events
    DevotionChangedEvent, ReligiousRitualEvent,
    # Narrative events
    ReligiousNarrativeEvent, SchismEvent,
    # System integration events
    ReligiousInfluenceEvent, ReligiousConflictEvent,
)

# Set up logging
logger = logging.getLogger(__name__)

class ReligionEventPublisher:
    """
    Centralized publisher for religion system events.
    
    Handles event publishing to both the main event dispatcher (when available)
    and WebSocket broadcasting for real-time frontend updates.
    """
    
    def __init__(self):
        self.event_dispatcher = None
        self.websocket_manager = None
        
        # Try to get the main event dispatcher
        if HAS_EVENT_DISPATCHER:
            try:
                self.event_dispatcher = get_dispatcher()
                logger.info("Religion event publisher connected to main event dispatcher")
            except Exception as e:
                logger.warning(f"Could not connect to main event dispatcher: {e}")
        
        # Try to get the WebSocket manager (set after initialization)
        try:
            self._setup_websocket_integration()
        except Exception as e:
            logger.info(f"WebSocket integration will be set up later: {e}")
    
    def _setup_websocket_integration(self):
        """Set up WebSocket integration for real-time event broadcasting."""
        try:
            # Import here to avoid circular imports
from backend.systems.religion.services.websocket_manager import religion_websocket_manager
            self.websocket_manager = religion_websocket_manager
            self.websocket_manager.event_publisher = self
            logger.info("Religion event publisher connected to WebSocket manager")
        except ImportError as e:
            logger.info(f"WebSocket manager not available yet: {e}")
    
    def _publish(self, event) -> bool:
        """
        Publish an event to both the event dispatcher and WebSocket clients.
        
        Args:
            event: The event to publish
            
        Returns:
            bool: True if published successfully
        """
        success = True
        
        # Publish to main event dispatcher if available
        if self.event_dispatcher:
            try:
                self.event_dispatcher.dispatch(event)
                logger.debug(f"Published event to main dispatcher: {event.__class__.__name__}")
            except Exception as e:
                logger.error(f"Failed to publish event to main dispatcher: {e}")
                success = False
        
        # Broadcast to WebSocket clients if available
        if self.websocket_manager:
            try:
                # Run the async WebSocket broadcast in a task
                asyncio.create_task(self._broadcast_websocket_event(event))
                logger.debug(f"Broadcasted event to WebSocket clients: {event.__class__.__name__}")
            except Exception as e:
                logger.error(f"Failed to broadcast event to WebSocket clients: {e}")
                success = False
        
        return success
    
    async def _broadcast_websocket_event(self, event):
        """
        Broadcast an event to WebSocket clients based on event type.
        
        Args:
            event: The event to broadcast
        """
        if not self.websocket_manager:
            return
        
        # Prepare event data for WebSocket broadcast
        event_data = {
            "event_type": event.__class__.__name__,
            "data": event.dict() if hasattr(event, 'dict') else event.__dict__,
            "timestamp": event.timestamp.isoformat() if hasattr(event, 'timestamp') else None,
            "message_id": str(event.event_id) if hasattr(event, 'event_id') else None
        }
        
        # Route to appropriate WebSocket handler based on event type
        try:
            # Core religion events
            if isinstance(event, (ReligionCreatedEvent, ReligionUpdatedEvent, ReligionDeletedEvent)):
                await self.websocket_manager._handle_religion_event(event_data)
            
            # Membership events
            elif isinstance(event, (MembershipCreatedEvent, MembershipUpdatedEvent, MembershipDeletedEvent, ConversionEvent)):
                await self.websocket_manager._handle_membership_event(event_data)
            
            # Devotion events
            elif isinstance(event, (DevotionChangedEvent, ReligiousRitualEvent)):
                await self.websocket_manager._handle_devotion_event(event_data)
            
            # Narrative events
            elif isinstance(event, (ReligiousNarrativeEvent, SchismEvent)):
                await self.websocket_manager._handle_narrative_event(event_data)
            
            # Influence events
            elif isinstance(event, (ReligiousInfluenceEvent, ReligiousConflictEvent)):
                await self.websocket_manager._handle_influence_event(event_data)
            
            else:
                logger.warning(f"Unknown event type for WebSocket broadcast: {event.__class__.__name__}")
                
        except Exception as e:
            logger.error(f"Error broadcasting event to WebSocket: {e}")
    
    # ============================================================================
    # Core Religion Events
    # ============================================================================
    
    def publish_religion_created(self, 
                               religion_id: UUID,
                               name: str, 
                               religion_type: str,
                               creator_id: Optional[UUID] = None,
                               region_id: Optional[str] = None,
                               metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Publish religion created event."""
        event = ReligionCreatedEvent(
            religion_id=religion_id,
            name=name,
            religion_type=religion_type,
            creator_id=creator_id,
            region_id=region_id,
            metadata=metadata
        )
        return self._publish(event)
    
    def publish_religion_updated(self,
                               religion_id: UUID,
                               changes: Dict[str, Any],
                               old_values: Optional[Dict[str, Any]] = None,
                               updated_by: Optional[UUID] = None) -> bool:
        """Publish religion updated event."""
        event = ReligionUpdatedEvent(
            religion_id=religion_id,
            changes=changes,
            old_values=old_values,
            updated_by=updated_by
        )
        return self._publish(event)
    
    def publish_religion_deleted(self,
                               religion_id: UUID,
                               name: str,
                               deletion_reason: Optional[str] = None,
                               deleted_by: Optional[UUID] = None) -> bool:
        """Publish religion deleted event."""
        event = ReligionDeletedEvent(
            religion_id=religion_id,
            name=name,
            deletion_reason=deletion_reason,
            deleted_by=deleted_by
        )
        return self._publish(event)
    
    # ============================================================================
    # Membership Events  
    # ============================================================================
    
    def publish_membership_created(self,
                                 membership_id: UUID,
                                 religion_id: UUID,
                                 entity_id: UUID,
                                 entity_type: str,
                                 role: str = "follower",
                                 devotion_level: float = 0.5) -> bool:
        """Publish membership created event."""
        event = MembershipCreatedEvent(
            membership_id=membership_id,
            religion_id=religion_id,
            entity_id=entity_id,
            entity_type=entity_type,
            role=role,
            devotion_level=devotion_level
        )
        return self._publish(event)
    
    def publish_membership_updated(self,
                                 membership_id: UUID,
                                 religion_id: UUID,
                                 entity_id: UUID,
                                 changes: Dict[str, Any],
                                 old_values: Optional[Dict[str, Any]] = None) -> bool:
        """Publish membership updated event."""
        event = MembershipUpdatedEvent(
            membership_id=membership_id,
            religion_id=religion_id,
            entity_id=entity_id,
            changes=changes,
            old_values=old_values
        )
        return self._publish(event)
    
    def publish_membership_deleted(self,
                                 membership_id: UUID,
                                 religion_id: UUID,
                                 entity_id: UUID,
                                 reason: Optional[str] = None) -> bool:
        """Publish membership deleted event."""
        event = MembershipDeletedEvent(
            membership_id=membership_id,
            religion_id=religion_id,
            entity_id=entity_id,
            reason=reason
        )
        return self._publish(event)
    
    def publish_conversion(self,
                         entity_id: UUID,
                         entity_type: str,
                         from_religion_id: Optional[UUID],
                         to_religion_id: UUID,
                         conversion_reason: Optional[str] = None,
                         conversion_strength: float = 1.0) -> bool:
        """Publish conversion event."""
        event = ConversionEvent(
            entity_id=entity_id,
            entity_type=entity_type,
            from_religion_id=from_religion_id,
            to_religion_id=to_religion_id,
            conversion_reason=conversion_reason,
            conversion_strength=conversion_strength
        )
        return self._publish(event)
    
    # ============================================================================
    # Devotion Events
    # ============================================================================
    
    def publish_devotion_changed(self,
                               membership_id: UUID,
                               religion_id: UUID,
                               entity_id: UUID,
                               old_devotion: float,
                               new_devotion: float,
                               change_reason: Optional[str] = None) -> bool:
        """Publish devotion changed event."""
        event = DevotionChangedEvent(
            membership_id=membership_id,
            religion_id=religion_id,
            entity_id=entity_id,
            old_devotion=old_devotion,
            new_devotion=new_devotion,
            change_reason=change_reason
        )
        return self._publish(event)
    
    def publish_religious_ritual(self,
                               ritual_id: UUID,
                               religion_id: UUID,
                               entity_id: UUID,
                               ritual_type: str,
                               ritual_name: str,
                               location: Optional[str] = None,
                               participants: Optional[List[UUID]] = None,
                               devotion_effect: Optional[float] = None) -> bool:
        """Publish religious ritual event."""
        event = ReligiousRitualEvent(
            ritual_id=ritual_id,
            religion_id=religion_id,
            entity_id=entity_id,
            ritual_type=ritual_type,
            ritual_name=ritual_name,
            location=location,
            participants=participants,
            devotion_effect=devotion_effect
        )
        return self._publish(event)
    
    # ============================================================================
    # Narrative Events
    # ============================================================================
    
    def publish_religious_narrative(self,
                                  narrative_id: UUID,
                                  religion_id: UUID,
                                  narrative_type: str,
                                  title: str,
                                  content: str,
                                  entities_involved: Optional[List[UUID]] = None,
                                  location: Optional[str] = None,
                                  impact_level: str = "minor") -> bool:
        """Publish religious narrative event."""
        event = ReligiousNarrativeEvent(
            narrative_id=narrative_id,
            religion_id=religion_id,
            narrative_type=narrative_type,
            title=title,
            content=content,
            entities_involved=entities_involved,
            location=location,
            impact_level=impact_level
        )
        return self._publish(event)
    
    def publish_schism(self,
                     schism_id: UUID,
                     parent_religion_id: UUID,
                     new_religion_id: Optional[UUID] = None,
                     schism_type: str = "doctrinal",
                     cause: str = "unknown",
                     leader_id: Optional[UUID] = None,
                     followers_affected: Optional[List[UUID]] = None) -> bool:
        """Publish schism event."""
        event = SchismEvent(
            schism_id=schism_id,
            parent_religion_id=parent_religion_id,
            new_religion_id=new_religion_id,
            schism_type=schism_type,
            cause=cause,
            leader_id=leader_id,
            followers_affected=followers_affected
        )
        return self._publish(event)
    
    # ============================================================================
    # System Integration Events
    # ============================================================================
    
    def publish_religious_influence(self,
                                  religion_id: UUID,
                                  influence_type: str,
                                  target_type: str,
                                  target_id: Union[UUID, str],
                                  influence_strength: float,
                                  influence_change: float,
                                  cause: Optional[str] = None) -> bool:
        """Publish religious influence event."""
        event = ReligiousInfluenceEvent(
            religion_id=religion_id,
            influence_type=influence_type,
            target_type=target_type,
            target_id=target_id,
            influence_strength=influence_strength,
            influence_change=influence_change,
            cause=cause
        )
        return self._publish(event)
    
    def publish_religious_conflict(self,
                                 conflict_id: UUID,
                                 religion_ids: List[UUID],
                                 conflict_type: str,
                                 cause: str,
                                 location: Optional[str] = None,
                                 intensity: float = 1.0,
                                 resolution: Optional[str] = None) -> bool:
        """Publish religious conflict event."""
        event = ReligiousConflictEvent(
            conflict_id=conflict_id,
            religion_ids=religion_ids,
            conflict_type=conflict_type,
            cause=cause,
            location=location,
            intensity=intensity,
            resolution=resolution
        )
        return self._publish(event)

# Global instance for easy access
_religion_event_publisher = None

def get_religion_event_publisher() -> ReligionEventPublisher:
    """Get the global religion event publisher instance."""
    global _religion_event_publisher
    if _religion_event_publisher is None:
        _religion_event_publisher = ReligionEventPublisher()
    return _religion_event_publisher

def publish_religion_event(event) -> bool:
    """Publish a religion event using the global publisher."""
    publisher = get_religion_event_publisher()
    return publisher._publish(event) 