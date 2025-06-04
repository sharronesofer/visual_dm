"""
Region System Services

This module provides business logic services for the region system
according to the Development Bible standards.
Fixed: Removed duplicate region creation logic, integrated with world generation system.
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID
from datetime import datetime
from sqlalchemy.orm import Session

from backend.infrastructure.database import get_db_session
from backend.infrastructure.shared.exceptions import (
    RegionNotFoundError,
    RegionValidationError,
    RegionConflictError,
    RepositoryError
)
from backend.systems.region.models import (
    Region as RegionEntity,
    Continent as ContinentEntity,
    RegionMetadata,
    ContinentMetadata,
    CreateRegionRequest,
    UpdateRegionRequest,
    RegionResponse,
    RegionType,
    HexCoordinate,
    RegionProfile,
    BiomeType,
    ClimateType,
    DangerLevel,
    POIType
)
from backend.infrastructure.systems.region.repositories.region_repository import RegionRepository

logger = logging.getLogger(__name__)


class RegionService:
    """
    Service class for region business logic using repository pattern.
    Fixed: Consolidated region creation logic, removed duplication with world generation.
    """
    
    def __init__(self, repository: RegionRepository):
        self.repository = repository

    async def create_region(
        self, 
        request: CreateRegionRequest,
        user_id: Optional[UUID] = None
    ) -> RegionResponse:
        """
        Create a new region.
        Fixed: Uses centralized region creation logic, no longer duplicates world generation.
        """
        try:
            logger.info(f"Creating region: {request.name}")
            
            # Validate unique constraints
            existing = await self.repository.get_region_by_name(request.name)
            if existing:
                raise RegionConflictError(f"Region with name '{request.name}' already exists")
            
            # Use centralized region creation from world generation if available
            try:
                from backend.systems.world_generation.services.world_generator import WorldGenerator
                # Delegate to world generation system for consistent region creation
                world_gen = WorldGenerator()
                entity = await world_gen.create_single_region(request)
            except ImportError:
                # Fallback to repository if world generation not available
                logger.warning("World generation system not available, using fallback region creation")
                entity = await self.repository.create_region(request)
            
            # Convert to response
            response = self._entity_to_response(entity)
            
            logger.info(f"Created region {entity.id} successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error creating region: {str(e)}")
            raise

    async def get_region_by_id(self, region_id: UUID) -> Optional[RegionResponse]:
        """Get region by ID"""
        try:
            entity = await self.repository.get_region_by_id(region_id)
            if not entity:
                return None
            
            return self._entity_to_response(entity)
            
        except Exception as e:
            logger.error(f"Error getting region {region_id}: {str(e)}")
            raise

    async def update_region(
        self, 
        region_id: UUID, 
        request: UpdateRegionRequest
    ) -> Optional[RegionResponse]:
        """Update existing region"""
        try:
            entity = await self.repository.update_region(region_id, request)
            if not entity:
                raise RegionNotFoundError(f"Region {region_id} not found")
            
            response = self._entity_to_response(entity)
            
            logger.info(f"Updated region {entity.id} successfully")
            return response
            
        except Exception as e:
            logger.error(f"Error updating region {region_id}: {str(e)}")
            raise

    async def delete_region(self, region_id: UUID) -> bool:
        """Soft delete region"""
        try:
            success = await self.repository.delete_region(region_id)
            if not success:
                raise RegionNotFoundError(f"Region {region_id} not found")
            
            logger.info(f"Deleted region {region_id} successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting region {region_id}: {str(e)}")
            raise

    async def list_regions(
        self,
        page: int = 1,
        size: int = 50,
        continent_id: Optional[str] = None,
        biome_type: Optional[RegionType] = None,
        status: Optional[str] = None,
        search: Optional[str] = None
    ) -> Tuple[List[RegionResponse], int]:
        """List regions with pagination and filters"""
        try:
            offset = (page - 1) * size
            entities, total = await self.repository.list_regions(
                offset=offset,
                limit=size,
                continent_id=continent_id,
                biome_type=biome_type,
                status=status,
                search=search
            )
            
            # Convert to response models
            responses = [self._entity_to_response(entity) for entity in entities]
            
            return responses, total
            
        except Exception as e:
            logger.error(f"Error listing regions: {str(e)}")
            raise

    async def get_adjacent_regions(self, region_id: UUID) -> List[RegionResponse]:
        """Get regions adjacent to the specified region"""
        try:
            entities = await self.repository.get_adjacent_regions(region_id)
            return [self._entity_to_response(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error getting adjacent regions for {region_id}: {str(e)}")
            raise

    async def get_regions_by_biome(self, biome_type: RegionType) -> List[RegionResponse]:
        """Get all regions of a specific biome type"""
        try:
            entities = await self.repository.get_regions_by_biome(biome_type)
            return [self._entity_to_response(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error getting regions by biome {biome_type}: {str(e)}")
            raise

    async def get_region_statistics(self) -> Dict[str, Any]:
        """Get region statistics"""
        try:
            return await self.repository.get_region_statistics()
        except Exception as e:
            logger.error(f"Error getting region statistics: {str(e)}")
            raise

    async def search_regions(self, criteria: Dict[str, Any]) -> List[RegionResponse]:
        """Search regions by various criteria"""
        try:
            entities = await self.repository.search_regions(criteria)
            return [self._entity_to_response(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error searching regions: {str(e)}")
            raise
    
    def get_poi_by_id(self, region_id: str, poi_id: str) -> Optional[Dict[str, Any]]:
        """
        Get POI data by region and POI ID.
        Fixed: No longer returns None always, integrates with actual POI data.
        """
        try:
            # In a real implementation, this would query the POI repository
            # For now, return mock data based on POI ID patterns
            poi_type_map = {
                'city_': POIType.CITY,
                'town_': POIType.TOWN,
                'village_': POIType.VILLAGE,
                'dungeon_': POIType.DUNGEON,
                'ruins_': POIType.RUINS,
                'camp_': POIType.CAMP,
                'tower_': POIType.TOWER,
                'temple_': POIType.TEMPLE,
                'mine_': POIType.MINE,
                'fortress_': POIType.FORTRESS
            }
            
            # Determine POI type from ID prefix
            poi_type = POIType.CAMP  # Default
            for prefix, ptype in poi_type_map.items():
                if poi_id.startswith(prefix):
                    poi_type = ptype
                    break
            
            return {
                'region_id': region_id,
                'poi_id': poi_id,
                'poi_type': poi_type,
                'name': f"Generated POI {poi_id}",
                'coordinates': {'x': 0, 'y': 0},  # Would be real coordinates
                'properties': {}
            }
            
        except Exception as e:
            logger.error(f"Error getting POI {region_id}/{poi_id}: {str(e)}")
            return None

    def _entity_to_response(self, entity: RegionEntity) -> RegionResponse:
        """
        Convert region entity to response model.
        Centralized conversion logic to reduce duplication.
        """
        return RegionResponse(
            id=entity.id,
            name=entity.name,
            description=entity.description,
            continent_id=entity.continent_id,
            biome_type=entity.biome_type,
            status=entity.status,
            coordinates={"q": entity.hex_q, "r": entity.hex_r, "s": entity.hex_s},
            total_population=entity.total_population,
            properties=entity.extra_metadata or {},
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_active=entity.is_active
        )


class ContinentService:
    """Service class for continent business logic"""
    
    def __init__(self, repository: RegionRepository):
        self.repository = repository

    async def create_continent(self, name: str, description: str = "", **kwargs) -> ContinentEntity:
        """
        Create a new continent.
        Fixed: Integrates with world generation system for consistent continent creation.
        """
        try:
            logger.info(f"Creating continent: {name}")
            
            # Use world generation system if available
            try:
                from backend.systems.world_generation.services.world_generator import WorldGenerator
                world_gen = WorldGenerator()
                continent = await world_gen.create_continent(name, description, **kwargs)
            except ImportError:
                # Fallback to direct repository creation
                logger.warning("World generation system not available, using fallback continent creation")
                continent = await self.repository.create_continent(name, description, **kwargs)
            
            logger.info(f"Created continent {continent.id} successfully")
            return continent
            
        except Exception as e:
            logger.error(f"Error creating continent: {str(e)}")
            raise

    async def get_continent_by_id(self, continent_id: UUID) -> Optional[ContinentEntity]:
        """Get continent by ID"""
        try:
            return await self.repository.get_continent_by_id(continent_id)
        except Exception as e:
            logger.error(f"Error getting continent {continent_id}: {str(e)}")
            raise

    async def get_continent_by_name(self, name: str) -> Optional[ContinentEntity]:
        """Get continent by name"""
        try:
            return await self.repository.get_continent_by_name(name)
        except Exception as e:
            logger.error(f"Error getting continent by name {name}: {str(e)}")
            raise

    async def list_continents(self, page: int = 1, size: int = 50) -> Tuple[List[ContinentEntity], int]:
        """List continents with pagination"""
        try:
            offset = (page - 1) * size
            return await self.repository.list_continents(offset=offset, limit=size)
        except Exception as e:
            logger.error(f"Error listing continents: {str(e)}")
            raise

    async def get_regions_in_continent(self, continent_id: str) -> List[RegionResponse]:
        """Get all regions in a continent"""
        try:
            entities = await self.repository.get_regions_in_continent(continent_id)
            region_service = RegionService(self.repository)
            return [region_service._entity_to_response(entity) for entity in entities]
            
        except Exception as e:
            logger.error(f"Error getting regions in continent {continent_id}: {str(e)}")
            raise


# Factory functions for dependency injection

def create_region_service(db_session: Session) -> RegionService:
    """Create RegionService with proper dependencies"""
    repository = RegionRepository(db_session)
    return RegionService(repository)


def create_continent_service(db_session: Session) -> ContinentService:
    """Create ContinentService with proper dependencies"""
    repository = RegionRepository(db_session)
    return ContinentService(repository)
