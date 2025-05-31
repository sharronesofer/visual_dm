"""
Region System Models

Comprehensive models for the region system including regions, continents,
biomes, resources, POIs, and hex-based coordinate system. Supports the
full world generation paradigm from development_bible.md.
"""

import json
import math
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from enum import Enum, IntEnum
from dataclasses import dataclass, field
from uuid import UUID

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, JSON, ForeignKey,
    Text, Enum as SQLEnum, Index
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from pydantic import BaseModel, Field

from backend.infrastructure.database import BaseModel as DBBaseModel, UUIDMixin, GUID


# ============================================================================
# ENUMS AND CONSTANTS
# ============================================================================

class RegionType(Enum):
    """Types of regions based on geographic and political characteristics"""
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
    """Biome types for environmental characteristics"""
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
    """Climate classifications"""
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
    """Types of natural resources"""
    IRON = "iron"
    COPPER = "copper"
    GOLD = "gold"
    SILVER = "silver"
    GEMS = "gems"
    COAL = "coal"
    STONE = "stone"
    MARBLE = "marble"
    TIMBER = "timber"
    FERTILE_SOIL = "fertile_soil"
    FRESH_WATER = "fresh_water"
    FISH = "fish"
    GAME = "game"
    HERBS = "herbs"
    MAGICAL_CRYSTALS = "magical_crystals"
    MITHRIL = "mithril"
    ADAMANTINE = "adamantine"
    RARE_EARTH = "rare_earth"
    OIL = "oil"
    NATURAL_GAS = "natural_gas"


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


class HexCoordinateSchema(BaseModel):
    """Pydantic schema for hex coordinates"""
    q: int = Field(..., description="Hex Q coordinate")
    r: int = Field(..., description="Hex R coordinate")
    s: int = Field(..., description="Hex S coordinate (calculated)")
    
    @classmethod
    def from_hex_coordinate(cls, hex_coord: HexCoordinate) -> 'HexCoordinateSchema':
        """Create schema from HexCoordinate"""
        return cls(q=hex_coord.q, r=hex_coord.r, s=hex_coord.s)
    
    def to_hex_coordinate(self) -> HexCoordinate:
        """Convert to HexCoordinate"""
        return HexCoordinate(self.q, self.r)


# ============================================================================
# DATACLASS MODELS (For business logic and analytics)
# ============================================================================

@dataclass
class ResourceNode:
    """Individual resource node within a region"""
    resource_type: ResourceType
    abundance: float  # 0.0 to 1.0
    quality: float    # 0.0 to 1.0
    accessibility: float  # 0.0 to 1.0
    depletion_rate: float = 0.0
    current_reserves: float = 1.0
    location: Optional[HexCoordinate] = None
    
    def calculate_value(self) -> float:
        """Calculate the economic value of this resource node"""
        return self.abundance * self.quality * self.accessibility * self.current_reserves


@dataclass
class RegionProfile:
    """Environmental and geographic profile of a region"""
    dominant_biome: BiomeType
    secondary_biomes: List[BiomeType] = field(default_factory=list)
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
    
    def calculate_habitability(self) -> float:
        """Calculate overall habitability score"""
        factors = [
            self.soil_fertility,
            self.water_availability,
            1.0 - abs(0.5 - self.humidity),  # Optimal humidity around 0.5
            len(self.natural_hazards) == 0  # No natural hazards is better
        ]
        return sum(factors) / len(factors)


@dataclass
class RegionMetadata:
    """Comprehensive metadata for a region"""
    id: Union[str, UUID]
    name: str
    description: str = ""
    region_type: RegionType = RegionType.WILDERNESS
    profile: RegionProfile = field(default_factory=lambda: RegionProfile(BiomeType.TEMPERATE_FOREST))
    
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
    
    # System state
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def calculate_total_resource_value(self) -> float:
        """Calculate total economic value of all resources"""
        return sum(node.calculate_value() for node in self.resource_nodes)
    
    def get_resource_abundance(self, resource_type: ResourceType) -> float:
        """Get abundance of a specific resource type"""
        nodes = [node for node in self.resource_nodes if node.resource_type == resource_type]
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


