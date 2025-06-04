"""
POI Generator Service

Handles procedural POI creation, placement algorithms, and world generation
integration for creating realistic and balanced POI distributions.
"""

from typing import Dict, List, Optional, Tuple, Set, Any, Callable
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
import logging
from datetime import datetime
import random
import math

from backend.infrastructure.systems.poi.models import PoiEntity, POIType, POIState
from backend.infrastructure.database.database_service import get_database_service
from backend.infrastructure.events.services.event_dispatcher import EventDispatcher
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class GenerationType(str, Enum):
    """Types of POI generation algorithms"""
    RANDOM = "random"
    CLUSTERED = "clustered"
    GRID_BASED = "grid_based"
    NOISE_BASED = "noise_based"
    RIVER_FOLLOWING = "river_following"
    ROAD_NETWORK = "road_network"
    RESOURCE_BASED = "resource_based"
    DEFENSIVE = "defensive"
    NATURAL_FEATURES = "natural_features"


class BiomeType(str, Enum):
    """Biome types that affect POI generation"""
    GRASSLAND = "grassland"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    DESERT = "desert"
    SWAMP = "swamp"
    COASTAL = "coastal"
    TUNDRA = "tundra"
    VOLCANIC = "volcanic"
    MAGICAL = "magical"


@dataclass
class GenerationRule:
    """Rules for generating specific types of POIs"""
    poi_type: POIType
    probability_base: float = 0.1
    min_distance_same_type: float = 50.0
    min_distance_any_poi: float = 20.0
    preferred_biomes: List[BiomeType] = field(default_factory=list)
    avoid_biomes: List[BiomeType] = field(default_factory=list)
    elevation_preference: Tuple[float, float] = (0.0, 1.0)
    near_water_preference: float = 0.0
    population_scaling: float = 1.0
    resource_dependencies: List[str] = field(default_factory=list)
    requires_trade_route: bool = False
    defensive_bonus: float = 0.0


@dataclass
class WorldCell:
    """Represents a cell in the world grid for generation"""
    x: float
    y: float
    biome: BiomeType = BiomeType.GRASSLAND
    elevation: float = 0.5
    water_distance: float = 1.0
    resources: List[str] = field(default_factory=list)
    defensiveness: float = 0.5
    fertility: float = 0.5
    magical_resonance: float = 0.0
    existing_pois: List[UUID] = field(default_factory=list)


@dataclass
class GenerationParameters:
    """Parameters for POI generation"""
    world_size: Tuple[float, float] = (1000.0, 1000.0)
    cell_size: float = 10.0
    total_population_target: int = 50000
    poi_density: float = 0.1
    civilization_level: float = 0.5
    magic_prevalence: float = 0.3
    trade_network_density: float = 0.5
    natural_disaster_frequency: float = 0.1
    seed: Optional[int] = None


