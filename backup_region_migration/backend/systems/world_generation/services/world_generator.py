"""
World Generation Service

Main orchestrator for creating single-continent game worlds with optional islands.
Focused on creating continent-sized worlds (100-200 regions) rather than multi-continent worlds.
"""

import math
import random
import time
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from backend.infrastructure.utils import GenerationError
from backend.systems.region.models import (
    RegionMetadata, ContinentMetadata, RegionProfile, ResourceNode,
    HexCoordinate, RegionType, BiomeType, ClimateType, ResourceType, 
    POIType, DangerLevel
)
from backend.systems.world_generation.config.biome_config import BiomeConfigManager
from backend.systems.world_generation.config.world_templates import WorldTemplateManager
from backend.systems.world_generation.algorithms.perlin_noise import PerlinNoiseGenerator
from backend.systems.world_generation.algorithms.biome_placement import BiomePlacementEngine


@dataclass
class WorldGenerationConfig:
    """Configuration for single-continent world generation."""
    # World sizing - continent-focused
    main_continent_size: Tuple[int, int] = (80, 120)  # Number of regions
    island_count: int = 3  # Additional smaller landmasses
    island_size_range: Tuple[int, int] = (5, 15)  # Regions per island
    
    # Geographic diversity
    biome_diversity: float = 0.8  # How many different biomes to include
    climate_variation: float = 0.7  # How much climate varies across the world
    elevation_complexity: float = 0.6  # How complex the terrain should be
    
    # Resource and content distribution
    resource_abundance: float = 0.5  # Overall resource richness
    poi_density: float = 0.8  # Points of interest per region
    settlement_density: float = 0.3  # Starting settlements per region
    
    # Gameplay balance
    danger_progression: Tuple[float, float, float] = (0.6, 0.3, 0.1)  # safe, moderate, dangerous
    resource_clustering: float = 0.7  # How much resources cluster together
    travel_connectivity: float = 0.8  # How well-connected regions are


@dataclass
class WorldGenerationResult:
    """Result of world generation process."""
    main_continent: ContinentMetadata
    islands: List[ContinentMetadata]
    all_regions: List[RegionMetadata]
    generation_stats: Dict[str, Any]
    generation_time: float
    seed_used: int
    config_used: WorldGenerationConfig