@dataclass
class ContinentMetadata:
    """Metadata for continents containing multiple regions"""
    id: Union[str, UUID]
    name: str
    description: str = ""
    
    # Geographic data
    total_area_square_km: float = 0.0
    climate_zones: List[ClimateType] = field(default_factory=list)
    major_biomes: List[BiomeType] = field(default_factory=list)
    
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
# DATABASE MODELS (SQLAlchemy ORM)
# ============================================================================

class Region(DBBaseModel, UUIDMixin):
    """Main region database model"""
    __tablename__ = "regions"
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    region_type = Column(SQLEnum(RegionType), default=RegionType.WILDERNESS)
    
    # Geographic data
    hex_coordinates_json = Column(JSON)  # Stored as list of {q, r, s} dicts
    center_hex_q = Column(Integer)
    center_hex_r = Column(Integer)
    area_square_km = Column(Float, default=0.0)
    perimeter_km = Column(Float, default=0.0)
    
    # Environmental profile
    dominant_biome = Column(SQLEnum(BiomeType), default=BiomeType.TEMPERATE_FOREST)
    secondary_biomes_json = Column(JSON)  # List of BiomeType values
    climate = Column(SQLEnum(ClimateType), default=ClimateType.TEMPERATE)
    elevation = Column(Float, default=0.0)
    elevation_variance = Column(Float, default=0.0)
    temperature_min = Column(Float, default=10.0)
    temperature_max = Column(Float, default=25.0)
    precipitation = Column(Float, default=500.0)
    humidity = Column(Float, default=0.5)
    soil_fertility = Column(Float, default=0.5)
    water_availability = Column(Float, default=0.5)
    natural_hazards_json = Column(JSON)
    
    # Political data
    controlling_faction_id = Column(GUID(), ForeignKey('factions.id'), nullable=True)
    government_type = Column(String(100), default="none")
    political_stability = Column(Float, default=0.5)
    law_level = Column(Integer, default=5)
    
    # Economic data
    wealth_level = Column(Float, default=0.5)
    trade_routes_json = Column(JSON)
    primary_industries_json = Column(JSON)
    
    # Demographic data
    population = Column(Integer, default=0)
    population_density = Column(Float, default=0.0)
    major_settlements_json = Column(JSON)
    
    # Gameplay data
    danger_level = Column(SQLEnum(DangerLevel), default=DangerLevel.SAFE)
    exploration_status = Column(Float, default=0.0)
    discovery_date = Column(DateTime)
    
    # Connections
    continent_id = Column(GUID(), ForeignKey('continents.id'), nullable=True)
    neighboring_region_ids_json = Column(JSON)
    
    # Dynamic state
    current_events_json = Column(JSON)
    historical_events_json = Column(JSON)
    
    # Relationships
    continent = relationship("Continent", back_populates="regions")
    resource_nodes = relationship("RegionResourceNode", back_populates="region", cascade="all, delete-orphan")
    pois = relationship("RegionPOI", back_populates="region", cascade="all, delete-orphan")
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_region_continent', 'continent_id'),
        Index('idx_region_faction', 'controlling_faction_id'),
        Index('idx_region_type', 'region_type'),
        Index('idx_region_biome', 'dominant_biome'),
        Index('idx_region_danger', 'danger_level'),
        Index('idx_region_coords', 'center_hex_q', 'center_hex_r'),
    )
    
    @hybrid_property
    def hex_coordinates(self) -> List[HexCoordinate]:
        """Get hex coordinates as HexCoordinate objects"""
        if not self.hex_coordinates_json:
            return []
        return [HexCoordinate.from_dict(coord_dict) for coord_dict in self.hex_coordinates_json]
    
    @hex_coordinates.setter
    def hex_coordinates(self, coordinates: List[HexCoordinate]):
        """Set hex coordinates from HexCoordinate objects"""
        self.hex_coordinates_json = [coord.to_dict() for coord in coordinates]
        
        if coordinates:
            # Update center coordinate
            avg_q = sum(coord.q for coord in coordinates) / len(coordinates)
            avg_r = sum(coord.r for coord in coordinates) / len(coordinates)
            center = HexCoordinate.from_fractional(avg_q, avg_r)
            self.center_hex_q = center.q
            self.center_hex_r = center.r
            
            # Update area
            hex_area_km2 = 10.0  # Configurable
            self.area_square_km = len(coordinates) * hex_area_km2
            
            # Update population density
            if self.area_square_km > 0:
                self.population_density = self.population / self.area_square_km
    
    @property
    def center_coordinate(self) -> Optional[HexCoordinate]:
        """Get center coordinate as HexCoordinate"""
        if self.center_hex_q is not None and self.center_hex_r is not None:
            return HexCoordinate(self.center_hex_q, self.center_hex_r)
        return None
    
    def to_metadata(self) -> RegionMetadata:
        """Convert to RegionMetadata dataclass"""
        # Create profile
        profile = RegionProfile(
            dominant_biome=self.dominant_biome,
            secondary_biomes=[BiomeType(biome) for biome in (self.secondary_biomes_json or [])],
            climate=self.climate,
            elevation=self.elevation,
            elevation_variance=self.elevation_variance,
            temperature_range=(self.temperature_min, self.temperature_max),
            precipitation=self.precipitation,
            humidity=self.humidity,
            soil_fertility=self.soil_fertility,
            water_availability=self.water_availability,
            natural_hazards=self.natural_hazards_json or []
        )
        
        # Create resource nodes
        resource_nodes = []
        for db_node in self.resource_nodes:
            location = None
            if db_node.hex_q is not None and db_node.hex_r is not None:
                location = HexCoordinate(db_node.hex_q, db_node.hex_r)
            
            resource_nodes.append(ResourceNode(
                resource_type=db_node.resource_type,
                abundance=db_node.abundance,
                quality=db_node.quality,
                accessibility=db_node.accessibility,
                depletion_rate=db_node.depletion_rate,
                current_reserves=db_node.current_reserves,
                location=location
            ))
        
        return RegionMetadata(
            id=self.id,
            name=self.name,
            description=self.description or "",
            region_type=self.region_type,
            profile=profile,
            hex_coordinates=self.hex_coordinates,
            center_coordinate=self.center_coordinate,
            area_square_km=self.area_square_km,
            perimeter_km=self.perimeter_km,
            controlling_faction_id=self.controlling_faction_id,
            government_type=self.government_type,
            political_stability=self.political_stability,
            law_level=self.law_level,
            wealth_level=self.wealth_level,
            trade_routes=self.trade_routes_json or [],
            primary_industries=self.primary_industries_json or [],
            population=self.population,
            population_density=self.population_density,
            major_settlements=self.major_settlements_json or [],
            resource_nodes=resource_nodes,
            poi_ids=[poi.id for poi in self.pois],
            danger_level=self.danger_level,
            exploration_status=self.exploration_status,
            discovery_date=self.discovery_date,
            neighboring_region_ids=self.neighboring_region_ids_json or [],
            continent_id=self.continent_id,
            current_events=self.current_events_json or [],
            historical_events=self.historical_events_json or [],
            created_at=self.created_at,
            updated_at=self.updated_at
        )


