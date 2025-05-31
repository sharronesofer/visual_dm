"""Map service for managing map entities."""

from typing import List, Optional, Dict, Any, Tuple
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.systems.map.models import Map
from backend.infrastructure.services import BaseService
from backend.infrastructure.database import get_db

class MapService(BaseService[Map]):
    """Service for managing map entities."""
    
    def __init__(self, db: Session = Depends(get_db)):
        """Initialize the map service.
        
        Args:
            db: Database session
        """
        super().__init__(Map, db)
    
    async def get_maps_by_world(self, world_id: int) -> List[Map]:
        """Get all maps for a specific world.
        
        Args:
            world_id: World ID
            
        Returns:
            List of maps
        """
        filters = {"world_id": world_id}
        return await self.get_by_filter(filters)
    
    async def update_map_metadata(self, map_id: int, metadata: Dict[str, Any]) -> Map:
        """Update metadata for a map.
        
        Args:
            map_id: Map ID
            metadata: Updated metadata
            
        Returns:
            Updated map entity
            
        Raises:
            HTTPException: If map not found or update fails
        """
        map_entity = await self.get_by_id(map_id)
        if not map_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Map with ID {map_id} not found"
            )
        
        # Update metadata fields
        update_data = {}
        metadata_fields = ["name", "description", "tags", "visibility", "scale"]
        
        for field in metadata_fields:
            if field in metadata:
                update_data[field] = metadata[field]
        
        return await self.update(map_id, update_data)
    
    async def add_location_to_map(self, map_id: int, location_data: Dict[str, Any]) -> Map:
        """Add a location to a map.
        
        Args:
            map_id: Map ID
            location_data: Location data to add
            
        Returns:
            Updated map entity
            
        Raises:
            HTTPException: If map not found or update fails
        """
        map_entity = await self.get_by_id(map_id)
        if not map_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Map with ID {map_id} not found"
            )
        
        # Add location to map
        locations = map_entity.locations or []
        
        # Generate a location ID
        location_id = 1
        if locations:
            location_id = max(loc.get("id", 0) for loc in locations) + 1
        
        # Add ID to location data
        location_data["id"] = location_id
        
        # Append location to locations list
        locations.append(location_data)
        
        return await self.update(map_id, {"locations": locations})
    
    async def update_location(
        self, map_id: int, location_id: int, location_data: Dict[str, Any]
    ) -> Map:
        """Update a location on a map.
        
        Args:
            map_id: Map ID
            location_id: Location ID
            location_data: Updated location data
            
        Returns:
            Updated map entity
            
        Raises:
            HTTPException: If map or location not found or update fails
        """
        map_entity = await self.get_by_id(map_id)
        if not map_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Map with ID {map_id} not found"
            )
        
        # Find location to update
        locations = map_entity.locations or []
        location_index = -1
        
        for i, loc in enumerate(locations):
            if loc.get("id") == location_id:
                location_index = i
                break
        
        if location_index == -1:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location with ID {location_id} not found on map"
            )
        
        # Update location
        location_data["id"] = location_id  # Ensure ID is preserved
        locations[location_index] = location_data
        
        return await self.update(map_id, {"locations": locations})
    
    async def remove_location(self, map_id: int, location_id: int) -> Map:
        """Remove a location from a map.
        
        Args:
            map_id: Map ID
            location_id: Location ID
            
        Returns:
            Updated map entity
            
        Raises:
            HTTPException: If map not found or update fails
        """
        map_entity = await self.get_by_id(map_id)
        if not map_entity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Map with ID {map_id} not found"
            )
        
        # Remove location from map
        locations = map_entity.locations or []
        filtered_locations = [loc for loc in locations if loc.get("id") != location_id]
        
        if len(filtered_locations) == len(locations):
            # Location not found, but we'll simply return the unchanged map
            return map_entity
        
        return await self.update(map_id, {"locations": filtered_locations}) 