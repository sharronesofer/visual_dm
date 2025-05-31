"""
Region Event Service

Service for dispatching region events to other systems. Provides a centralized
way to publish region-related events to the global event bus for cross-system
communication.
"""

import logging
from typing import Optional, Dict, Any, List
from uuid import UUID

# Temporary mock EventDispatcher to avoid circular imports
class MockEventDispatcher:
    """Mock event dispatcher for testing"""
    
    @classmethod
    def get_instance(cls):
        return cls()
    
    async def publish(self, event):
        """Mock publish method"""
        logger.info(f"Mock publishing event: {event.event_type}")

from backend.systems.region.events.region_events import (
    RegionCreatedEvent, RegionUpdatedEvent, RegionDeletedEvent,
    TerritoryClaimedEvent, TerritoryReleasedEvent, TerritoryContestedEvent,
    PopulationChangedEvent, SettlementCreatedEvent, SettlementDestroyedEvent,
    RegionDiscoveredEvent, RegionExploredEvent,
    ResourceDiscoveredEvent, ResourceDepletedEvent, ResourceExtractedEvent,
    POICreatedEvent, POIUpdatedEvent, POIDiscoveredEvent,
    BiomeChangedEvent, ClimateChangedEvent, DangerLevelChangedEvent,
    ContinentGeneratedEvent, WorldGeneratedEvent,
    CharacterLocationChangedEvent, CharacterEnteredRegionEvent, CharacterLeftRegionEvent,
    QuestLocationValidatedEvent, QuestRegionCompletedEvent,
    create_region_created_event, create_territory_claimed_event, create_character_location_event
)
from backend.systems.region.models import (
    RegionMetadata, ContinentMetadata, HexCoordinate, RegionType, BiomeType, 
    ClimateType, DangerLevel
)

logger = logging.getLogger(__name__)


