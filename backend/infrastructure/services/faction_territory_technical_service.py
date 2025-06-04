"""
Faction Territory Technical Service - Infrastructure Layer

This service handles all technical concerns for faction territory operations,
including logging, async operations, and external service integrations.
"""

import logging
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

from backend.systems.faction.models import FactionEntity
from backend.systems.region.models import RegionMetadata, HexCoordinate
from backend.systems.region.services.event_service import get_region_event_service


class FactionTerritoryTechnicalService:
    """Technical service for faction territory operations"""
    
    def __init__(self):
        """Initialize technical dependencies"""
        self.logger = logging.getLogger(__name__)
        self.region_event_service = get_region_event_service()
        self.logger.info("FactionTerritoryTechnicalService initialized")

    async def publish_territory_claimed_event(
        self,
        region_metadata: RegionMetadata,
        faction_id: UUID,
        faction_name: str,
        previous_controller: Optional[UUID] = None,
        claim_method: str = "conquest",
        control_strength: float = 1.0,
        claim_details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Technical: Dispatch territory claimed event to region system"""
        try:
            # Prepare event data with technical metadata
            event_details = {
                "claim_timestamp": datetime.utcnow().isoformat(),
                "claim_reason": f"Faction {faction_name} claimed territory via {claim_method}",
                "technical_metadata": {
                    "service_version": "1.0",
                    "event_source": "faction_territory_service"
                },
                **(claim_details or {})
            }
            
            # Dispatch to region event service
            await self.region_event_service.publish_territory_claimed(
                region_metadata=region_metadata,
                faction_id=faction_id,
                faction_name=faction_name,
                previous_controller=previous_controller,
                claim_method=claim_method,
                control_strength=control_strength,
                claim_details=event_details
            )
            
            # Technical logging
            self.logger.info(
                f"Territory claimed event published: faction={faction_name}, "
                f"region={region_metadata.name}, method={claim_method}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to publish territory claimed event: {e}")
            raise

    async def publish_territory_released_event(
        self,
        faction_id: UUID,
        faction_name: str,
        region_id: UUID,
        region_name: str,
        release_reason: str = "voluntary",
        new_controller: Optional[UUID] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Technical: Dispatch territory released event to region system"""
        try:
            # Dispatch to region event service
            await self.region_event_service.publish_territory_released(
                region_id=region_id,
                region_name=region_name,
                faction_id=faction_id,
                faction_name=faction_name,
                release_reason=release_reason,
                new_controller=new_controller,
                continent_id=continent_id
            )
            
            # Technical logging
            self.logger.info(
                f"Territory released event published: faction={faction_name}, "
                f"region={region_name}, reason={release_reason}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to publish territory released event: {e}")
            raise

    async def publish_territory_contested_event(
        self,
        region_id: UUID,
        region_name: str,
        contesting_factions: List[UUID],
        current_controller: Optional[UUID] = None,
        contest_type: str = "military",
        contest_details: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Technical: Dispatch territory contested event to region system"""
        try:
            # Prepare contest details with technical metadata
            enhanced_details = {
                "contest_start_timestamp": datetime.utcnow().isoformat(),
                "number_of_contesting_factions": len(contesting_factions),
                "technical_metadata": {
                    "service_version": "1.0",
                    "event_source": "faction_territory_service"
                },
                **(contest_details or {})
            }
            
            # Dispatch to region event service
            await self.region_event_service.publish_territory_contested(
                region_id=region_id,
                region_name=region_name,
                contesting_factions=contesting_factions,
                current_controller=current_controller,
                contest_type=contest_type,
                contest_details=enhanced_details,
                continent_id=continent_id
            )
            
            # Technical logging
            self.logger.info(
                f"Territory contested event published: region={region_name}, "
                f"contesting_factions={len(contesting_factions)}, type={contest_type}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to publish territory contested event: {e}")
            raise

    async def publish_settlement_created_event(
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
        """Technical: Dispatch settlement created event to region system"""
        try:
            # Create default settlement location (would be calculated from region data)
            settlement_location = HexCoordinate(q=0, r=0, s=0)
            
            # Dispatch to region event service
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
            
            # Technical logging
            self.logger.info(
                f"Settlement created event published: faction={faction_name}, "
                f"settlement={settlement_name}, type={settlement_type}, region={region_name}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to publish settlement created event: {e}")
            raise

    async def publish_population_changed_event(
        self,
        region_id: UUID,
        region_name: str,
        old_population: int,
        new_population: int,
        change_reason: str = "natural_growth",
        affected_demographics: Optional[Dict[str, Any]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Technical: Dispatch population changed event to region system"""
        try:
            # Dispatch to region event service
            await self.region_event_service.publish_population_changed(
                region_id=region_id,
                region_name=region_name,
                old_population=old_population,
                new_population=new_population,
                change_reason=change_reason,
                affected_demographics=affected_demographics,
                continent_id=continent_id
            )
            
            # Technical logging
            population_change = new_population - old_population
            change_direction = "increased" if population_change > 0 else "decreased"
            self.logger.info(
                f"Population changed event published: region={region_name}, "
                f"{change_direction} by {abs(population_change)}, reason={change_reason}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to publish population changed event: {e}")
            raise

    async def publish_territorial_warfare_events(
        self,
        attacking_faction_id: UUID,
        attacking_faction_name: str,
        defending_faction_id: UUID,
        defending_faction_name: str,
        region_id: UUID,
        region_name: str,
        battle_outcome: str,
        casualties: Optional[Dict[str, int]] = None,
        continent_id: Optional[UUID] = None
    ) -> None:
        """Technical: Handle complex territorial warfare event publishing"""
        try:
            # Based on battle outcome, publish appropriate territory change events
            if battle_outcome == "attacker_victory":
                # Attacker wins - they claim the territory
                await self.publish_territory_released_event(
                    faction_id=defending_faction_id,
                    faction_name=defending_faction_name,
                    region_id=region_id,
                    region_name=region_name,
                    release_reason="military_defeat",
                    new_controller=attacking_faction_id,
                    continent_id=continent_id
                )
                
                # Note: Territory claiming would be handled by business logic
                # This service only handles the technical event publishing
                
            elif battle_outcome == "defender_victory":
                # Defender wins - they maintain control, contest ends
                await self.publish_territory_contested_event(
                    region_id=region_id,
                    region_name=region_name,
                    contesting_factions=[],  # Contest resolved
                    current_controller=defending_faction_id,
                    contest_type="military_resolved",
                    contest_details={
                        "resolution": "defender_victory",
                        "defeated_attacker": str(attacking_faction_id),
                        "casualties": casualties or {}
                    },
                    continent_id=continent_id
                )
                
            elif battle_outcome == "stalemate":
                # Stalemate - territory remains contested
                await self.publish_territory_contested_event(
                    region_id=region_id,
                    region_name=region_name,
                    contesting_factions=[attacking_faction_id, defending_faction_id],
                    current_controller=defending_faction_id,
                    contest_type="military_stalemate",
                    contest_details={
                        "resolution": "stalemate",
                        "ongoing_conflict": True,
                        "casualties": casualties or {}
                    },
                    continent_id=continent_id
                )
            
            # Technical logging for warfare
            self.logger.info(
                f"Territorial warfare events published: "
                f"attacker={attacking_faction_name}, defender={defending_faction_name}, "
                f"region={region_name}, outcome={battle_outcome}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to publish territorial warfare events: {e}")
            raise

    def log_territory_operation(
        self,
        operation: str,
        faction_name: str,
        region_name: str,
        details: Optional[Dict[str, Any]] = None,
        level: str = "info"
    ) -> None:
        """Technical: Centralized logging for territory operations"""
        log_message = f"Territory operation: {operation} - faction={faction_name}, region={region_name}"
        
        if details:
            log_message += f", details={details}"
        
        # Route to appropriate log level
        if level == "debug":
            self.logger.debug(log_message)
        elif level == "warning":
            self.logger.warning(log_message)
        elif level == "error":
            self.logger.error(log_message)
        else:
            self.logger.info(log_message)

    def validate_region_metadata(self, region_metadata: RegionMetadata) -> bool:
        """Technical: Validate region metadata structure"""
        try:
            # Basic technical validation
            if not region_metadata.id or not region_metadata.name:
                self.logger.error("Invalid region metadata: missing id or name")
                return False
            
            # Log validation success
            self.logger.debug(f"Region metadata validated: {region_metadata.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Region metadata validation failed: {e}")
            return False

    def get_region_event_service_status(self) -> Dict[str, Any]:
        """Technical: Get status of region event service connection"""
        try:
            # This would check the actual service status
            status = {
                "connected": True,
                "service_type": type(self.region_event_service).__name__,
                "last_check": datetime.utcnow().isoformat()
            }
            
            self.logger.debug("Region event service status checked")
            return status
            
        except Exception as e:
            self.logger.error(f"Failed to check region event service status: {e}")
            return {
                "connected": False,
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }


def get_faction_territory_technical_service() -> FactionTerritoryTechnicalService:
    """Factory function for creating faction territory technical service"""
    return FactionTerritoryTechnicalService() 