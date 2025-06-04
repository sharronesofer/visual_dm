"""
Integration interfaces for connecting the economy system with other game systems.

This module provides abstraction layers for communicating with NPC, faction,
and region systems to enable proper cross-system integration.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID
from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class NPCSystemInterface(ABC):
    """Interface for integrating with the NPC system"""
    
    @abstractmethod
    def get_npc_wealth(self, npc_id: UUID) -> float:
        """Get the current wealth of an NPC"""
        pass
    
    @abstractmethod
    def get_npc_traits(self, npc_id: UUID) -> Dict[str, Any]:
        """Get the personality traits of an NPC"""
        pass
    
    @abstractmethod
    def get_npcs_in_region(self, region_id: str, 
                          trait_filters: Optional[Dict[str, Any]] = None) -> List[UUID]:
        """Get NPCs in a region, optionally filtered by traits"""
        pass
    
    @abstractmethod
    def move_npc_to_region(self, npc_id: UUID, target_region_id: str, 
                          reason: str = "economic_opportunity") -> bool:
        """Move an NPC to a target region"""
        pass
    
    @abstractmethod
    def create_wandering_npc(self, region_id: str, npc_type: str = "merchant") -> UUID:
        """Create a new wandering NPC in a region"""
        pass


class FactionSystemInterface(ABC):
    """Interface for integrating with the faction system"""
    
    @abstractmethod
    def get_faction_wealth(self, faction_id: UUID) -> float:
        """Get the current wealth of a faction"""
        pass
    
    @abstractmethod
    def get_faction_controlled_regions(self, faction_id: UUID) -> List[str]:
        """Get regions controlled by a faction"""
        pass
    
    @abstractmethod
    def get_faction_relations(self, faction_id: UUID) -> Dict[UUID, str]:
        """Get faction relationships (allied, neutral, hostile)"""
        pass


class RegionSystemInterface(ABC):
    """Interface for integrating with the region system"""
    
    @abstractmethod
    def get_region_population(self, region_id: str) -> int:
        """Get the population of a region"""
        pass
    
    @abstractmethod
    def get_nearby_regions(self, region_id: str, max_distance: int = 2) -> List[str]:
        """Get regions within a certain distance"""
        pass
    
    @abstractmethod
    def calculate_travel_time(self, from_region: str, to_region: str) -> int:
        """Calculate travel time in days between regions"""
        pass


class DefaultNPCSystemInterface(NPCSystemInterface):
    """Default implementation of NPC system interface with fallback behavior"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_npc_wealth(self, npc_id: UUID) -> float:
        """Get NPC wealth with fallback to random values"""
        try:
            # Try to query actual NPC system if available
            # For now, use placeholder logic
            import random
            # Generate consistent "wealth" based on NPC ID
            random.seed(str(npc_id))
            return random.uniform(100, 10000)
        except Exception as e:
            logger.warning(f"Could not get NPC wealth for {npc_id}, using fallback: {e}")
            return 1000.0  # Default moderate wealth
    
    def get_npc_traits(self, npc_id: UUID) -> Dict[str, Any]:
        """Get NPC traits with fallback values"""
        try:
            # Try to query actual NPC system if available
            # For now, use placeholder logic
            import random
            random.seed(str(npc_id))
            return {
                "wanderlust": random.uniform(0.1, 0.9),
                "entrepreneurial": random.uniform(0.1, 0.9),
                "risk_tolerance": random.uniform(0.1, 0.9),
                "wealth_seeking": random.uniform(0.1, 0.9)
            }
        except Exception as e:
            logger.warning(f"Could not get NPC traits for {npc_id}, using fallback: {e}")
            return {
                "wanderlust": 0.5,
                "entrepreneurial": 0.5,
                "risk_tolerance": 0.5,
                "wealth_seeking": 0.5
            }
    
    def get_npcs_in_region(self, region_id: str, 
                          trait_filters: Optional[Dict[str, Any]] = None) -> List[UUID]:
        """Get NPCs in region with fallback generation"""
        try:
            # Try to query actual NPC system if available
            # For now, generate placeholder NPCs
            import random
            random.seed(region_id)
            num_npcs = random.randint(5, 15)
            npcs = []
            
            for i in range(num_npcs):
                # Generate consistent UUIDs based on region and index
                npc_uuid_str = f"{region_id}-npc-{i:03d}-12345678"
                npc_id = UUID(bytes=npc_uuid_str[:32].encode()[:16].ljust(16, b'0'))
                
                # Apply trait filters if provided
                if trait_filters:
                    traits = self.get_npc_traits(npc_id)
                    meets_criteria = True
                    
                    for trait, min_value in trait_filters.items():
                        if traits.get(trait, 0) < min_value:
                            meets_criteria = False
                            break
                    
                    if meets_criteria:
                        npcs.append(npc_id)
                else:
                    npcs.append(npc_id)
            
            return npcs
        except Exception as e:
            logger.warning(f"Could not get NPCs in region {region_id}, using fallback: {e}")
            return []
    
    def move_npc_to_region(self, npc_id: UUID, target_region_id: str, 
                          reason: str = "economic_opportunity") -> bool:
        """Move NPC with logging (actual movement would be implemented by NPC system)"""
        try:
            # This would integrate with actual NPC mobility system
            logger.info(f"Moving NPC {npc_id} to region {target_region_id} for {reason}")
            # Return True as if successful for now
            return True
        except Exception as e:
            logger.warning(f"Could not move NPC {npc_id} to region {target_region_id}: {e}")
            return False
    
    def create_wandering_npc(self, region_id: str, npc_type: str = "merchant") -> UUID:
        """Create wandering NPC with placeholder implementation"""
        try:
            # This would integrate with actual NPC creation system
            import random
            # Generate a new UUID for the created NPC
            creation_seed = f"{region_id}-{npc_type}-{random.randint(1000, 9999)}"
            npc_id = UUID(bytes=creation_seed[:32].encode()[:16].ljust(16, b'0'))
            
            logger.info(f"Created wandering {npc_type} NPC {npc_id} in region {region_id}")
            return npc_id
        except Exception as e:
            logger.warning(f"Could not create wandering NPC in region {region_id}: {e}")
            # Return a fallback UUID
            return UUID('00000000-0000-0000-0000-000000000000')