class POIGenerator:
    """Service for procedural POI generation and placement"""
    
    def __init__(self, db_session: Optional[Session] = None):
        if db_session:
            self.db_session = db_session
        else:
            # Get a real session from the database service
            db_service = get_database_service()
            self.db_session = db_service.create_session()
        
        self.event_dispatcher = EventDispatcher.get_instance()
        
        # Generation data
        self.world_grid: Dict[Tuple[int, int], WorldCell] = {}
        self.generation_rules: Dict[POIType, GenerationRule] = {}
        self.trade_routes: List[List[Tuple[float, float]]] = []
        self.water_bodies: List[List[Tuple[float, float]]] = []
        
        # Initialize default generation rules
        self._initialize_generation_rules()
    
    def _initialize_generation_rules(self):
        """Initialize default generation rules for each POI type"""
        self.generation_rules = {
            POIType.CITY: GenerationRule(
                poi_type=POIType.CITY,
                probability_base=0.02,
                min_distance_same_type=200.0,
                min_distance_any_poi=50.0,
                preferred_biomes=[BiomeType.GRASSLAND, BiomeType.COASTAL],
                near_water_preference=0.5,
                population_scaling=2.0,
                requires_trade_route=True
            ),
            
            POIType.TOWN: GenerationRule(
                poi_type=POIType.TOWN,
                probability_base=0.05,
                min_distance_same_type=100.0,
                min_distance_any_poi=30.0,
                preferred_biomes=[BiomeType.GRASSLAND, BiomeType.FOREST],
                near_water_preference=0.3,
                population_scaling=1.5
            ),
            
            POIType.VILLAGE: GenerationRule(
                poi_type=POIType.VILLAGE,
                probability_base=0.15,
                min_distance_same_type=50.0,
                min_distance_any_poi=20.0,
                preferred_biomes=[BiomeType.GRASSLAND, BiomeType.FOREST, BiomeType.COASTAL],
                near_water_preference=0.4,
                population_scaling=1.0,
                resource_dependencies=["food", "water"]
            ),
            
            POIType.FORTRESS: GenerationRule(
                poi_type=POIType.FORTRESS,
                probability_base=0.03,
                min_distance_same_type=150.0,
                min_distance_any_poi=40.0,
                preferred_biomes=[BiomeType.MOUNTAIN, BiomeType.GRASSLAND],
                elevation_preference=(0.6, 1.0),
                defensive_bonus=0.8,
                population_scaling=0.5
            ),
            
            POIType.MINE: GenerationRule(
                poi_type=POIType.MINE,
                probability_base=0.04,
                min_distance_same_type=75.0,
                min_distance_any_poi=20.0,
                preferred_biomes=[BiomeType.MOUNTAIN, BiomeType.DESERT],
                elevation_preference=(0.5, 1.0),
                resource_dependencies=["metal", "stone"],
                population_scaling=0.6
            )
        }
    
    def generate_pois_for_region(self, region_bounds: Tuple[float, float, float, float],
                                params: GenerationParameters) -> List[PoiEntity]:
        """Generate POIs for a specific region"""
        try:
            min_x, min_y, max_x, max_y = region_bounds
            generated_pois = []
            
            # Calculate region area and target POI count
            region_area = (max_x - min_x) * (max_y - min_y)
            target_poi_count = int(region_area * params.poi_density)
            
            logger.info(f"Generating ~{target_poi_count} POIs for region {region_bounds}")
            
            # Generate POIs by type in order of importance
            poi_type_order = [POIType.CITY, POIType.FORTRESS, POIType.TOWN, POIType.VILLAGE, POIType.MINE]
            
            for poi_type in poi_type_order:
                type_pois = self._generate_pois_of_type(
                    poi_type, region_bounds, params, generated_pois
                )
                generated_pois.extend(type_pois)
            
            # Store POIs in database
            for poi in generated_pois:
                self.db_session.add(poi)
            
            self.db_session.commit()
            
            # Dispatch generation event
            self.event_dispatcher.publish({
                'type': 'pois_generated',
                'region_bounds': region_bounds,
                'poi_count': len(generated_pois),
                'timestamp': datetime.utcnow().isoformat()
            })
            
            return generated_pois
            
        except Exception as e:
            logger.error(f"Error generating POIs for region: {e}")
            return []
    
    def find_optimal_poi_location(self, poi_type: POIType, 
                                 search_area: Tuple[float, float, float, float],
                                 existing_pois: List[PoiEntity] = None,
                                 params: GenerationParameters = None) -> Optional[Tuple[float, float]]:
        """Find the optimal location for a specific POI type"""
        try:
            min_x, min_y, max_x, max_y = search_area
            existing_pois = existing_pois or []
            params = params or GenerationParameters()
            
            rule = self.generation_rules.get(poi_type)
            if not rule:
                return None
            
            best_location = None
            best_score = 0.0
            attempts = 0
            max_attempts = 1000
            
            while attempts < max_attempts:
                # Random candidate location
                x = random.uniform(min_x, max_x)
                y = random.uniform(min_y, max_y)
                
                # Check distance constraints
                if not self._check_distance_constraints(x, y, poi_type, existing_pois, rule):
                    attempts += 1
                    continue
                
                # Calculate suitability score (simplified)
                suitability = rule.probability_base * random.uniform(0.5, 1.5)
                
                if suitability > best_score:
                    best_score = suitability
                    best_location = (x, y)
                
                attempts += 1
            
            return best_location if best_score > 0.05 else None
            
        except Exception as e:
            logger.error(f"Error finding optimal POI location: {e}")
            return None
    
    def _generate_pois_of_type(self, poi_type: POIType, region_bounds: Tuple[float, float, float, float],
                              params: GenerationParameters, existing_pois: List[PoiEntity]) -> List[PoiEntity]:
        """Generate POIs of a specific type within a region"""
        generated_pois = []
        rule = self.generation_rules.get(poi_type)
        if not rule:
            return generated_pois
        
        min_x, min_y, max_x, max_y = region_bounds
        region_area = (max_x - min_x) * (max_y - min_y)
        
        # Calculate target count for this POI type
        base_count = int(region_area * rule.probability_base * params.poi_density)
        target_count = max(1, base_count)
        
        attempts = 0
        max_attempts = target_count * 50
        
        while len(generated_pois) < target_count and attempts < max_attempts:
            location = self.find_optimal_poi_location(
                poi_type, region_bounds, existing_pois + generated_pois, params
            )
            
            if location:
                poi = self._create_poi_at_location(poi_type, location[0], location[1], params)
                if poi:
                    generated_pois.append(poi)
            
            attempts += 1
        
        logger.info(f"Generated {len(generated_pois)} {poi_type.value} POIs (target: {target_count})")
        return generated_pois
    
    def _create_poi_at_location(self, poi_type: POIType, x: float, y: float,
                               params: GenerationParameters) -> Optional[PoiEntity]:
        """Create a POI entity at a specific location"""
        try:
            # Generate POI properties
            name = self._generate_poi_name(poi_type)
            description = self._generate_poi_description(poi_type)
            population = self._calculate_poi_population(poi_type, params)
            
            poi = PoiEntity(
                name=name,
                description=description,
                poi_type=poi_type.value,
                state=POIState.GROWING.value if population > 100 else POIState.ACTIVE.value,
                location_x=x,
                location_y=y,
                population=population,
                max_population=int(population * random.uniform(1.5, 3.0)),
                resources={},
                properties={
                    'generated': True,
                    'generation_seed': params.seed
                }
            )
            
            return poi
            
        except Exception as e:
            logger.error(f"Error creating POI at location: {e}")
            return None
    
    def _generate_poi_name(self, poi_type: POIType) -> str:
        """Generate a name for a POI based on its type"""
        prefixes = {
            POIType.CITY: ["New", "Great", "Old", "Royal"],
            POIType.TOWN: ["Little", "East", "West", "North", "South"],
            POIType.VILLAGE: ["Upper", "Lower", "Green", "Stone"],
            POIType.FORTRESS: ["Fort", "Castle", "Keep", "Stronghold"],
            POIType.MINE: ["Deep", "Iron", "Gold", "Stone"]
        }
        
        suffixes = {
            POIType.CITY: ["haven", "town", "burg", "grad"],
            POIType.TOWN: ["ton", "field", "bridge", "ford"],
            POIType.VILLAGE: ["ham", "worth", "by", "thorpe"],
            POIType.FORTRESS: ["guard", "hold", "watch", "wall"],
            POIType.MINE: ["mine", "pit", "shaft", "quarry"]
        }
        
        prefix = random.choice(prefixes.get(poi_type, [""]))
        suffix = random.choice(suffixes.get(poi_type, ["place"]))
        
        if prefix:
            return f"{prefix} {suffix.title()}"
        else:
            return suffix.title()
    
    def _generate_poi_description(self, poi_type: POIType) -> str:
        """Generate a description for a POI"""
        descriptions = {
            POIType.CITY: "A bustling city with busy markets and grand buildings",
            POIType.TOWN: "A growing town with expanding trade and population",
            POIType.VILLAGE: "A quiet village nestled in peaceful surroundings",
            POIType.FORTRESS: "A fortified stronghold commanding the landscape",
            POIType.MINE: "A mining operation extracting valuable resources"
        }
        
        return descriptions.get(poi_type, f"A {poi_type.value} settlement")
    
    def _calculate_poi_population(self, poi_type: POIType, params: GenerationParameters) -> int:
        """Calculate population for a POI based on type"""
        base_populations = {
            POIType.CITY: (5000, 50000),
            POIType.TOWN: (1000, 5000),
            POIType.VILLAGE: (50, 1000),
            POIType.FORTRESS: (200, 2000),
            POIType.MINE: (100, 1000)
        }
        
        min_pop, max_pop = base_populations.get(poi_type, (100, 1000))
        population = random.randint(min_pop, max_pop)
        
        # Apply civilization level modifier
        population = int(population * (0.5 + params.civilization_level))
        
        return max(min_pop // 2, population)
    
    def _check_distance_constraints(self, x: float, y: float, poi_type: POIType,
                                   existing_pois: List[PoiEntity], rule: GenerationRule) -> bool:
        """Check if a location satisfies distance constraints"""
        for poi in existing_pois:
            if not poi.location_x or not poi.location_y:
                continue
            
            distance = math.sqrt((x - poi.location_x)**2 + (y - poi.location_y)**2)
            
            # Check minimum distance to same type
            if poi.poi_type == poi_type.value and distance < rule.min_distance_same_type:
                return False
            
            # Check minimum distance to any POI
            if distance < rule.min_distance_any_poi:
                return False
        
        return True


def get_poi_generator(db_session: Optional[Session] = None) -> POIGenerator:
    """Factory function to create POIGenerator instance"""
    return POIGenerator(db_session) 