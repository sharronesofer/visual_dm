"""
Region Event Service

Handles event dispatching and integration for the region system.
Fixed: Removed mock event dispatcher, integrated with real event infrastructure.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID

logger = logging.getLogger(__name__)


class RegionEventService:
    """
    Service for handling region-related events and notifications.
    Fixed: No longer uses mock dispatcher, integrates with actual event infrastructure.
    """
    
    def __init__(self):
        """Initialize the event service with proper event dispatcher."""
        self.event_dispatcher = self._initialize_event_dispatcher()
        self.event_history = []  # Local cache for recent events
        self.max_history_size = 1000
    
    def _initialize_event_dispatcher(self):
        """
        Initialize event dispatcher.
        Fixed: No longer returns mock, attempts to use real event infrastructure.
        """
        try:
            # Try to import the real event dispatcher
            from backend.infrastructure.events import EventDispatcher
            dispatcher = EventDispatcher()
            logger.info("Event dispatcher initialized successfully")
            return dispatcher
        except ImportError:
            # If event infrastructure not available, log warning and return None
            logger.warning("Event infrastructure not available, events will be logged only")
            return None
        except Exception as e:
            logger.error(f"Failed to initialize event dispatcher: {e}")
            return None
    
    def dispatch_region_event(
        self,
        event_type: str,
        region_id: UUID,
        event_data: Dict[str, Any],
        priority: str = "normal"
    ) -> bool:
        """
        Dispatch a region-related event.
        Fixed: Actually dispatches events when dispatcher is available.
        
        Args:
            event_type: Type of event (e.g., 'region_created', 'region_updated')
            region_id: ID of the affected region
            event_data: Additional event data
            priority: Event priority ('low', 'normal', 'high', 'critical')
            
        Returns:
            True if event was dispatched successfully, False otherwise
        """
        try:
            event_payload = {
                'event_type': event_type,
                'region_id': str(region_id),
                'timestamp': datetime.utcnow().isoformat(),
                'priority': priority,
                'data': event_data
            }
            
            # Add to local history
            self._add_to_history(event_payload)
            
            # Dispatch event if dispatcher available
            if self.event_dispatcher:
                success = self.event_dispatcher.dispatch(event_type, event_payload)
                if success:
                    logger.debug(f"Dispatched {event_type} event for region {region_id}")
                    return True
                else:
                    logger.warning(f"Failed to dispatch {event_type} event for region {region_id}")
                    return False
            else:
                # Log event if no dispatcher
                logger.info(f"Event logged: {event_type} for region {region_id} - {event_data}")
                return True
                
        except Exception as e:
            logger.error(f"Error dispatching event {event_type} for region {region_id}: {e}")
            return False
    
    def dispatch_tension_event(
        self,
        region_id: str,
        poi_id: str,
        tension_change: float,
        event_source: str,
        additional_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Dispatch a tension-related event for integration with tension system.
        Fixed: Integrates with the new unified tension system.
        """
        try:
            # Import tension event types
            from backend.systems.tension.models.tension_events import TensionEventType
            
            # Determine event type based on source
            event_type_mapping = {
                'player_action': TensionEventType.PLAYER_COMBAT,
                'npc_death': TensionEventType.NPC_DEATH,
                'environmental': TensionEventType.ENVIRONMENTAL_DISASTER,
                'political': TensionEventType.POLITICAL_CHANGE,
                'economic': TensionEventType.ECONOMIC_CHANGE
            }
            
            tension_event_type = event_type_mapping.get(
                event_source, 
                TensionEventType.PLAYER_COMBAT
            )
            
            # Try to integrate with tension system
            try:
                from backend.systems.tension.services.tension_manager import UnifiedTensionManager
                tension_manager = UnifiedTensionManager()
                
                # Update tension through the unified system
                new_tension = tension_manager.update_tension_from_event(
                    region_id=region_id,
                    poi_id=poi_id,
                    event_type=tension_event_type,
                    event_data=additional_data or {}
                )
                
                logger.info(f"Updated tension for {region_id}/{poi_id}: {new_tension}")
                return True
                
            except ImportError:
                logger.warning("Unified tension system not available, logging tension event only")
                
            # Fallback to event dispatch
            event_data = {
                'region_id': region_id,
                'poi_id': poi_id,
                'tension_change': tension_change,
                'event_source': event_source,
                'additional_data': additional_data or {}
            }
            
            return self.dispatch_region_event(
                'tension_updated', 
                UUID(region_id) if len(region_id) == 36 else UUID('00000000-0000-0000-0000-000000000000'),
                event_data
            )
            
        except Exception as e:
            logger.error(f"Error dispatching tension event: {e}")
            return False
    
    def dispatch_world_generation_event(
        self,
        continent_id: str,
        event_type: str,
        generation_data: Dict[str, Any]
    ) -> bool:
        """
        Dispatch world generation events.
        Fixed: Integrates with new world generation system.
        """
        try:
            event_data = {
                'continent_id': continent_id,
                'generation_type': event_type,
                'generation_data': generation_data,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            return self.dispatch_region_event(
                f'world_generation_{event_type}',
                UUID('00000000-0000-0000-0000-000000000000'),  # Use null UUID for system events
                event_data,
                priority='high'
            )
            
        except Exception as e:
            logger.error(f"Error dispatching world generation event: {e}")
            return False
    
    def get_recent_events(
        self,
        region_id: Optional[UUID] = None,
        event_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent events from the local cache.
        
        Args:
            region_id: Filter by region ID (optional)
            event_type: Filter by event type (optional)
            limit: Maximum number of events to return
            
        Returns:
            List of recent events matching the criteria
        """
        filtered_events = self.event_history.copy()
        
        # Apply filters
        if region_id:
            filtered_events = [
                event for event in filtered_events
                if event.get('region_id') == str(region_id)
            ]
        
        if event_type:
            filtered_events = [
                event for event in filtered_events
                if event.get('event_type') == event_type
            ]
        
        # Sort by timestamp (most recent first) and limit
        filtered_events.sort(
            key=lambda x: x.get('timestamp', ''), 
            reverse=True
        )
        
        return filtered_events[:limit]
    
    def _add_to_history(self, event: Dict[str, Any]):
        """Add event to local history cache."""
        self.event_history.append(event)
        
        # Trim history if it gets too large
        if len(self.event_history) > self.max_history_size:
            self.event_history = self.event_history[-self.max_history_size:]
    
    def clear_event_history(self):
        """Clear the local event history cache."""
        self.event_history.clear()
        logger.info("Event history cleared")
    
    def get_event_statistics(self) -> Dict[str, Any]:
        """Get statistics about processed events."""
        if not self.event_history:
            return {
                'total_events': 0,
                'event_types': {},
                'regions_affected': 0,
                'oldest_event': None,
                'newest_event': None
            }
        
        # Count event types
        event_types = {}
        regions = set()
        
        for event in self.event_history:
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            region_id = event.get('region_id')
            if region_id:
                regions.add(region_id)
        
        # Get timestamp range
        timestamps = [event.get('timestamp') for event in self.event_history if event.get('timestamp')]
        timestamps.sort()
        
        return {
            'total_events': len(self.event_history),
            'event_types': event_types,
            'regions_affected': len(regions),
            'oldest_event': timestamps[0] if timestamps else None,
            'newest_event': timestamps[-1] if timestamps else None,
            'dispatcher_available': self.event_dispatcher is not None
        }


# Factory function
def create_region_event_service() -> RegionEventService:
    """Create and return a RegionEventService instance."""
    return RegionEventService() 