"""
World Generation Service

Comprehensive world generation system with continent management, biome validation,
and procedural algorithms for the region system.
"""

import logging
import random
import math
from typing import Dict, List, Optional, Tuple, Any, Set
from uuid import UUID, uuid4
from dataclasses import dataclass
from enum import Enum

from backend.systems.region.models import (
    Region as RegionEntity,
    Continent as ContinentEntity,
    RegionMetadata,
    ContinentMetadata,
    HexCoordinate,
    RegionType,
    BiomeType,
    ClimateType,
    DangerLevel
)
from backend.systems.region.repositories.region_repository import RegionRepository
from backend.infrastructure.utils import PerlinNoise
# from backend.infrastructure.data import GameDataRegistry  # Optional import

logger = logging.getLogger(__name__)


class GenerationAlgorithm(Enum):
    """World generation algorithms"""
    PERLIN_NOISE = "perlin_noise"
    DIAMOND_SQUARE = "diamond_square"
    VORONOI = "voronoi"
    CELLULAR_AUTOMATA = "cellular_automata"


@dataclass
class BiomeRule:
    """Rules for biome adjacency and placement"""
    biome_type: RegionType
    allowed_neighbors: Set[RegionType]
    min_cluster_size: int
    max_cluster_size: int
    elevation_range: Tuple[float, float]
    temperature_range: Tuple[float, float]
    humidity_range: Tuple[float, float]
    rarity: float  # 0.0 to 1.0


@dataclass
class ContinentTemplate:
    """Template for continent generation"""
    name: str
    size_range: Tuple[int, int]  # Min/max regions
    biome_distribution: Dict[RegionType, float]
    climate_zones: List[ClimateType]
    generation_algorithm: GenerationAlgorithm
    seed_modifier: int


@dataclass
class WorldGenerationParameters:
    """Parameters for world generation"""
    world_seed: int
    continent_count: int
    total_regions: int
    biome_diversity: float
    climate_variation: float
    resource_abundance: float
    poi_density: float
    use_realistic_geography: bool


