"""
Service for continent creation and management.

This module provides business logic for continent-related operations.
"""
import random
from typing import Optional, List, Dict, Any
from uuid import uuid4
from datetime import datetime

from backend.systems.world_generation.models import (
    ContinentSchema, ContinentBoundarySchema, CoordinateSchema, ContinentCreationRequestSchema
)
from backend.systems.world_generation.continent_repository import continent_repository, ContinentRepository
from backend.systems.world_generation.world_generation_utils import (
    generate_continent_region_coordinates,
    get_continent_boundary,
    CONTINENT_MIN_REGIONS,
    CONTINENT_MAX_REGIONS
)

# Import RegionService - this will need to be resolved in your actual codebase
# This is an example of integration with the region system
try:
    from backend.systems.region.services.region_service import region_service, RegionService
    from backend.systems.region.schemas.region import RegionCreationSchema
except ImportError:
    # Fallback for testing or if region system isn't available
    class RegionService:
        def create_new_region(self, region_data, continent_id=None):
            return type('obj', (object,), {'region_id': str(uuid4())})
        
    class RegionCreationSchema:
        def __init__(self, coordinates=None, biome=None):
            self.coordinates = coordinates
            self.biome = biome
            
    region_service = RegionService()

class ContinentService:
    """
    Service for continent creation and management.
    """
    def __init__(self, repository: ContinentRepository, region_svc: RegionService):
        self.repository = repository
        self.region_service = region_svc

    def create_new_continent(self, creation_request: ContinentCreationRequestSchema) -> ContinentSchema:
        """
        Creates a new continent with procedurally generated regions.
        
        Args:
            creation_request: The continent creation request
            
        Returns:
            The created continent with generated regions
        """
        continent_id = str(uuid4())
        seed = creation_request.seed if creation_request.seed else str(random.getrandbits(64))
        random.seed(seed)  # Seed for deterministic generation if seed is provided

        num_regions_target = creation_request.num_regions_target
        if not (CONTINENT_MIN_REGIONS <= num_regions_target <= CONTINENT_MAX_REGIONS):
            num_regions_target = random.randint(CONTINENT_MIN_REGIONS, CONTINENT_MAX_REGIONS)

        region_coords_schemas = generate_continent_region_coordinates(num_regions_target)
        
        created_region_ids = []
        # Create actual region objects via RegionService
        for coord_schema in region_coords_schemas:
            # biome assignment can be more sophisticated here, e.g., based on coord, seed, etc.
            biome = random.choice(["Plains", "Forest", "Mountain", "Desert", "Swamp"])
            region_create_data = RegionCreationSchema(coordinates=coord_schema, biome=biome)
            # The region service will assign its own ID and calculate lat/lon
            created_region = self.region_service.create_new_region(region_create_data, continent_id=continent_id)
            created_region_ids.append(created_region.region_id)

        boundary_coords = get_continent_boundary(region_coords_schemas)
        boundary_schema = None
        if boundary_coords:
            boundary_schema = ContinentBoundarySchema(
                min_x=boundary_coords[0],
                max_x=boundary_coords[1],
                min_y=boundary_coords[2],
                max_y=boundary_coords[3]
            )

        metadata = creation_request.metadata.copy() if hasattr(creation_request, 'metadata') else {}
        metadata['generation_date'] = datetime.utcnow().isoformat()
        
        continent = ContinentSchema(
            continent_id=continent_id,
            name=creation_request.name if creation_request.name else f"Continent {continent_id[:8]}",
            seed=seed,
            region_coordinates=region_coords_schemas,
            region_ids=created_region_ids,
            origin_coordinate=region_coords_schemas[0] if region_coords_schemas else None,  # Assuming first is origin
            boundary=boundary_schema,
            creation_timestamp=datetime.utcnow(),
            num_regions=len(region_coords_schemas),
            metadata=metadata
        )
        return self.repository.create_continent(continent)

    def get_continent_details(self, continent_id: str) -> Optional[ContinentSchema]:
        """
        Retrieves details of a continent by ID.
        
        Args:
            continent_id: The ID of the continent to retrieve
            
        Returns:
            The continent details if found, None otherwise
        """
        return self.repository.get_continent_by_id(continent_id)

    def list_all_continents(self) -> List[ContinentSchema]:
        """
        Lists all continents.
        
        Returns:
            List of all continents
        """
        return self.repository.list_all_continents()
    
    def update_continent_metadata(self, continent_id: str, metadata: Dict[str, Any]) -> Optional[ContinentSchema]:
        """
        Updates metadata for a continent.
        
        Args:
            continent_id: The ID of the continent to update
            metadata: The metadata to update or add
            
        Returns:
            The updated continent if found, None otherwise
        """
        continent = self.repository.get_continent_by_id(continent_id)
        if not continent:
            return None
        
        # Update or add metadata fields
        if not continent.metadata:
            continent.metadata = {}
        continent.metadata.update(metadata)
        
        return self.repository.update_continent(continent_id, continent)
    
    def delete_continent(self, continent_id: str) -> bool:
        """
        Deletes a continent and potentially its regions.
        
        Args:
            continent_id: The ID of the continent to delete
            
        Returns:
            True if the continent was deleted, False otherwise
        """
        # Future implementation might also delete associated regions
        return self.repository.delete_continent(continent_id)

# Singleton instance
continent_service = ContinentService(repository=continent_repository, region_svc=region_service) 