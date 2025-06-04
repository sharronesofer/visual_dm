"""
World Generation Business Service - Pure Business Logic

Main orchestrator for creating single-continent game worlds with optional islands.
Focused on creating continent-sized worlds (100-200 regions) rather than multi-continent worlds.
Integrates with game time system for ongoing world simulation.
"""

import math
import random
import time
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID, uuid4

from backend.systems.region.models import (
    RegionMetadata, ContinentMetadata, RegionProfile, ResourceNode,
    HexCoordinate, RegionType, BiomeType, ClimateType, ResourceType, 
    POIType, DangerLevel
)
from backend.systems.world_generation.models import (
    WorldGenerationConfig, CreateWorldGenerationData, WorldGenerationResult,
    WorldGenerationRecord, GeneratedWorldData,
    WorldGenerationRepository, WorldContentRepository,
    WorldGenerationConfigService, WorldGenerationValidationService
)
from backend.systems.world_generation.algorithms.perlin_noise import PerlinNoiseGenerator
from backend.systems.world_generation.algorithms.biome_placement import BiomePlacementEngine


class WorldGenerationBusinessService:
    """Service class for world generation business logic - pure business rules"""
    
    def __init__(self, 
                 world_repository: WorldGenerationRepository,
                 content_repository: WorldContentRepository,
                 config_service: WorldGenerationConfigService,
                 validation_service: WorldGenerationValidationService):
        self.world_repository = world_repository
        self.content_repository = content_repository
        self.config_service = config_service
        self.validation_service = validation_service
        
        # Generation statistics
        self.stats = {
            'regions_generated': 0,
            'continents_generated': 0,
            'islands_generated': 0,
            'biome_distribution': {},
            'resource_distribution': {},
            'poi_distribution': {},
            'generation_errors': [],
            'simulation_active': False,
            'last_simulation_tick': None
        }

    def generate_world(self, 
                      create_data: CreateWorldGenerationData) -> WorldGenerationResult:
        """
        Generate a complete single-continent world with optional islands.
        
        Args:
            create_data: World generation request data
            
        Returns:
            WorldGenerationResult with main continent and islands
        """
        start_time = time.time()
        
        config = create_data.config or WorldGenerationConfig()
        
        # Apply template if specified
        if create_data.template_name:
            config = self._apply_world_template(config, create_data.template_name)
        
        # Validate configuration
        validated_config = self.config_service.validate_generation_config(config)
        
        # Set seed for deterministic generation
        seed = config.world_seed or random.randint(0, 1000000)
        random.seed(seed)
        
        try:
            # Initialize algorithms
            noise_generator = PerlinNoiseGenerator(seed=seed)
            biome_placement_rules = self.config_service.get_biome_placement_rules()
            biome_engine = BiomePlacementEngine(biome_placement_rules)
            
            # Generate main continent
            main_continent_size = random.randint(*config.main_continent_size)
            main_continent = self._generate_continent(
                name=f"{create_data.world_name} - Main Continent",
                size=main_continent_size,
                config=config,
                noise_generator=noise_generator,
                biome_engine=biome_engine,
                is_main_landmass=True
            )
            
            # Generate islands
            islands = []
            for i in range(config.island_count):
                island_size = random.randint(*config.island_size_range)
                island = self._generate_continent(
                    name=f"{create_data.world_name} - Island {i+1}",
                    size=island_size,
                    config=config,
                    noise_generator=noise_generator,
                    biome_engine=biome_engine,
                    is_main_landmass=False
                )
                islands.append(island)
            
            # Collect all regions
            all_regions = main_continent.regions.copy()
            for island in islands:
                all_regions.extend(island.regions)
            
            # Validate generated regions
            if not self.validation_service.validate_region_constraints(all_regions):
                raise ValueError("Generated regions failed validation constraints")
            
            # Create simplified region data for API
            regions_data = self._create_simplified_regions(all_regions)
            
            # Generate full world content if requested
            npcs_data = []
            factions_data = []
            trade_routes_data = []
            
            if config.generate_full_world:
                # Generate factions first (needed for NPCs)
                factions_data = self._generate_world_factions(all_regions, config)
                
                # Generate NPCs with faction affiliations
                npcs_data = self._generate_world_npcs(all_regions, factions_data, config)
                
                # Generate trade routes and economy
                trade_routes_data = self._generate_trade_routes(all_regions, config)
                
                # Update generation stats
                self.stats['npcs_generated'] = len(npcs_data)
                self.stats['factions_generated'] = len(factions_data) 
                self.stats['trade_routes_generated'] = len(trade_routes_data)
            
            # Update generation stats
            self.stats['regions_generated'] = len(all_regions)
            self.stats['continents_generated'] = 1
            self.stats['islands_generated'] = len(islands)
            self.stats['template_used'] = create_data.template_name or 'custom'
            
            generation_time = time.time() - start_time
            
            # Business rule: Create result with all generated content
            result = WorldGenerationResult(
                main_continent=main_continent,
                islands=islands,
                all_regions=all_regions,
                regions=regions_data,
                npcs=npcs_data,
                factions=factions_data,
                trade_routes=trade_routes_data,
                generation_stats=self.stats.copy(),
                generation_time=generation_time,
                seed_used=seed,
                config_used=config
            )
            
            # Business rule: Persist world generation record if successful
            if create_data.user_id:
                self._save_world_generation_record(create_data, result)
            
            return result
            
        except Exception as e:
            self.stats['generation_errors'].append(str(e))
            raise ValueError(f"World generation failed: {str(e)}")

    def _apply_world_template(self, config: WorldGenerationConfig, template_name: str) -> WorldGenerationConfig:
        """Apply a world template to the configuration."""
        template = self.config_service.get_world_template(template_name)
        if not template:
            raise ValueError(f"Unknown world template: {template_name}")
        
        # Business rule: Template overrides config values
        template_config = template.get('config', {})
        
        # Apply template values to config
        for field, value in template_config.items():
            if hasattr(config, field):
                setattr(config, field, value)
        
        return config

    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get available world generation templates"""
        return self.config_service.get_available_templates()

    def create_single_region(self, 
                           name: str,
                           biome_type: Optional[BiomeType] = None,
                           climate_type: Optional[ClimateType] = None,
                           hex_coordinates: Optional[List[HexCoordinate]] = None,
                           config: Optional[WorldGenerationConfig] = None) -> RegionMetadata:
        """
        Create a single region with specified parameters.
        
        This is useful for creating custom regions or filling in gaps in generated worlds.
        """
        if config is None:
            config = WorldGenerationConfig()
        
        # Business rule: Generate default coordinates if not provided
        if hex_coordinates is None:
            hex_coordinates = self._generate_default_hex_coordinates()
        
        # Business rule: Determine biome and climate if not specified
        if biome_type is None:
            biome_type = BiomeType.TEMPERATE_FOREST  # Default biome
        
        if climate_type is None:
            climate_type = self._determine_climate_from_biome(biome_type)
        
        # Business rule: Calculate environmental factors
        avg_elevation = random.uniform(0.2, 0.8)
        temperature = self._calculate_temperature_for_biome(biome_type, avg_elevation)
        humidity = self._calculate_humidity_for_biome(biome_type)
        
        # Create region using business logic
        region = RegionMetadata(
            id=uuid4(),
            name=name,
            description=f"A {biome_type.value.replace('_', ' ')} region with {climate_type.value} climate",
            region_type=self._determine_region_type(biome_type),
            hex_coordinates=hex_coordinates,
            profile=RegionProfile(
                dominant_biome=biome_type,
                climate=climate_type,
                soil_fertility=self._calculate_soil_fertility(biome_type, humidity),
                water_availability=self._calculate_water_availability(biome_type, humidity),
                precipitation=humidity * 1000.0,  # Convert to mm
                humidity=humidity,
                elevation=avg_elevation * 3000.0  # Convert to meters
            ),
            danger_level=self._calculate_danger_level(biome_type, avg_elevation),
            estimated_population=self._estimate_population(biome_type),
            area_square_km=len(hex_coordinates) * 100.0,  # ~100 sq km per hex
            wealth_level=random.uniform(0.3, 0.8),
            political_stability=random.uniform(0.4, 0.9),
            exploration_status=random.uniform(0.1, 0.6),
            resource_nodes=self._generate_region_resources(biome_type, config),
            points_of_interest=[],  # POIs can be added separately if needed
            continent_id=None  # Will be set by calling system if needed
        )
        
        # Update generation statistics
        self.stats['regions_generated'] += 1
        biome_name = biome_type.value
        self.stats['biome_distribution'][biome_name] = self.stats['biome_distribution'].get(biome_name, 0) + 1
        
        return region

    def _generate_default_hex_coordinates(self) -> List[HexCoordinate]:
        """Generate default hex coordinates for a region"""
        # Business rule: Default region size is 15x15 hex grid
        coordinates = []
        for q in range(-7, 8):
            for r in range(max(-7, -q-7), min(8, -q+8)):
                s = -q - r
                coordinates.append(HexCoordinate(q=q, r=r, s=s))
        return coordinates

    def _determine_climate_from_biome(self, biome_type: BiomeType) -> ClimateType:
        """Business rule: Determine climate type based on biome"""
        biome_climate_map = {
            BiomeType.TEMPERATE_FOREST: ClimateType.TEMPERATE,
            BiomeType.DECIDUOUS_FOREST: ClimateType.TEMPERATE,
            BiomeType.CONIFEROUS_FOREST: ClimateType.CONTINENTAL,
            BiomeType.TROPICAL_RAINFOREST: ClimateType.TROPICAL,
            BiomeType.GRASSLAND: ClimateType.TEMPERATE,
            BiomeType.PRAIRIE: ClimateType.CONTINENTAL,
            BiomeType.SAVANNA: ClimateType.TROPICAL,
            BiomeType.DESERT: ClimateType.ARID,
            BiomeType.ARCTIC: ClimateType.POLAR,
            BiomeType.TUNDRA: ClimateType.POLAR,
            BiomeType.MOUNTAINS: ClimateType.CONTINENTAL,
            BiomeType.HILLS: ClimateType.TEMPERATE,
            BiomeType.SWAMP: ClimateType.SUBTROPICAL,
            BiomeType.MARSH: ClimateType.TEMPERATE,
            BiomeType.COASTAL: ClimateType.OCEANIC,
            BiomeType.ISLAND: ClimateType.OCEANIC,
        }
        return biome_climate_map.get(biome_type, ClimateType.TEMPERATE)

    def _calculate_temperature_for_biome(self, biome_type: BiomeType, elevation: float) -> float:
        """Business rule: Calculate temperature based on biome and elevation"""
        base_temperatures = {
            BiomeType.TROPICAL_RAINFOREST: 0.9,
            BiomeType.DESERT: 0.95,
            BiomeType.SAVANNA: 0.85,
            BiomeType.TEMPERATE_FOREST: 0.6,
            BiomeType.DECIDUOUS_FOREST: 0.55,
            BiomeType.GRASSLAND: 0.65,
            BiomeType.PRAIRIE: 0.6,
            BiomeType.CONIFEROUS_FOREST: 0.4,
            BiomeType.TUNDRA: 0.2,
            BiomeType.ARCTIC: 0.1,
            BiomeType.MOUNTAINS: 0.3,
            BiomeType.HILLS: 0.5,
        }
        
        base_temp = base_temperatures.get(biome_type, 0.5)
        # Business rule: Higher elevation = lower temperature
        elevation_modifier = elevation * -0.3
        return max(0.0, min(1.0, base_temp + elevation_modifier))

    def _calculate_humidity_for_biome(self, biome_type: BiomeType) -> float:
        """Business rule: Calculate humidity based on biome type"""
        biome_humidity = {
            BiomeType.TROPICAL_RAINFOREST: 0.95,
            BiomeType.SWAMP: 0.9,
            BiomeType.MARSH: 0.85,
            BiomeType.COASTAL: 0.8,
            BiomeType.TEMPERATE_FOREST: 0.7,
            BiomeType.DECIDUOUS_FOREST: 0.65,
            BiomeType.CONIFEROUS_FOREST: 0.6,
            BiomeType.GRASSLAND: 0.5,
            BiomeType.PRAIRIE: 0.45,
            BiomeType.SAVANNA: 0.4,
            BiomeType.HILLS: 0.55,
            BiomeType.MOUNTAINS: 0.5,
            BiomeType.TUNDRA: 0.3,
            BiomeType.ARCTIC: 0.2,
            BiomeType.DESERT: 0.1,
        }
        return biome_humidity.get(biome_type, 0.5)

    def _generate_continent(self,
                           name: str,
                           size: int,
                           config: WorldGenerationConfig,
                           noise_generator: PerlinNoiseGenerator,
                           biome_engine: BiomePlacementEngine,
                           is_main_landmass: bool = True) -> ContinentMetadata:
        """Generate a continent with regions using business logic"""
        
        # Business rule: Calculate continent radius from size
        radius = int(math.sqrt(size / math.pi)) + 2
        
        # Generate hex grid for continent
        hex_grid = self._generate_hex_grid(radius)
        
        # Generate height map using noise
        height_map = {}
        for coord in hex_grid:
            noise_x = coord.q * 0.1
            noise_y = coord.r * 0.1
            height = noise_generator.noise(noise_x, noise_y)
            height_map[coord] = max(0.0, min(1.0, height))
        
        # Generate climate map
        climate_map = self._generate_climate_map(hex_grid, height_map, config)
        
        # Generate biome map using business rules
        biome_map = biome_engine.generate_biome_map(hex_grid, height_map, climate_map, config)
        
        # Validate biome adjacency
        if not self.validation_service.validate_biome_adjacency(biome_map):
            raise ValueError("Generated biome map failed adjacency validation")
        
        # Create regions from maps
        regions = self._create_regions_from_maps(hex_grid, biome_map, height_map, climate_map, config)
        
        # Business rule: Limit to target size
        if len(regions) > size:
            regions = regions[:size]
        
        # Create continent metadata
        continent = ContinentMetadata(
            id=uuid4(),
            name=name,
            regions=regions,
            created_at=datetime.utcnow()
        )
        
        # Update continent references in regions
        for region in regions:
            region.continent_id = continent.id
        
        return continent

    def _generate_hex_grid(self, radius: int) -> List[HexCoordinate]:
        """Generate hex coordinates in a rough circular pattern"""
        coordinates = []
        for q in range(-radius, radius + 1):
            for r in range(max(-radius, -q-radius), min(radius + 1, -q+radius + 1)):
                s = -q - r
                # Business rule: Filter to roughly circular shape
                if abs(q) + abs(r) + abs(s) <= radius * 2:
                    coordinates.append(HexCoordinate(q=q, r=r, s=s))
        return coordinates

    def _generate_climate_map(self,
                             hex_grid: List[HexCoordinate],
                             height_map: Dict[HexCoordinate, float],
                             config: WorldGenerationConfig) -> Dict[HexCoordinate, Tuple[float, float]]:
        """Generate climate map with temperature and humidity"""
        climate_map = {}
        
        for coord in hex_grid:
            elevation = height_map.get(coord, 0.5)
            
            # Business rule: Climate varies by position and elevation
            # Simulate latitude effect (distance from center)
            distance_from_center = math.sqrt(coord.q**2 + coord.r**2)
            max_distance = max(math.sqrt(c.q**2 + c.r**2) for c in hex_grid)
            
            if max_distance > 0:
                latitude_factor = distance_from_center / max_distance
            else:
                latitude_factor = 0
            
            # Temperature decreases with distance from center (latitude) and elevation
            base_temperature = 0.8 - (latitude_factor * 0.6) - (elevation * 0.3)
            temperature = max(0.0, min(1.0, base_temperature + random.uniform(-0.1, 0.1)))
            
            # Humidity varies with climate patterns
            base_humidity = 0.6 + random.uniform(-0.3, 0.3)
            # Coastal areas are more humid
            if self._is_coastal_hex(coord, hex_grid):
                base_humidity += 0.2
            humidity = max(0.0, min(1.0, base_humidity))
            
            climate_map[coord] = (temperature, humidity)
        
        return climate_map

    def _is_coastal_hex(self, coord: HexCoordinate, hex_grid: List[HexCoordinate]) -> bool:
        """Check if a hex is on the coast (edge of landmass)"""
        # Business rule: A hex is coastal if it's near the edge of the grid
        neighbors = [
            HexCoordinate(coord.q+1, coord.r-1, coord.s),
            HexCoordinate(coord.q+1, coord.r, coord.s-1),
            HexCoordinate(coord.q, coord.r+1, coord.s-1),
            HexCoordinate(coord.q-1, coord.r+1, coord.s),
            HexCoordinate(coord.q-1, coord.r, coord.s+1),
            HexCoordinate(coord.q, coord.r-1, coord.s+1),
        ]
        
        # If any neighbor is not in the grid, this hex is coastal
        for neighbor in neighbors:
            if neighbor not in hex_grid:
                return True
        return False

    def _create_regions_from_maps(self,
                                 hex_coords: List[HexCoordinate],
                                 biome_map: Dict[HexCoordinate, BiomeType],
                                 height_map: Dict[HexCoordinate, float],
                                 climate_map: Dict[HexCoordinate, Tuple[float, float]],
                                 config: WorldGenerationConfig) -> List[RegionMetadata]:
        """Create region metadata from generated maps"""
        regions = []
        
        for coord in hex_coords:
            biome = biome_map.get(coord, BiomeType.TEMPERATE_FOREST)
            elevation = height_map.get(coord, 0.5)
            temperature, humidity = climate_map.get(coord, (0.5, 0.5))
            
            # Determine climate type
            climate_type = self._determine_climate_type(temperature, humidity, elevation)
            
            # Create region
            region = RegionMetadata(
                id=uuid4(),
                name=self._generate_region_name(biome, len(regions) + 1),
                description=f"A {biome.value.replace('_', ' ')} region",
                region_type=self._determine_region_type(biome),
                hex_coordinates=[coord],  # Each region gets one hex for now
                profile=RegionProfile(
                    dominant_biome=biome,
                    climate=climate_type,
                    soil_fertility=self._calculate_soil_fertility(biome, humidity),
                    water_availability=self._calculate_water_availability(biome, humidity),
                    precipitation=humidity * 1000.0,
                    humidity=humidity,
                    elevation=elevation * 3000.0  # Convert to meters
                ),
                danger_level=self._calculate_danger_level(biome, elevation),
                estimated_population=self._estimate_population(biome),
                area_square_km=100.0,  # ~100 sq km per hex
                wealth_level=random.uniform(0.3, 0.8),
                political_stability=random.uniform(0.4, 0.9),
                exploration_status=random.uniform(0.1, 0.6),
                resource_nodes=self._generate_region_resources(biome, config),
                points_of_interest=[]
            )
            
            regions.append(region)
        
        return regions

    def _determine_climate_type(self, temperature: float, humidity: float, elevation: float) -> ClimateType:
        """Business rule: Determine climate type from environmental factors"""
        if temperature > 0.8:
            if humidity > 0.7:
                return ClimateType.TROPICAL
            else:
                return ClimateType.ARID
        elif temperature > 0.6:
            if humidity > 0.6:
                return ClimateType.SUBTROPICAL
            else:
                return ClimateType.SEMI_ARID
        elif temperature > 0.4:
            if humidity > 0.5:
                return ClimateType.TEMPERATE
            else:
                return ClimateType.CONTINENTAL
        elif temperature > 0.2:
            return ClimateType.CONTINENTAL
        else:
            return ClimateType.POLAR

    def _calculate_soil_fertility(self, biome: BiomeType, humidity: float) -> float:
        """Business rule: Calculate soil fertility based on biome and humidity"""
        base_fertility = {
            BiomeType.TEMPERATE_FOREST: 0.8,
            BiomeType.DECIDUOUS_FOREST: 0.7,
            BiomeType.GRASSLAND: 0.9,
            BiomeType.PRAIRIE: 0.85,
            BiomeType.TROPICAL_RAINFOREST: 0.6,  # Nutrients leached by rain
            BiomeType.SAVANNA: 0.7,
            BiomeType.SWAMP: 0.5,  # Waterlogged
            BiomeType.MARSH: 0.4,
            BiomeType.DESERT: 0.2,
            BiomeType.TUNDRA: 0.3,
            BiomeType.ARCTIC: 0.1,
            BiomeType.MOUNTAINS: 0.4,
            BiomeType.HILLS: 0.6,
            BiomeType.COASTAL: 0.7,
        }.get(biome, 0.5)
        
        # Humidity affects fertility (but too much can hurt)
        humidity_modifier = min(humidity * 0.5, 0.3) - max(0, (humidity - 0.8) * 0.5)
        return max(0.0, min(1.0, base_fertility + humidity_modifier))

    def _calculate_water_availability(self, biome: BiomeType, humidity: float) -> float:
        """Business rule: Calculate water availability"""
        base_water = {
            BiomeType.TROPICAL_RAINFOREST: 0.95,
            BiomeType.SWAMP: 1.0,
            BiomeType.MARSH: 0.9,
            BiomeType.COASTAL: 0.8,
            BiomeType.TEMPERATE_FOREST: 0.7,
            BiomeType.DECIDUOUS_FOREST: 0.65,
            BiomeType.CONIFEROUS_FOREST: 0.6,
            BiomeType.GRASSLAND: 0.5,
            BiomeType.PRAIRIE: 0.45,
            BiomeType.SAVANNA: 0.4,
            BiomeType.HILLS: 0.55,
            BiomeType.MOUNTAINS: 0.6,  # Snow melt
            BiomeType.TUNDRA: 0.3,
            BiomeType.ARCTIC: 0.2,
            BiomeType.DESERT: 0.1,
        }.get(biome, 0.5)
        
        # Humidity directly affects water availability
        return max(0.0, min(1.0, base_water + humidity * 0.3))

    def _generate_region_resources(self, biome: BiomeType, config: WorldGenerationConfig) -> List[ResourceNode]:
        """Business rule: Generate resources based on biome and abundance config"""
        resources = []
        biome_resources = self.config_service.get_biome_configuration(biome.value)
        
        if not biome_resources:
            return resources
        
        resource_data = biome_resources.get('resources', {})
        
        for resource_type_str, abundance in resource_data.items():
            try:
                resource_type = ResourceType(resource_type_str)
                
                # Business rule: Generate resource if random check passes
                if random.random() < abundance * config.resource_abundance:
                    quantity = int(abundance * 100 * config.resource_abundance * random.uniform(0.5, 1.5))
                    
                    resource_node = ResourceNode(
                        id=uuid4(),
                        resource_type=resource_type,
                        quantity=max(1, quantity),
                        quality=random.uniform(0.3, 1.0)
                    )
                    resources.append(resource_node)
                    
            except ValueError:
                # Skip unknown resource types
                continue
        
        return resources

    def _determine_region_type(self, biome: BiomeType) -> RegionType:
        """Business rule: Determine region type based on biome"""
        biome_region_map = {
            BiomeType.TEMPERATE_FOREST: RegionType.WILDERNESS,
            BiomeType.DECIDUOUS_FOREST: RegionType.WILDERNESS,
            BiomeType.CONIFEROUS_FOREST: RegionType.WILDERNESS,
            BiomeType.TROPICAL_RAINFOREST: RegionType.WILDERNESS,
            BiomeType.GRASSLAND: RegionType.FRONTIER,
            BiomeType.PRAIRIE: RegionType.FRONTIER,
            BiomeType.SAVANNA: RegionType.TRIBAL_LANDS,
            BiomeType.DESERT: RegionType.WASTELAND,
            BiomeType.ARCTIC: RegionType.WASTELAND,
            BiomeType.TUNDRA: RegionType.WILDERNESS,
            BiomeType.MOUNTAINS: RegionType.WILDERNESS,
            BiomeType.HILLS: RegionType.FRONTIER,
            BiomeType.SWAMP: RegionType.WILDERNESS,
            BiomeType.MARSH: RegionType.WILDERNESS,
            BiomeType.COASTAL: RegionType.FRONTIER,
        }
        return biome_region_map.get(biome, RegionType.WILDERNESS)

    def _calculate_danger_level(self, biome: BiomeType, elevation: float) -> DangerLevel:
        """Business rule: Calculate danger level based on biome and elevation"""
        base_danger = {
            BiomeType.DESERT: 0.8,
            BiomeType.ARCTIC: 0.9,
            BiomeType.MOUNTAINS: 0.7,
            BiomeType.SWAMP: 0.6,
            BiomeType.TROPICAL_RAINFOREST: 0.5,
            BiomeType.CONIFEROUS_FOREST: 0.4,
            BiomeType.TUNDRA: 0.6,
            BiomeType.TEMPERATE_FOREST: 0.3,
            BiomeType.DECIDUOUS_FOREST: 0.2,
            BiomeType.GRASSLAND: 0.2,
            BiomeType.PRAIRIE: 0.2,
            BiomeType.SAVANNA: 0.4,
            BiomeType.HILLS: 0.3,
            BiomeType.COASTAL: 0.3,
            BiomeType.MARSH: 0.4,
        }.get(biome, 0.3)
        
        # Higher elevation = more dangerous
        danger_score = base_danger + (elevation * 0.3)
        
        if danger_score > 0.7:
            return DangerLevel.DANGEROUS
        elif danger_score > 0.4:
            return DangerLevel.MODERATE
        else:
            return DangerLevel.SAFE

    def _estimate_population(self, biome: BiomeType) -> int:
        """Business rule: Estimate population based on biome habitability"""
        population_config = self.config_service.get_population_parameters()
        base_populations = population_config.get('base_populations', {})
        
        base_pop = base_populations.get(biome.value, 500)
        
        # Add some randomness
        return int(base_pop * random.uniform(0.7, 1.3))

    def _generate_region_name(self, biome: BiomeType, index: int) -> str:
        """Business rule: Generate region names based on biome"""
        prefixes = {
            BiomeType.TEMPERATE_FOREST: ["Green", "Wild", "Ancient", "Deep"],
            BiomeType.MOUNTAINS: ["High", "Stone", "Peak", "Summit"],
            BiomeType.DESERT: ["Burning", "Golden", "Endless", "Dry"],
            BiomeType.COASTAL: ["Salt", "Harbor", "Bay", "Shore"],
            BiomeType.GRASSLAND: ["Rolling", "Wide", "Open", "Vast"],
            BiomeType.SWAMP: ["Murky", "Dark", "Misty", "Bog"],
        }
        
        suffixes = {
            BiomeType.TEMPERATE_FOREST: ["Woods", "Forest", "Grove", "Thicket"],
            BiomeType.MOUNTAINS: ["Peaks", "Range", "Heights", "Crags"],
            BiomeType.DESERT: ["Sands", "Wastes", "Dunes", "Expanse"],
            BiomeType.COASTAL: ["Coast", "Bay", "Harbor", "Shore"],
            BiomeType.GRASSLAND: ["Plains", "Fields", "Meadows", "Steppes"],
            BiomeType.SWAMP: ["Marsh", "Bog", "Fen", "Mire"],
        }
        
        prefix_list = prefixes.get(biome, ["Unknown"])
        suffix_list = suffixes.get(biome, ["Lands"])
        
        prefix = random.choice(prefix_list)
        suffix = random.choice(suffix_list)
        
        return f"{prefix} {suffix} #{index}"

    def _create_simplified_regions(self, all_regions: List[RegionMetadata]) -> List[Dict[str, Any]]:
        """Create simplified region data for API responses"""
        simplified = []
        
        for region in all_regions:
            simplified.append({
                'id': str(region.id),
                'name': region.name,
                'description': region.description,
                'biome': region.profile.dominant_biome.value,
                'climate': region.profile.climate.value,
                'danger_level': region.danger_level.value,
                'population': region.estimated_population,
                'coordinates': [{'q': coord.q, 'r': coord.r, 's': coord.s} for coord in region.hex_coordinates],
                'resources': [res.resource_type.value for res in region.resource_nodes],
                'area_km2': region.area_square_km
            })
        
        return simplified

    def _generate_world_factions(self, all_regions: List[RegionMetadata], config: WorldGenerationConfig) -> List[Dict[str, Any]]:
        """Business rule: Generate factions for the world"""
        factions = []
        
        # Business rule: Create initial factions based on config
        for i in range(config.starting_factions):
            # Choose a region for the faction's home base
            home_region = random.choice(all_regions)
            
            faction = {
                'id': str(uuid4()),
                'name': f"Faction {i+1}",
                'description': f"A faction based in {home_region.name}",
                'home_region_id': str(home_region.id),
                'type': random.choice(['political', 'mercantile', 'religious', 'military']),
                'influence': random.uniform(0.2, 0.8),
                'resources': random.uniform(0.3, 0.9),
                'members': random.randint(50, 500)
            }
            factions.append(faction)
        
        return factions

    def _generate_world_npcs(self, all_regions: List[RegionMetadata], factions_data: List[Dict[str, Any]], config: WorldGenerationConfig) -> List[Dict[str, Any]]:
        """Business rule: Generate NPCs for the world"""
        npcs = []
        
        for region in all_regions:
            # Business rule: NPC count based on population and density config
            npc_count = int(region.estimated_population * config.npc_density / 100)
            npc_count = max(1, min(npc_count, 50))  # Limit NPCs per region
            
            for i in range(npc_count):
                # Assign faction membership randomly
                faction = random.choice(factions_data) if factions_data and random.random() < 0.3 else None
                
                npc = {
                    'id': str(uuid4()),
                    'name': f"NPC {len(npcs)+1}",
                    'region_id': str(region.id),
                    'faction_id': faction['id'] if faction else None,
                    'role': random.choice(['merchant', 'guard', 'farmer', 'artisan', 'scholar']),
                    'level': random.randint(1, 10),
                    'disposition': random.choice(['friendly', 'neutral', 'hostile'])
                }
                npcs.append(npc)
        
        return npcs

    def _generate_trade_routes(self, all_regions: List[RegionMetadata], config: WorldGenerationConfig) -> List[Dict[str, Any]]:
        """Business rule: Generate trade routes between regions"""
        trade_routes = []
        
        # Business rule: Connect regions based on proximity and resources
        route_count = int(len(all_regions) * config.trade_route_density)
        
        for i in range(route_count):
            # Pick two random regions
            region_a = random.choice(all_regions)
            region_b = random.choice([r for r in all_regions if r.id != region_a.id])
            
            # Business rule: Trade value based on resource compatibility
            trade_value = random.uniform(100, 1000)
            
            route = {
                'id': str(uuid4()),
                'region_a_id': str(region_a.id),
                'region_b_id': str(region_b.id),
                'trade_goods': [res.resource_type.value for res in region_a.resource_nodes[:2]],
                'trade_value': trade_value,
                'difficulty': random.choice(['easy', 'moderate', 'difficult']),
                'frequency': random.choice(['daily', 'weekly', 'monthly'])
            }
            trade_routes.append(route)
        
        return trade_routes

    def _save_world_generation_record(self, create_data: CreateWorldGenerationData, result: WorldGenerationResult):
        """Business rule: Save world generation record for tracking"""
        record = WorldGenerationRecord(
            id=uuid4(),
            world_name=create_data.world_name,
            world_seed=result.seed_used,
            template_used=create_data.template_name,
            generation_config=result.config_used.__dict__,
            generation_stats=result.generation_stats,
            generation_time=result.generation_time,
            created_at=datetime.utcnow(),
            main_continent_id=result.main_continent.id,
            island_ids=[island.id for island in result.islands],
            region_count=len(result.all_regions),
            npc_count=len(result.npcs),
            faction_count=len(result.factions),
            trade_route_count=len(result.trade_routes)
        )
        
        self.world_repository.save_world_generation(record)
        
        # Also save the detailed content
        content_data = GeneratedWorldData(
            record=record,
            main_continent=result.main_continent,
            islands=result.islands,
            regions=result.regions,
            npcs=result.npcs,
            factions=result.factions,
            trade_routes=result.trade_routes
        )
        
        self.content_repository.save_world_content(record.id, content_data)

    def get_world_generation_by_id(self, world_id: UUID) -> Optional[WorldGenerationRecord]:
        """Get world generation record by ID"""
        return self.world_repository.get_world_generation(world_id)

    def get_world_content(self, world_id: UUID) -> Optional[GeneratedWorldData]:
        """Get complete world content by ID"""
        return self.content_repository.get_world_content(world_id)

    def list_world_generations(self, active_only: bool = False) -> List[WorldGenerationRecord]:
        """List world generation records"""
        return self.world_repository.list_world_generations(active_only)

    def get_generation_statistics(self) -> Dict[str, Any]:
        """Get current generation statistics"""
        return self.stats.copy()


def create_world_generation_business_service(
    world_repository: WorldGenerationRepository,
    content_repository: WorldContentRepository,
    config_service: WorldGenerationConfigService,
    validation_service: WorldGenerationValidationService
) -> WorldGenerationBusinessService:
    """Factory function to create world generation business service"""
    return WorldGenerationBusinessService(
        world_repository, 
        content_repository,
        config_service,
        validation_service
    ) 