class WorldGenerationService:
    """Comprehensive world generation service"""
    
    def __init__(self, repository: RegionRepository, data_registry=None):
        self.repository = repository
        self.data_registry = data_registry  # Optional GameDataRegistry
        self.biome_rules = self._initialize_biome_rules()
        self.continent_templates = self._initialize_continent_templates()
        self.noise_generator = PerlinNoise()
        
    def _initialize_biome_rules(self) -> Dict[RegionType, BiomeRule]:
        """Initialize biome adjacency and placement rules"""
        return {
            RegionType.PLAINS: BiomeRule(
                biome_type=RegionType.PLAINS,
                allowed_neighbors={RegionType.FOREST, RegionType.HILLS, RegionType.GRASSLAND, RegionType.RIVER},
                min_cluster_size=3,
                max_cluster_size=8,
                elevation_range=(0.2, 0.6),
                temperature_range=(0.3, 0.8),
                humidity_range=(0.3, 0.7),
                rarity=0.8
            ),
            RegionType.FOREST: BiomeRule(
                biome_type=RegionType.FOREST,
                allowed_neighbors={RegionType.PLAINS, RegionType.HILLS, RegionType.MOUNTAINS, RegionType.RIVER},
                min_cluster_size=4,
                max_cluster_size=12,
                elevation_range=(0.1, 0.7),
                temperature_range=(0.4, 0.9),
                humidity_range=(0.6, 1.0),
                rarity=0.7
            ),
            RegionType.MOUNTAINS: BiomeRule(
                biome_type=RegionType.MOUNTAINS,
                allowed_neighbors={RegionType.HILLS, RegionType.FOREST, RegionType.TUNDRA},
                min_cluster_size=2,
                max_cluster_size=6,
                elevation_range=(0.7, 1.0),
                temperature_range=(0.0, 0.5),
                humidity_range=(0.2, 0.8),
                rarity=0.3
            ),
            RegionType.DESERT: BiomeRule(
                biome_type=RegionType.DESERT,
                allowed_neighbors={RegionType.PLAINS, RegionType.HILLS, RegionType.OASIS},
                min_cluster_size=3,
                max_cluster_size=10,
                elevation_range=(0.1, 0.5),
                temperature_range=(0.7, 1.0),
                humidity_range=(0.0, 0.3),
                rarity=0.4
            ),
            RegionType.SWAMP: BiomeRule(
                biome_type=RegionType.SWAMP,
                allowed_neighbors={RegionType.FOREST, RegionType.RIVER, RegionType.COAST},
                min_cluster_size=2,
                max_cluster_size=5,
                elevation_range=(0.0, 0.3),
                temperature_range=(0.5, 0.9),
                humidity_range=(0.8, 1.0),
                rarity=0.2
            ),
            RegionType.TUNDRA: BiomeRule(
                biome_type=RegionType.TUNDRA,
                allowed_neighbors={RegionType.MOUNTAINS, RegionType.TAIGA, RegionType.ICE},
                min_cluster_size=3,
                max_cluster_size=8,
                elevation_range=(0.0, 0.6),
                temperature_range=(0.0, 0.3),
                humidity_range=(0.2, 0.6),
                rarity=0.3
            )
        }
    
    def _initialize_continent_templates(self) -> List[ContinentTemplate]:
        """Initialize continent generation templates"""
        return [
            ContinentTemplate(
                name="Temperate Continent",
                size_range=(50, 120),
                biome_distribution={
                    RegionType.PLAINS: 0.3,
                    RegionType.FOREST: 0.25,
                    RegionType.HILLS: 0.2,
                    RegionType.MOUNTAINS: 0.15,
                    RegionType.RIVER: 0.1
                },
                climate_zones=[ClimateType.TEMPERATE, ClimateType.CONTINENTAL],
                generation_algorithm=GenerationAlgorithm.PERLIN_NOISE,
                seed_modifier=1000
            ),
            ContinentTemplate(
                name="Tropical Continent",
                size_range=(40, 100),
                biome_distribution={
                    RegionType.JUNGLE: 0.4,
                    RegionType.PLAINS: 0.2,
                    RegionType.SWAMP: 0.15,
                    RegionType.COAST: 0.15,
                    RegionType.RIVER: 0.1
                },
                climate_zones=[ClimateType.TROPICAL, ClimateType.SUBTROPICAL],
                generation_algorithm=GenerationAlgorithm.VORONOI,
                seed_modifier=2000
            ),
            ContinentTemplate(
                name="Arctic Continent",
                size_range=(30, 80),
                biome_distribution={
                    RegionType.TUNDRA: 0.4,
                    RegionType.TAIGA: 0.3,
                    RegionType.MOUNTAINS: 0.2,
                    RegionType.ICE: 0.1
                },
                climate_zones=[ClimateType.ARCTIC, ClimateType.SUBARCTIC],
                generation_algorithm=GenerationAlgorithm.CELLULAR_AUTOMATA,
                seed_modifier=3000
            ),
            ContinentTemplate(
                name="Arid Continent",
                size_range=(35, 90),
                biome_distribution={
                    RegionType.DESERT: 0.5,
                    RegionType.PLAINS: 0.2,
                    RegionType.HILLS: 0.15,
                    RegionType.OASIS: 0.1,
                    RegionType.COAST: 0.05
                },
                climate_zones=[ClimateType.ARID, ClimateType.SEMIARID],
                generation_algorithm=GenerationAlgorithm.DIAMOND_SQUARE,
                seed_modifier=4000
            )
        ]
    
    async def generate_world(self, parameters: WorldGenerationParameters) -> Dict[str, Any]:
        """Generate a complete world with continents and regions"""
        try:
            logger.info(f"Starting world generation with seed {parameters.world_seed}")
            random.seed(parameters.world_seed)
            
            # Generate continents
            continents = await self._generate_continents(parameters)
            
            # Generate regions for each continent
            all_regions = []
            for continent in continents:
                regions = await self._generate_continent_regions(continent, parameters)
                all_regions.extend(regions)
            
            # Validate biome adjacency
            await self._validate_and_fix_biome_adjacency(all_regions)
            
            # Generate POIs and resources
            await self._generate_pois_and_resources(all_regions, parameters)
            
            # Save to database
            saved_continents = []
            for continent_data in continents:
                saved_continent = await self.repository.create_continent(
                    name=continent_data['name'],
                    description=continent_data['description'],
                    world_seed=str(parameters.world_seed),
                    generation_algorithm=continent_data['algorithm'].value,
                    size=continent_data['size'],
                    generation_parameters=continent_data['parameters']
                )
                saved_continents.append(saved_continent)
            
            saved_regions = []
            for region_data in all_regions:
                request = CreateRegionRequest(
                    name=region_data['name'],
                    description=region_data['description'],
                    continent_id=region_data['continent_id'],
                    biome_type=region_data['biome_type'],
                    coordinates=region_data['coordinates'],
                    properties=region_data['properties']
                )
                saved_region = await self.repository.create_region(request)
                saved_regions.append(saved_region)
            
            result = {
                'world_seed': parameters.world_seed,
                'continents': len(saved_continents),
                'regions': len(saved_regions),
                'generation_time': 'completed',
                'continent_details': [
                    {
                        'id': str(c.id),
                        'name': c.name,
                        'size': c.size,
                        'algorithm': c.generation_algorithm
                    } for c in saved_continents
                ],
                'biome_distribution': self._calculate_biome_distribution(saved_regions)
            }
            
            logger.info(f"World generation completed: {len(saved_continents)} continents, {len(saved_regions)} regions")
            return result
            
        except Exception as e:
            logger.error(f"World generation failed: {str(e)}")
            raise
    
    async def _generate_continents(self, parameters: WorldGenerationParameters) -> List[Dict[str, Any]]:
        """Generate continent configurations"""
        continents = []
        regions_per_continent = parameters.total_regions // parameters.continent_count
        
        for i in range(parameters.continent_count):
            # Select template based on diversity
            template_index = i % len(self.continent_templates)
            template = self.continent_templates[template_index]
            
            # Adjust size based on parameters
            min_size, max_size = template.size_range
            size = min(max_size, max(min_size, regions_per_continent))
            
            continent = {
                'name': f"{template.name} {i + 1}",
                'description': f"Generated {template.name.lower()} using {template.generation_algorithm.value}",
                'template': template,
                'size': size,
                'algorithm': template.generation_algorithm,
                'seed': parameters.world_seed + template.seed_modifier + i,
                'parameters': {
                    'biome_diversity': parameters.biome_diversity,
                    'climate_variation': parameters.climate_variation,
                    'resource_abundance': parameters.resource_abundance
                }
            }
            continents.append(continent)
        
        return continents
    
    async def _generate_continent_regions(self, continent: Dict[str, Any], parameters: WorldGenerationParameters) -> List[Dict[str, Any]]:
        """Generate regions for a specific continent"""
        template = continent['template']
        regions = []
        
        # Generate hex grid for continent
        hex_coords = self._generate_hex_grid(continent['size'])
        
        # Generate elevation map
        elevation_map = self._generate_elevation_map(hex_coords, continent['seed'], template.generation_algorithm)
        
        # Generate climate data
        climate_map = self._generate_climate_map(hex_coords, continent['seed'], template.climate_zones)
        
        # Assign biomes based on template distribution and environmental factors
        biome_assignments = self._assign_biomes(hex_coords, elevation_map, climate_map, template)
        
        # Create region data
        for i, coord in enumerate(hex_coords):
            region = {
                'name': f"{continent['name']} Region {i + 1}",
                'description': f"Region in {continent['name']} with {biome_assignments[i].value} biome",
                'continent_id': continent['name'],  # Will be updated with actual ID after continent creation
                'coordinates': coord,
                'biome_type': biome_assignments[i],
                'elevation': elevation_map[i],
                'climate': climate_map[i],
                'properties': {
                    'generation_seed': continent['seed'],
                    'algorithm': template.generation_algorithm.value,
                    'template': template.name
                }
            }
            regions.append(region)
        
        return regions
    
    def _generate_hex_grid(self, size: int) -> List[HexCoordinate]:
        """Generate hexagonal grid coordinates for a continent"""
        coords = []
        radius = int(math.sqrt(size / math.pi))  # Approximate radius for circular continent
        
        for q in range(-radius, radius + 1):
            r1 = max(-radius, -q - radius)
            r2 = min(radius, -q + radius)
            for r in range(r1, r2 + 1):
                s = -q - r
                coords.append(HexCoordinate(q=q, r=r, s=s))
                if len(coords) >= size:
                    break
            if len(coords) >= size:
                break
        
        return coords[:size]
    
    def _generate_elevation_map(self, coords: List[HexCoordinate], seed: int, algorithm: GenerationAlgorithm) -> List[float]:
        """Generate elevation values for coordinates"""
        random.seed(seed)
        elevations = []
        
        if algorithm == GenerationAlgorithm.PERLIN_NOISE:
            for coord in coords:
                noise_val = self.noise_generator.noise(coord.q * 0.1, coord.r * 0.1, seed)
                elevation = (noise_val + 1) / 2  # Normalize to 0-1
                elevations.append(max(0.0, min(1.0, elevation)))
        
        elif algorithm == GenerationAlgorithm.DIAMOND_SQUARE:
            # Simplified diamond-square for hex grid
            for coord in coords:
                distance_from_center = math.sqrt(coord.q**2 + coord.r**2 + coord.s**2)
                base_elevation = 1.0 - (distance_from_center / 10.0)
                noise = random.uniform(-0.3, 0.3)
                elevation = max(0.0, min(1.0, base_elevation + noise))
                elevations.append(elevation)
        
        elif algorithm == GenerationAlgorithm.CELLULAR_AUTOMATA:
            # Generate using cellular automata rules
            for coord in coords:
                # Simple cellular automata approximation
                cell_value = random.random()
                if cell_value > 0.6:
                    elevation = random.uniform(0.7, 1.0)  # High elevation
                elif cell_value > 0.3:
                    elevation = random.uniform(0.3, 0.7)  # Medium elevation
                else:
                    elevation = random.uniform(0.0, 0.3)  # Low elevation
                elevations.append(elevation)
        
        else:  # VORONOI
            # Voronoi-based elevation
            for coord in coords:
                # Distance to nearest "seed point"
                seed_points = [(random.randint(-5, 5), random.randint(-5, 5)) for _ in range(5)]
                min_distance = min(math.sqrt((coord.q - sx)**2 + (coord.r - sy)**2) for sx, sy in seed_points)
                elevation = 1.0 - (min_distance / 10.0)
                elevations.append(max(0.0, min(1.0, elevation)))
        
        return elevations
    
    def _generate_climate_map(self, coords: List[HexCoordinate], seed: int, climate_zones: List[ClimateType]) -> List[ClimateType]:
        """Generate climate zones for coordinates"""
        random.seed(seed)
        climate_map = []
        
        for coord in coords:
            # Assign climate based on position and randomness
            distance_from_center = math.sqrt(coord.q**2 + coord.r**2)
            
            if distance_from_center < 3:
                # Central regions get primary climate
                climate = climate_zones[0] if climate_zones else ClimateType.TEMPERATE
            elif distance_from_center < 6:
                # Middle regions get secondary climate
                climate = climate_zones[1] if len(climate_zones) > 1 else climate_zones[0]
            else:
                # Outer regions get random climate from available
                climate = random.choice(climate_zones) if climate_zones else ClimateType.TEMPERATE
            
            climate_map.append(climate)
        
        return climate_map
    
    def _assign_biomes(self, coords: List[HexCoordinate], elevations: List[float], 
                      climates: List[ClimateType], template: ContinentTemplate) -> List[RegionType]:
        """Assign biomes based on environmental factors and template distribution"""
        biomes = []
        
        # Create weighted biome list based on template distribution
        weighted_biomes = []
        for biome, weight in template.biome_distribution.items():
            count = int(weight * len(coords))
            weighted_biomes.extend([biome] * count)
        
        # Fill remaining slots with random biomes
        while len(weighted_biomes) < len(coords):
            biome = random.choice(list(template.biome_distribution.keys()))
            weighted_biomes.append(biome)
        
        # Shuffle and assign
        random.shuffle(weighted_biomes)
        
        for i, coord in enumerate(coords):
            elevation = elevations[i]
            climate = climates[i]
            
            # Get suggested biome from template
            suggested_biome = weighted_biomes[i] if i < len(weighted_biomes) else RegionType.PLAINS
            
            # Validate biome against environmental constraints
            if suggested_biome in self.biome_rules:
                rule = self.biome_rules[suggested_biome]
                elev_min, elev_max = rule.elevation_range
                
                # Check if elevation is suitable
                if elev_min <= elevation <= elev_max:
                    biomes.append(suggested_biome)
                else:
                    # Find alternative biome that fits elevation
                    alternative = self._find_suitable_biome(elevation, climate)
                    biomes.append(alternative)
            else:
                biomes.append(suggested_biome)
        
        return biomes
    
    def _find_suitable_biome(self, elevation: float, climate: ClimateType) -> RegionType:
        """Find a biome suitable for given environmental conditions"""
        suitable_biomes = []
        
        for biome_type, rule in self.biome_rules.items():
            elev_min, elev_max = rule.elevation_range
            if elev_min <= elevation <= elev_max:
                suitable_biomes.append(biome_type)
        
        if suitable_biomes:
            return random.choice(suitable_biomes)
        else:
            # Fallback based on elevation
            if elevation > 0.7:
                return RegionType.MOUNTAINS
            elif elevation < 0.2:
                return RegionType.SWAMP
            else:
                return RegionType.PLAINS
    
    async def _validate_and_fix_biome_adjacency(self, regions: List[Dict[str, Any]]) -> None:
        """Validate and fix biome adjacency rules"""
        # Create coordinate to region mapping
        coord_to_region = {
            (r['coordinates'].q, r['coordinates'].r, r['coordinates'].s): r 
            for r in regions
        }
        
        changes_made = True
        iterations = 0
        max_iterations = 5
        
        while changes_made and iterations < max_iterations:
            changes_made = False
            iterations += 1
            
            for region in regions:
                coord = region['coordinates']
                biome = region['biome_type']
                
                if biome not in self.biome_rules:
                    continue
                
                rule = self.biome_rules[biome]
                neighbors = coord.neighbors()
                
                # Check each neighbor
                for neighbor_coord in neighbors:
                    neighbor_key = (neighbor_coord.q, neighbor_coord.r, neighbor_coord.s)
                    if neighbor_key in coord_to_region:
                        neighbor_region = coord_to_region[neighbor_key]
                        neighbor_biome = neighbor_region['biome_type']
                        
                        # Check if neighbor biome is allowed
                        if neighbor_biome not in rule.allowed_neighbors:
                            # Find a suitable replacement
                            suitable_biomes = [b for b in rule.allowed_neighbors if b in self.biome_rules]
                            if suitable_biomes:
                                new_biome = random.choice(suitable_biomes)
                                neighbor_region['biome_type'] = new_biome
                                changes_made = True
                                logger.debug(f"Fixed biome adjacency: changed {neighbor_biome} to {new_biome}")
        
        logger.info(f"Biome adjacency validation completed in {iterations} iterations")
    
    async def _generate_pois_and_resources(self, regions: List[Dict[str, Any]], parameters: WorldGenerationParameters) -> None:
        """Generate points of interest and resources for regions"""
        for region in regions:
            biome = region['biome_type']
            elevation = region['elevation']
            
            # Generate POIs based on biome and parameters
            poi_count = int(parameters.poi_density * random.uniform(1, 4))
            pois = []
            
            for _ in range(poi_count):
                poi_type = self._select_poi_type(biome, elevation)
                poi = {
                    'type': poi_type,
                    'name': f"{poi_type.title()} in {region['name']}",
                    'coordinates': {
                        'x': random.uniform(-0.5, 0.5),
                        'y': random.uniform(-0.5, 0.5)
                    },
                    'size': random.uniform(0.1, 0.3),
                    'importance': random.choice(['minor', 'major', 'legendary'])
                }
                pois.append(poi)
            
            # Generate resources based on biome
            resources = self._generate_region_resources(biome, parameters.resource_abundance)
            
            # Add to region properties
            region['properties'].update({
                'pois': pois,
                'resources': resources,
                'poi_count': len(pois),
                'resource_richness': sum(resources.values()) / len(resources) if resources else 0.0
            })
    
    def _select_poi_type(self, biome: RegionType, elevation: float) -> str:
        """Select appropriate POI type for biome and elevation"""
        poi_types = {
            RegionType.MOUNTAINS: ['cave', 'peak', 'mine', 'monastery'],
            RegionType.FOREST: ['grove', 'ruins', 'village', 'tower'],
            RegionType.PLAINS: ['settlement', 'farm', 'crossroads', 'monument'],
            RegionType.DESERT: ['oasis', 'tomb', 'caravan_stop', 'mirage'],
            RegionType.SWAMP: ['hut', 'bog', 'shrine', 'bridge'],
            RegionType.COAST: ['port', 'lighthouse', 'shipwreck', 'fishing_village']
        }
        
        available_types = poi_types.get(biome, ['landmark', 'ruins', 'camp'])
        
        # Adjust based on elevation
        if elevation > 0.8:
            high_elevation_types = ['peak', 'monastery', 'tower', 'observatory']
            available_types.extend(high_elevation_types)
        elif elevation < 0.2:
            low_elevation_types = ['marsh', 'dock', 'mill', 'bridge']
            available_types.extend(low_elevation_types)
        
        return random.choice(available_types)
    
    def _generate_region_resources(self, biome: RegionType, abundance: float) -> Dict[str, float]:
        """Generate resources for a region based on biome"""
        base_resources = {
            RegionType.MOUNTAINS: {'stone': 0.8, 'metal': 0.6, 'gems': 0.3},
            RegionType.FOREST: {'wood': 0.9, 'herbs': 0.5, 'game': 0.4},
            RegionType.PLAINS: {'grain': 0.7, 'livestock': 0.6, 'clay': 0.3},
            RegionType.DESERT: {'salt': 0.5, 'glass_sand': 0.4, 'rare_minerals': 0.2},
            RegionType.SWAMP: {'peat': 0.6, 'rare_herbs': 0.4, 'fish': 0.5},
            RegionType.COAST: {'fish': 0.8, 'salt': 0.6, 'pearls': 0.2}
        }
        
        resources = base_resources.get(biome, {'basic_materials': 0.5})
        
        # Apply abundance modifier
        modified_resources = {}
        for resource, base_amount in resources.items():
            amount = base_amount * abundance * random.uniform(0.7, 1.3)
            modified_resources[resource] = max(0.0, min(1.0, amount))
        
        return modified_resources
    
    def _calculate_biome_distribution(self, regions: List[RegionEntity]) -> Dict[str, int]:
        """Calculate biome distribution statistics"""
        distribution = {}
        for region in regions:
            biome = region.biome_type
            distribution[biome] = distribution.get(biome, 0) + 1
        return distribution
    
    async def validate_world_consistency(self) -> Dict[str, Any]:
        """Validate world consistency and return report"""
        try:
            # Get all regions and continents
            regions, _ = await self.repository.list_regions(limit=10000)
            continents, _ = await self.repository.list_continents(limit=100)
            
            validation_report = {
                'total_regions': len(regions),
                'total_continents': len(continents),
                'biome_adjacency_violations': 0,
                'orphaned_regions': 0,
                'empty_continents': 0,
                'biome_distribution': {},
                'issues': []
            }
            
            # Check biome adjacency
            coord_to_region = {
                (r.hex_q, r.hex_r, r.hex_s): r for r in regions
            }
            
            for region in regions:
                coord = HexCoordinate(q=region.hex_q, r=region.hex_r, s=region.hex_s)
                biome = RegionType(region.biome_type)
                
                if biome in self.biome_rules:
                    rule = self.biome_rules[biome]
                    neighbors = coord.neighbors()
                    
                    for neighbor_coord in neighbors:
                        neighbor_key = (neighbor_coord.q, neighbor_coord.r, neighbor_coord.s)
                        if neighbor_key in coord_to_region:
                            neighbor_region = coord_to_region[neighbor_key]
                            neighbor_biome = RegionType(neighbor_region.biome_type)
                            
                            if neighbor_biome not in rule.allowed_neighbors:
                                validation_report['biome_adjacency_violations'] += 1
                                validation_report['issues'].append(
                                    f"Biome adjacency violation: {biome.value} next to {neighbor_biome.value} at {coord}"
                                )
            
            # Check for orphaned regions (regions without valid continent)
            continent_ids = {str(c.id) for c in continents}
            for region in regions:
                if region.continent_id not in continent_ids:
                    validation_report['orphaned_regions'] += 1
                    validation_report['issues'].append(f"Orphaned region: {region.name}")
            
            # Check for empty continents
            regions_by_continent = {}
            for region in regions:
                continent_id = region.continent_id
                if continent_id not in regions_by_continent:
                    regions_by_continent[continent_id] = 0
                regions_by_continent[continent_id] += 1
            
            for continent in continents:
                continent_id = str(continent.id)
                if continent_id not in regions_by_continent:
                    validation_report['empty_continents'] += 1
                    validation_report['issues'].append(f"Empty continent: {continent.name}")
            
            # Calculate biome distribution
            for region in regions:
                biome = region.biome_type
                validation_report['biome_distribution'][biome] = validation_report['biome_distribution'].get(biome, 0) + 1
            
            validation_report['is_valid'] = (
                validation_report['biome_adjacency_violations'] == 0 and
                validation_report['orphaned_regions'] == 0 and
                validation_report['empty_continents'] == 0
            )
            
            return validation_report
            
        except Exception as e:
            logger.error(f"World validation failed: {str(e)}")
            raise


# Factory function for dependency injection
def create_world_generation_service(repository: RegionRepository) -> WorldGenerationService:
    """Create world generation service instance"""
    return WorldGenerationService(repository) 