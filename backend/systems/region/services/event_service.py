"""
Region Event Service - Pure Business Logic

Handles event creation and business logic for the region system.
Technical event dispatching moved to infrastructure layer.
Fixed: Now uses strings per Bible and follows clean architecture.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from uuid import UUID


class RegionEventBusinessService:
    """
    Service for handling region-related events - pure business logic.
    Uses strings per Bible and follows clean architecture principles.
    """
    
    def __init__(self):
        """Initialize the event service."""
        self.event_history = []  # Local business cache for recent events
        self.max_history_size = 1000

    def create_region_created_event(
        self,
        region_id: UUID,
        region_name: str,
        region_type: str,  # Use string per Bible
        continent_id: Optional[UUID] = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Create a region created event with business validation.
        
        Returns:
            Dict containing the event data for infrastructure to handle
        """
        event_data = {
            "event_type": "region_created",
            "region_id": str(region_id),
            "region_name": region_name,
            "region_type": region_type,
            "continent_id": str(continent_id) if continent_id else None,
            "created_by": created_by,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "normal"
        }
        
        # Add to local history for business logic needs
        self._add_to_history(event_data)
        
        return event_data

    def create_region_updated_event(
        self,
        region_id: UUID,
        region_name: str,
        changed_fields: List[str],
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        continent_id: Optional[UUID] = None,
        updated_by: str = "system"
    ) -> Dict[str, Any]:
        """
        Create a region updated event with business validation.
        """
        event_data = {
            "event_type": "region_updated",
            "region_id": str(region_id),
            "region_name": region_name,
            "changed_fields": changed_fields,
            "old_values": old_values,
            "new_values": new_values,
            "continent_id": str(continent_id) if continent_id else None,
            "updated_by": updated_by,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "normal"
        }
        
        self._add_to_history(event_data)
        return event_data

    def create_region_deleted_event(
        self,
        region_id: UUID,
        region_name: str,
        continent_id: Optional[UUID] = None,
        deleted_by: str = "system",
        backup_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a region deleted event with business validation.
        """
        event_data = {
            "event_type": "region_deleted",
            "region_id": str(region_id),
            "region_name": region_name,
            "continent_id": str(continent_id) if continent_id else None,
            "deleted_by": deleted_by,
            "backup_data": backup_data or {},
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "high"
        }
        
        self._add_to_history(event_data)
        return event_data

    def create_territory_claimed_event(
        self,
        faction_id: str,
        region_id: UUID,
        territory_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a territory claimed event.
        """
        event_data = {
            "event_type": "territory_claimed",
            "faction_id": faction_id,
            "region_id": str(region_id),
            "territory_data": territory_data,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "high"
        }
        
        self._add_to_history(event_data)
        return event_data

    def create_resource_discovered_event(
        self,
        region_id: UUID,
        resource_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a resource discovered event.
        """
        # Business validation: Ensure resource type is string per Bible
        if "resource_type" not in resource_data:
            raise ValueError("resource_type is required for resource discovery events")
        
        event_data = {
            "event_type": "resource_discovered",
            "region_id": str(region_id),
            "resource_data": resource_data,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "normal"
        }
        
        self._add_to_history(event_data)
        return event_data

    def create_environmental_change_event(
        self,
        region_id: UUID,
        change_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create an environmental change event.
        """
        # Business validation
        required_fields = ["change_type"]
        for field in required_fields:
            if field not in change_data:
                raise ValueError(f"{field} is required for environmental change events")
        
        event_data = {
            "event_type": "environmental_change",
            "region_id": str(region_id),
            "change_data": change_data,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "normal"
        }
        
        self._add_to_history(event_data)
        return event_data

    def create_character_entered_region_event(
        self,
        character_id: str,
        region_id: UUID
    ) -> Dict[str, Any]:
        """
        Create a character entered region event.
        """
        event_data = {
            "event_type": "character_entered_region",
            "character_id": character_id,
            "region_id": str(region_id),
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "low"
        }
        
        self._add_to_history(event_data)
        return event_data

    def create_world_generation_event(
        self,
        generation_type: str,
        generation_data: Dict[str, Any],
        continent_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create world generation events with business validation.
        """
        # Business rule: Validate generation event types
        valid_generation_types = [
            'continent_created', 'world_generated', 'region_generated',
            'biome_generated', 'resource_placed', 'poi_generated'
        ]
        
        if generation_type not in valid_generation_types:
            raise ValueError(f"Invalid generation event type: {generation_type}")
        
        event_data = {
            "event_type": f"world_generation_{generation_type}",
            "generation_type": generation_type,
            "continent_id": continent_id,
            "generation_data": generation_data,
            "timestamp": datetime.utcnow().isoformat(),
            "priority": "high"
        }
        
        self._add_to_history(event_data)
        return event_data

    def get_recent_events(
        self,
        region_id: Optional[UUID] = None,
        event_type: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get recent events from local history with business filtering.
        """
        filtered_events = self.event_history
        
        # Business rule: Filter by region_id if provided
        if region_id:
            filtered_events = [
                event for event in filtered_events 
                if event.get('region_id') == str(region_id)
            ]
        
        # Business rule: Filter by event_type if provided
        if event_type:
            filtered_events = [
                event for event in filtered_events 
                if event.get('event_type') == event_type
            ]
        
        # Business rule: Return most recent events first, limited by limit
        return list(reversed(filtered_events))[:limit]

    def get_event_statistics(self) -> Dict[str, Any]:
        """
        Calculate business statistics from event history.
        """
        if not self.event_history:
            return {
                "total_events": 0,
                "event_types": {},
                "priority_distribution": {},
                "recent_activity": 0
            }
        
        # Business calculations
        event_types = {}
        priority_distribution = {}
        recent_activity = 0
        current_time = datetime.utcnow()
        
        for event in self.event_history:
            # Count event types
            event_type = event.get('event_type', 'unknown')
            event_types[event_type] = event_types.get(event_type, 0) + 1
            
            # Count priority distribution
            priority = event.get('priority', 'normal')
            priority_distribution[priority] = priority_distribution.get(priority, 0) + 1
            
            # Count recent activity (last hour)
            try:
                event_time = datetime.fromisoformat(event.get('timestamp', ''))
                if (current_time - event_time).total_seconds() < 3600:  # 1 hour
                    recent_activity += 1
            except:
                pass
        
        return {
            "total_events": len(self.event_history),
            "event_types": event_types,
            "priority_distribution": priority_distribution,
            "recent_activity": recent_activity
        }

    def clear_event_history(self):
        """Clear the local event history - business operation"""
        self.event_history.clear()

    def _add_to_history(self, event: Dict[str, Any]):
        """Add event to local history with size management"""
        self.event_history.append(event)
        
        # Business rule: Maintain maximum history size
        if len(self.event_history) > self.max_history_size:
            # Remove oldest events
            excess_count = len(self.event_history) - self.max_history_size
            self.event_history = self.event_history[excess_count:]


def get_region_event_service() -> RegionEventBusinessService:
    """Get a default region event service instance"""
    return RegionEventBusinessService() 