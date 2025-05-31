"""
Character Location Service

Service for managing character location tracking and integration with the region system.
Handles character movement between regions and dispatches appropriate events.
"""

import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from backend.systems.character.models import CharacterEntity
from backend.systems.region.models import HexCoordinate
from backend.systems.region.services.event_service import get_region_event_service

logger = logging.getLogger(__name__)


class CharacterLocationService:
    """Service for managing character location and region integration"""
    
    def __init__(self):
        self.region_event_service = get_region_event_service()
        logger.info("CharacterLocationService initialized")
    
    async def move_character_to_region(
        self,
        character_id: UUID,
        character_name: str,
        new_region_id: UUID,
        new_region_name: str,
        new_location: Optional[HexCoordinate] = None,
        old_region_id: Optional[UUID] = None,
        old_region_name: Optional[str] = None,
        old_location: Optional[HexCoordinate] = None,
        movement_method: str = "walking",
        travel_time: Optional[float] = None
    ) -> None:
        """Move a character to a new region and dispatch appropriate events"""
        try:
            # Dispatch character location changed event
            await self.region_event_service.publish_character_location_changed(
                character_id=character_id,
                character_name=character_name,
                old_region_id=old_region_id,
                new_region_id=new_region_id,
                old_location=old_location,
                new_location=new_location,
                movement_method=movement_method,
                travel_time=travel_time
            )
            
            # Dispatch character left region event if there was a previous region
            if old_region_id and old_region_name:
                await self.region_event_service.publish_character_left_region(
                    character_id=character_id,
                    character_name=character_name,
                    region_id=old_region_id,
                    region_name=old_region_name,
                    exit_location=old_location or HexCoordinate(q=0, r=0, s=0),
                    exit_method=movement_method,
                    destination_region_id=new_region_id
                )
            
            # Dispatch character entered region event
            await self.region_event_service.publish_character_entered_region(
                character_id=character_id,
                character_name=character_name,
                region_id=new_region_id,
                region_name=new_region_name,
                entry_location=new_location or HexCoordinate(q=0, r=0, s=0),
                entry_method=movement_method,
                previous_region_id=old_region_id
            )
            
            logger.info(f"Character {character_name} moved from {old_region_name} to {new_region_name}")
            
        except Exception as e:
            logger.error(f"Error moving character {character_name}: {e}")
            raise
    
    async def teleport_character(
        self,
        character_id: UUID,
        character_name: str,
        destination_region_id: UUID,
        destination_region_name: str,
        destination_location: Optional[HexCoordinate] = None,
        source_region_id: Optional[UUID] = None,
        source_region_name: Optional[str] = None,
        source_location: Optional[HexCoordinate] = None
    ) -> None:
        """Teleport a character to a new region"""
        await self.move_character_to_region(
            character_id=character_id,
            character_name=character_name,
            new_region_id=destination_region_id,
            new_region_name=destination_region_name,
            new_location=destination_location,
            old_region_id=source_region_id,
            old_region_name=source_region_name,
            old_location=source_location,
            movement_method="teleport",
            travel_time=0.0
        )
    
    async def track_character_exploration(
        self,
        character_id: UUID,
        character_name: str,
        region_id: UUID,
        region_name: str,
        exploration_increase: float,
        discoveries_made: List[str] = None
    ) -> None:
        """Track character exploration progress in a region"""
        try:
            # This would integrate with the region system to update exploration levels
            # For now, we'll just dispatch an event
            await self.region_event_service.publish_region_explored(
                region_id=region_id,
                region_name=region_name,
                old_exploration_level=0.0,  # Would be fetched from region system
                new_exploration_level=exploration_increase,
                explored_by=character_name,
                discoveries_made=discoveries_made or [],
                exploration_details={
                    "character_id": str(character_id),
                    "exploration_method": "character_movement"
                }
            )
            
            logger.info(f"Character {character_name} explored {region_name} (+{exploration_increase})")
            
        except Exception as e:
            logger.error(f"Error tracking exploration for {character_name}: {e}")
            raise
    
    async def handle_character_discovery(
        self,
        character_id: UUID,
        character_name: str,
        region_id: UUID,
        region_name: str,
        discovery_type: str = "exploration",
        discovery_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle when a character discovers a new region"""
        try:
            await self.region_event_service.publish_region_discovered(
                region_id=region_id,
                region_name=region_name,
                discovered_by=character_name,
                discovery_method=discovery_type,
                previously_known=False,
                discovery_details={
                    "character_id": str(character_id),
                    "discovery_timestamp": datetime.utcnow().isoformat(),
                    **(discovery_details or {})
                }
            )
            
            logger.info(f"Character {character_name} discovered region {region_name}")
            
        except Exception as e:
            logger.error(f"Error handling discovery for {character_name}: {e}")
            raise


# Singleton instance
_character_location_service: Optional[CharacterLocationService] = None


def get_character_location_service() -> CharacterLocationService:
    """Get the singleton character location service instance"""
    global _character_location_service
    if _character_location_service is None:
        _character_location_service = CharacterLocationService()
    return _character_location_service 