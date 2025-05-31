"""
Enhanced World Generation System for Region System

Comprehensive world generation with continent management, biome adjacency validation,
and integration with RegionMetadata, ContinentMetadata, and HexCoordinate systems.
Supports the full world generation paradigm from development_bible.md.
"""

import math
import random
import uuid
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from backend.infrastructure.utils import GenerationError
from backend.systems.region.models import (
    RegionMetadata, ContinentMetadata, RegionProfile, ResourceNode,
    HexCoordinate, RegionType, BiomeType, ClimateType, ResourceType, 
    POIType, DangerLevel, REGION_HEXES_PER_REGION,
    REGION_AREA_SQ_KM, MAJOR_POIS_PER_REGION, MINOR_POIS_PER_REGION_MIN
)

# Temporarily disable data registry import to avoid circular dependencies
# from backend.infrastructure.data import GameDataRegistry

@dataclass
class BiomeConfig:
    """Enhanced configuration for biome generation."""
    name: str
    biome_type: BiomeType
    temperature_range: Tuple[float, float]
    humidity_range: Tuple[float, float]
    elevation_range: Tuple[float, float]
    climate_types: List[ClimateType]
    features: List[str]
    resources: Dict[ResourceType, float]
    adjacent_biomes: List[BiomeType]  # Valid adjacent biomes
    transition_difficulty: float = 0.5  # How hard it is to transition to this biome
    rarity: float = 1.0  # Rarity factor (1.0 = common, 0.1 = very rare)

@dataclass  
class ContinentGenerationConfig:
    """Configuration for continent generation."""
    size_range: Tuple[int, int] = (50, 200)  # Number of regions
    climate_diversity: float = 0.7  # How diverse climates should be
    biome_clustering: float = 0.6  # How much biomes cluster together
    resource_abundance: float = 0.5  # Overall resource richness
    poi_density: float = 0.8  # POI generation density
    danger_distribution: Tuple[float, float, float] = (0.6, 0.3, 0.1)  # safe, moderate, dangerous

@dataclass
class WorldGenerationResult:
    """Result of world generation process."""
    continents: List[ContinentMetadata]
    regions: List[RegionMetadata]
    generation_stats: Dict[str, Any]
    generation_time: float
    seed_used: int

