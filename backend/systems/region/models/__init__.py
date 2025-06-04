"""
Region System Models - Pure Business Domain

This module contains pure business domain models and data structures 
for the region system without database or infrastructure dependencies.
"""

import math
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from uuid import UUID

# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class RegionType(Enum):
    """Types of regions based on geographic and political characteristics - Updated per JSON schema"""
    KINGDOM = "kingdom"
    DUCHY = "duchy"
    COUNTY = "county"
    CITY_STATE = "city_state"
    TRIBAL_LANDS = "tribal_lands"
    WILDERNESS = "wilderness"
    WASTELAND = "wasteland"
    FRONTIER = "frontier"
    DISPUTED_TERRITORY = "disputed_territory"
    NEUTRAL_ZONE = "neutral_zone"


class BiomeType(Enum):
    """Biome types for environmental characteristics - Updated per JSON schema"""
    TEMPERATE_FOREST = "temperate_forest"
    DECIDUOUS_FOREST = "deciduous_forest"
    CONIFEROUS_FOREST = "coniferous_forest"
    TROPICAL_RAINFOREST = "tropical_rainforest"
    GRASSLAND = "grassland"
    PRAIRIE = "prairie"
    SAVANNA = "savanna"
    DESERT = "desert"
    ARCTIC = "arctic"
    TUNDRA = "tundra"
    MOUNTAINS = "mountains"
    HILLS = "hills"
    SWAMP = "swamp"
    MARSH = "marsh"
    COASTAL = "coastal"
    ISLAND = "island"
    VOLCANIC = "volcanic"
    MAGICAL_FOREST = "magical_forest"
    SHADOWLANDS = "shadowlands"
    FEYWILD = "feywild"


class ClimateType(Enum):
    """Climate classifications - Updated per JSON schema"""
    TROPICAL = "tropical"
    SUBTROPICAL = "subtropical"
    TEMPERATE = "temperate"
    CONTINENTAL = "continental"
    POLAR = "polar"
    ARID = "arid"
    SEMI_ARID = "semi_arid"
    MEDITERRANEAN = "mediterranean"
    MONSOON = "monsoon"
    OCEANIC = "oceanic"
    MAGICAL = "magical"


class ResourceType(Enum):
    """Types of natural resources - Expanded per JSON schema"""
    # Precious metals and gems
    IRON = "iron"
    COPPER = "copper"
    GOLD = "gold"
    SILVER = "silver"
    GEMS = "gems"
    MITHRIL = "mithril"
    ADAMANTINE = "adamantine"
    
    # Building materials
    COAL = "coal"
    STONE = "stone"
    MARBLE = "marble"
    TIMBER = "timber"
    RARE_EARTH = "rare_earth"
    
    # Organic resources
    FERTILE_SOIL = "fertile_soil"
    FRESH_WATER = "fresh_water"
    FISH = "fish"
    GAME = "game"
    HERBS = "herbs"
    FRUITS = "fruits"
    VEGETABLES = "vegetables"
    GRAIN = "grain"
    LIVESTOCK = "livestock"
    
    # Energy resources
    OIL = "oil"
    NATURAL_GAS = "natural_gas"
    
    # Magical resources
    MAGICAL_CRYSTALS = "magical_crystals"
    MANA_CRYSTALS = "mana_crystals"
    ENCHANTED_HERBS = "enchanted_herbs"


class POIType(Enum):
    """Types of Points of Interest"""
    SETTLEMENT = "settlement"
    DUNGEON = "dungeon"
    TEMPLE = "temple"
    TOWER = "tower"
    RUIN = "ruin"
    CAMP = "camp"
    FORTRESS = "fortress"
    NATURAL_LANDMARK = "natural_landmark"
    MAGICAL_SITE = "magical_site"
    TRADING_POST = "trading_post"
    SHRINE = "shrine"
    CAVE = "cave"
    BRIDGE = "bridge"
    CROSSROADS = "crossroads"
    PORTAL = "portal"


class DangerLevel(IntEnum):
    """Danger levels for regions"""
    VERY_SAFE = 1
    SAFE = 2
    MODERATE = 3
    DANGEROUS = 4
    VERY_DANGEROUS = 5
    EXTREMELY_DANGEROUS = 6
    LETHAL = 7
    LEGENDARY = 8
    MYTHICAL = 9
    APOCALYPTIC = 10


