"""
Faction Integration for World State System

This module provides integration between the world state system and faction system,
allowing world state to track faction-related events and territorial control.
"""

from typing import Optional, List, Dict, Any, Protocol
from uuid import UUID
from datetime import datetime
import logging

from backend.systems.world_state.world_types import StateCategory
from backend.systems.world_state.services.services import WorldStateService

logger = logging.getLogger(__name__)


class FactionServiceProtocol(Protocol):
    """Protocol for faction service integration"""
    
    async def get_faction_by_id(self, faction_id: UUID) -> Optional[Any]:
        """Get faction by ID"""
        ...
    
    async def list_factions(self, **kwargs) -> Any:
        """List factions"""
        ...


class FactionWorldStateIntegration:
    """Integration service for faction and world state systems"""
    
    def __init__(self, 
                 world_state_service: WorldStateService,
                 faction_service: Optional[FactionServiceProtocol] = None):
        self.world_state_service = world_state_service
        self.faction_service = faction_service
    
    # ===== TERRITORIAL CONTROL =====
    
    async def set_region_controller(
        self,
        region_id: str,
        faction_id: Optional[UUID],
        reason: str = "Territorial control change"
    ) -> bool:
        """Set which faction controls a region"""
        try:
            # Validate faction exists if provided
            if faction_id and self.faction_service:
                faction = await self.faction_service.get_faction_by_id(faction_id)
                if not faction:
                    logger.warning(f"Faction {faction_id} not found when setting region control")
                    return False
            
            # Update world state
            controller_key = f"regions.{region_id}.controlling_faction"
            await self.world_state_service.set_state_variable(
                controller_key,
                str(faction_id) if faction_id else None,
                region_id=region_id,
                category=StateCategory.POLITICAL,
                reason=reason
            )
            
            # Record territorial event
            await self.record_territorial_event(
                region_id,
                faction_id,
                "control_change",
                reason
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set region controller: {e}")
            return False
    
    async def get_region_controller(self, region_id: str) -> Optional[UUID]:
        """Get the faction that controls a region"""
        try:
            controller_key = f"regions.{region_id}.controlling_faction"
            controller_str = await self.world_state_service.get_state_variable(
                controller_key,
                region_id=region_id
            )
            
            if controller_str:
                return UUID(controller_str)
            return None
            
        except Exception as e:
            logger.error(f"Failed to get region controller: {e}")
            return None
    
    async def get_faction_territories(self, faction_id: UUID) -> List[str]:
        """Get all regions controlled by a faction"""
        try:
            # Query all regions for this faction
            query_result = await self.world_state_service.query_state(
                category=StateCategory.POLITICAL,
                key_pattern="regions.*.controlling_faction"
            )
            
            territories = []
            faction_str = str(faction_id)
            
            for key, value in query_result.items():
                if value == faction_str:
                    # Extract region_id from key like "regions.region_1.controlling_faction"
                    parts = key.split('.')
                    if len(parts) >= 2:
                        territories.append(parts[1])
            
            return territories
            
        except Exception as e:
            logger.error(f"Failed to get faction territories: {e}")
            return []
    
    # ===== FACTION EVENTS =====
    
    async def record_territorial_event(
        self,
        region_id: str,
        faction_id: Optional[UUID],
        event_type: str,
        description: str
    ) -> str:
        """Record a territorial control event"""
        try:
            event_description = f"Region {region_id}: {description}"
            if faction_id:
                event_description += f" (Faction: {faction_id})"
            
            return await self.world_state_service.record_world_event(
                event_type=f"territorial_{event_type}",
                description=event_description,
                affected_regions=[region_id],
                category=StateCategory.POLITICAL,
                metadata={
                    'region_id': region_id,
                    'faction_id': str(faction_id) if faction_id else None,
                    'event_subtype': event_type
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to record territorial event: {e}")
            return ""
    
    async def record_faction_action(
        self,
        faction_id: UUID,
        action_type: str,
        description: str,
        affected_regions: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Record a faction action in world state"""
        try:
            event_metadata = {
                'faction_id': str(faction_id),
                'action_type': action_type,
                **(metadata or {})
            }
            
            return await self.world_state_service.record_world_event(
                event_type=f"faction_{action_type}",
                description=f"Faction {faction_id}: {description}",
                affected_regions=affected_regions or [],
                category=StateCategory.POLITICAL,
                metadata=event_metadata
            )
            
        except Exception as e:
            logger.error(f"Failed to record faction action: {e}")
            return ""
    
    # ===== FACTION INFLUENCE =====
    
    async def set_faction_influence(
        self,
        region_id: str,
        faction_id: UUID,
        influence_level: float,
        reason: str = "Influence change"
    ) -> bool:
        """Set faction influence level in a region (0.0 to 1.0)"""
        try:
            # Validate influence level
            influence_level = max(0.0, min(1.0, influence_level))
            
            influence_key = f"regions.{region_id}.faction_influence.{faction_id}"
            await self.world_state_service.set_state_variable(
                influence_key,
                influence_level,
                region_id=region_id,
                category=StateCategory.POLITICAL,
                reason=reason
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set faction influence: {e}")
            return False
    
    async def get_faction_influence(
        self,
        region_id: str,
        faction_id: UUID
    ) -> float:
        """Get faction influence level in a region"""
        try:
            influence_key = f"regions.{region_id}.faction_influence.{faction_id}"
            influence = await self.world_state_service.get_state_variable(
                influence_key,
                region_id=region_id,
                default=0.0
            )
            
            return float(influence)
            
        except Exception as e:
            logger.error(f"Failed to get faction influence: {e}")
            return 0.0
    
    async def get_region_faction_influences(self, region_id: str) -> Dict[str, float]:
        """Get all faction influences in a region"""
        try:
            query_result = await self.world_state_service.query_state(
                category=StateCategory.POLITICAL,
                region_id=region_id,
                key_pattern=f"regions.{region_id}.faction_influence.*"
            )
            
            influences = {}
            for key, value in query_result.items():
                # Extract faction_id from key like "regions.region_1.faction_influence.faction_uuid"
                parts = key.split('.')
                if len(parts) >= 4:
                    faction_id = parts[3]
                    influences[faction_id] = float(value)
            
            return influences
            
        except Exception as e:
            logger.error(f"Failed to get region faction influences: {e}")
            return {}
    
    # ===== DIPLOMATIC RELATIONS =====
    
    async def set_diplomatic_relation(
        self,
        faction1_id: UUID,
        faction2_id: UUID,
        relation_type: str,
        relation_value: float,
        reason: str = "Diplomatic change"
    ) -> bool:
        """Set diplomatic relation between two factions"""
        try:
            # Ensure consistent ordering for bilateral relations
            if faction1_id > faction2_id:
                faction1_id, faction2_id = faction2_id, faction1_id
            
            relation_key = f"diplomacy.{faction1_id}.{faction2_id}.{relation_type}"
            await self.world_state_service.set_state_variable(
                relation_key,
                relation_value,
                category=StateCategory.POLITICAL,
                reason=reason
            )
            
            # Record diplomatic event
            await self.record_diplomatic_event(
                faction1_id,
                faction2_id,
                relation_type,
                relation_value,
                reason
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to set diplomatic relation: {e}")
            return False
    
    async def get_diplomatic_relation(
        self,
        faction1_id: UUID,
        faction2_id: UUID,
        relation_type: str
    ) -> Optional[float]:
        """Get diplomatic relation between two factions"""
        try:
            # Ensure consistent ordering
            if faction1_id > faction2_id:
                faction1_id, faction2_id = faction2_id, faction1_id
            
            relation_key = f"diplomacy.{faction1_id}.{faction2_id}.{relation_type}"
            return await self.world_state_service.get_state_variable(relation_key)
            
        except Exception as e:
            logger.error(f"Failed to get diplomatic relation: {e}")
            return None
    
    async def record_diplomatic_event(
        self,
        faction1_id: UUID,
        faction2_id: UUID,
        relation_type: str,
        relation_value: float,
        description: str
    ) -> str:
        """Record a diplomatic event"""
        try:
            event_description = f"Diplomatic {relation_type} between {faction1_id} and {faction2_id}: {description} (value: {relation_value})"
            
            return await self.world_state_service.record_world_event(
                event_type=f"diplomatic_{relation_type}",
                description=event_description,
                category=StateCategory.POLITICAL,
                metadata={
                    'faction1_id': str(faction1_id),
                    'faction2_id': str(faction2_id),
                    'relation_type': relation_type,
                    'relation_value': relation_value
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to record diplomatic event: {e}")
            return ""
    
    # ===== INTEGRATION UTILITIES =====
    
    async def sync_faction_data(self, faction_id: UUID) -> bool:
        """Sync faction data from faction service to world state"""
        try:
            if not self.faction_service:
                logger.warning("No faction service available for sync")
                return False
            
            faction = await self.faction_service.get_faction_by_id(faction_id)
            if not faction:
                logger.warning(f"Faction {faction_id} not found for sync")
                return False
            
            # Store faction metadata in world state
            faction_key = f"factions.{faction_id}"
            faction_data = {
                'name': getattr(faction, 'name', 'Unknown'),
                'status': getattr(faction, 'status', 'active'),
                'last_sync': datetime.utcnow().isoformat()
            }
            
            await self.world_state_service.set_state_variable(
                faction_key,
                faction_data,
                category=StateCategory.POLITICAL,
                reason="Faction data sync"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync faction data: {e}")
            return False
    
    async def get_world_faction_summary(self) -> Dict[str, Any]:
        """Get a summary of all faction-related world state data"""
        try:
            # Get all faction territories
            territories_query = await self.world_state_service.query_state(
                category=StateCategory.POLITICAL,
                key_pattern="regions.*.controlling_faction"
            )
            
            # Get all faction influences
            influences_query = await self.world_state_service.query_state(
                category=StateCategory.POLITICAL,
                key_pattern="regions.*.faction_influence.*"
            )
            
            # Get diplomatic relations
            diplomacy_query = await self.world_state_service.query_state(
                category=StateCategory.POLITICAL,
                key_pattern="diplomacy.*"
            )
            
            return {
                'territorial_control': len(territories_query),
                'influence_relationships': len(influences_query),
                'diplomatic_relations': len(diplomacy_query),
                'last_updated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get world faction summary: {e}")
            return {'error': str(e)}


async def create_faction_world_state_integration(
    world_state_service: WorldStateService,
    faction_service: Optional[FactionServiceProtocol] = None
) -> FactionWorldStateIntegration:
    """Factory function to create faction world state integration"""
    return FactionWorldStateIntegration(world_state_service, faction_service) 