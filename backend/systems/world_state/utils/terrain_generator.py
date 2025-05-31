"""
Terrain Generation System

This module provides the core terrain generation functionality for the world generation system.
It includes:
1. Multi-scale noise generation for realistic terrain
2. Biome determination based on environmental factors
3. Biome transition zones for natural blending
4. River and feature generation

Implementation follows the Development Bible guidelines.
"""

from typing import Dict, List, Tuple, Optional, Any, Set
import random
import math
import time
import json
import numpy as np
from dataclasses import dataclass, field
import os

@dataclass
class NoiseLayer:
    """Configuration for a noise layer in terrain generation."""
    scale: float  # Scale of the noise (higher = more zoomed out)
    amplitude: float  # Strength of this layer's influence
    octaves: int = 1  # Number of octaves for fractal noise
    persistence: float = 0.5  # How much each octave contributes
    lacunarity: float = 2.0  # How much detail is added in each octave
    seed_offset: int = 0  # Offset to the base seed for this layer

@dataclass
class TerrainConfig:
    """Configuration for terrain generation."""
    elevation_layers: List[NoiseLayer] = field(default_factory=list)
    moisture_layers: List[NoiseLayer] = field(default_factory=list)
    temperature_layers: List[NoiseLayer] = field(default_factory=list)
    river_threshold: float = 0.85  # Threshold for river generation
    mountain_threshold: float = 0.75  # Threshold for mountain generation
    lake_threshold: float = 0.3  # Threshold for lake generation
    transition_width: float = 0.15  # Width of biome transition zones
    
    @classmethod
    def default(cls) -> 'TerrainConfig':
        """Create a default terrain configuration with sensible values."""
        return cls(
            elevation_layers=[
                NoiseLayer(scale=100.0, amplitude=1.0, octaves=4, seed_offset=0),
                NoiseLayer(scale=50.0, amplitude=0.5, octaves=2, seed_offset=1000),
                NoiseLayer(scale=25.0, amplitude=0.25, octaves=1, seed_offset=2000),
            ],
            moisture_layers=[
                NoiseLayer(scale=120.0, amplitude=1.0, octaves=3, seed_offset=3000),
                NoiseLayer(scale=60.0, amplitude=0.6, octaves=2, seed_offset=4000),
            ],
            temperature_layers=[
                NoiseLayer(scale=150.0, amplitude=1.0, octaves=2, seed_offset=5000),
                NoiseLayer(scale=75.0, amplitude=0.4, octaves=1, seed_offset=6000),
            ],
        )

@dataclass
class BiomeInfo:
    """Detailed information about a biome."""
    id: str
    name: str
    temperature_range: Tuple[float, float]
    moisture_range: Tuple[float, float]
    elevation_range: Tuple[float, float]
    features: List[str]
    resources: Dict[str, float]
    color: str
    is_water: bool = False
    is_transition: bool = False
    base_biomes: List[str] = field(default_factory=list)  # For transition biomes