class MetropolisType(Enum):
    """Types of metropolises - Per Bible requirements"""
    ARCANE = "arcane"
    INDUSTRIAL = "industrial" 
    SACRED = "sacred"
    RUINED = "ruined"
    NATURAL = "natural"


# ============================================================================
# COORDINATE SYSTEM MODELS
# ============================================================================

@dataclass
class HexCoordinate:
    """Hex-based coordinate system for regions and locations"""
    q: int  # Column (hex coordinate)
    r: int  # Row (hex coordinate)
    s: int = field(init=False)  # Calculated from q and r
    
    def __post_init__(self):
        """Calculate s coordinate (must satisfy q + r + s = 0)"""
        self.s = -self.q - self.r
    
    def __eq__(self, other):
        if not isinstance(other, HexCoordinate):
            return False
        return self.q == other.q and self.r == other.r
    
    def __hash__(self):
        return hash((self.q, self.r))
    
    def __str__(self):
        return f"Hex({self.q}, {self.r}, {self.s})"
    
    def distance_to(self, other: 'HexCoordinate') -> int:
        """Calculate hex distance to another coordinate"""
        return (abs(self.q - other.q) + abs(self.q + self.r - other.q - other.r) + abs(self.r - other.r)) // 2
    
    def neighbors(self) -> List['HexCoordinate']:
        """Get all six neighboring hex coordinates"""
        directions = [
            (1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)
        ]
        return [HexCoordinate(self.q + dq, self.r + dr) for dq, dr in directions]
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary for serialization"""
        return {"q": self.q, "r": self.r, "s": self.s}
    
    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> 'HexCoordinate':
        """Create from dictionary"""
        return cls(data["q"], data["r"])
    
    def to_pixel(self, hex_size: float = 1.0) -> Tuple[float, float]:
        """Convert to pixel coordinates for display"""
        x = hex_size * (3/2 * self.q)
        y = hex_size * (math.sqrt(3)/2 * self.q + math.sqrt(3) * self.r)
        return (x, y)
    
    @classmethod
    def from_pixel(cls, x: float, y: float, hex_size: float = 1.0) -> 'HexCoordinate':
        """Convert from pixel coordinates"""
        q = (2/3 * x) / hex_size
        r = (-1/3 * x + math.sqrt(3)/3 * y) / hex_size
        return cls.from_fractional(q, r)
    
    @classmethod
    def from_fractional(cls, q: float, r: float) -> 'HexCoordinate':
        """Convert from fractional coordinates with rounding"""
        s = -q - r
        
        rq = round(q)
        rr = round(r)
        rs = round(s)
        
        q_diff = abs(rq - q)
        r_diff = abs(rr - r)
        s_diff = abs(rs - s)
        
        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs
        
        return cls(rq, rr)


# ============================================================================
# RESOURCE MODELS - Enhanced per JSON schema
# ============================================================================

@dataclass
class ResourceNode:
    """Individual resource node within a region - Enhanced per JSON schema"""
    resource_type: str  # Resource type ID from JSON schema
    abundance: float  # 0.0 to 1.0
    quality: float    # 0.0 to 1.0
    accessibility: float  # 0.0 to 1.0
    depletion_rate: float = 0.0
    current_reserves: float = 1.0
    location: Optional[HexCoordinate] = None
    
    # Additional fields from JSON schema
    category: Optional[str] = None  # 'food', 'materials', 'precious', 'magical'
    base_value: float = 1.0
    weight: float = 1.0
    perishable: bool = False
    preservation_methods: List[str] = field(default_factory=list)
    uses: List[str] = field(default_factory=list)
    
    def calculate_value(self) -> float:
        """Calculate the economic value of this resource node"""
        base_value = self.abundance * self.quality * self.accessibility * self.current_reserves
        
        # Use base_value from JSON schema if available
        value_multiplier = self.base_value if self.base_value > 0 else 1.0
        
        # Enhanced value calculation with category multipliers
        category_multipliers = {
            'precious': 15.0,
            'magical': 20.0,
            'materials': 5.0,
            'food': 2.0
        }
        
        category_multiplier = category_multipliers.get(self.category, 1.0)
        return base_value * value_multiplier * category_multiplier


# ============================================================================
# REGION PROFILE MODEL
# ============================================================================

@dataclass
class RegionProfile:
    """Environmental and geographic profile of a region"""
    dominant_biome: str  # Biome type ID
    secondary_biomes: List[str] = field(default_factory=list)  # List of biome type IDs
    climate: ClimateType = ClimateType.TEMPERATE
    elevation: float = 0.0  # Average elevation in meters
    elevation_variance: float = 0.0  # Standard deviation of elevation
    temperature_range: Tuple[float, float] = (10.0, 25.0)  # Min/max in Celsius
    precipitation: float = 500.0  # Annual precipitation in mm
    humidity: float = 0.5  # 0.0 to 1.0
    wind_patterns: Dict[str, Any] = field(default_factory=dict)
    seasonal_variations: Dict[str, Any] = field(default_factory=dict)
    natural_hazards: List[str] = field(default_factory=list)
    soil_fertility: float = 0.5  # 0.0 to 1.0
    water_availability: float = 0.5  # 0.0 to 1.0
    
    # Additional fields from JSON schema biome definitions
    fertility_modifier: float = 1.0
    water_availability_modifier: float = 1.0
    traversal_difficulty: float = 0.5  # 0.0 to 1.0
    resource_abundance: List[str] = field(default_factory=list)
    typical_climates: List[str] = field(default_factory=list)
    danger_sources: List[str] = field(default_factory=list)
    
    def calculate_habitability(self) -> float:
        """Calculate overall habitability score"""
        factors = [
            self.soil_fertility * self.fertility_modifier,
            self.water_availability * self.water_availability_modifier,
            1.0 - abs(0.5 - self.humidity),  # Optimal humidity around 0.5
            1.0 - (self.traversal_difficulty * 0.5),  # Easier traversal = more habitable
            1.0 if len(self.natural_hazards) == 0 else 0.5  # Penalty for natural hazards
        ]
        
        base_score = sum(factors) / len(factors)
        return min(1.0, max(0.0, base_score))


# ============================================================================
# COMPREHENSIVE REGION METADATA - Updated per Bible
# ============================================================================

@dataclass
class RegionMetadata:
    """Comprehensive metadata for a region - Updated per Bible requirements"""
    id: Union[str, UUID]
    name: str
    description: str = ""
    region_type: str = "wilderness"  # Region type ID
    profile: RegionProfile = field(default_factory=lambda: RegionProfile("temperate_forest"))
    
    # Geographic data
    hex_coordinates: List[HexCoordinate] = field(default_factory=list)
    center_coordinate: Optional[HexCoordinate] = None
    area_square_km: float = 0.0
    perimeter_km: float = 0.0
    
    # Political data
    controlling_faction_id: Optional[Union[str, UUID]] = None
    government_type: str = "none"
    political_stability: float = 0.5  # 0.0 to 1.0
    law_level: int = 5  # 1-10 scale
    
    # Economic data
    wealth_level: float = 0.5  # 0.0 to 1.0
    trade_routes: List[str] = field(default_factory=list)
    primary_industries: List[str] = field(default_factory=list)
    
    # Demographic data
    population: int = 0
    population_density: float = 0.0  # People per sq km
    major_settlements: List[str] = field(default_factory=list)
    
    # Resources and features
    resource_nodes: List[ResourceNode] = field(default_factory=list)
    poi_ids: List[str] = field(default_factory=list)
    
    # Gameplay data
    danger_level: DangerLevel = DangerLevel.SAFE
    exploration_status: float = 0.0  # 0.0 to 1.0
    discovery_date: Optional[datetime] = None
    
    # Connections
    neighboring_region_ids: List[Union[str, UUID]] = field(default_factory=list)
    continent_id: Optional[Union[str, UUID]] = None
    
    # Dynamic state
    current_events: List[str] = field(default_factory=list)
    historical_events: List[str] = field(default_factory=list)
    
    # ============================================================================
    # BIBLE-REQUIRED FIELDS - Added for full compliance
    # ============================================================================
    
    # Level and terrain system
    level_range: Tuple[int, int] = (1, 5)  # Min/max level for encounters/content
    terrain_types: List[str] = field(default_factory=list)  # List of terrain types present
    
    # Faction and politics
    factions: List[str] = field(default_factory=list)  # List of influential faction IDs
    tension_level: float = 0.0  # Current tension (0-100) between factions
    
    # Capitol system per Bible
    primary_capitol_id: Optional[str] = None    # Original (birth) capitol city - never changes
    secondary_capitol_id: Optional[str] = None  # Current controlling capitol - changes with conquest
    metropolis_type: Optional[str] = None       # Arcane/Industrial/Sacred/Ruined/Natural - never changes
    
    # Narrative systems per Bible
    motif_pool: List[str] = field(default_factory=list)     # 3 unique active motif IDs
    motif_history: List[str] = field(default_factory=list)  # Previously assigned motifs
    memory: List[str] = field(default_factory=list)         # Memory/core memory objects
    arc: Optional[str] = None                               # Current active arc ID
    arc_history: List[str] = field(default_factory=list)   # Resolved/failed arcs
    history: List[str] = field(default_factory=list)       # Major region events
    
    # System state
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_total_resource_value(self) -> float:
        """Calculate total economic value of all resources"""
        return sum(node.calculate_value() for node in self.resource_nodes)
    
    def get_resource_abundance(self, resource_type_id: str) -> float:
        """Get abundance of a specific resource type"""
        nodes = [node for node in self.resource_nodes if node.resource_type == resource_type_id]
        return sum(node.abundance for node in nodes)
    
    def add_hex_coordinate(self, hex_coord: HexCoordinate):
        """Add a hex coordinate to this region"""
        if hex_coord not in self.hex_coordinates:
            self.hex_coordinates.append(hex_coord)
            self._update_geographic_data()
    
    def _update_geographic_data(self):
        """Update area and center coordinate based on hex coordinates"""
        if not self.hex_coordinates:
            return
        
        # Calculate center (average of all coordinates)
        avg_q = sum(coord.q for coord in self.hex_coordinates) / len(self.hex_coordinates)
        avg_r = sum(coord.r for coord in self.hex_coordinates) / len(self.hex_coordinates)
        self.center_coordinate = HexCoordinate.from_fractional(avg_q, avg_r)
        
        # Estimate area (each hex is approximately X square km)
        hex_area_km2 = 10.0  # Configurable
        self.area_square_km = len(self.hex_coordinates) * hex_area_km2
        
        # Update population density
        if self.area_square_km > 0:
            self.population_density = self.population / self.area_square_km
    
    # ============================================================================
    # BIBLE-COMPLIANT NARRATIVE METHODS
    # ============================================================================
    
    def add_motif(self, motif_id: str) -> bool:
        """Add a motif to the active pool (max 3 unique)"""
        if motif_id not in self.motif_pool and len(self.motif_pool) < 3:
            self.motif_pool.append(motif_id)
            return True
        return False
    
    def retire_motif(self, motif_id: str) -> bool:
        """Move a motif from active pool to history"""
        if motif_id in self.motif_pool:
            self.motif_pool.remove(motif_id)
            if motif_id not in self.motif_history:
                self.motif_history.append(motif_id)
            return True
        return False
    
    def set_primary_capitol(self, capitol_id: str):
        """Set the primary capitol (never changes after first assignment)"""
        if self.primary_capitol_id is None:
            self.primary_capitol_id = capitol_id
            # If no secondary capitol set, make it the same initially
            if self.secondary_capitol_id is None:
                self.secondary_capitol_id = capitol_id
    
    def change_secondary_capitol(self, new_capitol_id: str):
        """Change the current controlling capitol (for conquest/revolt)"""
        old_capitol = self.secondary_capitol_id
        self.secondary_capitol_id = new_capitol_id
        
        # Log the capitol change as a major event
        event = f"Capitol changed from {old_capitol} to {new_capitol_id}"
        self.history.append(event)
        self.current_events.append(event)
    
    def start_arc(self, arc_id: str) -> bool:
        """Start a new arc (only if no current arc active)"""
        if self.arc is None:
            self.arc = arc_id
            return True
        return False
    
    def complete_arc(self, success: bool = True) -> bool:
        """Complete the current arc"""
        if self.arc is not None:
            arc_result = f"{self.arc}:{'success' if success else 'failure'}"
            self.arc_history.append(arc_result)
            
            # Log as major event and core memory
            event = f"Arc {self.arc} {'completed successfully' if success else 'failed'}"
            self.history.append(event)
            self.memory.append(f"CORE_MEMORY:{event}")
            
            self.arc = None
            return True
        return False
    
    def add_core_memory(self, event: str):
        """Add a core memory that never gets summarized"""
        core_memory = f"CORE_MEMORY:{event}"
        if core_memory not in self.memory:
            self.memory.append(core_memory)
    
    def log_major_event(self, event: str, is_core_memory: bool = False):
        """Log a major region event"""
        self.history.append(event)
        self.current_events.append(event)
        
        if is_core_memory:
            self.add_core_memory(event)


# ============================================================================
# CONTINENT METADATA
# ============================================================================

@dataclass
class ContinentMetadata:
    """Metadata for continents containing multiple regions"""
    id: Union[str, UUID]
    name: str
    description: str = ""
    
    # Geographic data
    total_area_square_km: float = 0.0
    climate_zones: List[ClimateType] = field(default_factory=list)
    major_biomes: List[str] = field(default_factory=list)  # List of biome type IDs
    
    # Political data
    major_powers: List[Union[str, UUID]] = field(default_factory=list)
    political_situation: str = "stable"
    
    # Regions
    region_ids: List[Union[str, UUID]] = field(default_factory=list)
    
    # Generation data
    generation_seed: Optional[int] = None
    generation_parameters: Dict[str, Any] = field(default_factory=dict)
    
    # System state
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def get_total_population(self, regions: List[RegionMetadata]) -> int:
        """Calculate total population across all regions"""
        continent_regions = [r for r in regions if r.continent_id == self.id]
        return sum(r.population for r in continent_regions)
    
    def get_dominant_climate(self) -> Optional[ClimateType]:
        """Get the most common climate type"""
        if not self.climate_zones:
            return None
        
        climate_counts = {}
        for climate in self.climate_zones:
            climate_counts[climate] = climate_counts.get(climate, 0) + 1
        
        return max(climate_counts.items(), key=lambda x: x[1])[0]


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class RegionStatus(Enum):
    """Status enum for regions"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"


