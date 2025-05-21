"""
Region system service layer.

This module contains the service layer for the region system.
"""

from typing import List, Dict, Optional, Any, Union
from datetime import datetime
import random
import uuid

from backend.systems.region.repository import RegionRepository
from backend.systems.region.schemas import RegionSchema, TileSchema
from backend.systems.region.worldgen import WorldGenerator
from backend.systems.region.mapping import map_region_to_latlon, fetch_weather_for_latlon

class RegionService:
    """Service layer for the region system."""
    
    def __init__(self, repository: Optional[RegionRepository] = None):
        """
        Initialize the RegionService.
        
        Args:
            repository: The repository to use for database operations
        """
        self.repository = repository or RegionRepository()
        self.world_generator = WorldGenerator()
    
    def get_region_by_id(self, region_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a region by ID.
        
        Args:
            region_id: The ID of the region to get
            
        Returns:
            The region, or None if not found
        """
        region = self.repository.get_region_by_id(region_id)
        return region
    
    def list_all_regions(self) -> List[Dict[str, Any]]:
        """
        List all regions.
        
        Returns:
            List of all regions
        """
        return self.repository.list_all_regions()
    
    def get_regions_by_continent(self, continent_id: str) -> List[Dict[str, Any]]:
        """
        Get all regions in a continent.
        
        Args:
            continent_id: The ID of the continent
            
        Returns:
            List of regions in the continent
        """
        return self.repository.get_regions_by_continent(continent_id)
    
    def update_region(self, region_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update a region.
        
        Args:
            region_id: The ID of the region to update
            data: The updated region data
            
        Returns:
            The updated region, or None if not found
        """
        # Get the current region
        region = self.repository.get_region_by_id(region_id)
        if not region:
            return None
        
        # Update the region
        updated_region = self.repository.update_region(region_id, data)
        return updated_region
    
    def delete_region(self, region_id: str) -> bool:
        """
        Delete a region.
        
        Args:
            region_id: The ID of the region to delete
            
        Returns:
            True if the region was deleted, False if not found
        """
        region = self.repository.get_region_by_id(region_id)
        if not region:
            return False
        
        self.repository.delete_region(region_id)
        return True
    
    def get_region_details_with_weather(self, region_id: str) -> Optional[Dict[str, Any]]:
        """
        Get region details with weather.
        
        Args:
            region_id: The ID of the region to get
            
        Returns:
            Region details with weather, or None if not found
        """
        region = self.repository.get_region_by_id(region_id)
        if not region:
            return None
        
        # Get coordinates
        coordinates = region.get('coordinates', {})
        
        # Map to lat/lon
        lat, lon = map_region_to_latlon(coordinates)
        
        # Fetch weather
        weather = fetch_weather_for_latlon(lat, lon)
        
        # Return combined data
        return {
            "region": region,
            "weather": weather,
            "mapping": {
                "latitude": lat,
                "longitude": lon
            }
        }
    
    def get_region_map_tiles(self, region_id: str) -> Dict[str, TileSchema]:
        """
        Get the tiles for a region map.
        
        Args:
            region_id: The ID of the region
            
        Returns:
            A dictionary of tiles keyed by coordinate string
            
        Raises:
            Exception: If there is an error fetching the map
        """
        return self.repository.get_region_map_tiles(region_id)
    
    def seed_region_map(
        self, 
        region_id: str, 
        width: int = 10, 
        height: int = 10,
        terrain_types: List[str] = None
    ) -> Dict[str, Any]:
        """
        Seed a basic region map with clustered terrain tags.
        
        Args:
            region_id: The ID of the region to seed
            width: The width of the map
            height: The height of the map
            terrain_types: The terrain types to use
            
        Returns:
            Information about the seeded region
            
        Raises:
            Exception: If there is an error seeding the region
        """
        if terrain_types is None:
            terrain_types = ["forest", "plains", "mountain", "swamp", "coast", "desert"]
        
        # Start with empty map
        terrain_map = [[None for _ in range(height)] for _ in range(width)]
        
        # Scatter initial seeds
        for _ in range(8):  # number of seeds
            tx = random.randint(0, width - 1)
            ty = random.randint(0, height - 1)
            terrain = random.choice(terrain_types)
            terrain_map[tx][ty] = terrain
        
        # Spread seeds outward
        for x in range(width):
            for y in range(height):
                if not terrain_map[x][y]:
                    neighbors = []
                    
                    # Check neighboring tiles
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < width and 0 <= ny < height:
                                if terrain_map[nx][ny]:
                                    neighbors.append(terrain_map[nx][ny])
                    
                    if neighbors:
                        terrain_map[x][y] = random.choice(neighbors)
                    else:
                        terrain_map[x][y] = random.choice(terrain_types)
        
        # Save final terrain map into tiles
        new_tiles = {}
        for x in range(width):
            for y in range(height):
                new_tiles[f"{x}_{y}"] = {
                    "tags": [terrain_map[x][y]],
                    "poi": None
                }
        
        # Store the tiles in the repository
        self.repository.save_region_map_tiles(region_id, new_tiles)
        
        return {
            "region_id": region_id,
            "width": width,
            "height": height,
            "tiles_created": len(new_tiles)
        }
    
    def generate_region(self, seed_x: int, seed_y: int) -> Dict[str, Any]:
        """
        Generate a new region with starting coordinates.
        
        Args:
            seed_x: The X-coordinate seed for region generation
            seed_y: The Y-coordinate seed for region generation
            
        Returns:
            Information about the generated region
            
        Raises:
            Exception: If there is an error generating the region
        """
        # Generate a unique region ID
        region_id = f"r_{uuid.uuid4().hex[:8]}"
        
        # Generate region data using WorldGenerator
        region_data = self.world_generator.generate_region(seed_x, seed_y, size=1)
        
        # Add additional metadata
        region_data["id"] = region_id
        region_data["created_at"] = datetime.utcnow().isoformat()
        region_data["last_updated"] = datetime.utcnow().isoformat()
        
        # Save the region
        self.repository.create_region(region_data)
        
        # Also generate a map for this region
        map_result = self.seed_region_map(region_id)
        
        return {
            "region_id": region_id,
            "coordinates": {"x": seed_x, "y": seed_y},
            "tiles_created": map_result["tiles_created"]
        }
    
    def get_character_questlog(self, character_id: str) -> List[Dict[str, Any]]:
        """
        Get a character's questlog.
        
        Args:
            character_id: The ID of the character
            
        Returns:
            The character's questlog
        """
        return self.repository.get_character_questlog(character_id)
    
    def add_quest_to_character(self, character_id: str, quest_entry: Dict[str, Any]) -> bool:
        """
        Add a quest to a character's questlog.
        
        Args:
            character_id: The ID of the character
            quest_entry: The quest to add
            
        Returns:
            True if the quest was added successfully
        """
        return self.repository.add_quest_to_character(character_id, quest_entry)


# Create a singleton instance of the service
region_service = RegionService() 