class DefaultFactionSystemInterface(FactionSystemInterface):
    """Default implementation of faction system interface"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_faction_wealth(self, faction_id: UUID) -> float:
        """Get faction wealth with fallback"""
        try:
            # Query actual faction system if available
            import random
            random.seed(str(faction_id))
            return random.uniform(10000, 100000)
        except Exception as e:
            logger.warning(f"Could not get faction wealth for {faction_id}: {e}")
            return 50000.0
    
    def get_faction_controlled_regions(self, faction_id: UUID) -> List[str]:
        """Get faction controlled regions with fallback"""
        try:
            # Query actual faction system if available
            return []  # Placeholder
        except Exception as e:
            logger.warning(f"Could not get faction controlled regions for {faction_id}: {e}")
            return []
    
    def get_faction_relations(self, faction_id: UUID) -> Dict[UUID, str]:
        """Get faction relations with fallback"""
        try:
            # Query actual faction system if available
            return {}  # Placeholder
        except Exception as e:
            logger.warning(f"Could not get faction relations for {faction_id}: {e}")
            return {}


class DefaultRegionSystemInterface(RegionSystemInterface):
    """Default implementation of region system interface"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def get_region_population(self, region_id: str) -> int:
        """Get region population with fallback"""
        try:
            # Query actual region system if available
            import random
            random.seed(region_id)
            return random.randint(500, 5000)
        except Exception as e:
            logger.warning(f"Could not get region population for {region_id}: {e}")
            return 1000
    
    def get_nearby_regions(self, region_id: str, max_distance: int = 2) -> List[str]:
        """Get nearby regions with fallback"""
        try:
            # Query actual region system if available
            # For now, generate some placeholder nearby regions
            import random
            random.seed(region_id)
            nearby = []
            for i in range(random.randint(1, 4)):
                nearby_id = f"{region_id}-nearby-{i}"
                nearby.append(nearby_id)
            return nearby
        except Exception as e:
            logger.warning(f"Could not get nearby regions for {region_id}: {e}")
            return []
    
    def calculate_travel_time(self, from_region: str, to_region: str) -> int:
        """Calculate travel time with fallback"""
        try:
            # Use actual region system pathfinding if available
            import random
            combined_seed = f"{from_region}-{to_region}"
            random.seed(combined_seed)
            return random.randint(1, 7)  # 1-7 days travel time
        except Exception as e:
            logger.warning(f"Could not calculate travel time from {from_region} to {to_region}: {e}")
            return 3  # Default 3 days


class SystemIntegrationManager:
    """Manages integration with all game systems"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.npc_interface = DefaultNPCSystemInterface(db_session)
        self.faction_interface = DefaultFactionSystemInterface(db_session)
        self.region_interface = DefaultRegionSystemInterface(db_session)
    
    def set_npc_interface(self, interface: NPCSystemInterface):
        """Set a custom NPC system interface"""
        self.npc_interface = interface
    
    def set_faction_interface(self, interface: FactionSystemInterface):
        """Set a custom faction system interface"""
        self.faction_interface = interface
    
    def set_region_interface(self, interface: RegionSystemInterface):
        """Set a custom region system interface"""
        self.region_interface = interface


# Global instance for easy access
_integration_manager: Optional[SystemIntegrationManager] = None


def get_integration_manager(db_session: Session) -> SystemIntegrationManager:
    """Get or create the global integration manager"""
    global _integration_manager
    if _integration_manager is None:
        _integration_manager = SystemIntegrationManager(db_session)
    return _integration_manager


def set_integration_manager(manager: SystemIntegrationManager):
    """Set a custom integration manager"""
    global _integration_manager
    _integration_manager = manager 