class Continent(DBBaseModel, UUIDMixin):
    """Continent database model"""
    __tablename__ = "continents"
    
    # Basic information
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    
    # Geographic data
    total_area_square_km = Column(Float, default=0.0)
    climate_zones_json = Column(JSON)  # List of ClimateType values
    major_biomes_json = Column(JSON)   # List of BiomeType values
    
    # Political data
    major_powers_json = Column(JSON)  # List of faction IDs
    political_situation = Column(String(100), default="stable")
    
    # Generation data
    generation_seed = Column(Integer)
    generation_parameters_json = Column(JSON)
    
    # Relationships
    regions = relationship("Region", back_populates="continent", cascade="all, delete-orphan")
    
    def to_metadata(self) -> ContinentMetadata:
        """Convert to ContinentMetadata dataclass"""
        return ContinentMetadata(
            id=self.id,
            name=self.name,
            description=self.description or "",
            total_area_square_km=self.total_area_square_km,
            climate_zones=[ClimateType(climate) for climate in (self.climate_zones_json or [])],
            major_biomes=[BiomeType(biome) for biome in (self.major_biomes_json or [])],
            major_powers=self.major_powers_json or [],
            political_situation=self.political_situation,
            region_ids=[region.id for region in self.regions],
            generation_seed=self.generation_seed,
            generation_parameters=self.generation_parameters_json or {},
            created_at=self.created_at,
            updated_at=self.updated_at
        )


