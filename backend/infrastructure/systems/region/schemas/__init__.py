"""
Pydantic API Schemas for Region System

These schemas provide input/output validation for the region system API endpoints.
They serve as the contract between the API layer and the business logic.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator
from enum import Enum


# ============================================================================
# API ENUMS (for validation)
# ============================================================================

class RegionTypeEnum(str, Enum):
    """Region types for API validation."""
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


class BiomeTypeEnum(str, Enum):
    """Biome types for API validation."""
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


class ClimateTypeEnum(str, Enum):
    """Climate types for API validation."""
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


class DangerLevelEnum(int, Enum):
    """Danger levels for API validation."""
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
# COORDINATE SCHEMAS
# ============================================================================

class HexCoordinateSchema(BaseModel):
    """Hex coordinate for API serialization."""
    q: int = Field(..., description="Q coordinate (column)")
    r: int = Field(..., description="R coordinate (row)")
    s: int = Field(..., description="S coordinate (calculated)")
    
    @validator('s', always=True)
    def validate_s_coordinate(cls, v, values):
        """Ensure s = -q - r for valid hex coordinates."""
        if 'q' in values and 'r' in values:
            expected_s = -values['q'] - values['r']
            if v != expected_s:
                return expected_s
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "q": 1,
                "r": 2,
                "s": -3
            }
        }


# ============================================================================
# RESOURCE SCHEMAS
# ============================================================================

class ResourceNodeSchema(BaseModel):
    """Resource node data for API."""
    resource_type: str = Field(..., description="Type of resource")
    abundance: float = Field(..., ge=0.0, le=1.0, description="Resource abundance (0.0-1.0)")
    quality: float = Field(..., ge=0.0, le=1.0, description="Resource quality (0.0-1.0)")
    accessibility: float = Field(..., ge=0.0, le=1.0, description="Resource accessibility (0.0-1.0)")
    depletion_rate: float = Field(0.0, ge=0.0, le=1.0, description="Depletion rate per time unit")
    current_reserves: float = Field(1.0, ge=0.0, le=1.0, description="Current reserve level")
    location: Optional[HexCoordinateSchema] = Field(None, description="Specific location within region")
    
    class Config:
        schema_extra = {
            "example": {
                "resource_type": "gold",
                "abundance": 0.8,
                "quality": 0.7,
                "accessibility": 0.6,
                "depletion_rate": 0.01,
                "current_reserves": 0.9,
                "location": {"q": 1, "r": 2, "s": -3}
            }
        }


# ============================================================================
# REGION PROFILE SCHEMAS
# ============================================================================

class RegionProfileSchema(BaseModel):
    """Environmental profile data for API."""
    dominant_biome: BiomeTypeEnum = Field(..., description="Primary biome type")
    secondary_biomes: List[BiomeTypeEnum] = Field(default_factory=list, description="Secondary biome types")
    climate: ClimateTypeEnum = Field(ClimateTypeEnum.TEMPERATE, description="Climate classification")
    elevation: float = Field(0.0, description="Average elevation in meters")
    elevation_variance: float = Field(0.0, ge=0.0, description="Elevation standard deviation")
    temperature_range: Tuple[float, float] = Field((10.0, 25.0), description="Min/max temperature in Celsius")
    precipitation: float = Field(500.0, ge=0.0, description="Annual precipitation in mm")
    humidity: float = Field(0.5, ge=0.0, le=1.0, description="Humidity level (0.0-1.0)")
    soil_fertility: float = Field(0.5, ge=0.0, le=1.0, description="Soil fertility (0.0-1.0)")
    water_availability: float = Field(0.5, ge=0.0, le=1.0, description="Water availability (0.0-1.0)")
    natural_hazards: List[str] = Field(default_factory=list, description="List of natural hazards")
    wind_patterns: Dict[str, Any] = Field(default_factory=dict, description="Wind pattern data")
    seasonal_variations: Dict[str, Any] = Field(default_factory=dict, description="Seasonal variation data")


# ============================================================================
# REGION SCHEMAS
# ============================================================================

class RegionCreateSchema(BaseModel):
    """Schema for creating a new region."""
    name: str = Field(..., min_length=1, max_length=255, description="Region name")
    description: Optional[str] = Field(None, max_length=2000, description="Region description")
    region_type: RegionTypeEnum = Field(RegionTypeEnum.WILDERNESS, description="Type of region")
    dominant_biome: BiomeTypeEnum = Field(BiomeTypeEnum.TEMPERATE_FOREST, description="Primary biome")
    climate: ClimateTypeEnum = Field(ClimateTypeEnum.TEMPERATE, description="Climate type")
    continent_id: Optional[UUID] = Field(None, description="Parent continent ID")
    population: int = Field(0, ge=0, description="Initial population")
    wealth_level: float = Field(0.5, ge=0.0, le=1.0, description="Wealth level (0.0-1.0)")
    political_stability: float = Field(0.5, ge=0.0, le=1.0, description="Political stability (0.0-1.0)")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional properties")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Emerald Valley",
                "description": "A lush valley rich in resources",
                "region_type": "kingdom",
                "dominant_biome": "temperate_forest",
                "climate": "temperate",
                "population": 5000,
                "wealth_level": 0.7,
                "political_stability": 0.8
            }
        }


class RegionUpdateSchema(BaseModel):
    """Schema for updating an existing region."""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Region name")
    description: Optional[str] = Field(None, max_length=2000, description="Region description")
    region_type: Optional[RegionTypeEnum] = Field(None, description="Type of region")
    population: Optional[int] = Field(None, ge=0, description="Population")
    wealth_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Wealth level")
    political_stability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Political stability")
    danger_level: Optional[DangerLevelEnum] = Field(None, description="Danger level")
    exploration_status: Optional[float] = Field(None, ge=0.0, le=1.0, description="Exploration progress")
    properties: Optional[Dict[str, Any]] = Field(None, description="Additional properties")
    
    class Config:
        schema_extra = {
            "example": {
                "population": 7500,
                "wealth_level": 0.8,
                "political_stability": 0.7
            }
        }


class RegionResponseSchema(BaseModel):
    """Schema for region API responses."""
    id: UUID = Field(..., description="Region unique identifier")
    name: str = Field(..., description="Region name")
    description: Optional[str] = Field(None, description="Region description")
    region_type: str = Field(..., description="Type of region")
    dominant_biome: str = Field(..., description="Primary biome")
    climate: str = Field(..., description="Climate type")
    status: str = Field("active", description="Region status")
    
    # Geographic data
    area_square_km: float = Field(0.0, description="Area in square kilometers")
    center_coordinate: Optional[HexCoordinateSchema] = Field(None, description="Center hex coordinate")
    hex_coordinates: List[HexCoordinateSchema] = Field(default_factory=list, description="All hex coordinates")
    
    # Demographic data
    population: int = Field(0, description="Current population")
    population_density: float = Field(0.0, description="Population per square km")
    
    # Political/Economic data
    wealth_level: float = Field(0.5, description="Wealth level (0.0-1.0)")
    political_stability: float = Field(0.5, description="Political stability (0.0-1.0)")
    danger_level: int = Field(2, description="Danger level (1-10)")
    exploration_status: float = Field(0.0, description="Exploration progress (0.0-1.0)")
    
    # Relationships
    continent_id: Optional[UUID] = Field(None, description="Parent continent ID")
    neighboring_region_ids: List[UUID] = Field(default_factory=list, description="Adjacent regions")
    
    # Resources and features
    resource_nodes: List[ResourceNodeSchema] = Field(default_factory=list, description="Resource nodes")
    poi_ids: List[str] = Field(default_factory=list, description="Points of interest")
    
    # System metadata
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Emerald Valley",
                "description": "A lush valley rich in resources",
                "region_type": "kingdom",
                "dominant_biome": "temperate_forest",
                "climate": "temperate",
                "population": 5000,
                "area_square_km": 150.0,
                "wealth_level": 0.7,
                "political_stability": 0.8,
                "danger_level": 2
            }
        }


# ============================================================================
# CONTINENT SCHEMAS
# ============================================================================

class ContinentCreateSchema(BaseModel):
    """Schema for creating a new continent."""
    name: str = Field(..., min_length=1, max_length=255, description="Continent name")
    description: Optional[str] = Field(None, max_length=2000, description="Continent description")
    generation_seed: Optional[int] = Field(None, description="Generation seed for reproducibility")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional properties")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Northern Continent",
                "description": "A vast northern landmass with diverse biomes",
                "generation_seed": 12345
            }
        }


class ContinentResponseSchema(BaseModel):
    """Schema for continent API responses."""
    id: UUID = Field(..., description="Continent unique identifier")
    name: str = Field(..., description="Continent name")
    description: Optional[str] = Field(None, description="Continent description")
    total_area_square_km: float = Field(0.0, description="Total area in square kilometers")
    political_situation: str = Field("stable", description="Political situation")
    climate_zones: List[str] = Field(default_factory=list, description="Climate types present")
    major_biomes: List[str] = Field(default_factory=list, description="Major biome types")
    region_count: int = Field(0, description="Number of regions in continent")
    generation_seed: Optional[int] = Field(None, description="Generation seed used")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional properties")
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Northern Continent",
                "description": "A vast northern landmass",
                "total_area_square_km": 5000000.0,
                "political_situation": "stable",
                "region_count": 45
            }
        }


# ============================================================================
# WORLD GENERATION SCHEMAS
# ============================================================================

class WorldGenerationParametersSchema(BaseModel):
    """Schema for world generation parameters."""
    seed: Optional[int] = Field(None, description="Generation seed")
    num_continents: int = Field(3, ge=1, le=10, description="Number of continents")
    continent_size_range: Tuple[int, int] = Field((50, 150), description="Min/max regions per continent")
    biome_diversity: float = Field(0.8, ge=0.0, le=1.0, description="Biome diversity factor")
    resource_abundance: float = Field(0.5, ge=0.0, le=1.0, description="Overall resource richness")
    danger_progression: Tuple[float, float, float] = Field((0.6, 0.3, 0.1), description="Safe, moderate, dangerous ratios")
    
    @validator('continent_size_range')
    def validate_size_range(cls, v):
        """Ensure min <= max for continent size range."""
        if v[0] > v[1]:
            raise ValueError("Minimum size cannot be greater than maximum size")
        return v
    
    @validator('danger_progression')
    def validate_danger_progression(cls, v):
        """Ensure danger progression ratios sum to 1.0."""
        if abs(sum(v) - 1.0) > 0.01:
            raise ValueError("Danger progression ratios must sum to 1.0")
        return v


# ============================================================================
# EXPORT ALL SCHEMAS
# ============================================================================

__all__ = [
    # Enums
    'RegionTypeEnum',
    'BiomeTypeEnum', 
    'ClimateTypeEnum',
    'DangerLevelEnum',
    
    # Coordinate schemas
    'HexCoordinateSchema',
    
    # Resource schemas
    'ResourceNodeSchema',
    
    # Profile schemas
    'RegionProfileSchema',
    
    # Region schemas
    'RegionCreateSchema',
    'RegionUpdateSchema', 
    'RegionResponseSchema',
    
    # Continent schemas
    'ContinentCreateSchema',
    'ContinentResponseSchema',
    
    # World generation schemas
    'WorldGenerationParametersSchema'
]