class RegionEventService:
    """Service for publishing region events to the global event system"""
    
    def __init__(self):
        # Use mock dispatcher for now to avoid circular imports
        self.dispatcher = MockEventDispatcher.get_instance()
        logger.info("RegionEventService initialized with mock dispatcher")
    
    # ============================================================================
    # CORE CRUD EVENT METHODS
    # ============================================================================
    
    async def publish_region_created(
        self,
        region_metadata: RegionMetadata,
        created_by: Optional[str] = None
    ) -> None:
        """Publish a region created event"""
        try:
            event = create_region_created_event(region_metadata, created_by)
            await self.dispatcher.publish(event)
            logger.info(f"Published region created event for region {region_metadata.name}")
        except Exception as e:
            logger.error(f"Error publishing region created event: {e}")
    
    async def publish_region_updated(
        self,
        region_id: UUID,
        region_name: str,
        changed_fields: Dict[str, Any],
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        continent_id: Optional[UUID] = None,
        updated_by: Optional[str] = None
    ) -> None:
        """Publish a region updated event"""
        try:
            event = RegionUpdatedEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                changed_fields=changed_fields,
                old_values=old_values,
                new_values=new_values,
                updated_by=updated_by
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published region updated event for region {region_name}")
        except Exception as e:
            logger.error(f"Error publishing region updated event: {e}")
    
    async def publish_region_deleted(
        self,
        region_id: UUID,
        region_name: str,
        continent_id: Optional[UUID] = None,
        deleted_by: Optional[str] = None,
        backup_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish a region deleted event"""
        try:
            event = RegionDeletedEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                deleted_by=deleted_by,
                backup_data=backup_data
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published region deleted event for region {region_name}")
        except Exception as e:
            logger.error(f"Error publishing region deleted event: {e}")
    
    # ============================================================================
    # TERRITORY CONTROL EVENT METHODS
    # ============================================================================
    
    async def publish_territory_claimed(
        self,
        region_metadata: RegionMetadata,
        faction_id: UUID,
        faction_name: str,
        previous_controller: Optional[UUID] = None,
        claim_method: str = "conquest",
        control_strength: float = 1.0,
        claim_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Publish a territory claimed event"""
        try:
            event = TerritoryClaimedEvent(
                region_id=region_metadata.id,
                region_name=region_metadata.name,
                continent_id=region_metadata.continent_id,
                faction_id=faction_id,
                faction_name=faction_name,
                previous_controller=previous_controller,
                control_strength=control_strength,
                claim_method=claim_method,
                claim_details=claim_details
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published territory claimed event: {faction_name} claimed {region_metadata.name}")
        except Exception as e:
            logger.error(f"Error publishing territory claimed event: {e}")
    
    async def publish_territory_released(
        self,
        region_id: UUID,
        region_name: str,
        faction_id: UUID,
        faction_name: str,
        release_reason: str = "voluntary",
        new_controller: Optional[UUID] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a territory released event"""
        try:
            event = TerritoryReleasedEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                faction_id=faction_id,
                faction_name=faction_name,
                release_reason=release_reason,
                new_controller=new_controller
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published territory released event: {faction_name} released {region_name}")
        except Exception as e:
            logger.error(f"Error publishing territory released event: {e}")
    
    async def publish_territory_contested(
        self,
        region_id: UUID,
        region_name: str,
        contesting_factions: List[UUID],
        current_controller: Optional[UUID] = None,
        contest_type: str = "military",
        contest_details: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a territory contested event"""
        try:
            event = TerritoryContestedEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                contesting_factions=contesting_factions,
                current_controller=current_controller,
                contest_type=contest_type,
                contest_details=contest_details
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published territory contested event for region {region_name}")
        except Exception as e:
            logger.error(f"Error publishing territory contested event: {e}")
    
    # ============================================================================
    # POPULATION EVENT METHODS
    # ============================================================================
    
    async def publish_population_changed(
        self,
        region_id: UUID,
        region_name: str,
        old_population: int,
        new_population: int,
        change_reason: str = "natural",
        affected_demographics: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a population changed event"""
        try:
            event = PopulationChangedEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                old_population=old_population,
                new_population=new_population,
                change_reason=change_reason,
                affected_demographics=affected_demographics
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published population changed event for {region_name}: {old_population} -> {new_population}")
        except Exception as e:
            logger.error(f"Error publishing population changed event: {e}")
    
    async def publish_settlement_created(
        self,
        region_id: UUID,
        region_name: str,
        settlement_name: str,
        settlement_type: str,
        location: HexCoordinate,
        initial_population: int = 0,
        founder_faction: Optional[UUID] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a settlement created event"""
        try:
            event = SettlementCreatedEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                settlement_name=settlement_name,
                settlement_type=settlement_type,
                location=location,
                initial_population=initial_population,
                founder_faction=founder_faction
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published settlement created event: {settlement_name} in {region_name}")
        except Exception as e:
            logger.error(f"Error publishing settlement created event: {e}")
    
    # ============================================================================
    # EXPLORATION EVENT METHODS
    # ============================================================================
    
    async def publish_region_discovered(
        self,
        region_id: UUID,
        region_name: str,
        discovered_by: Optional[str] = None,
        discovery_method: str = "exploration",
        previously_known: bool = False,
        discovery_details: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a region discovered event"""
        try:
            event = RegionDiscoveredEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                discovered_by=discovered_by,
                discovery_method=discovery_method,
                previously_known=previously_known,
                discovery_details=discovery_details
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published region discovered event: {region_name} discovered by {discovered_by}")
        except Exception as e:
            logger.error(f"Error publishing region discovered event: {e}")
    
    async def publish_region_explored(
        self,
        region_id: UUID,
        region_name: str,
        old_exploration_level: float,
        new_exploration_level: float,
        explored_by: Optional[str] = None,
        discoveries_made: List[str] = None,
        exploration_details: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a region explored event"""
        try:
            event = RegionExploredEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                old_exploration_level=old_exploration_level,
                new_exploration_level=new_exploration_level,
                explored_by=explored_by,
                discoveries_made=discoveries_made or [],
                exploration_details=exploration_details
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published region explored event: {region_name} exploration {old_exploration_level} -> {new_exploration_level}")
        except Exception as e:
            logger.error(f"Error publishing region explored event: {e}")
    
    # ============================================================================
    # RESOURCE EVENT METHODS
    # ============================================================================
    
    async def publish_resource_discovered(
        self,
        region_id: UUID,
        region_name: str,
        resource_type: str,
        location: HexCoordinate,
        abundance: float,
        quality: float,
        discovered_by: Optional[str] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a resource discovered event"""
        try:
            event = ResourceDiscoveredEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                resource_type=resource_type,
                location=location,
                abundance=abundance,
                quality=quality,
                discovered_by=discovered_by
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published resource discovered event: {resource_type} in {region_name}")
        except Exception as e:
            logger.error(f"Error publishing resource discovered event: {e}")
    
    # ============================================================================
    # CHARACTER LOCATION EVENT METHODS
    # ============================================================================
    
    async def publish_character_location_changed(
        self,
        character_id: UUID,
        character_name: str,
        old_region_id: Optional[UUID],
        new_region_id: Optional[UUID],
        old_location: Optional[HexCoordinate] = None,
        new_location: Optional[HexCoordinate] = None,
        movement_method: str = "walking",
        travel_time: Optional[float] = None
    ) -> None:
        """Publish a character location changed event"""
        try:
            event = create_character_location_event(
                character_id=character_id,
                character_name=character_name,
                old_region_id=old_region_id,
                new_region_id=new_region_id,
                old_location=old_location,
                new_location=new_location,
                movement_method=movement_method
            )
            event.travel_time = travel_time
            await self.dispatcher.publish(event)
            logger.info(f"Published character location changed event: {character_name} moved from {old_region_id} to {new_region_id}")
        except Exception as e:
            logger.error(f"Error publishing character location changed event: {e}")
    
    async def publish_character_entered_region(
        self,
        character_id: UUID,
        character_name: str,
        region_id: UUID,
        region_name: str,
        entry_location: HexCoordinate,
        entry_method: str = "walking",
        previous_region_id: Optional[UUID] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a character entered region event"""
        try:
            event = CharacterEnteredRegionEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                character_id=character_id,
                character_name=character_name,
                entry_location=entry_location,
                entry_method=entry_method,
                previous_region_id=previous_region_id
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published character entered region event: {character_name} entered {region_name}")
        except Exception as e:
            logger.error(f"Error publishing character entered region event: {e}")
    
    async def publish_character_left_region(
        self,
        character_id: UUID,
        character_name: str,
        region_id: UUID,
        region_name: str,
        exit_location: HexCoordinate,
        exit_method: str = "walking",
        destination_region_id: Optional[UUID] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a character left region event"""
        try:
            event = CharacterLeftRegionEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                character_id=character_id,
                character_name=character_name,
                exit_location=exit_location,
                exit_method=exit_method,
                destination_region_id=destination_region_id
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published character left region event: {character_name} left {region_name}")
        except Exception as e:
            logger.error(f"Error publishing character left region event: {e}")
    
    # ============================================================================
    # QUEST INTEGRATION EVENT METHODS
    # ============================================================================
    
    async def publish_quest_location_validated(
        self,
        region_id: UUID,
        region_name: str,
        quest_id: UUID,
        quest_name: str,
        location: HexCoordinate,
        validation_status: str = "valid",
        validation_details: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a quest location validated event"""
        try:
            event = QuestLocationValidatedEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                quest_id=quest_id,
                quest_name=quest_name,
                location=location,
                validation_status=validation_status,
                validation_details=validation_details
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published quest location validated event: {quest_name} in {region_name} - {validation_status}")
        except Exception as e:
            logger.error(f"Error publishing quest location validated event: {e}")
    
    # ============================================================================
    # WORLD GENERATION EVENT METHODS
    # ============================================================================
    
    async def publish_continent_generated(
        self,
        continent_metadata: ContinentMetadata,
        region_count: int,
        generated_by: Optional[str] = None
    ) -> None:
        """Publish a continent generated event"""
        try:
            event = ContinentGeneratedEvent(
                continent_id=continent_metadata.id,
                continent_name=continent_metadata.name,
                region_count=region_count,
                total_area_square_km=continent_metadata.total_area_square_km,
                generation_seed=continent_metadata.generation_seed,
                generation_parameters=continent_metadata.generation_parameters,
                generated_by=generated_by
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published continent generated event: {continent_metadata.name} with {region_count} regions")
        except Exception as e:
            logger.error(f"Error publishing continent generated event: {e}")
    
    async def publish_world_generated(
        self,
        continent_count: int,
        total_region_count: int,
        total_area_square_km: float,
        generation_seed: Optional[int] = None,
        generation_time_seconds: Optional[float] = None,
        generation_statistics: Optional[Dict[str, Any]] = None,
        generated_by: Optional[str] = None
    ) -> None:
        """Publish a world generated event"""
        try:
            event = WorldGeneratedEvent(
                continent_count=continent_count,
                total_region_count=total_region_count,
                total_area_square_km=total_area_square_km,
                generation_seed=generation_seed,
                generation_time_seconds=generation_time_seconds,
                generation_statistics=generation_statistics,
                generated_by=generated_by
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published world generated event: {continent_count} continents, {total_region_count} regions")
        except Exception as e:
            logger.error(f"Error publishing world generated event: {e}")
    
    # ============================================================================
    # ENVIRONMENTAL EVENT METHODS
    # ============================================================================
    
    async def publish_biome_changed(
        self,
        region_id: UUID,
        region_name: str,
        old_biome: BiomeType,
        new_biome: BiomeType,
        change_cause: str = "natural",
        change_speed: str = "gradual",
        affected_area_percent: float = 100.0,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a biome changed event"""
        try:
            event = BiomeChangedEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                old_biome=old_biome,
                new_biome=new_biome,
                change_cause=change_cause,
                change_speed=change_speed,
                affected_area_percent=affected_area_percent
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published biome changed event: {region_name} changed from {old_biome.value} to {new_biome.value}")
        except Exception as e:
            logger.error(f"Error publishing biome changed event: {e}")
    
    async def publish_danger_level_changed(
        self,
        region_id: UUID,
        region_name: str,
        old_danger_level: DangerLevel,
        new_danger_level: DangerLevel,
        change_cause: str = "unknown",
        threat_details: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Publish a danger level changed event"""
        try:
            event = DangerLevelChangedEvent(
                region_id=region_id,
                region_name=region_name,
                continent_id=continent_id,
                old_danger_level=old_danger_level,
                new_danger_level=new_danger_level,
                change_cause=change_cause,
                threat_details=threat_details
            )
            await self.dispatcher.publish(event)
            logger.info(f"Published danger level changed event: {region_name} danger {old_danger_level.value} -> {new_danger_level.value}")
        except Exception as e:
            logger.error(f"Error publishing danger level changed event: {e}")


# Singleton instance
_region_event_service: Optional[RegionEventService] = None


def get_region_event_service() -> RegionEventService:
    """Get the singleton region event service instance"""
    global _region_event_service
    if _region_event_service is None:
        _region_event_service = RegionEventService()
    return _region_event_service 