class TerrainGenerator:
    """
    Generates terrain features like elevation, temperature, moisture, and biomes.
    Creates realistic and varied terrain with proper transitions between biomes.
    """
    
    def __init__(self, seed: int, config: TerrainConfig):
        """
        Initialize the terrain generator.
        
        Args:
            seed: Base seed for all terrain generation
            config: Configuration for terrain generation
        """
        self.seed = seed
        self.config = config
        self.biomes = {}
        self.biome_order = []
        self.waterbiomes = []
        self.landbiomes = []
        self._noise_cache = {}
        
    def load_biome_data(self, data_dir: str):
        """
        Load biome data from the biomes.json file.
        
        Args:
            data_dir: Directory containing modding data files
        """
        biome_file = os.path.join(data_dir, "biomes.json")
        
        try:
            if os.path.exists(biome_file):
                with open(biome_file, 'r') as f:
                    biome_data = json.load(f)
            else:
                # Use default biomes if the file doesn't exist
                biome_data = {
                    "ocean": {
                        "name": "Ocean",
                        "temperature_range": [0.0, 1.0],
                        "moisture_range": [0.0, 1.0],
                        "elevation_range": [0.0, 0.3],
                        "features": ["deep_water", "fish"],
                        "resources": {"fish": 0.8, "salt": 0.6},
                        "color": "#0077BE",
                        "is_water": True
                    },
                    "desert": {
                        "name": "Desert",
                        "temperature_range": [0.7, 1.0],
                        "moisture_range": [0.0, 0.3],
                        "elevation_range": [0.3, 0.8],
                        "features": ["dunes", "cacti"],
                        "resources": {"sand": 0.9, "gold": 0.2},
                        "color": "#EDC9AF"
                    },
                    "plains": {
                        "name": "Plains",
                        "temperature_range": [0.3, 0.7],
                        "moisture_range": [0.3, 0.6],
                        "elevation_range": [0.3, 0.6],
                        "features": ["grassland", "rolling_hills"],
                        "resources": {"grain": 0.8, "livestock": 0.7},
                        "color": "#7CFC00"
                    },
                    "forest": {
                        "name": "Forest",
                        "temperature_range": [0.3, 0.7],
                        "moisture_range": [0.6, 1.0],
                        "elevation_range": [0.3, 0.7],
                        "features": ["trees", "wildlife"],
                        "resources": {"wood": 0.9, "game": 0.7},
                        "color": "#228B22"
                    },
                    "mountains": {
                        "name": "Mountains",
                        "temperature_range": [0.0, 0.6],
                        "moisture_range": [0.2, 0.8],
                        "elevation_range": [0.7, 1.0],
                        "features": ["peaks", "caves"],
                        "resources": {"stone": 0.9, "ore": 0.6},
                        "color": "#808080"
                    },
                    "tundra": {
                        "name": "Tundra",
                        "temperature_range": [0.0, 0.3],
                        "moisture_range": [0.2, 0.6],
                        "elevation_range": [0.3, 0.7],
                        "features": ["permafrost", "sparse_vegetation"],
                        "resources": {"fur": 0.7, "herbs": 0.4},
                        "color": "#A9A9A9"
                    },
                    "swamp": {
                        "name": "Swamp",
                        "temperature_range": [0.5, 0.8],
                        "moisture_range": [0.7, 1.0],
                        "elevation_range": [0.3, 0.4],
                        "features": ["marsh", "mangroves"],
                        "resources": {"herbs": 0.8, "exotic_creatures": 0.5},
                        "color": "#2F4F4F"
                    },
                    "river": {
                        "name": "River",
                        "temperature_range": [0.0, 1.0],
                        "moisture_range": [0.0, 1.0],
                        "elevation_range": [0.0, 0.9],
                        "features": ["flowing_water", "fish"],
                        "resources": {"fresh_water": 1.0, "fish": 0.7},
                        "color": "#1E90FF",
                        "is_water": True
                    }
                }
            
            # Process biome data into BiomeInfo objects
            self.biomes = {}
            self.biome_order = list(biome_data.keys())
            self.waterbiomes = []
            self.landbiomes = []
            
            for biome_id, data in biome_data.items():
                biome_info = BiomeInfo(
                    id=biome_id,
                    name=data["name"],
                    temperature_range=tuple(data["temperature_range"]),
                    moisture_range=tuple(data["moisture_range"]),
                    elevation_range=tuple(data["elevation_range"]),
                    features=data["features"],
                    resources=data["resources"],
                    color=data["color"],
                    is_water=data.get("is_water", False)
                )
                
                self.biomes[biome_id] = biome_info
                
                if biome_info.is_water:
                    self.waterbiomes.append(biome_id)
                else:
                    self.landbiomes.append(biome_id)
                    
        except Exception as e:
            print(f"Error loading biome data: {e}")
            # Fallback to empty biomes - should be caught by the caller
            self.biomes = {}
            self.biome_order = []
            self.waterbiomes = []
            self.landbiomes = []
    
    def generate_transition_biomes(self):
        """
        Generate transition biomes between adjacent biome types.
        Creates blended biomes for smoother terrain transitions.
        """
        transition_biomes = {}
        
        # Only generate transitions between land biomes
        landbiome_ids = [b for b in self.biome_order if not self.biomes[b].is_water and not self.biomes[b].is_transition]
        
        for i, biome1_id in enumerate(landbiome_ids):
            biome1 = self.biomes[biome1_id]
            
            for biome2_id in landbiome_ids[i+1:]:
                biome2 = self.biomes[biome2_id]
                
                # Check if biomes could be adjacent based on their ranges
                temp_adjacent = self._ranges_overlap(biome1.temperature_range, biome2.temperature_range)
                moisture_adjacent = self._ranges_overlap(biome1.moisture_range, biome2.moisture_range)
                elev_adjacent = self._ranges_overlap(biome1.elevation_range, biome2.elevation_range)
                
                # Only create transitions for biomes that could be adjacent
                if (temp_adjacent and moisture_adjacent) or (temp_adjacent and elev_adjacent) or (moisture_adjacent and elev_adjacent):
                    # Create transition biome ID and name
                    transition_id = f"transition_{biome1_id}_{biome2_id}"
                    transition_name = f"{biome1.name}-{biome2.name} Transition"
                    
                    # Create merged ranges for the transition
                    temp_range = self._merge_ranges(biome1.temperature_range, biome2.temperature_range)
                    moisture_range = self._merge_ranges(biome1.moisture_range, biome2.moisture_range)
                    elev_range = self._merge_ranges(biome1.elevation_range, biome2.elevation_range)
                    
                    # Merge features and resources
                    features = list(set(biome1.features + biome2.features))
                    resources = self._merge_resources(biome1.resources, biome2.resources)
                    
                    # Create blended color
                    color = self._blend_colors(biome1.color, biome2.color)
                    
                    # Create transition biome
                    transition_biomes[transition_id] = BiomeInfo(
                        id=transition_id,
                        name=transition_name,
                        temperature_range=temp_range,
                        moisture_range=moisture_range,
                        elevation_range=elev_range,
                        features=features,
                        resources=resources,
                        color=color,
                        is_water=False,
                        is_transition=True,
                        base_biomes=[biome1_id, biome2_id]
                    )
        
        # Add transition biomes to the main biome dictionary
        for transition_id, biome_info in transition_biomes.items():
            self.biomes[transition_id] = biome_info
            self.biome_order.append(transition_id)
    
    def generate_terrain(self, 
                         region_x: int, 
                         region_y: int, 
                         size: int, 
                         region_seed: int,
                         biome_influence: Dict[str, float] = None) -> Dict[str, Any]:
        """
        Generate terrain for a region with the given parameters.
        
        Args:
            region_x: X coordinate of the region in world grid
            region_y: Y coordinate of the region in world grid
            size: Size of the region (number of tiles per side)
            region_seed: Seed for deterministic generation
            biome_influence: Optional biome influences to apply
            
        Returns:
            Dictionary with terrain data including elevation, moisture, temperature,
            biomes, and rivers
        """
        # Create region grid maps (using numpy for efficient operations)
        grid_size = size  # Default to square grid
        
        # Initialize terrain maps
        elevation_map = np.zeros((grid_size, grid_size))
        temperature_map = np.zeros((grid_size, grid_size))
        moisture_map = np.zeros((grid_size, grid_size))
        
        # Generate terrain maps
        for y in range(grid_size):
            for x in range(grid_size):
                # Convert grid coords to world coords
                world_x = region_x * grid_size + x
                world_y = region_y * grid_size + y
                
                # Generate elevation
                elevation_map[y, x] = self._generate_noise(
                    world_x, world_y, 
                    self.config.elevation_layers,
                    region_seed
                )
                
                # Generate temperature (affected by elevation and latitude)
                base_temp = self._generate_noise(
                    world_x, world_y,
                    self.config.temperature_layers,
                    region_seed
                )
                
                # Adjust temperature based on elevation (higher = colder)
                elevation_factor = 1.0 - (elevation_map[y, x] * 0.5)
                
                # Adjust temperature based on latitude (equator = hotter)
                world_height = 1000  # Arbitrary world height
                latitude_factor = 1.0 - abs(region_y - (world_height / 2)) / (world_height / 2)
                
                temperature_map[y, x] = base_temp * elevation_factor * latitude_factor
                
                # Generate moisture (affected by proximity to water)
                moisture_map[y, x] = self._generate_noise(
                    world_x, world_y,
                    self.config.moisture_layers,
                    region_seed
                )
        
        # Generate rivers based on elevation
        river_map = self._generate_improved_rivers(elevation_map, region_seed, size)
        
        # Apply rivers to moisture map (increase moisture near rivers)
        for y in range(grid_size):
            for x in range(grid_size):
                if river_map[y, x] > 0:
                    # Increase moisture along rivers
                    moisture_map[y, x] = min(1.0, moisture_map[y, x] + 0.3)
                    
                    # Spread moisture effect to nearby cells
                    for dy in range(-2, 3):
                        for dx in range(-2, 3):
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < grid_size and 0 <= ny < grid_size):
                                distance = math.sqrt(dx*dx + dy*dy)
                                if distance <= 2:
                                    moisture_bonus = 0.2 * (1 - distance/2)
                                    moisture_map[ny, nx] = min(1.0, moisture_map[ny, nx] + moisture_bonus)
        
        # Identify primary and transition biomes for each cell
        biome_map = []
        for y in range(grid_size):
            biome_row = []
            for x in range(grid_size):
                biome_id = self._determine_biome(
                    elevation_map[y, x], 
                    temperature_map[y, x], 
                    moisture_map[y, x],
                    river_map[y, x] > 0
                )
                biome_row.append(biome_id)
            biome_map.append(biome_row)
        
        # Create final terrain data
        terrain_data = {
            'elevation': elevation_map.tolist(),
            'temperature': temperature_map.tolist(),
            'moisture': moisture_map.tolist(),
            'biomes': biome_map,
            'rivers': river_map.tolist(),
        }
        
        return terrain_data
        
    def _generate_noise(self, x: float, y: float, noise_layers: List[NoiseLayer], region_seed: int) -> float:
        """
        Generate layered noise for a specific coordinate.
        
        Args:
            x: X coordinate
            y: Y coordinate
            noise_layers: List of noise configuration layers to apply
            region_seed: Base seed for this region
            
        Returns:
            float: Combined noise value in range 0-1
        """
        # Check cache first
        cache_key = f"{x}:{y}:{region_seed}:{id(noise_layers)}"
        if cache_key in self._noise_cache:
            return self._noise_cache[cache_key]
            
        # Ensure deterministic noise by seeding the random number generator
        random.seed(region_seed)
        
        result = 0.0
        normalization = 0.0
        
        for layer in noise_layers:
            # Create a unique seed for this layer
            layer_seed = region_seed + layer.seed_offset
            random.seed(layer_seed)
            
            # Generate base noise
            value = self._perlin_noise(x / layer.scale, y / layer.scale, layer_seed)
            
            # Apply fractal Brownian motion (fBm) if using multiple octaves
            if layer.octaves > 1:
                value = self._fractal_noise(x, y, layer.scale, layer.octaves, 
                                       layer.persistence, layer.lacunarity, layer_seed)
            
            # Add this layer's contribution
            result += value * layer.amplitude
            normalization += layer.amplitude
        
        # Normalize the result to 0-1 range
        if normalization > 0:
            result /= normalization
            
        # Ensure we're within 0-1 bounds
        result = max(0.0, min(1.0, result))
        
        # Cache the result
        self._noise_cache[cache_key] = result
        
        return result
    
    def _perlin_noise(self, x: float, y: float, seed: int) -> float:
        """
        Generate a single octave of Perlin-like noise.
        This is a simplified implementation for performance.
        
        Args:
            x: X coordinate
            y: Y coordinate
            seed: Seed value for deterministic generation
            
        Returns:
            float: Noise value in range 0-1
        """
        # Hash the coordinates with the seed for deterministic randomness
        def pseudo_random(ix, iy):
            # Simple but fast hashing function
            h = seed + ix * 374761393 + iy * 668265263
            h = (h ^ (h >> 13)) * 1274126177
            return (h ^ (h >> 16)) / 0xFFFFFFFF
        
        # Integer and fractional parts
        x0, y0 = int(x), int(y)
        x1, y1 = x0 + 1, y0 + 1
        
        # Fractional parts for interpolation
        sx, sy = x - x0, y - y0
        
        # Improved smoothing function (smoother than linear interpolation)
        def smoothstep(t):
            return t * t * (3 - 2 * t)
        
        # Apply smoothstep to coordinates
        sx, sy = smoothstep(sx), smoothstep(sy)
        
        # Get random values at the corners
        n00 = pseudo_random(x0, y0)
        n10 = pseudo_random(x1, y0)
        n01 = pseudo_random(x0, y1)
        n11 = pseudo_random(x1, y1)
        
        # Bilinear interpolation
        nx0 = n00 * (1 - sx) + n10 * sx
        nx1 = n01 * (1 - sx) + n11 * sx
        n = nx0 * (1 - sy) + nx1 * sy
        
        return n

    def _fractal_noise(self, x: float, y: float, scale: float, octaves: int, 
                      persistence: float, lacunarity: float, seed: int) -> float:
        """
        Generate fractal noise using multiple octaves of Perlin noise.
        
        Args:
            x: X coordinate
            y: Y coordinate
            scale: Base scale of the noise
            octaves: Number of layers of detail
            persistence: How much each octave contributes
            lacunarity: How much detail is added at each octave
            seed: Base seed value
            
        Returns:
            float: Noise value in range 0-1
        """
        total = 0.0
        frequency = 1.0 / scale
        amplitude = 1.0
        max_value = 0.0
        
        for i in range(octaves):
            # Each octave has its own seed offset
            octave_seed = seed + i * 1000
            
            # Add the contribution of this octave
            total += self._perlin_noise(x * frequency, y * frequency, octave_seed) * amplitude
            
            # Keep track of the maximum possible value
            max_value += amplitude
            
            # Increase the frequency (add detail)
            frequency *= lacunarity
            
            # Decrease the amplitude (reduce contribution of higher octaves)
            amplitude *= persistence
        
        # Normalize to 0-1
        return total / max_value if max_value > 0 else 0
    
    def _ranges_overlap(self, range1: Tuple[float, float], range2: Tuple[float, float]) -> bool:
        """Check if two ranges overlap."""
        return range1[0] <= range2[1] and range2[0] <= range1[1]
    
    def _merge_ranges(self, range1: Tuple[float, float], range2: Tuple[float, float]) -> Tuple[float, float]:
        """Merge two ranges by taking their intersection."""
        return (max(range1[0], range2[0]), min(range1[1], range2[1]))
    
    def _merge_resources(self, res1: Dict[str, float], res2: Dict[str, float]) -> Dict[str, float]:
        """Merge resource dictionaries, averaging values for shared resources."""
        result = res1.copy()
        
        for resource, value in res2.items():
            if resource in result:
                # Average the values
                result[resource] = (result[resource] + value) / 2
            else:
                # Just add the new resource
                result[resource] = value
                
        return result
    
    def _blend_colors(self, color1: str, color2: str) -> str:
        """Blend two hex colors together."""
        # Convert hex to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) / 255.0 for i in (0, 2, 4))
            
        # Convert RGB to hex
        def rgb_to_hex(rgb_tuple):
            return '#{:02x}{:02x}{:02x}'.format(
                int(rgb_tuple[0] * 255),
                int(rgb_tuple[1] * 255),
                int(rgb_tuple[2] * 255)
            )
            
        # Get RGB values
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        # Blend colors (simple average)
        blended = tuple((a + b) / 2 for a, b in zip(rgb1, rgb2))
        
        return rgb_to_hex(blended)
    
    def _generate_improved_rivers(self, elevation_map: np.ndarray, 
                               region_seed: int, size: int) -> np.ndarray:
        """
        Generate rivers that flow naturally from high to low elevation.
        
        Args:
            elevation_map: 2D numpy array of elevation values
            region_seed: Seed for this region's river generation
            size: Size of the region
            
        Returns:
            2D numpy array with river masks (1 for river, 0 for no river)
        """
        # Initialize rivers map
        river_map = np.zeros_like(elevation_map)
        
        # Find potential river starting points (high elevation)
        height, width = elevation_map.shape
        rng = random.Random(region_seed)
        
        # Determine number of rivers based on region size
        num_rivers = max(1, int(math.sqrt(size) / 4))
        
        # Find potential river sources (higher elevation areas)
        potential_sources = []
        for y in range(height):
            for x in range(width):
                if elevation_map[y, x] > self.config.mountain_threshold:
                    potential_sources.append((x, y))
        
        # If no suitable sources found, create some random ones
        if not potential_sources:
            for _ in range(3):
                x = rng.randint(0, width - 1)
                y = rng.randint(0, height - 1)
                potential_sources.append((x, y))
        
        # Select random sources
        sources = rng.sample(potential_sources, min(num_rivers, len(potential_sources)))
        
        # For each source, trace a river path
        for source_x, source_y in sources:
            current_x, current_y = source_x, source_y
            max_steps = width + height  # Prevent infinite loops
            steps = 0
            
            # Mark the river path
            while 0 <= current_x < width and 0 <= current_y < height and steps < max_steps:
                river_map[current_y, current_x] = 1
                
                # Define neighbors
                neighbors = []
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)]:
                    nx, ny = current_x + dx, current_y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbors.append((nx, ny, elevation_map[ny, nx]))
                
                if not neighbors:
                    break
                    
                # Find neighbor with lowest elevation
                next_x, next_y, next_elev = min(neighbors, key=lambda n: n[2])
                
                # If we can't go lower, we've reached a lake or ocean
                if next_elev >= elevation_map[current_y, current_x]:
                    break
                    
                current_x, current_y = next_x, next_y
                steps += 1
                
                # Add some randomness to river width based on elevation and distance
                if rng.random() < 0.3:
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        nx, ny = current_x + dx, current_y + dy
                        if (0 <= nx < width and 0 <= ny < height and
                            river_map[ny, nx] == 0):  # Don't overwrite existing river
                            river_map[ny, nx] = 0.7  # Lighter river weight for banks
        
        return river_map
    
    def _determine_biome(self, elevation: float, temperature: float, 
                      moisture: float, is_river: bool = False) -> str:
        """
        Determine the biome based on environmental factors.
        
        Args:
            elevation: Elevation value (0-1)
            temperature: Temperature value (0-1)
            moisture: Moisture value (0-1)
            is_river: Whether this cell is part of a river
            
        Returns:
            Biome ID string
        """
        # Handle special cases first
        if is_river:
            return "river"
        
        if elevation < 0.2:
            return "ocean"
            
        if elevation > 0.85:
            if temperature < 0.2:
                return "snow_peak"
            else:
                return "mountain"
        
        # Calculate scores for each biome based on how well it matches conditions
        scores = {}
        for biome_id, biome in self.biomes.items():
            # Skip special biomes
            if biome_id in ["ocean", "river", "mountain", "snow_peak"] or biome.is_water:
                continue
                
            # Calculate scores based on how well each factor fits
            temp_score = self._calculate_factor_score(temperature, biome.temperature_range)
            moisture_score = self._calculate_factor_score(moisture, biome.moisture_range)
            elevation_score = self._calculate_factor_score(elevation, biome.elevation_range)
            
            # Weight the factors differently
            total_score = (
                temp_score * 0.4 +
                moisture_score * 0.4 +
                elevation_score * 0.2
            )
            
            scores[biome_id] = total_score
            
        # Choose the highest scoring biome
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]
        
        # Fallback to a basic biome if no scores
        if temperature > 0.7 and moisture < 0.3:
            return "desert"
        elif temperature > 0.3 and moisture > 0.6:
            return "forest"
        else:
            return "plains"
    
    def _calculate_factor_score(self, value: float, range_tuple: Tuple[float, float]) -> float:
        """
        Calculate how well a value fits within a range.
        
        Args:
            value: Value to check
            range_tuple: (min, max) range
            
        Returns:
            Score from 0 to 1, where 1 is a perfect fit
        """
        min_val, max_val = range_tuple
        
        # If value is within range, perfect score
        if min_val <= value <= max_val:
            # Bonus for being near the middle of the range
            mid_point = (min_val + max_val) / 2
            distance_from_mid = abs(value - mid_point) / (max_val - min_val) if max_val > min_val else 0
            return 1.0 - (distance_from_mid * 0.2)  # Small penalty for being away from middle
        
        # If outside range, score decreases with distance
        if value < min_val:
            return max(0, 1.0 - (min_val - value) * 2)
        else:  # value > max_val
            return max(0, 1.0 - (value - max_val) * 2)
    
    def get_biome_info(self, biome_id: str) -> Optional[BiomeInfo]:
        """
        Get information about a specific biome.
        
        Args:
            biome_id: The ID of the biome
            
        Returns:
            BiomeInfo object or None if not found
        """
        return self.biomes.get(biome_id)
    
    def get_all_biomes(self) -> Dict[str, BiomeInfo]:
        """
        Get information about all available biomes.
        
        Returns:
            Dictionary mapping biome IDs to BiomeInfo objects
        """
        return self.biomes 