class RegionResourceNode(DBBaseModel, UUIDMixin):
    """Resource nodes within regions"""
    __tablename__ = "region_resource_nodes"
    
    # Foreign keys
    region_id = Column(GUID(), ForeignKey('regions.id'), nullable=False)
    
    # Resource data
    resource_type = Column(SQLEnum(ResourceType), nullable=False)
    abundance = Column(Float, default=0.5)  # 0.0 to 1.0
    quality = Column(Float, default=0.5)    # 0.0 to 1.0
    accessibility = Column(Float, default=0.5)  # 0.0 to 1.0
    depletion_rate = Column(Float, default=0.0)
    current_reserves = Column(Float, default=1.0)
    
    # Location within region
    hex_q = Column(Integer)
    hex_r = Column(Integer)
    
    # Economic data
    extraction_difficulty = Column(Float, default=0.5)
    market_value_modifier = Column(Float, default=1.0)
    
    # Relationships
    region = relationship("Region", back_populates="resource_nodes")
    
    __table_args__ = (
        Index('idx_resource_region', 'region_id'),
        Index('idx_resource_type', 'resource_type'),
        Index('idx_resource_location', 'hex_q', 'hex_r'),
    )
    
    def calculate_value(self) -> float:
        """Calculate economic value of this resource node"""
        return (self.abundance * self.quality * self.accessibility * 
                self.current_reserves * self.market_value_modifier)


class RegionPOI(DBBaseModel, UUIDMixin):
    """Points of Interest within regions"""
    __tablename__ = "region_pois"
    
    # Foreign keys
    region_id = Column(GUID(), ForeignKey('regions.id'), nullable=False)
    
    # Basic information
    name = Column(String(200), nullable=False)
    description = Column(Text)
    poi_type = Column(SQLEnum(POIType), nullable=False)
    
    # Location
    hex_q = Column(Integer, nullable=False)
    hex_r = Column(Integer, nullable=False)
    
    # Properties
    size_category = Column(String(50), default="small")  # small, medium, large, huge
    importance_level = Column(Integer, default=1)  # 1-10 scale
    is_active = Column(Boolean, default=True)
    is_discovered = Column(Boolean, default=False)
    discovery_date = Column(DateTime)
    
    # State and conditions
    current_state = Column(String(100), default="normal")
    danger_rating = Column(Integer, default=1)  # 1-10 scale
    
    # Gameplay data
    has_been_cleared = Column(Boolean, default=False)
    last_visit_date = Column(DateTime)
    visit_count = Column(Integer, default=0)
    
    # Connections
    connected_poi_ids_json = Column(JSON)  # Connected POIs
    
    # Relationships
    region = relationship("Region", back_populates="pois")
    
    __table_args__ = (
        Index('idx_poi_region', 'region_id'),
        Index('idx_poi_type', 'poi_type'),
        Index('idx_poi_location', 'hex_q', 'hex_r'),
        Index('idx_poi_discovered', 'is_discovered'),
    )
    
    @property
    def hex_coordinate(self) -> HexCoordinate:
        """Get location as HexCoordinate"""
        return HexCoordinate(self.hex_q, self.hex_r)
    
    @hex_coordinate.setter
    def hex_coordinate(self, coord: HexCoordinate):
        """Set location from HexCoordinate"""
        self.hex_q = coord.q
        self.hex_r = coord.r


# ============================================================================
# PYDANTIC SCHEMAS (For API and validation)
# ============================================================================

