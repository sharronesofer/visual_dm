"""
Faction Territory Service

Service for managing faction territorial control and integration with the region system.
Handles faction territory claims, releases, and contests, dispatching appropriate events.
"""

import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from backend.systems.faction.models import FactionEntity
from backend.systems.region.models import RegionMetadata
from backend.systems.region.services.event_service import get_region_event_service

logger = logging.getLogger(__name__)


class FactionTerritoryService:
    """Service for managing faction territorial control and region integration"""
    
    def __init__(self):
        self.region_event_service = get_region_event_service()
        logger.info("FactionTerritoryService initialized")
    
    async def claim_territory(
        self,
        faction_id: UUID,
        faction_name: str,
        region_metadata: RegionMetadata,
        claim_method: str = "conquest",
        control_strength: float = 1.0,
        previous_controller: Optional[UUID] = None,
        claim_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Handle faction claiming territory in a region"""
        try:
            # Dispatch territory claimed event
            await self.region_event_service.publish_territory_claimed(
                region_metadata=region_metadata,
                faction_id=faction_id,
                faction_name=faction_name,
                previous_controller=previous_controller,
                claim_method=claim_method,
                control_strength=control_strength,
                claim_details={
                    "claim_timestamp": datetime.utcnow().isoformat(),
                    "claim_reason": f"Faction {faction_name} claimed territory via {claim_method}",
                    **(claim_details or {})
                }
            )
            
            logger.info(f"Faction {faction_name} claimed territory in {region_metadata.name} via {claim_method}")
            
        except Exception as e:
            logger.error(f"Error claiming territory for faction {faction_name}: {e}")
            raise
    
    async def release_territory(
        self,
        faction_id: UUID,
        faction_name: str,
        region_id: UUID,
        region_name: str,
        release_reason: str = "voluntary",
        new_controller: Optional[UUID] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Handle faction releasing control of territory"""
        try:
            # Dispatch territory released event
            await self.region_event_service.publish_territory_released(
                region_id=region_id,
                region_name=region_name,
                faction_id=faction_id,
                faction_name=faction_name,
                release_reason=release_reason,
                new_controller=new_controller,
                continent_id=continent_id
            )
            
            logger.info(f"Faction {faction_name} released territory in {region_name} due to {release_reason}")
            
        except Exception as e:
            logger.error(f"Error releasing territory for faction {faction_name}: {e}")
            raise
    
    async def contest_territory(
        self,
        region_id: UUID,
        region_name: str,
        contesting_factions: List[UUID],
        current_controller: Optional[UUID] = None,
        contest_type: str = "military",
        contest_details: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Handle territory being contested by multiple factions"""
        try:
            # Dispatch territory contested event
            await self.region_event_service.publish_territory_contested(
                region_id=region_id,
                region_name=region_name,
                contesting_factions=contesting_factions,
                current_controller=current_controller,
                contest_type=contest_type,
                contest_details={
                    "contest_start_timestamp": datetime.utcnow().isoformat(),
                    "number_of_contesting_factions": len(contesting_factions),
                    **(contest_details or {})
                },
                continent_id=continent_id
            )
            
            logger.info(f"Territory {region_name} is being contested by {len(contesting_factions)} factions")
            
        except Exception as e:
            logger.error(f"Error handling territory contest in {region_name}: {e}")
            raise
    
    async def establish_settlement(
        self,
        faction_id: UUID,
        faction_name: str,
        region_id: UUID,
        region_name: str,
        settlement_name: str,
        settlement_type: str = "outpost",
        initial_population: int = 100,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Handle faction establishing a settlement in a region"""
        try:
            # Create a default location for the settlement
            from backend.systems.region.models import HexCoordinate
            settlement_location = HexCoordinate(q=0, r=0, s=0)  # Would be calculated based on region
            
            # Dispatch settlement created event
            await self.region_event_service.publish_settlement_created(
                region_id=region_id,
                region_name=region_name,
                settlement_name=settlement_name,
                settlement_type=settlement_type,
                location=settlement_location,
                initial_population=initial_population,
                founder_faction=faction_id,
                continent_id=continent_id
            )
            
            logger.info(f"Faction {faction_name} established {settlement_type} '{settlement_name}' in {region_name}")
            
        except Exception as e:
            logger.error(f"Error establishing settlement for faction {faction_name}: {e}")
            raise
    
    async def update_population(
        self,
        region_id: UUID,
        region_name: str,
        old_population: int,
        new_population: int,
        change_reason: str = "natural_growth",
        affected_demographics: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Handle population changes in faction-controlled territory"""
        try:
            # Dispatch population changed event
            await self.region_event_service.publish_population_changed(
                region_id=region_id,
                region_name=region_name,
                old_population=old_population,
                new_population=new_population,
                change_reason=change_reason,
                affected_demographics=affected_demographics,
                continent_id=continent_id
            )
            
            population_change = new_population - old_population
            change_direction = "increased" if population_change > 0 else "decreased"
            logger.info(f"Population in {region_name} {change_direction} by {abs(population_change)} due to {change_reason}")
            
        except Exception as e:
            logger.error(f"Error updating population in {region_name}: {e}")
            raise
    
    async def handle_territorial_warfare(
        self,
        attacking_faction_id: UUID,
        attacking_faction_name: str,
        defending_faction_id: UUID,
        defending_faction_name: str,
        region_id: UUID,
        region_name: str,
        battle_outcome: str,  # "attacker_victory", "defender_victory", "stalemate"
        casualties: Optional[Dict[str, int]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Handle warfare between factions over territory"""
        try:
            if battle_outcome == "attacker_victory":
                # Attacker claims territory
                await self.release_territory(
                    faction_id=defending_faction_id,
                    faction_name=defending_faction_name,
                    region_id=region_id,
                    region_name=region_name,
                    release_reason="military_defeat",
                    new_controller=attacking_faction_id,
                    continent_id=continent_id
                )
                
                # Create mock region metadata for the claim
                from backend.systems.region.models import RegionMetadata, RegionProfile, RegionType, BiomeType, ClimateType, DangerLevel, HexCoordinate
                mock_region_metadata = RegionMetadata(
                    id=region_id,
                    name=region_name,
                    continent_id=continent_id,
                    region_type=RegionType.PLAINS,  # Default
                    profile=RegionProfile(
                        dominant_biome=BiomeType.GRASSLAND,
                        climate=ClimateType.TEMPERATE,
                        terrain_features=[]
                    ),
                    danger_level=DangerLevel.LOW,
                    hex_coordinates=[HexCoordinate(q=0, r=0, s=0)],
                    area_square_km=1000.0
                )
                
                await self.claim_territory(
                    faction_id=attacking_faction_id,
                    faction_name=attacking_faction_name,
                    region_metadata=mock_region_metadata,
                    claim_method="military_conquest",
                    previous_controller=defending_faction_id,
                    claim_details={
                        "battle_outcome": battle_outcome,
                        "casualties": casualties or {},
                        "previous_controller": str(defending_faction_id)
                    }
                )
                
            elif battle_outcome == "stalemate":
                # Territory becomes contested
                await self.contest_territory(
                    region_id=region_id,
                    region_name=region_name,
                    contesting_factions=[attacking_faction_id, defending_faction_id],
                    current_controller=defending_faction_id,
                    contest_type="military",
                    contest_details={
                        "battle_outcome": battle_outcome,
                        "casualties": casualties or {},
                        "conflict_type": "territorial_warfare"
                    },
                    continent_id=continent_id
                )
            
            logger.info(f"Territorial warfare in {region_name}: {attacking_faction_name} vs {defending_faction_name} - {battle_outcome}")
            
        except Exception as e:
            logger.error(f"Error handling territorial warfare in {region_name}: {e}")
            raise


# Singleton instance
_faction_territory_service: Optional[FactionTerritoryService] = None


def get_faction_territory_service() -> FactionTerritoryService:
    """Get the singleton faction territory service instance"""
    global _faction_territory_service
    if _faction_territory_service is None:
        _faction_territory_service = FactionTerritoryService()
    return _faction_territory_service 