class EnhancedWorldGenerator:
    """
    Comprehensive world generation system with continent management,
    biome adjacency validation, and full model integration.
    """
    
    def __init__(self, seed: Optional[int] = None):
        self.seed = seed or random.randint(0, 1000000)
        random.seed(self.seed)
        
        # Initialize biome configurations
        self.biome_configs = self._initialize_biome_configs()
        self.biome_adjacency_rules = self._build_biome_adjacency_rules()
        
        # Generation statistics
        self.stats = {
            'regions_generated': 0,
            'continents_generated': 0,
            'biome_distribution': {},
            'resource_distribution': {},
            'poi_distribution': {}
        }

    def _initialize_biome_configs(self) -> Dict[BiomeType, BiomeConfig]:
        """Initialize comprehensive biome configurations."""
        configs = {}
        
        # Temperate Forest
        configs[BiomeType.TEMPERATE_FOREST] = BiomeConfig(
            name="Temperate Forest",
            biome_type=BiomeType.TEMPERATE_FOREST,
            temperature_range=(0.4, 0.7),
            humidity_range=(0.5, 0.8),
            elevation_range=(0.1, 0.6),
            climate_types=[ClimateType.TEMPERATE, ClimateType.OCEANIC],
            features=["dense_canopy", "wildlife", "streams"],
            resources={
                ResourceType.TIMBER: 0.9,
                ResourceType.HERBS: 0.6,
                ResourceType.GAME: 0.7,
                ResourceType.FRESH_WATER: 0.8
            },
            adjacent_biomes=[BiomeType.DECIDUOUS_FOREST, BiomeType.GRASSLAND, BiomeType.HILLS],
            transition_difficulty=0.3,
            rarity=1.0
        )
        
        # Mountains
        configs[BiomeType.MOUNTAINS] = BiomeConfig(
            name="Mountains",
            biome_type=BiomeType.MOUNTAINS,
            temperature_range=(0.1, 0.5),
            humidity_range=(0.3, 0.7),
            elevation_range=(0.7, 1.0),
            climate_types=[ClimateType.CONTINENTAL, ClimateType.POLAR],
            features=["peaks", "caves", "mineral_veins"],
            resources={
                ResourceType.STONE: 0.9,
                ResourceType.IRON: 0.7,
                ResourceType.COPPER: 0.6,
                ResourceType.GEMS: 0.3,
                ResourceType.COAL: 0.5
            },
            adjacent_biomes=[BiomeType.HILLS, BiomeType.TUNDRA, BiomeType.CONIFEROUS_FOREST],
            transition_difficulty=0.8,
            rarity=0.7
        )
        
        # Grassland
        configs[BiomeType.GRASSLAND] = BiomeConfig(
            name="Grassland",
            biome_type=BiomeType.GRASSLAND,
            temperature_range=(0.5, 0.8),
            humidity_range=(0.3, 0.6),
            elevation_range=(0.0, 0.3),
            climate_types=[ClimateType.TEMPERATE, ClimateType.CONTINENTAL],
            features=["open_plains", "wildflowers", "gentle_hills"],
            resources={
                ResourceType.FERTILE_SOIL: 0.9,
                ResourceType.GAME: 0.8,
                ResourceType.HERBS: 0.5,
                ResourceType.FRESH_WATER: 0.4
            },
            adjacent_biomes=[BiomeType.TEMPERATE_FOREST, BiomeType.PRAIRIE, BiomeType.HILLS],
            transition_difficulty=0.2,
            rarity=1.0
        )
        
        # Desert
        configs[BiomeType.DESERT] = BiomeConfig(
            name="Desert",
            biome_type=BiomeType.DESERT,
            temperature_range=(0.7, 1.0),
            humidity_range=(0.0, 0.2),
            elevation_range=(0.0, 0.4),
            climate_types=[ClimateType.ARID, ClimateType.SEMI_ARID],
            features=["dunes", "oases", "rock_formations"],
            resources={
                ResourceType.STONE: 0.7,
                ResourceType.GEMS: 0.4,
                ResourceType.RARE_EARTH: 0.3,
                ResourceType.GOLD: 0.2
            },
            adjacent_biomes=[BiomeType.SAVANNA, BiomeType.HILLS],
            transition_difficulty=0.7,
            rarity=0.6
        )
        
        # Add more biomes...
        configs[BiomeType.COASTAL] = BiomeConfig(
            name="Coastal",
            biome_type=BiomeType.COASTAL,
            temperature_range=(0.4, 0.8),
            humidity_range=(0.6, 1.0),
            elevation_range=(0.0, 0.2),
            climate_types=[ClimateType.OCEANIC, ClimateType.MEDITERRANEAN],
            features=["beaches", "cliffs", "tidal_pools"],
            resources={
                ResourceType.FISH: 0.9,
                ResourceType.FRESH_WATER: 0.6,
                ResourceType.STONE: 0.5
            },
            adjacent_biomes=[BiomeType.TEMPERATE_FOREST, BiomeType.GRASSLAND],
            transition_difficulty=0.4,
            rarity=0.8
        )
        
        # Magical biomes
        configs[BiomeType.MAGICAL_FOREST] = BiomeConfig(
            name="Magical Forest",
            biome_type=BiomeType.MAGICAL_FOREST,
            temperature_range=(0.3, 0.7),
            humidity_range=(0.5, 0.9),
            elevation_range=(0.1, 0.8),
            climate_types=[ClimateType.MAGICAL],
            features=["enchanted_groves", "ley_lines", "mystical_creatures"],
            resources={
                ResourceType.MAGICAL_CRYSTALS: 0.8,
                ResourceType.HERBS: 0.9,
                ResourceType.TIMBER: 0.6,
                ResourceType.MITHRIL: 0.2
            },
            adjacent_biomes=[BiomeType.TEMPERATE_FOREST, BiomeType.FEYWILD],
            transition_difficulty=0.9,
            rarity=0.1
        )
        
        return configs

    def _build_biome_adjacency_rules(self) -> Dict[BiomeType, Set[BiomeType]]:
        """Build adjacency rules from biome configurations."""
        adjacency = {}
        for biome_type, config in self.biome_configs.items():
            adjacency[biome_type] = set(config.adjacent_biomes)
        return adjacency

    def generate_world(self, 
                      num_continents: int = 3,
                      continent_config: Optional[ContinentGenerationConfig] = None) -> WorldGenerationResult:
        """
        Generate a complete world with multiple continents.
        
        Args:
            num_continents: Number of continents to generate
            continent_config: Configuration for continent generation
            
        Returns:
            Complete world generation result
        """
        start_time = datetime.utcnow()
        
        if continent_config is None:
            continent_config = ContinentGenerationConfig()
        
        try:
            continents = []
            all_regions = []
            
            for i in range(num_continents):
                continent_seed = self.seed + i * 1000
                continent_result = self.generate_continent(
                    continent_id=str(uuid.uuid4()),
                    name=f"Continent {i + 1}",
                    seed=continent_seed,
                    config=continent_config
                )
                
                continents.append(continent_result.continent)
                all_regions.extend(continent_result.regions)
                self.stats['continents_generated'] += 1
            
            end_time = datetime.utcnow()
            generation_time = (end_time - start_time).total_seconds()
            
            return WorldGenerationResult(
                continents=continents,
                regions=all_regions,
                generation_stats=self.stats.copy(),
                generation_time=generation_time,
                seed_used=self.seed
            )
            
        except Exception as e:
            raise GenerationError(f"Failed to generate world: {str(e)}")

    def generate_continent(self, 
                          continent_id: str,
                          name: str,
                          seed: Optional[int] = None,
                          config: Optional[ContinentGenerationConfig] = None) -> 'ContinentGenerationResult':
        """
        Generate a complete continent with regions.
        
        Args:
            continent_id: Unique identifier for the continent
            name: Name of the continent
            seed: Seed for generation (optional)
            config: Generation configuration
            
        Returns:
            Complete continent with all regions
        """
        if seed:
            random.seed(seed)
        
        if config is None:
            config = ContinentGenerationConfig()
        
        try:
            # Determine continent size
            continent_size = random.randint(*config.size_range)
            
            # Generate continent hex grid
            continent_radius = int(math.sqrt(continent_size / math.pi))
            hex_grid = self._generate_hex_grid(continent_radius)
            
            # Generate height map
            height_map = self._generate_height_map(hex_grid, seed or self.seed)
            
            # Generate climate map
            climate_map = self._generate_climate_map(hex_grid, height_map)
            
            # Generate biome map with adjacency validation
            biome_map = self._generate_biome_map(hex_grid, height_map, climate_map, config)
            
            # Create regions from hex clusters
            regions = self._create_regions_from_biomes(
                continent_id, hex_grid, biome_map, height_map, climate_map, config
            )
            
            # Create continent metadata
            continent = self._create_continent_metadata(
                continent_id, name, regions, config, seed or self.seed
            )
            
            return ContinentGenerationResult(continent, regions)
            
        except Exception as e:
            raise GenerationError(f"Failed to generate continent: {str(e)}")

    def _generate_hex_grid(self, radius: int) -> List[HexCoordinate]:
        """Generate a hexagonal grid of coordinates."""
        hex_coords = []
        
        for q in range(-radius, radius + 1):
            r1 = max(-radius, -q - radius)
            r2 = min(radius, -q + radius)
            for r in range(r1, r2 + 1):
                hex_coords.append(HexCoordinate(q, r))
        
        return hex_coords

    def _generate_height_map(self, hex_grid: List[HexCoordinate], seed: int) -> Dict[HexCoordinate, float]:
        """Generate elevation map using improved noise generation."""
        height_map = {}
        
        # Multiple octaves of noise for realistic terrain
        for hex_coord in hex_grid:
            elevation = 0.0
            amplitude = 1.0
            frequency = 0.01
            
            # Multiple octaves
            for octave in range(4):
                noise_val = self._improved_noise(
                    hex_coord.q * frequency + seed,
                    hex_coord.r * frequency + seed
                )
                elevation += noise_val * amplitude
                amplitude *= 0.5
                frequency *= 2.0
            
            # Normalize and add some randomness
            elevation = (elevation + 1) / 2  # Normalize to 0-1
            elevation += random.uniform(-0.1, 0.1)
            height_map[hex_coord] = max(0.0, min(1.0, elevation))
        
        return height_map

    def _improved_noise(self, x: float, y: float) -> float:
        """Improved noise function for terrain generation."""
        # Simple improved noise - in a real implementation, use Perlin/Simplex noise
        return math.sin(x * 0.1) * math.cos(y * 0.1) + \
               0.5 * math.sin(x * 0.2) * math.cos(y * 0.2) + \
               0.25 * math.sin(x * 0.4) * math.cos(y * 0.4)

    def _generate_climate_map(self, 
                             hex_grid: List[HexCoordinate], 
                             height_map: Dict[HexCoordinate, float]) -> Dict[HexCoordinate, Tuple[float, float]]:
        """Generate temperature and humidity maps."""
        climate_map = {}
        
        # Find grid bounds for latitude simulation
        min_r = min(coord.r for coord in hex_grid)
        max_r = max(coord.r for coord in hex_grid)
        
        for hex_coord in hex_grid:
            # Latitude-based temperature (north is colder)
            latitude_factor = (hex_coord.r - min_r) / (max_r - min_r) if max_r != min_r else 0.5
            base_temperature = 1.0 - latitude_factor * 0.8  # Warmer at bottom
            
            # Elevation effect (higher = colder)
            elevation = height_map[hex_coord]
            temperature = base_temperature - (elevation * 0.5)
            temperature += random.uniform(-0.1, 0.1)
            temperature = max(0.0, min(1.0, temperature))
            
            # Humidity based on elevation and temperature
            base_humidity = 0.5 + (elevation * 0.3)  # Higher elevations get more precipitation
            humidity = base_humidity * (0.5 + temperature * 0.5)  # Warmer areas can hold more moisture
            humidity += random.uniform(-0.15, 0.15)
            humidity = max(0.0, min(1.0, humidity))
            
            climate_map[hex_coord] = (temperature, humidity)
        
        return climate_map

    def _generate_biome_map(self, 
                           hex_grid: List[HexCoordinate],
                           height_map: Dict[HexCoordinate, float],
                           climate_map: Dict[HexCoordinate, Tuple[float, float]],
                           config: ContinentGenerationConfig) -> Dict[HexCoordinate, BiomeType]:
        """Generate biome map with adjacency validation and clustering."""
        biome_map = {}
        
        # First pass: assign biomes based on environmental factors
        for hex_coord in hex_grid:
            elevation = height_map[hex_coord]
            temperature, humidity = climate_map[hex_coord]
            
            best_biome = self._select_biome_by_environment(elevation, temperature, humidity)
            biome_map[hex_coord] = best_biome
        
        # Second pass: validate adjacency and apply clustering
        biome_map = self._apply_biome_clustering(biome_map, hex_grid, config.biome_clustering)
        
        # Third pass: final adjacency validation
        biome_map = self._validate_biome_adjacency(biome_map, hex_grid)
        
        # Update statistics
        for biome in biome_map.values():
            self.stats['biome_distribution'][biome.value] = \
                self.stats['biome_distribution'].get(biome.value, 0) + 1
        
        return biome_map

    def _select_biome_by_environment(self, 
                                   elevation: float, 
                                   temperature: float, 
                                   humidity: float) -> BiomeType:
        """Select the best biome based on environmental factors."""
        best_biome = BiomeType.TEMPERATE_FOREST
        best_score = 0.0
        
        for biome_type, config in self.biome_configs.items():
            # Calculate environment compatibility score
            temp_score = self._calculate_range_score(temperature, config.temperature_range)
            humid_score = self._calculate_range_score(humidity, config.humidity_range)
            elev_score = self._calculate_range_score(elevation, config.elevation_range)
            
            # Weight the scores
            total_score = (temp_score * 0.4 + humid_score * 0.3 + elev_score * 0.3)
            
            # Apply rarity factor
            total_score *= config.rarity
            
            if total_score > best_score:
                best_score = total_score
                best_biome = biome_type
        
        return best_biome

    def _calculate_range_score(self, value: float, range_tuple: Tuple[float, float]) -> float:
        """Calculate how well a value fits within a range (0.0 to 1.0)."""
        min_val, max_val = range_tuple
        
        if min_val <= value <= max_val:
            return 1.0
        elif value < min_val:
            return max(0.0, 1.0 - (min_val - value))
        else:  # value > max_val
            return max(0.0, 1.0 - (value - max_val))

    def _apply_biome_clustering(self, 
                               biome_map: Dict[HexCoordinate, BiomeType],
                               hex_grid: List[HexCoordinate],
                               clustering_factor: float) -> Dict[HexCoordinate, BiomeType]:
        """Apply biome clustering to create more realistic biome distributions."""
        clustered_map = biome_map.copy()
        
        for hex_coord in hex_grid:
            neighbors = hex_coord.neighbors()
            neighbor_biomes = []
            
            for neighbor in neighbors:
                if neighbor in biome_map:
                    neighbor_biomes.append(biome_map[neighbor])
            
            if neighbor_biomes and random.random() < clustering_factor:
                # Choose the most common neighboring biome
                most_common = max(set(neighbor_biomes), key=neighbor_biomes.count)
                
                # Check if transition is valid
                if self._is_valid_biome_transition(biome_map[hex_coord], most_common):
                    clustered_map[hex_coord] = most_common
        
        return clustered_map

    def _validate_biome_adjacency(self, 
                                 biome_map: Dict[HexCoordinate, BiomeType],
                                 hex_grid: List[HexCoordinate]) -> Dict[HexCoordinate, BiomeType]:
        """Validate and fix biome adjacency violations."""
        validated_map = biome_map.copy()
        
        # Multiple passes to resolve conflicts
        for _ in range(3):
            changes_made = False
            
            for hex_coord in hex_grid:
                current_biome = validated_map[hex_coord]
                neighbors = hex_coord.neighbors()
                
                invalid_neighbors = []
                for neighbor in neighbors:
                    if neighbor in validated_map:
                        neighbor_biome = validated_map[neighbor]
                        if not self._is_valid_biome_transition(current_biome, neighbor_biome):
                            invalid_neighbors.append(neighbor)
                
                # If this hex has invalid neighbors, consider changing it
                if invalid_neighbors and len(invalid_neighbors) > len(neighbors) * 0.5:
                    # Find a valid alternative biome
                    valid_alternatives = []
                    for neighbor in neighbors:
                        if neighbor in validated_map:
                            neighbor_biome = validated_map[neighbor]
                            if neighbor_biome not in valid_alternatives:
                                valid_alternatives.append(neighbor_biome)
                    
                    for alt_biome in valid_alternatives:
                        if self._can_transition_to_biome(hex_coord, alt_biome, validated_map):
                            validated_map[hex_coord] = alt_biome
                            changes_made = True
                            break
            
            if not changes_made:
                break
        
        return validated_map

    def _is_valid_biome_transition(self, biome1: BiomeType, biome2: BiomeType) -> bool:
        """Check if two biomes can be adjacent."""
        if biome1 == biome2:
            return True
        
        # Check adjacency rules
        return (biome2 in self.biome_adjacency_rules.get(biome1, set()) or 
                biome1 in self.biome_adjacency_rules.get(biome2, set()))

    def _can_transition_to_biome(self, 
                                hex_coord: HexCoordinate,
                                target_biome: BiomeType,
                                biome_map: Dict[HexCoordinate, BiomeType]) -> bool:
        """Check if a hex can transition to a target biome without violating adjacency."""
        neighbors = hex_coord.neighbors()
        
        for neighbor in neighbors:
            if neighbor in biome_map:
                neighbor_biome = biome_map[neighbor]
                if not self._is_valid_biome_transition(target_biome, neighbor_biome):
                    return False
        
        return True

    def _create_regions_from_biomes(self,
                                   continent_id: str,
                                   hex_grid: List[HexCoordinate],
                                   biome_map: Dict[HexCoordinate, BiomeType],
                                   height_map: Dict[HexCoordinate, float],
                                   climate_map: Dict[HexCoordinate, Tuple[float, float]],
                                   config: ContinentGenerationConfig) -> List[RegionMetadata]:
        """Create regions by clustering hexes with similar biomes."""
        regions = []
        processed_hexes = set()
        region_id_counter = 1
        
        for hex_coord in hex_grid:
            if hex_coord in processed_hexes:
                continue
            
            # Start a new region cluster
            region_hexes = self._grow_region_cluster(
                hex_coord, biome_map, processed_hexes, max_size=REGION_HEXES_PER_REGION
            )
            
            if region_hexes:
                region = self._create_region_from_cluster(
                    region_id=f"{continent_id}_region_{region_id_counter}",
                    continent_id=continent_id,
                    hex_coords=region_hexes,
                    biome_map=biome_map,
                    height_map=height_map,
                    climate_map=climate_map,
                    config=config
                )
                
                regions.append(region)
                processed_hexes.update(region_hexes)
                region_id_counter += 1
                self.stats['regions_generated'] += 1
        
        return regions

    def _grow_region_cluster(self,
                            start_hex: HexCoordinate,
                            biome_map: Dict[HexCoordinate, BiomeType],
                            processed_hexes: set,
                            max_size: int) -> List[HexCoordinate]:
        """Grow a region cluster from a starting hex."""
        if start_hex in processed_hexes:
            return []
        
        target_biome = biome_map[start_hex]
        cluster = [start_hex]
        to_process = [start_hex]
        
        while to_process and len(cluster) < max_size:
            current_hex = to_process.pop(0)
            
            for neighbor in current_hex.neighbors():
                if (neighbor in biome_map and 
                    neighbor not in processed_hexes and
                    neighbor not in cluster and
                    biome_map[neighbor] == target_biome):
                    
                    cluster.append(neighbor)
                    to_process.append(neighbor)
                    
                    if len(cluster) >= max_size:
                        break
        
        return cluster

    def _create_region_from_cluster(self,
                                   region_id: str,
                                   continent_id: str,
                                   hex_coords: List[HexCoordinate],
                                   biome_map: Dict[HexCoordinate, BiomeType],
                                   height_map: Dict[HexCoordinate, float],
                                   climate_map: Dict[HexCoordinate, Tuple[float, float]],
                                   config: ContinentGenerationConfig) -> RegionMetadata:
        """Create a RegionMetadata from a cluster of hex coordinates."""
        
        # Determine dominant biome
        biome_counts = {}
        avg_elevation = 0.0
        avg_temperature = 0.0
        avg_humidity = 0.0
        
        for hex_coord in hex_coords:
            biome = biome_map[hex_coord]
            biome_counts[biome] = biome_counts.get(biome, 0) + 1
            avg_elevation += height_map[hex_coord]
            temp, humidity = climate_map[hex_coord]
            avg_temperature += temp
            avg_humidity += humidity
        
        num_hexes = len(hex_coords)
        avg_elevation /= num_hexes
        avg_temperature /= num_hexes
        avg_humidity /= num_hexes
        
        dominant_biome = max(biome_counts.items(), key=lambda x: x[1])[0]
        secondary_biomes = [b for b, count in biome_counts.items() 
                           if b != dominant_biome and count > 1]
        
        # Determine climate type
        climate = self._determine_climate_type(avg_temperature, avg_humidity, avg_elevation)
        
        # Create region profile
        profile = RegionProfile(
            dominant_biome=dominant_biome,
            secondary_biomes=secondary_biomes,
            climate=climate,
            elevation=avg_elevation * 1000,  # Convert to meters
            elevation_variance=self._calculate_elevation_variance(hex_coords, height_map),
            temperature_range=self._calculate_temperature_range(avg_temperature),
            precipitation=avg_humidity * 1200,  # Convert to mm/year
            humidity=avg_humidity,
            soil_fertility=self._calculate_soil_fertility(dominant_biome, avg_humidity),
            water_availability=self._calculate_water_availability(dominant_biome, avg_humidity)
        )
        
        # Generate resources
        resource_nodes = self._generate_region_resources(dominant_biome, hex_coords, config)
        
        # Determine region type and danger level
        region_type = self._determine_region_type(dominant_biome, len(hex_coords))
        danger_level = self._calculate_danger_level(dominant_biome, avg_elevation)
        
        # Generate region name
        region_name = self._generate_region_name(dominant_biome, region_type)
        
        return RegionMetadata(
            id=region_id,
            name=region_name,
            description=f"A {dominant_biome.value.replace('_', ' ')} region with {len(hex_coords)} hexes",
            region_type=region_type,
            profile=profile,
            hex_coordinates=hex_coords,
            area_square_km=len(hex_coords) * REGION_AREA_SQ_KM,
            continent_id=continent_id,
            resource_nodes=resource_nodes,
            danger_level=danger_level,
            population=self._estimate_population(region_type, len(hex_coords)),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

    def _determine_climate_type(self, temperature: float, humidity: float, elevation: float) -> ClimateType:
        """Determine climate type from environmental factors."""
        if elevation > 0.8:
            return ClimateType.POLAR
        elif temperature > 0.8 and humidity < 0.3:
            return ClimateType.ARID
        elif temperature > 0.8 and humidity > 0.7:
            return ClimateType.TROPICAL
        elif temperature > 0.6 and humidity < 0.5:
            return ClimateType.SEMI_ARID
        elif 0.4 < temperature < 0.7:
            return ClimateType.TEMPERATE
        elif temperature < 0.4:
            return ClimateType.CONTINENTAL
        else:
            return ClimateType.OCEANIC

    def _calculate_elevation_variance(self, 
                                    hex_coords: List[HexCoordinate],
                                    height_map: Dict[HexCoordinate, float]) -> float:
        """Calculate elevation variance for the region."""
        elevations = [height_map[coord] for coord in hex_coords]
        avg = sum(elevations) / len(elevations)
        variance = sum((e - avg) ** 2 for e in elevations) / len(elevations)
        return variance * 1000  # Convert to meters

    def _calculate_temperature_range(self, avg_temp: float) -> Tuple[float, float]:
        """Calculate temperature range in Celsius."""
        base_temp = avg_temp * 30 - 10  # Convert to Celsius range
        variation = random.uniform(5, 15)
        return (base_temp - variation, base_temp + variation)

    def _calculate_soil_fertility(self, biome: BiomeType, humidity: float) -> float:
        """Calculate soil fertility based on biome and humidity."""
        fertility_map = {
            BiomeType.GRASSLAND: 0.9,
            BiomeType.TEMPERATE_FOREST: 0.7,
            BiomeType.DECIDUOUS_FOREST: 0.8,
            BiomeType.PRAIRIE: 0.85,
            BiomeType.SAVANNA: 0.6,
            BiomeType.DESERT: 0.1,
            BiomeType.MOUNTAINS: 0.3,
            BiomeType.TUNDRA: 0.2,
            BiomeType.SWAMP: 0.5,
            BiomeType.COASTAL: 0.6
        }
        
        base_fertility = fertility_map.get(biome, 0.5)
        humidity_bonus = humidity * 0.3
        return min(1.0, base_fertility + humidity_bonus)

    def _calculate_water_availability(self, biome: BiomeType, humidity: float) -> float:
        """Calculate water availability."""
        water_map = {
            BiomeType.COASTAL: 0.9,
            BiomeType.SWAMP: 1.0,
            BiomeType.TROPICAL_RAINFOREST: 0.9,
            BiomeType.TEMPERATE_FOREST: 0.7,
            BiomeType.MOUNTAINS: 0.6,
            BiomeType.DESERT: 0.1,
            BiomeType.TUNDRA: 0.4
        }
        
        base_water = water_map.get(biome, 0.5)
        humidity_bonus = humidity * 0.4
        return min(1.0, base_water + humidity_bonus)

    def _generate_region_resources(self,
                                  dominant_biome: BiomeType,
                                  hex_coords: List[HexCoordinate],
                                  config: ContinentGenerationConfig) -> List[ResourceNode]:
        """Generate resource nodes for the region."""
        resources = []
        biome_config = self.biome_configs.get(dominant_biome)
        
        if not biome_config:
            return resources
        
        for resource_type, base_abundance in biome_config.resources.items():
            # Adjust abundance based on config
            adjusted_abundance = base_abundance * config.resource_abundance
            
            if adjusted_abundance > 0.1 and random.random() < adjusted_abundance:
                # Place resource node
                location = random.choice(hex_coords)
                
                resource_node = ResourceNode(
                    resource_type=resource_type,
                    abundance=adjusted_abundance * random.uniform(0.7, 1.3),
                    quality=random.uniform(0.4, 1.0),
                    accessibility=random.uniform(0.3, 0.9),
                    depletion_rate=random.uniform(0.001, 0.01),
                    current_reserves=1.0,
                    location=location
                )
                
                resources.append(resource_node)
                
                # Update statistics
                resource_key = resource_type.value
                self.stats['resource_distribution'][resource_key] = \
                    self.stats['resource_distribution'].get(resource_key, 0) + 1
        
        return resources

    def _determine_region_type(self, biome: BiomeType, size_hexes: int) -> RegionType:
        """Determine region type based on biome and size."""
        if biome in [BiomeType.MOUNTAINS, BiomeType.DESERT, BiomeType.TUNDRA]:
            return RegionType.WILDERNESS
        elif biome in [BiomeType.GRASSLAND, BiomeType.PRAIRIE] and size_hexes > 20:
            return RegionType.DUCHY if random.random() > 0.7 else RegionType.COUNTY
        elif biome == BiomeType.COASTAL:
            return RegionType.CITY_STATE if random.random() > 0.5 else RegionType.COUNTY
        elif biome in [BiomeType.TEMPERATE_FOREST, BiomeType.DECIDUOUS_FOREST]:
            return RegionType.COUNTY if random.random() > 0.6 else RegionType.WILDERNESS
        else:
            return RegionType.WILDERNESS

    def _calculate_danger_level(self, biome: BiomeType, elevation: float) -> DangerLevel:
        """Calculate danger level based on biome and elevation."""
        danger_map = {
            BiomeType.DESERT: DangerLevel.DANGEROUS,
            BiomeType.MOUNTAINS: DangerLevel.VERY_DANGEROUS,
            BiomeType.TUNDRA: DangerLevel.DANGEROUS,
            BiomeType.SWAMP: DangerLevel.DANGEROUS,
            BiomeType.MAGICAL_FOREST: DangerLevel.EXTREMELY_DANGEROUS,
            BiomeType.SHADOWLANDS: DangerLevel.LETHAL,
            BiomeType.GRASSLAND: DangerLevel.SAFE,
            BiomeType.PRAIRIE: DangerLevel.SAFE,
            BiomeType.COASTAL: DangerLevel.MODERATE
        }
        
        base_danger = danger_map.get(biome, DangerLevel.MODERATE)
        
        # Increase danger with elevation
        if elevation > 0.8:
            base_danger = DangerLevel(min(10, base_danger.value + 2))
        elif elevation > 0.6:
            base_danger = DangerLevel(min(10, base_danger.value + 1))
        
        return base_danger

    def _estimate_population(self, region_type: RegionType, size_hexes: int) -> int:
        """Estimate population based on region type and size."""
        base_density = {
            RegionType.CITY_STATE: 1000,
            RegionType.DUCHY: 500,
            RegionType.COUNTY: 200,
            RegionType.KINGDOM: 800,
            RegionType.TRIBAL_LANDS: 100,
            RegionType.FRONTIER: 50,
            RegionType.WILDERNESS: 10,
            RegionType.WASTELAND: 1
        }
        
        density = base_density.get(region_type, 100)
        return int(density * size_hexes * random.uniform(0.7, 1.3))

    def _generate_region_name(self, biome: BiomeType, region_type: RegionType) -> str:
        """Generate a name for the region."""
        biome_prefixes = {
            BiomeType.TEMPERATE_FOREST: ["Green", "Wood", "Forest"],
            BiomeType.MOUNTAINS: ["High", "Stone", "Peak"],
            BiomeType.GRASSLAND: ["Golden", "Wide", "Open"],
            BiomeType.DESERT: ["Sand", "Dry", "Sun"],
            BiomeType.COASTAL: ["Bay", "Shore", "Salt"],
            BiomeType.MAGICAL_FOREST: ["Mystic", "Enchanted", "Arcane"]
        }
        
        type_suffixes = {
            RegionType.KINGDOM: ["lands", "realm", "dominion"],
            RegionType.DUCHY: ["shire", "march", "vale"],
            RegionType.COUNTY: ["fields", "moor", "reach"],
            RegionType.WILDERNESS: ["wilds", "wastes", "expanse"],
            RegionType.CITY_STATE: ["port", "harbor", "crossing"]
        }
        
        prefixes = biome_prefixes.get(biome, ["Wild", "Far", "Old"])
        suffixes = type_suffixes.get(region_type, ["lands", "region", "territory"])
        
        prefix = random.choice(prefixes)
        suffix = random.choice(suffixes)
        
        return f"{prefix} {suffix.capitalize()}"

    def _create_continent_metadata(self,
                                  continent_id: str,
                                  name: str,
                                  regions: List[RegionMetadata],
                                  config: ContinentGenerationConfig,
                                  seed: int) -> ContinentMetadata:
        """Create continent metadata from generated regions."""
        
        # Calculate continent statistics
        total_area = sum(region.area_square_km for region in regions)
        climate_zones = list(set(region.profile.climate for region in regions))
        major_biomes = list(set(region.profile.dominant_biome for region in regions))
        
        # Identify major powers (largest regions by population)
        sorted_regions = sorted(regions, key=lambda r: r.population, reverse=True)
        major_powers = [r.id for r in sorted_regions[:3]]  # Top 3 by population
        
        return ContinentMetadata(
            id=continent_id,
            name=name,
            description=f"A continent with {len(regions)} regions spanning {total_area:.0f} square kilometers",
            total_area_square_km=total_area,
            climate_zones=climate_zones,
            major_biomes=major_biomes,
            major_powers=major_powers,
            political_situation="stable",
            region_ids=[region.id for region in regions],
            generation_seed=seed,
            generation_parameters={
                "size_range": config.size_range,
                "climate_diversity": config.climate_diversity,
                "biome_clustering": config.biome_clustering,
                "resource_abundance": config.resource_abundance,
                "poi_density": config.poi_density
            },
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

@dataclass
class ContinentGenerationResult:
    """Result of continent generation."""
    continent: ContinentMetadata
    regions: List[RegionMetadata]

# Backwards compatibility - keep the original WorldGenerator as an alias
WorldGenerator = EnhancedWorldGenerator

# Export enhanced functions
def validate_biome_adjacency(region1: RegionMetadata, region2: RegionMetadata) -> bool:
    """Validate if two regions have compatible biomes for adjacency."""
    generator = EnhancedWorldGenerator()
    return generator._is_valid_biome_transition(
        region1.profile.dominant_biome, 
        region2.profile.dominant_biome
    )

def generate_continent_with_validation(continent_name: str, 
                                     size_range: Tuple[int, int] = (50, 150),
                                     seed: Optional[int] = None) -> ContinentGenerationResult:
    """Generate a complete continent with full biome adjacency validation."""
    generator = EnhancedWorldGenerator(seed=seed)
    config = ContinentGenerationConfig(size_range=size_range)
    
    return generator.generate_continent(
        continent_id=str(uuid.uuid4()),
        name=continent_name,
        seed=seed,
        config=config
    )

# Keep the original attempt_rest function for backwards compatibility
def attempt_rest(region: str, poi: str) -> Dict[str, Any]:
    """
    Utility function for resting in a region/POI.
    
    Args:
        region: The region ID
        poi: The POI ID
        
    Returns:
        Dict with rest result details
    """
    from datetime import datetime
    from uuid import uuid4
    
    # Calculate rest quality based on POI safety
    rest_quality = random.uniform(0.3, 1.0)
    
    # Chance of random encounter during rest
    encounter_chance = 0.2 * (1 - rest_quality)  # Lower quality, higher encounter chance
    
    encounter = None
    if random.random() < encounter_chance:
        encounter_types = ['hostile', 'neutral', 'beneficial']
        encounter_type = random.choice(encounter_types)
        encounter = {
            'type': encounter_type,
            'description': f"A {encounter_type} encounter occurred during rest"
        }
    
    # Calculate recovery based on rest quality
    health_recovery = random.randint(5, 20) * rest_quality
    
    return {
        'rest_id': str(uuid4()),
        'timestamp': datetime.utcnow().isoformat(),
        'region_id': region,
        'poi_id': poi,
        'rest_quality': rest_quality,
        'health_recovery': health_recovery,
        'encounter': encounter,
        'success': True if not encounter or encounter.get('type') != 'hostile' else False
    } 