class RegionCreateSchema(BaseModel):
    """Schema for creating a new region"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    region_type: RegionType = RegionType.WILDERNESS
    continent_id: Optional[UUID] = None
    dominant_biome: BiomeType = BiomeType.TEMPERATE_FOREST
    climate: ClimateType = ClimateType.TEMPERATE
    government_type: str = "none"
    danger_level: DangerLevel = DangerLevel.SAFE


class RegionUpdateSchema(BaseModel):
    """Schema for updating a region"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    region_type: Optional[RegionType] = None
    political_stability: Optional[float] = Field(None, ge=0.0, le=1.0)
    wealth_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    population: Optional[int] = Field(None, ge=0)
    danger_level: Optional[DangerLevel] = None
    exploration_status: Optional[float] = Field(None, ge=0.0, le=1.0)


class RegionResponseSchema(BaseModel):
    """Schema for region API responses"""
    id: UUID
    name: str
    description: Optional[str]
    region_type: RegionType
    dominant_biome: BiomeType
    climate: ClimateType
    population: int
    area_square_km: float
    danger_level: DangerLevel
    exploration_status: float
    continent_id: Optional[UUID]
    center_coordinate: Optional[HexCoordinateSchema]
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ContinentCreateSchema(BaseModel):
    """Schema for creating a new continent"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    generation_seed: Optional[int] = None


class ContinentResponseSchema(BaseModel):
    """Schema for continent API responses"""
    id: UUID
    name: str
    description: Optional[str]
    total_area_square_km: float
    political_situation: str
    region_count: int = 0
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class ResourceNodeCreateSchema(BaseModel):
    """Schema for creating resource nodes"""
    resource_type: ResourceType
    abundance: float = Field(0.5, ge=0.0, le=1.0)
    quality: float = Field(0.5, ge=0.0, le=1.0)
    accessibility: float = Field(0.5, ge=0.0, le=1.0)
    hex_coordinate: Optional[HexCoordinateSchema] = None


class POICreateSchema(BaseModel):
    """Schema for creating POIs"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    poi_type: POIType
    hex_coordinate: HexCoordinateSchema
    size_category: str = "small"
    importance_level: int = Field(1, ge=1, le=10)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_region_from_metadata(metadata: RegionMetadata) -> Region:
    """Create a Region database model from RegionMetadata"""
    region = Region(
        id=metadata.id if isinstance(metadata.id, UUID) else UUID(str(metadata.id)),
        name=metadata.name,
        description=metadata.description,
        region_type=metadata.region_type,
        dominant_biome=metadata.profile.dominant_biome,
        secondary_biomes_json=[biome.value for biome in metadata.profile.secondary_biomes],
        climate=metadata.profile.climate,
        elevation=metadata.profile.elevation,
        elevation_variance=metadata.profile.elevation_variance,
        temperature_min=metadata.profile.temperature_range[0],
        temperature_max=metadata.profile.temperature_range[1],
        precipitation=metadata.profile.precipitation,
        humidity=metadata.profile.humidity,
        soil_fertility=metadata.profile.soil_fertility,
        water_availability=metadata.profile.water_availability,
        natural_hazards_json=metadata.profile.natural_hazards,
        controlling_faction_id=metadata.controlling_faction_id,
        government_type=metadata.government_type,
        political_stability=metadata.political_stability,
        law_level=metadata.law_level,
        wealth_level=metadata.wealth_level,
        trade_routes_json=metadata.trade_routes,
        primary_industries_json=metadata.primary_industries,
        population=metadata.population,
        major_settlements_json=metadata.major_settlements,
        danger_level=metadata.danger_level,
        exploration_status=metadata.exploration_status,
        discovery_date=metadata.discovery_date,
        continent_id=metadata.continent_id,
        neighboring_region_ids_json=[str(rid) for rid in metadata.neighboring_region_ids],
        current_events_json=metadata.current_events,
        historical_events_json=metadata.historical_events
    )
    
    # Set hex coordinates (this will trigger the setter and update derived fields)
    region.hex_coordinates = metadata.hex_coordinates
    
    return region