@dataclass
class CreateRegionRequest:
    """Request data for creating a new region"""
    name: str
    description: Optional[str] = None
    region_type: str = "wilderness"
    terrain_type: str = "temperate_forest"  # Maps to dominant_biome
    climate: str = "temperate"
    properties: Optional[Dict[str, Any]] = None
    status: str = "active"
    continent_id: Optional[UUID] = None


@dataclass
class UpdateRegionRequest:
    """Request data for updating a region"""
    name: Optional[str] = None
    description: Optional[str] = None
    region_type: Optional[str] = None
    terrain_type: Optional[str] = None  # Maps to dominant_biome
    climate: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    political_stability: Optional[float] = None
    wealth_level: Optional[float] = None
    population: Optional[int] = None


@dataclass
class RegionResponse:
    """Response data for region operations"""
    id: UUID
    name: str
    description: Optional[str]
    region_type: str
    terrain_type: str  # Maps from dominant_biome
    climate: str
    status: str
    properties: Optional[Dict[str, Any]] = None
    population: int = 0
    area_square_km: float = 0.0
    political_stability: float = 0.5
    wealth_level: float = 0.5
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    is_active: bool = True


@dataclass
class RegionListResponse:
    """Response data for region list operations"""
    regions: List[RegionResponse]
    total: int
    page: int
    size: int


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_hex_neighbors(hex_coord: HexCoordinate) -> List[HexCoordinate]:
    """Get neighboring hex coordinates"""
    return hex_coord.neighbors()