class WorldGenerator:
    """
    Main world generation orchestrator focused on single-continent worlds.
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
        
        # Load configuration managers
        self.biome_config = BiomeConfigManager()
        self.template_manager = WorldTemplateManager()
        
        # Initialize algorithms
        self.noise_generator = PerlinNoiseGenerator(seed=self.seed)
        self.biome_engine = BiomePlacementEngine(self.biome_config)
        
        # Generation statistics
        self.stats = {
            'regions_generated': 0,
            'continents_generated': 0,
            'islands_generated': 0,
            'biome_distribution': {},
            'resource_distribution': {},
            'poi_distribution': {},
            'generation_errors': []
        }

    def generate_world(self, 
                      config: Optional[WorldGenerationConfig] = None,
                      world_name: str = "New World") -> WorldGenerationResult:
        """
        Generate a complete single-continent world with optional islands.
        
        Args:
            config: World generation configuration
            world_name: Name for the generated world
            
        Returns:
            WorldGenerationResult with main continent and islands
        """
        start_time = time.time()
        
        if config is None:
            config = WorldGenerationConfig()
        
        try:
            # Generate main continent
            main_continent_size = random.randint(*config.main_continent_size)
            main_continent = self._generate_continent(
                name=f"{world_name} - Main Continent",
                size=main_continent_size,
                config=config,
                is_main_landmass=True
            )
            
            # Generate islands
            islands = []
            for i in range(config.island_count):
                island_size = random.randint(*config.island_size_range)
                island = self._generate_continent(
                    name=f"{world_name} - Island {i+1}",
                    size=island_size,
                    config=config,
                    is_main_landmass=False
                )
                islands.append(island)
            
            # Collect all regions
            all_regions = main_continent.regions.copy()
            for island in islands:
                all_regions.extend(island.regions)
            
            # Update generation stats
            self.stats['regions_generated'] = len(all_regions)
            self.stats['continents_generated'] = 1
            self.stats['islands_generated'] = len(islands)
            
            generation_time = time.time() - start_time
            
            return WorldGenerationResult(
                main_continent=main_continent,
                islands=islands,
                all_regions=all_regions,
                generation_stats=self.stats.copy(),
                generation_time=generation_time,
                seed_used=self.seed,
                config_used=config
            )
            
        except Exception as e:
            self.stats['generation_errors'].append(str(e))
            raise GenerationError(f"World generation failed: {str(e)}")

    def _generate_continent(self,
                           name: str,
                           size: int,
                           config: WorldGenerationConfig,
                           is_main_landmass: bool = True) -> ContinentMetadata:
        """Generate a single continent or island."""
        
        # Calculate hex grid size based on desired region count
        hex_radius = math.ceil(math.sqrt(size / 3.14))  # Approximate circular arrangement
        
        # Generate the foundational maps
        hex_grid = self._generate_hex_grid(hex_radius)
        height_map = self.noise_generator.generate_elevation_map(hex_grid)
        climate_map = self._generate_climate_map(hex_grid, height_map, config)
        biome_map = self.biome_engine.generate_biome_map(
            hex_grid, height_map, climate_map, config
        )
        
        # Create regions from the generated maps
        regions = self._create_regions_from_maps(
            hex_grid[:size],  # Limit to desired size
            biome_map,
            height_map,
            climate_map,
            config
        )
        
        # Create continent metadata
        continent_metadata = ContinentMetadata(
            id=uuid4(),
            name=name,
            description=f"Generated {'main continent' if is_main_landmass else 'island'} with {len(regions)} regions",
            total_area_square_km=sum(r.area_square_km for r in regions),
            climate_zones=list(set(r.profile.climate for r in regions)),
            major_biomes=list(set(r.profile.dominant_biome for r in regions)),
            region_ids=[r.id for r in regions],
            generation_seed=self.seed,
            generation_parameters={
                'size': size,
                'is_main_landmass': is_main_landmass,
                'biome_diversity': config.biome_diversity,
                'resource_abundance': config.resource_abundance
            }
        )
        
        # Attach regions to continent
        continent_metadata.regions = regions
        
        return continent_metadata

    def _generate_hex_grid(self, radius: int) -> List[HexCoordinate]:
        """Generate a hexagonal grid of coordinates."""
        coordinates = []
        for q in range(-radius, radius + 1):
            r1 = max(-radius, -q - radius)
            r2 = min(radius, -q + radius)
            for r in range(r1, r2 + 1):
                coordinates.append(HexCoordinate(q, r))
        return coordinates

    def _generate_climate_map(self,
                             hex_grid: List[HexCoordinate],
                             height_map: Dict[HexCoordinate, float],
                             config: WorldGenerationConfig) -> Dict[HexCoordinate, Tuple[float, float]]:
        """Generate temperature and humidity for each hex."""
        climate_map = {}
        
        for coord in hex_grid:
            # Base temperature affected by latitude (distance from center)
            latitude_factor = abs(coord.q) / len(hex_grid)
            base_temp = 0.8 - (latitude_factor * 0.6)  # Warmer at center
            
            # Elevation affects temperature (higher = cooler)
            elevation = height_map.get(coord, 0.5)
            temp_adjustment = elevation * -0.3
            temperature = max(0.0, min(1.0, base_temp + temp_adjustment))
            
            # Humidity based on distance from coast and elevation
            # Simplified: assume coastal areas are more humid
            distance_from_edge = min(abs(coord.q), abs(coord.r)) / (len(hex_grid) / 2)
            base_humidity = 0.7 - (distance_from_edge * 0.4)
            humidity_adjustment = (1.0 - elevation) * 0.2  # Lower elevation = more humid
            humidity = max(0.0, min(1.0, base_humidity + humidity_adjustment))
            
            climate_map[coord] = (temperature, humidity)
        
        return climate_map

    def _create_regions_from_maps(self,
                                 hex_coords: List[HexCoordinate],
                                 biome_map: Dict[HexCoordinate, BiomeType],
                                 height_map: Dict[HexCoordinate, float],
                                 climate_map: Dict[HexCoordinate, Tuple[float, float]],
                                 config: WorldGenerationConfig) -> List[RegionMetadata]:
        """Create region metadata from generated maps."""
        regions = []
        
        for i, coord in enumerate(hex_coords):
            # Get environmental data for this coordinate
            biome = biome_map.get(coord, BiomeType.TEMPERATE_FOREST)
            elevation = height_map.get(coord, 0.5)
            temperature, humidity = climate_map.get(coord, (0.5, 0.5))
            
            # Create region profile
            climate_type = self._determine_climate_type(temperature, humidity, elevation)
            
            profile = RegionProfile(
                dominant_biome=biome,
                climate=climate_type,
                elevation=elevation * 1000,  # Convert to meters
                temperature_range=(temperature * 40 - 10, (temperature + 0.2) * 40 - 10),
                precipitation=humidity * 1000,  # Convert to mm
                humidity=humidity,
                soil_fertility=self._calculate_soil_fertility(biome, humidity),
                water_availability=self._calculate_water_availability(biome, humidity)
            )
            
            # Generate resources based on biome
            resources = self._generate_region_resources(biome, config)
            
            # Create region metadata
            region = RegionMetadata(
                id=uuid4(),
                name=self._generate_region_name(biome, i),
                description=f"A {biome.value.replace('_', ' ')} region",
                region_type=self._determine_region_type(biome),
                profile=profile,
                hex_coordinates=[coord],
                center_coordinate=coord,
                area_square_km=random.uniform(80, 120),  # Hex size variation
                population=self._estimate_population(biome),
                resource_nodes=resources,
                danger_level=self._calculate_danger_level(biome, elevation),
                exploration_status=0.0  # Unexplored initially
            )
            
            regions.append(region)
        
        return regions

    def _determine_climate_type(self, temperature: float, humidity: float, elevation: float) -> ClimateType:
        """Determine climate type based on environmental factors."""
        if temperature > 0.8 and humidity < 0.3:
            return ClimateType.ARID
        elif temperature > 0.7 and humidity > 0.7:
            return ClimateType.TROPICAL
        elif temperature < 0.3:
            return ClimateType.POLAR
        elif elevation > 0.7:
            return ClimateType.CONTINENTAL
        elif humidity > 0.8:
            return ClimateType.OCEANIC
        else:
            return ClimateType.TEMPERATE

    def _calculate_soil_fertility(self, biome: BiomeType, humidity: float) -> float:
        """Calculate soil fertility based on biome and humidity."""
        base_fertility = {
            BiomeType.GRASSLAND: 0.9,
            BiomeType.TEMPERATE_FOREST: 0.7,
            BiomeType.DECIDUOUS_FOREST: 0.8,
            BiomeType.PRAIRIE: 0.8,
            BiomeType.SWAMP: 0.6,
            BiomeType.DESERT: 0.1,
            BiomeType.MOUNTAINS: 0.3,
            BiomeType.TUNDRA: 0.2,
            BiomeType.COASTAL: 0.6
        }.get(biome, 0.5)
        
        # Humidity bonus
        humidity_bonus = humidity * 0.2
        return min(1.0, base_fertility + humidity_bonus)

    def _calculate_water_availability(self, biome: BiomeType, humidity: float) -> float:
        """Calculate water availability based on biome and humidity."""
        base_water = {
            BiomeType.SWAMP: 1.0,
            BiomeType.COASTAL: 0.9,
            BiomeType.TEMPERATE_FOREST: 0.7,
            BiomeType.GRASSLAND: 0.5,
            BiomeType.DESERT: 0.1,
            BiomeType.MOUNTAINS: 0.6,
            BiomeType.TUNDRA: 0.4
        }.get(biome, 0.5)
        
        # Humidity directly affects water availability
        return min(1.0, base_water + (humidity * 0.3))

    def _generate_region_resources(self, biome: BiomeType, config: WorldGenerationConfig) -> List[ResourceNode]:
        """Generate resource nodes for a region based on its biome."""
        resources = []
        
        # Get biome-specific resource probabilities from config
        biome_resources = self.biome_config.get_biome_resources(biome)
        
        for resource_type, base_probability in biome_resources.items():
            # Apply global abundance modifier
            adjusted_probability = base_probability * config.resource_abundance
            
            if random.random() < adjusted_probability:
                resource = ResourceNode(
                    resource_type=resource_type,
                    abundance=random.uniform(0.3, 0.9),
                    quality=random.uniform(0.4, 0.8),
                    accessibility=random.uniform(0.5, 0.9),
                    depletion_rate=random.uniform(0.01, 0.05),
                    current_reserves=1.0
                )
                resources.append(resource)
        
        return resources

    def _determine_region_type(self, biome: BiomeType) -> RegionType:
        """Determine region type based on biome."""
        mapping = {
            BiomeType.GRASSLAND: RegionType.COUNTY,
            BiomeType.TEMPERATE_FOREST: RegionType.WILDERNESS,
            BiomeType.MOUNTAINS: RegionType.WILDERNESS,
            BiomeType.DESERT: RegionType.FRONTIER,
            BiomeType.SWAMP: RegionType.WILDERNESS,
            BiomeType.COASTAL: RegionType.DUCHY,
            BiomeType.TUNDRA: RegionType.FRONTIER
        }
        return mapping.get(biome, RegionType.WILDERNESS)

    def _calculate_danger_level(self, biome: BiomeType, elevation: float) -> DangerLevel:
        """Calculate danger level based on biome and terrain."""
        base_danger = {
            BiomeType.GRASSLAND: DangerLevel.SAFE,
            BiomeType.TEMPERATE_FOREST: DangerLevel.MODERATE,
            BiomeType.MOUNTAINS: DangerLevel.DANGEROUS,
            BiomeType.DESERT: DangerLevel.DANGEROUS,
            BiomeType.SWAMP: DangerLevel.VERY_DANGEROUS,
            BiomeType.TUNDRA: DangerLevel.DANGEROUS,
            BiomeType.COASTAL: DangerLevel.SAFE
        }.get(biome, DangerLevel.MODERATE)
        
        # High elevation increases danger
        if elevation > 0.7:
            base_danger = min(DangerLevel.LETHAL, DangerLevel(base_danger.value + 1))
        
        return base_danger

    def _estimate_population(self, biome: BiomeType) -> int:
        """Estimate initial population based on biome habitability."""
        base_population = {
            BiomeType.GRASSLAND: random.randint(1000, 5000),
            BiomeType.TEMPERATE_FOREST: random.randint(500, 2000),
            BiomeType.COASTAL: random.randint(800, 3000),
            BiomeType.MOUNTAINS: random.randint(100, 800),
            BiomeType.DESERT: random.randint(50, 500),
            BiomeType.SWAMP: random.randint(100, 600),
            BiomeType.TUNDRA: random.randint(50, 300)
        }.get(biome, random.randint(200, 1000))
        
        return base_population

    def _generate_region_name(self, biome: BiomeType, index: int) -> str:
        """Generate a name for a region based on its biome."""
        biome_prefixes = {
            BiomeType.GRASSLAND: ["Green", "Golden", "Vast", "Windswept"],
            BiomeType.TEMPERATE_FOREST: ["Deep", "Ancient", "Misty", "Whispering"],
            BiomeType.MOUNTAINS: ["High", "Jagged", "Snow-capped", "Towering"],
            BiomeType.DESERT: ["Burning", "Endless", "Shifting", "Sun-baked"],
            BiomeType.SWAMP: ["Murky", "Poisonous", "Forgotten", "Treacherous"],
            BiomeType.COASTAL: ["Windward", "Saltwater", "Tidal", "Storm-lashed"],
            BiomeType.TUNDRA: ["Frozen", "Barren", "Ice-bound", "Desolate"]
        }
        
        biome_suffixes = {
            BiomeType.GRASSLAND: ["Plains", "Meadows", "Steppes", "Fields"],
            BiomeType.TEMPERATE_FOREST: ["Woods", "Grove", "Thicket", "Glade"],
            BiomeType.MOUNTAINS: ["Peaks", "Range", "Heights", "Crags"],
            BiomeType.DESERT: ["Wastes", "Dunes", "Expanse", "Badlands"],
            BiomeType.SWAMP: ["Marsh", "Bog", "Fen", "Mire"],
            BiomeType.COASTAL: ["Coast", "Shore", "Bay", "Cliffs"],
            BiomeType.TUNDRA: ["Tundra", "Wastes", "Flats", "Reaches"]
        }
        
        prefix = random.choice(biome_prefixes.get(biome, ["Unknown"]))
        suffix = random.choice(biome_suffixes.get(biome, ["Region"]))
        
        return f"{prefix} {suffix}"


def create_world_generator(seed: Optional[int] = None) -> WorldGenerator:
    """Factory function to create a world generator."""
    return WorldGenerator(seed=seed) 