def create_continent_from_metadata(metadata: ContinentMetadata) -> Continent:
    """Create a Continent database model from ContinentMetadata"""
    return Continent(
        id=metadata.id if isinstance(metadata.id, UUID) else UUID(str(metadata.id)),
        name=metadata.name,
        description=metadata.description,
        total_area_square_km=metadata.total_area_square_km,
        climate_zones_json=[climate.value for climate in metadata.climate_zones],
        major_biomes_json=[biome.value for biome in metadata.major_biomes],
        major_powers_json=[str(pid) for pid in metadata.major_powers],
        political_situation=metadata.political_situation,
        generation_seed=metadata.generation_seed,
        generation_parameters_json=metadata.generation_parameters
    )


# ============================================================================
# COMPATIBILITY ALIASES AND LEGACY MODELS
# ============================================================================

# Enum aliases for backward compatibility
TerrainType = BiomeType  # Legacy alias
POICategory = POIType    # Legacy alias

class RegionStatus(Enum):
    """Status enum for regions"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    ARCHIVED = "archived"

# Database model aliases for backward compatibility
RegionEntity = Region  # Main alias expected by services
ContinentEntity = Continent  # Continent alias
RegionBaseModel = Region  # Base model alias
RegionModel = Region  # Model alias

# Legacy dataclass aliases
CoordinateSchema = HexCoordinateSchema
LevelRange = tuple  # Simple tuple for level ranges
EnvironmentalProfile = RegionProfile  # Environmental profile alias
GeographicData = dict  # Geographic data as dict
PoliticalData = dict   # Political data as dict
EconomicData = dict    # Economic data as dict
PointOfInterest = dict # POI as dict

# ============================================================================
# LEGACY REQUEST/RESPONSE MODELS (For backward compatibility)
# ============================================================================

class CreateRegionRequest(BaseModel):
    """Legacy create region request schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    region_type: Optional[str] = "wilderness"
    terrain_type: Optional[str] = "temperate_forest"
    climate: Optional[str] = "temperate"
    properties: Optional[Dict[str, Any]] = None
    status: str = "active"

