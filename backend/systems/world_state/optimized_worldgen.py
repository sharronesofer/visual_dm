"""
Optimized World Generation & Geography System

This module provides an enhanced world generation system with:
1. Multi-scale noise generation for more realistic and coherent geography
2. Biome transition zones for natural biome blending
3. Improved terrain feature generation (rivers, mountains, coastlines)
4. Memory optimization for large world generation
5. Deterministic generation with consistent seeds

Implementation follows the Development Bible guidelines:
- Canonical region structure (225 hex tiles)
- Continent generation parameters
- Region-based biome allocation
"""

from typing import Dict, List, Tuple, Optional, Any, Set
import random
import math
import time
import json
import numpy as np
from dataclasses import dataclass, field
import os

from backend.systems.world_state.core.world_models import (
    Region,
    PointOfInterest,
    TerrainType
)
from backend.systems.world_state.utils.terrain_generator import (
    TerrainGenerator,
    TerrainConfig,
    NoiseLayer,
    BiomeInfo,
    RegionParams
)

class OptimizedWorldGenerator:
    """
    Enhanced world generation system with improved geography, biomes, and optimization.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the world generator with configuration settings.
        
        Args:
            config_path: Path to a JSON configuration file
        """
        self.default_config = {
            "base_seed": 12345,
            "region_size": 225,
            "map_width": 5,
            "map_height": 5,
            "elevation_noise_layers": [
                {"scale": 100.0, "amplitude": 1.0, "persistence": 0.5},
                {"scale": 50.0, "amplitude": 0.5, "persistence": 0.5},
                {"scale": 25.0, "amplitude": 0.25, "persistence": 0.5}
            ],
            "temperature_base": 0.5,
            "temperature_variation": 0.3,
            "moisture_base": 0.5,
            "moisture_variation": 0.3,
            "ocean_threshold": 0.2,
            "mountain_threshold": 0.8,
            "river_threshold": 0.7,
            "coast_threshold": 0.3,
            "river_count_per_region": 2
        }
        
        # Load configuration
        self.config = self.default_config.copy()
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
                
        # Create terrain configuration from our settings
        terrain_config = TerrainConfig(
            base_seed=self.config["base_seed"],
            ocean_threshold=self.config["ocean_threshold"],
            mountain_threshold=self.config["mountain_threshold"],
            river_threshold=self.config["river_threshold"],
            coast_threshold=self.config["coast_threshold"],
            elevation_noise_layers=self.config["elevation_noise_layers"],
            temperature_base=self.config["temperature_base"],
            temperature_variation=self.config["temperature_variation"],
            moisture_base=self.config["moisture_base"],
            moisture_variation=self.config["moisture_variation"]
        )
        
        # Initialize the terrain generator
        self.terrain_generator = TerrainGenerator(terrain_config)
        
        # Cache for generated regions
        self.region_cache = {}
        
    def generate_world_map(self, width: int = None, height: int = None, seed: int = None) -> WorldMap:
        """
        Generate a complete world map with regions.
        
        Args:
            width: Width of the world in regions (default from config)
            height: Height of the world in regions (default from config)
            seed: Random seed (default from config)
            
        Returns:
            WorldMap object containing all regions
        """
        # Use defaults from config if not specified
        width = width or self.config["map_width"]
        height = height or self.config["map_height"]
        seed = seed or self.config["base_seed"]
        
        # Create a fresh generator with this seed if different
        if seed != self.config["base_seed"]:
            terrain_config = TerrainConfig(
                base_seed=seed,
                ocean_threshold=self.config["ocean_threshold"],
                mountain_threshold=self.config["mountain_threshold"],
                river_threshold=self.config["river_threshold"],
                coast_threshold=self.config["coast_threshold"],
                elevation_noise_layers=self.config["elevation_noise_layers"],
                temperature_base=self.config["temperature_base"],
                temperature_variation=self.config["temperature_variation"],
                moisture_base=self.config["moisture_base"],
                moisture_variation=self.config["moisture_variation"]
            )
            terrain_generator = TerrainGenerator(terrain_config)
        else:
            terrain_generator = self.terrain_generator
            
        # Clear cache for new generation
        self.region_cache = {}
        
        # Create empty world map
        world_map = WorldMap(width=width, height=height, seed=seed)
        
        start_time = time.time()
        print(f"Generating world map {width}x{height} with seed {seed}...")
        
        # Generate each region
        for y in range(height):
            for x in range(width):
                # Calculate regional variations
                region_x_factor = x / max(1, width - 1)  # 0 to 1 along x-axis
                region_y_factor = y / max(1, height - 1)  # 0 to 1 along y-axis
                
                # Vary temperature north to south (hotter at equator)
                temp_y_offset = -(region_y_factor - 0.5) ** 2 * 4 * self.config["temperature_variation"]
                
                # Add some longitudinal temperature variation
                temp_x_offset = (math.sin(region_x_factor * math.pi * 2) * 
                                self.config["temperature_variation"] * 0.3)
                
                # Combine offsets
                temperature_offset = temp_y_offset + temp_x_offset
                
                # Calculate regional seed
                region_seed = seed + (y * width + x) * 1000
                
                # Generate the region with these specific conditions
                region = self.generate_region(
                    x, y,
                    seed=region_seed,
                    temperature_offset=temperature_offset
                )
                
                # Add the region to the world map
                world_map.regions[(x, y)] = region
        
        # Generate world-level rivers that span multiple regions
        self._generate_world_rivers(world_map, seed)
        
        # Generate points of interest
        self._generate_points_of_interest(world_map, seed)
        
        end_time = time.time()
        print(f"World generation completed in {end_time - start_time:.2f} seconds")
        
        return world_map
        
    def generate_region(self, region_x: int, region_y: int, 
                      size: int = None, seed: int = None,
                      temperature_offset: float = 0.0,
                      moisture_offset: float = 0.0) -> Region:
        """
        Generate a single region of the world.
        
        Args:
            region_x: X-coordinate of the region in the world
            region_y: Y-coordinate of the region in the world
            size: Number of cells in the region (default from config)
            seed: Random seed (default derived from base seed and coordinates)
            temperature_offset: Adjustment to temperature (-1 to 1)
            moisture_offset: Adjustment to moisture (-1 to 1)
            
        Returns:
            Region object with terrain data
        """
        # Use defaults if not specified
        size = size or self.config["region_size"]
        
        # Check if this region is already cached
        cache_key = (region_x, region_y, size, seed, temperature_offset, moisture_offset)
        if cache_key in self.region_cache:
            return self.region_cache[cache_key]
            
        # If no seed provided, derive it from coordinates and base seed
        if seed is None:
            base_seed = self.config["base_seed"]
            seed = base_seed + (region_y * 1000 + region_x * 10)
            
        # Create a region object
        region = Region(
            x=region_x,
            y=region_y,
            size=size,
            seed=seed,
            terrain={},
            biomes={},
            resources={},
            points_of_interest=[]
        )
        
        # Generate terrain data for this region
        terrain_data = self.terrain_generator.generate_terrain(
            region_x=region_x,
            region_y=region_y,
            size=size,
            seed=seed,
            temperature_offset=temperature_offset,
            moisture_offset=moisture_offset
        )
        
        # Populate the region with the terrain data
        for cell_id, cell_data in terrain_data.items():
            # Extract terrain type from biome
            biome_info = self.terrain_generator.get_biome_info(cell_data["biome"])
            terrain_type = TerrainType.PLAINS  # Default
            
            if biome_info:
                # Map biome to terrain type
                if biome_info.is_water:
                    terrain_type = TerrainType.WATER
                elif cell_data["biome"] == "mountain" or cell_data["biome"] == "snow_peak":
                    terrain_type = TerrainType.MOUNTAIN
                elif cell_data["biome"] == "forest" or cell_data["biome"] == "rainforest":
                    terrain_type = TerrainType.FOREST
                elif cell_data["biome"] == "desert" or cell_data["biome"] == "savanna":
                    terrain_type = TerrainType.DESERT
                elif cell_data["biome"] == "tundra" or cell_data["biome"] == "taiga":
                    terrain_type = TerrainType.TUNDRA
                elif cell_data["biome"] == "swamp" or cell_data["biome"] == "marsh":
                    terrain_type = TerrainType.SWAMP
                else:
                    terrain_type = TerrainType.PLAINS
            
            # Set terrain and additional data
            region.terrain[cell_id] = terrain_type
            region.biomes[cell_id] = cell_data["biome"]
            region.resources[cell_id] = cell_data.get("resources", {})
            
        # Cache the region
        self.region_cache[cache_key] = region
        
        return region
        
    def _generate_world_rivers(self, world_map: WorldMap, seed: int):
        """
        Generate major rivers that span multiple regions.
        
        Args:
            world_map: The WorldMap to add rivers to
            seed: Random seed for river generation
        """
        # Create a random generator for river creation
        rng = random.Random(seed + 42)  # Different seed component
        
        # Determine number of major rivers
        num_major_rivers = max(1, min(5, (world_map.width + world_map.height) // 3))
        
        # Find suitable starting points (mountains or high elevations)
        potential_sources = []
        
        # Scan regions for mountain terrain
        for (x, y), region in world_map.regions.items():
            mountain_cells = [cell_id for cell_id, terrain in region.terrain.items() 
                             if terrain == TerrainType.MOUNTAIN]
            
            if mountain_cells:
                # Add some of these as potential sources
                for cell_id in rng.sample(mountain_cells, min(2, len(mountain_cells))):
                    potential_sources.append((x, y, cell_id))
        
        # If not enough mountain sources, add some random high points
        if len(potential_sources) < num_major_rivers:
            for _ in range(num_major_rivers - len(potential_sources)):
                x = rng.randint(0, world_map.width - 1)
                y = rng.randint(0, world_map.height - 1)
                
                # Pick a random cell in this region
                region = world_map.regions.get((x, y))
                if region and region.terrain:
                    cell_id = rng.choice(list(region.terrain.keys()))
                    potential_sources.append((x, y, cell_id))
        
        # Select random sources for our rivers
        river_sources = rng.sample(potential_sources, min(num_major_rivers, len(potential_sources)))
        
        # Generate rivers from each source
        for region_x, region_y, start_cell in river_sources:
            # Start at this cell
            current_x, current_y = region_x, region_y
            current_cell = start_cell
            
            # Track cells that are part of this river
            river_cells = []
            
            # Prevent infinite loops
            max_steps = world_map.width * world_map.height * 10
            steps = 0
            
            # Find path to lowest neighboring cell (downhill)
            while steps < max_steps:
                # Mark this cell as river
                region = world_map.regions.get((current_x, current_y))
                if not region:
                    break
                    
                # Change the terrain to water for this cell
                region.terrain[current_cell] = TerrainType.WATER
                region.biomes[current_cell] = "river"
                
                # Add to our river path
                river_cells.append((current_x, current_y, current_cell))
                
                # Determine which neighboring cells exist
                # This is a simplified approach - in a real system, you'd need
                # to know the actual neighboring cells based on your grid system
                neighbors = self._find_neighboring_cells(world_map, current_x, current_y, current_cell)
                
                # Find the lowest elevation neighbor
                lowest_elevation = float('inf')
                next_cell = None
                next_x, next_y = current_x, current_y
                
                for nx, ny, ncell, elevation in neighbors:
                    # Skip cells we've already visited
                    if (nx, ny, ncell) in river_cells:
                        continue
                        
                    # Find lowest elevation
                    if elevation < lowest_elevation:
                        lowest_elevation = elevation
                        next_cell = ncell
                        next_x, next_y = nx, ny
                
                # If we can't find a lower neighbor or we've reached water, stop
                if next_cell is None or lowest_elevation == 0:
                    # We've reached a lake or ocean, or we're stuck
                    break
                    
                # Move to the next cell
                current_x, current_y = next_x, next_y
                current_cell = next_cell
                steps += 1
    
    def _find_neighboring_cells(self, world_map: WorldMap, region_x: int, region_y: int, 
                              cell_id: str) -> List[Tuple[int, int, str, float]]:
        """
        Find neighboring cells across region boundaries.
        
        Args:
            world_map: The world map
            region_x: X coordinate of current region
            region_y: Y coordinate of current region
            cell_id: ID of current cell
            
        Returns:
            List of (region_x, region_y, cell_id, elevation) for neighbors
        """
        # This is a simplified implementation
        # In a real system, you'd need to understand your cell ID format
        # and how to find neighbors, especially across region boundaries
        
        # Mock implementation - in reality this would examine cell IDs
        # and determine actual neighbors based on your grid structure
        neighbors = []
        current_region = world_map.regions.get((region_x, region_y))
        if not current_region:
            return []
            
        # Try to find logical neighboring cells
        # This assumes cell_id follows some format like "x,y" inside the region
        try:
            # Example if cell_id is "x,y" format
            if ',' in cell_id:
                local_x, local_y = map(int, cell_id.split(','))
                
                # Check all 8 neighbors
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), 
                              (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nx, ny = local_x + dx, local_y + dy
                    
                    # Check if this neighbor is within current region
                    neighbor_id = f"{nx},{ny}"
                    
                    if neighbor_id in current_region.terrain:
                        # Get approximate elevation from biome
                        biome = current_region.biomes.get(neighbor_id, "plains")
                        elevation = self._get_biome_elevation(biome)
                        neighbors.append((region_x, region_y, neighbor_id, elevation))
                    else:
                        # Might be in neighboring region
                        # Determine which region
                        region_size = int(math.sqrt(current_region.size))
                        
                        # Check if we need to move to adjacent region
                        new_region_x, new_region_y = region_x, region_y
                        new_local_x, new_local_y = nx, ny
                        
                        if nx < 0:
                            new_region_x -= 1
                            new_local_x += region_size
                        elif nx >= region_size:
                            new_region_x += 1
                            new_local_x -= region_size
                            
                        if ny < 0:
                            new_region_y -= 1
                            new_local_y += region_size
                        elif ny >= region_size:
                            new_region_y += 1
                            new_local_y -= region_size
                            
                        # Check if the new region exists
                        new_region = world_map.regions.get((new_region_x, new_region_y))
                        if new_region:
                            # Create the cell ID in the new region
                            new_cell_id = f"{new_local_x},{new_local_y}"
                            
                            if new_cell_id in new_region.terrain:
                                biome = new_region.biomes.get(new_cell_id, "plains")
                                elevation = self._get_biome_elevation(biome)
                                neighbors.append((new_region_x, new_region_y, new_cell_id, elevation))
        except Exception as e:
            # Fallback for testing
            print(f"Error finding neighbors: {e}")
            
            # Create some mock neighbors in same region
            for i in range(3):
                mock_id = f"mock_{i}"
                if mock_id in current_region.terrain:
                    biome = current_region.biomes.get(mock_id, "plains")
                    elevation = self._get_biome_elevation(biome)
                    neighbors.append((region_x, region_y, mock_id, elevation))
        
        return neighbors
    
    def _get_biome_elevation(self, biome: str) -> float:
        """
        Get approximate elevation value for a biome.
        
        Args:
            biome: Biome ID string
            
        Returns:
            Approximate elevation value from 0 to 1
        """
        # Map biomes to elevation values
        elevation_map = {
            "ocean": 0.0,
            "river": 0.1,
            "beach": 0.2,
            "swamp": 0.25,
            "marsh": 0.25,
            "desert": 0.35,
            "savanna": 0.4,
            "plains": 0.5,
            "grassland": 0.5,
            "forest": 0.6,
            "rainforest": 0.6,
            "taiga": 0.65,
            "tundra": 0.7,
            "hills": 0.75,
            "mountain": 0.85,
            "snow_peak": 0.95
        }
        
        return elevation_map.get(biome, 0.5)  # Default to plains elevation
    
    def _generate_points_of_interest(self, world_map: WorldMap, seed: int):
        """
        Generate points of interest across the world.
        
        Args:
            world_map: The world map to add POIs to
            seed: Random seed for POI generation
        """
        # Create a random generator for POI creation
        rng = random.Random(seed + 100)  # Different seed component
        
        # Calculate number of POIs based on world size
        num_regions = world_map.width * world_map.height
        num_pois = max(5, num_regions // 2)  # At least 5, or half the number of regions
        
        # POI types with their terrain preferences
        poi_types = {
            "settlement": [TerrainType.PLAINS, TerrainType.FOREST, TerrainType.DESERT],
            "ruins": [TerrainType.PLAINS, TerrainType.FOREST, TerrainType.DESERT, TerrainType.MOUNTAIN],
            "dungeon": [TerrainType.MOUNTAIN, TerrainType.FOREST],
            "landmark": [TerrainType.MOUNTAIN, TerrainType.PLAINS, TerrainType.DESERT],
            "shrine": [TerrainType.PLAINS, TerrainType.FOREST, TerrainType.MOUNTAIN]
        }
        
        # Generate POIs
        for _ in range(num_pois):
            # Randomly select a region
            region_x = rng.randint(0, world_map.width - 1)
            region_y = rng.randint(0, world_map.height - 1)
            region = world_map.regions.get((region_x, region_y))
            
            if not region or not region.terrain:
                continue
                
            # Choose a POI type
            poi_type = rng.choice(list(poi_types.keys()))
            preferred_terrains = poi_types[poi_type]
            
            # Find suitable cells
            suitable_cells = [cell_id for cell_id, terrain in region.terrain.items()
                            if terrain in preferred_terrains]
            
            # If no suitable cells, try any non-water cell
            if not suitable_cells:
                suitable_cells = [cell_id for cell_id, terrain in region.terrain.items()
                                if terrain != TerrainType.WATER]
            
            if not suitable_cells:
                continue
                
            # Select a random suitable cell
            cell_id = rng.choice(suitable_cells)
            
            # Create the POI
            poi = PointOfInterest(
                name=f"{poi_type.capitalize()} {region_x}-{region_y}-{cell_id}",
                poi_type=poi_type,
                region_x=region_x,
                region_y=region_y,
                cell_id=cell_id,
                description=f"A {poi_type} located in region {region_x},{region_y}"
            )
            
            # Add to the region
            region.points_of_interest.append(poi) 