def calculate_hex_distance(hex1: HexCoordinate, hex2: HexCoordinate) -> int:
    """Calculate distance between two hex coordinates"""
    return hex1.distance_to(hex2)


def validate_region_adjacency(region1: RegionMetadata, region2: RegionMetadata) -> bool:
    """Check if two regions are adjacent"""
    for coord1 in region1.hex_coordinates:
        for coord2 in region2.hex_coordinates:
            if calculate_hex_distance(coord1, coord2) <= 1:
                return True
    return False


def validate_region_type(region_type: str) -> bool:
    """Check if region type is valid per JSON schema"""
    valid_types = [e.value for e in RegionType]
    return region_type in valid_types


def validate_biome_type(biome_type: str) -> bool:
    """Check if biome type is valid per JSON schema"""
    valid_biomes = [e.value for e in BiomeType]
    return biome_type in valid_biomes


def validate_resource_type(resource_type: str) -> bool:
    """Check if resource type is valid per JSON schema"""
    valid_resources = [e.value for e in ResourceType]
    return resource_type in valid_resources


def get_valid_region_types() -> List[str]:
    """Get list of valid region types"""
    return [e.value for e in RegionType]


def get_valid_biome_types() -> List[str]:
    """Get list of valid biome types"""
    return [e.value for e in BiomeType]


def get_valid_resource_types() -> List[str]:
    """Get list of valid resource types"""
    return [e.value for e in ResourceType] 