class UpdateRegionRequest(BaseModel):
    """Legacy update region request schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    region_type: Optional[str] = None
    terrain_type: Optional[str] = None
    climate: Optional[str] = None
    properties: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    political_stability: Optional[float] = Field(None, ge=0.0, le=1.0)
    wealth_level: Optional[float] = Field(None, ge=0.0, le=1.0)
    population: Optional[int] = Field(None, ge=0)

class RegionResponse(BaseModel):
    """Legacy region response schema"""
    id: UUID
    name: str
    description: Optional[str]
    region_type: str
    terrain_type: str
    climate: str
    status: str
    properties: Optional[Dict[str, Any]] = None
    population: int = 0
    area_square_km: float = 0.0
    political_stability: float = 0.5
    wealth_level: float = 0.5
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    model_config = ConfigDict(from_attributes=True)
    
    @classmethod
    def from_orm(cls, region: Region) -> 'RegionResponse':
        """Create from Region ORM model"""
        return cls(
            id=region.id,
            name=region.name,
            description=region.description,
            region_type=region.region_type.value if region.region_type else "wilderness",
            terrain_type=region.dominant_biome.value if region.dominant_biome else "temperate_forest",
            climate=region.climate.value if region.climate else "temperate",
            status="active",  # Default status
            properties={},  # Default empty properties
            population=region.population,
            area_square_km=region.area_square_km,
            political_stability=region.political_stability,
            wealth_level=region.wealth_level,
            created_at=region.created_at,
            updated_at=region.updated_at,
            is_active=True  # Default active
        )

class RegionListResponse(BaseModel):
    """Legacy region list response schema"""
    regions: List[RegionResponse]
    total: int
    page: int
    size: int
    
    model_config = ConfigDict(from_attributes=True)

# ============================================================================
# CONSTANTS (Expected by the system)
# ============================================================================

# Hex and area constants
REGION_HEXES_PER_REGION = 37  # Standard region size in hexes
REGION_AREA_SQ_KM = 10.0      # Square km per hex
CONTINENT_SIZE_RANGE = (50, 500)  # Min/max regions per continent

# POI density constants (from development bible)
MAJOR_POIS_PER_REGION = 20
MINOR_POIS_PER_REGION_MIN = 200
MINOR_POIS_PER_REGION_MAX = 400

# ============================================================================
# UTILITY FUNCTIONS (Expected by the system)
# ============================================================================

def get_hex_neighbors(hex_coord: HexCoordinate) -> List[HexCoordinate]:
    """Get neighboring hex coordinates (alias for backward compatibility)"""
    return hex_coord.neighbors()

def calculate_hex_distance(hex1: HexCoordinate, hex2: HexCoordinate) -> int:
    """Calculate distance between hex coordinates (alias for backward compatibility)"""
    return hex1.distance_to(hex2)

def validate_region_adjacency(region1: RegionMetadata, region2: RegionMetadata) -> bool:
    """Validate if two regions are adjacent"""
    for coord1 in region1.hex_coordinates:
        for coord2 in region2.hex_coordinates:
            if calculate_hex_distance(coord1, coord2) <= 1:
                return True
    return False

# ============================================================================
# ENHANCED DATABASE MODELS FOR COMPATIBILITY
# ============================================================================

# Add compatibility fields to Region model via monkey patching
def _add_legacy_properties(region_cls):
    """Add legacy properties to Region class"""
    
    @property
    def terrain_type(self):
        """Legacy terrain type property"""
        return self.dominant_biome.value if self.dominant_biome else "temperate_forest"
    
    @terrain_type.setter
    def terrain_type(self, value):
        """Set terrain type from string"""
        if isinstance(value, str):
            try:
                self.dominant_biome = BiomeType(value)
            except ValueError:
                self.dominant_biome = BiomeType.TEMPERATE_FOREST
    
    @property
    def is_active(self):
        """Legacy active status property"""
        return True  # Default to active
    
    @property
    def status(self):
        """Legacy status property"""
        return "active"  # Default status
    
    @property
    def properties(self):
        """Legacy properties field"""
        return {}  # Empty properties dict
    
    # Add properties to the class
    region_cls.terrain_type = terrain_type
    region_cls.is_active = is_active
    region_cls.status = status
    region_cls.properties = properties
    
    return region_cls

# Apply legacy properties
Region = _add_legacy_properties(Region)
RegionEntity = Region  # Update alias after enhancements

# Export all models and schemas
__all__ = [
    # Enums
    "RegionType", "BiomeType", "ClimateType", "ResourceType", "POIType", "DangerLevel",
    
    # Legacy enum aliases
    "TerrainType", "POICategory", "RegionStatus",
    
    # Coordinate system
    "HexCoordinate", "HexCoordinateSchema",
    
    # Legacy coordinate aliases
    "CoordinateSchema",
    
    # Dataclass models
    "ResourceNode", "RegionProfile", "RegionMetadata", "ContinentMetadata",
    
    # Legacy dataclass aliases
    "LevelRange", "EnvironmentalProfile", "GeographicData", "PoliticalData", 
    "EconomicData", "PointOfInterest",
    
    # Database models
    "Region", "Continent", "RegionResourceNode", "RegionPOI",
    
    # Legacy database aliases
    "RegionEntity", "ContinentEntity", "RegionBaseModel", "RegionModel",
    
    # Pydantic schemas
    "RegionCreateSchema", "RegionUpdateSchema", "RegionResponseSchema",
    "ContinentCreateSchema", "ContinentResponseSchema",
    "ResourceNodeCreateSchema", "POICreateSchema",
    
    # Legacy request/response models
    "CreateRegionRequest", "UpdateRegionRequest", "RegionResponse", "RegionListResponse",
    
    # Constants
    "REGION_HEXES_PER_REGION", "REGION_AREA_SQ_KM", "CONTINENT_SIZE_RANGE",
    "MAJOR_POIS_PER_REGION", "MINOR_POIS_PER_REGION_MIN", "MINOR_POIS_PER_REGION_MAX",
    
    # Utility functions
    "create_region_from_metadata", "create_continent_from_metadata",
    "get_hex_neighbors", "calculate_hex_distance", "validate_region_adjacency"
] 