from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, validator

# String constants for validation (per Bible - use strings not enums)
VALID_REGION_TYPES = [
    "kingdom", "duchy", "county", "city_state", "tribal_lands",
    "wilderness", "wasteland", "frontier", "disputed_territory", "neutral_zone"
]

VALID_BIOME_TYPES = [
    "temperate_forest", "deciduous_forest", "coniferous_forest", "tropical_rainforest",
    "grassland", "prairie", "savanna", "desert", "arctic", "tundra",
    "mountains", "hills", "swamp", "marsh", "coastal", "island",
    "volcanic", "magical_forest", "shadowlands", "feywild"
]

VALID_CLIMATE_TYPES = [
    "tropical", "subtropical", "temperate", "continental", "polar",
    "arid", "semi_arid", "mediterranean", "monsoon", "oceanic", "magical"
]

VALID_RESOURCE_TYPES = [
    "grain", "meat", "fish", "fruits", "vegetables",
    "wood", "stone", "iron", "leather", "cloth",
    "gold", "silver", "gems", "mana_crystals", "enchanted_herbs"
]

# ============================================================================
# BASE SCHEMAS
# ============================================================================

class HexCoordinateSchema(BaseModel):
    """Hex coordinate using cube coordinates (q, r, s where q + r + s = 0)"""
    q: int = Field(..., description="Q coordinate in cube coordinate system")
    r: int = Field(..., description="R coordinate in cube coordinate system")
    s: int = Field(..., description="S coordinate in cube coordinate system")
    
    @validator('s')
    def validate_cube_coordinates(cls, s, values):
        """Ensure cube coordinate constraint q + r + s = 0"""
        if 'q' in values and 'r' in values:
            q, r = values['q'], values['r']
            if q + r + s != 0:
                raise ValueError(f"Cube coordinates must satisfy q + r + s = 0, got q={q}, r={r}, s={s}")
        return s
    
    class Config:
        schema_extra = {
            "example": {
                "q": 1,
                "r": -1,
                "s": 0
            }
        }

class ResourceNodeSchema(BaseModel):
    """Resource node within a region using strings per Bible"""
    resource_type: str = Field(..., description="Type of resource (string per Bible)")
    abundance: float = Field(..., ge=0.0, le=1.0, description="Resource abundance (0.0 to 1.0)")
    quality: float = Field(..., ge=0.0, le=1.0, description="Resource quality (0.0 to 1.0)")
    accessibility: float = Field(..., ge=0.0, le=1.0, description="How accessible the resource is (0.0 to 1.0)")
    depletion_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Rate at which resource depletes")
    current_reserves: float = Field(default=1.0, ge=0.0, le=1.0, description="Current reserves remaining")
    location: Optional[HexCoordinateSchema] = Field(None, description="Specific hex location within region")
    
    @validator('resource_type')
    def validate_resource_type(cls, v):
        """Validate resource type against known types (strings per Bible)"""
        if v not in VALID_RESOURCE_TYPES:
            raise ValueError(f"Invalid resource type: {v}. Must be one of: {VALID_RESOURCE_TYPES}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "resource_type": "gold",
                "abundance": 0.8,
                "quality": 0.9,
                "accessibility": 0.6,
                "depletion_rate": 0.1,
                "current_reserves": 0.7,
                "location": {
                    "q": 2,
                    "r": -1,
                    "s": -1
                }
            }
        }

# ============================================================================
# REGION SCHEMAS
# ============================================================================

class RegionCreateSchema(BaseModel):
    """Schema for creating a new region using strings per Bible"""
    name: str = Field(..., min_length=1, max_length=255, description="Region name")
    description: Optional[str] = Field(None, max_length=2000, description="Region description")
    region_type: str = Field(default="wilderness", description="Type of region (string per Bible)")
    dominant_biome: str = Field(default="temperate_forest", description="Dominant biome type (string per Bible)")
    climate: str = Field(default="temperate", description="Climate type (string per Bible)")
    continent_id: Optional[UUID] = Field(None, description="ID of the continent this region belongs to")
    population: int = Field(default=0, ge=0, description="Current population")
    area_square_km: float = Field(default=0.0, ge=0.0, description="Area in square kilometers")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional properties")
    
    # Bible-required fields for narrative system
    level_range: Optional[List[int]] = Field(default=[1, 5], description="Level range [min, max] for encounters/content")
    tension_level: Optional[float] = Field(default=0.0, ge=0.0, le=100.0, description="Current tension level (0-100)")
    motif_pool: Optional[List[str]] = Field(default_factory=list, description="Active motif IDs (max 3)")
    primary_capitol_id: Optional[str] = Field(None, description="Primary (birth) capitol city ID - never changes")
    secondary_capitol_id: Optional[str] = Field(None, description="Current controlling capitol ID - changes with conquest")
    metropolis_type: Optional[str] = Field(None, description="Metropolis type: arcane/industrial/sacred/ruined/natural")
    factions: Optional[List[str]] = Field(default_factory=list, description="Influential faction IDs")
    terrain_types: Optional[List[str]] = Field(default_factory=list, description="List of terrain types present")
    
    @validator('region_type')
    def validate_region_type(cls, v):
        """Validate region type (string per Bible)"""
        if v not in VALID_REGION_TYPES:
            raise ValueError(f"Invalid region type: {v}. Must be one of: {VALID_REGION_TYPES}")
        return v
    
    @validator('dominant_biome')
    def validate_biome_type(cls, v):
        """Validate biome type (string per Bible)"""
        if v not in VALID_BIOME_TYPES:
            raise ValueError(f"Invalid biome type: {v}. Must be one of: {VALID_BIOME_TYPES}")
        return v
    
    @validator('climate')
    def validate_climate_type(cls, v):
        """Validate climate type (string per Bible)"""
        if v not in VALID_CLIMATE_TYPES:
            raise ValueError(f"Invalid climate type: {v}. Must be one of: {VALID_CLIMATE_TYPES}")
        return v
    
    @validator('level_range')
    def validate_level_range(cls, v):
        """Validate level range"""
        if v is not None:
            if len(v) != 2:
                raise ValueError("Level range must be [min, max]")
            if v[0] < 1 or v[1] > 20 or v[0] > v[1]:
                raise ValueError("Level range must be valid (1-20, min <= max)")
        return v
    
    @validator('motif_pool')
    def validate_motif_pool(cls, v):
        """Validate motif pool"""
        if v is not None:
            if len(v) > 3:
                raise ValueError("Motif pool cannot exceed 3 active motifs")
            if len(set(v)) != len(v):
                raise ValueError("Motif pool must contain unique motifs")
        return v
    
    @validator('metropolis_type')
    def validate_metropolis_type(cls, v):
        """Validate metropolis type"""
        if v is not None:
            valid_types = ["arcane", "industrial", "sacred", "ruined", "natural"]
            if v not in valid_types:
                raise ValueError(f"Invalid metropolis type: {v}. Must be one of: {valid_types}")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Greenwood Valley",
                "description": "A peaceful valley known for its lush forests",
                "region_type": "duchy",
                "dominant_biome": "temperate_forest",
                "climate": "temperate",
                "population": 15000,
                "area_square_km": 2500.0,
                "level_range": [1, 5],
                "tension_level": 10.0,
                "motif_pool": ["forest_mystery", "ancient_ruins"],
                "primary_capitol_id": "greenwood_capital",
                "metropolis_type": "natural",
                "factions": ["forest_druids", "merchant_guild"],
                "terrain_types": ["forest", "hills", "river"]
            }
        }

class RegionUpdateSchema(BaseModel):
    """Schema for updating an existing region using strings per Bible"""
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Region name")
    description: Optional[str] = Field(None, max_length=2000, description="Region description")
    region_type: Optional[str] = Field(None, description="Type of region (string per Bible)")
    population: Optional[int] = Field(None, ge=0, description="Current population")
    wealth_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Wealth level (0.0 to 1.0)")
    political_stability: Optional[float] = Field(None, ge=0.0, le=1.0, description="Political stability (0.0 to 1.0)")
    danger_level: Optional[int] = Field(None, ge=1, le=10, description="Danger level (1-10)")
    exploration_status: Optional[float] = Field(None, ge=0.0, le=1.0, description="Exploration status (0.0 to 1.0)")
    properties: Optional[Dict[str, Any]] = Field(None, description="Additional properties")
    
    # Bible-required narrative and political fields
    level_range: Optional[List[int]] = Field(None, description="Level range [min, max] for encounters/content")
    tension_level: Optional[float] = Field(None, ge=0.0, le=100.0, description="Current tension level (0-100)")
    motif_pool: Optional[List[str]] = Field(None, description="Active motif IDs (max 3)")
    secondary_capitol_id: Optional[str] = Field(None, description="Current controlling capitol ID - changes with conquest")
    factions: Optional[List[str]] = Field(None, description="Influential faction IDs")
    terrain_types: Optional[List[str]] = Field(None, description="List of terrain types present")
    
    @validator('region_type')
    def validate_region_type(cls, v):
        """Validate region type (string per Bible)"""
        if v is not None and v not in VALID_REGION_TYPES:
            raise ValueError(f"Invalid region type: {v}. Must be one of: {VALID_REGION_TYPES}")
        return v
    
    @validator('level_range')
    def validate_level_range(cls, v):
        """Validate level range"""
        if v is not None:
            if len(v) != 2:
                raise ValueError("Level range must be [min, max]")
            if v[0] < 1 or v[1] > 20 or v[0] > v[1]:
                raise ValueError("Level range must be valid (1-20, min <= max)")
        return v
    
    @validator('motif_pool')
    def validate_motif_pool(cls, v):
        """Validate motif pool"""
        if v is not None:
            if len(v) > 3:
                raise ValueError("Motif pool cannot exceed 3 active motifs")
            if len(set(v)) != len(v):
                raise ValueError("Motif pool must contain unique motifs")
        return v
    
    class Config:
        schema_extra = {
            "example": {
                "population": 18000,
                "wealth_level": 0.7,
                "political_stability": 0.8,
                "danger_level": 3,
                "tension_level": 15.0,
                "motif_pool": ["growing_prosperity", "trade_expansion"],
                "secondary_capitol_id": "new_trade_center",
                "factions": ["merchant_guild", "farmers_association"]
            }
        }

class RegionResponseSchema(BaseModel):
    """Schema for region responses using strings per Bible"""
    id: UUID = Field(..., description="Unique region identifier")
    name: str = Field(..., description="Region name")
    description: str = Field(..., description="Region description")
    region_type: str = Field(..., description="Type of region (string per Bible)")
    dominant_biome: str = Field(..., description="Dominant biome type (string per Bible)")
    climate: str = Field(..., description="Climate type (string per Bible)")
    population: int = Field(..., description="Current population")
    area_square_km: float = Field(..., description="Area in square kilometers")
    danger_level: int = Field(..., description="Danger level (1-10)")
    exploration_status: float = Field(..., description="Exploration status (0.0 to 1.0)")
    continent_id: Optional[UUID] = Field(None, description="ID of the continent this region belongs to")
    center_coordinate: Optional[HexCoordinateSchema] = Field(None, description="Center hex coordinate")
    hex_coordinates: List[HexCoordinateSchema] = Field(default_factory=list, description="All hex coordinates")
    resource_nodes: List[ResourceNodeSchema] = Field(default_factory=list, description="Resource nodes in region")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    # Bible-required fields for complete region information
    level_range: List[int] = Field(default=[1, 5], description="Level range [min, max] for encounters/content")
    tension_level: float = Field(default=0.0, description="Current tension level (0-100)")
    motif_pool: List[str] = Field(default_factory=list, description="Active motif IDs (max 3)")
    motif_history: List[str] = Field(default_factory=list, description="Previously assigned motifs")
    memory: List[str] = Field(default_factory=list, description="Memory/core memory objects")
    arc: Optional[str] = Field(None, description="Current active arc ID")
    arc_history: List[str] = Field(default_factory=list, description="Resolved/failed arcs")
    history: List[str] = Field(default_factory=list, description="Major region events")
    primary_capitol_id: Optional[str] = Field(None, description="Primary (birth) capitol city ID - never changes")
    secondary_capitol_id: Optional[str] = Field(None, description="Current controlling capitol ID - changes with conquest")
    metropolis_type: Optional[str] = Field(None, description="Metropolis type: arcane/industrial/sacred/ruined/natural")
    factions: List[str] = Field(default_factory=list, description="Influential faction IDs")
    terrain_types: List[str] = Field(default_factory=list, description="List of terrain types present")
    wealth_level: float = Field(default=0.5, description="Wealth level (0.0 to 1.0)")
    political_stability: float = Field(default=0.5, description="Political stability (0.0 to 1.0)")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "Greenwood Valley",
                "description": "A peaceful valley known for its lush forests",
                "region_type": "duchy",
                "dominant_biome": "temperate_forest",
                "climate": "temperate",
                "population": 15000,
                "area_square_km": 2500.0,
                "danger_level": 2,
                "exploration_status": 0.8,
                "continent_id": "456e7890-e12b-34d5-a678-901234567890",
                "center_coordinate": {
                    "q": 0,
                    "r": 0,
                    "s": 0
                },
                "hex_coordinates": [
                    {"q": 0, "r": 0, "s": 0},
                    {"q": 1, "r": -1, "s": 0}
                ],
                "resource_nodes": [
                    {
                        "resource_type": "timber",
                        "abundance": 0.9,
                        "quality": 0.8,
                        "accessibility": 0.7,
                        "depletion_rate": 0.05,
                        "current_reserves": 0.95
                    }
                ],
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z",
                "level_range": [1, 5],
                "tension_level": 10.0,
                "motif_pool": ["forest_mystery", "ancient_ruins"],
                "motif_history": ["old_growth_legend"],
                "memory": ["CORE_MEMORY:Founded by forest druids in ancient times"],
                "arc": "trade_route_expansion",
                "arc_history": ["bandit_troubles:success"],
                "history": ["Founded by druids", "Trade routes established", "Bandit troubles resolved"],
                "primary_capitol_id": "greenwood_capital",
                "secondary_capitol_id": "greenwood_capital",
                "metropolis_type": "natural",
                "factions": ["forest_druids", "merchant_guild"],
                "terrain_types": ["forest", "hills", "river"],
                "wealth_level": 0.7,
                "political_stability": 0.8
            }
        }

# ============================================================================
# CONTINENT SCHEMAS
# ============================================================================

class ContinentCreateSchema(BaseModel):
    """Schema for creating a new continent"""
    name: str = Field(..., min_length=1, max_length=255, description="Continent name")
    description: Optional[str] = Field(None, max_length=2000, description="Continent description")
    properties: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional properties")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Aethermoor",
                "description": "The great northern continent, known for its magical forests and ancient ruins"
            }
        }

class ContinentResponseSchema(BaseModel):
    """Schema for continent responses using strings per Bible"""
    id: UUID = Field(..., description="Unique continent identifier")
    name: str = Field(..., description="Continent name")
    description: str = Field(..., description="Continent description")
    total_area_square_km: float = Field(..., description="Total area in square kilometers")
    political_situation: str = Field(..., description="Current political situation")
    climate_zones: List[str] = Field(default_factory=list, description="Climate zones (strings per Bible)")
    major_biomes: List[str] = Field(default_factory=list, description="Major biomes (strings per Bible)")
    region_count: int = Field(..., description="Number of regions in this continent")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "456e7890-e12b-34d5-a678-901234567890",
                "name": "Aethermoor",
                "description": "The great northern continent, known for its magical forests and ancient ruins",
                "total_area_square_km": 15000000.0,
                "political_situation": "stable",
                "climate_zones": ["temperate", "continental", "polar"],
                "major_biomes": ["temperate_forest", "coniferous_forest", "mountains"],
                "region_count": 25,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        }

# ============================================================================
# ANALYTICS & REPORTING SCHEMAS
# ============================================================================

class PopulationAnalyticsSchema(BaseModel):
    """Schema for population analytics data"""
    total_population: int = Field(..., description="Total population across all regions")
    average_population_per_region: float = Field(..., description="Average population per region")
    most_populated_region: dict = Field(..., description="Information about the most populated region")
    least_populated_region: dict = Field(..., description="Information about the least populated region")
    population_by_region_type: Dict[str, int] = Field(..., description="Population breakdown by region type")
    population_by_biome: Dict[str, int] = Field(..., description="Population breakdown by biome type")
    population_growth_trends: List[dict] = Field(default_factory=list, description="Historical population trends")
    
    class Config:
        schema_extra = {
            "example": {
                "total_population": 2500000,
                "average_population_per_region": 50000.0,
                "most_populated_region": {
                    "name": "Capital Region",
                    "population": 500000,
                    "region_type": "kingdom"
                },
                "least_populated_region": {
                    "name": "Frozen Wastes",
                    "population": 50,
                    "region_type": "wasteland"
                },
                "population_by_region_type": {
                    "kingdom": 800000,
                    "duchy": 600000,
                    "city_state": 400000
                },
                "population_by_biome": {
                    "temperate_forest": 900000,
                    "grassland": 700000,
                    "mountains": 300000
                }
            }
        }

class EconomicAnalyticsSchema(BaseModel):
    """Schema for economic analytics data"""
    total_wealth: float = Field(..., description="Total economic value across all regions")
    average_wealth_per_region: float = Field(..., description="Average wealth level per region")
    wealthiest_region: dict = Field(..., description="Information about the wealthiest region")
    poorest_region: dict = Field(..., description="Information about the poorest region")
    wealth_by_region_type: Dict[str, float] = Field(..., description="Wealth breakdown by region type")
    resource_distribution: Dict[str, int] = Field(..., description="Resource availability by type")
    trade_routes: List[dict] = Field(default_factory=list, description="Major trade routes")
    economic_trends: List[dict] = Field(default_factory=list, description="Historical economic trends")
    
    class Config:
        schema_extra = {
            "example": {
                "total_wealth": 45.5,
                "average_wealth_per_region": 0.65,
                "wealthiest_region": {
                    "name": "Golden Harbor",
                    "wealth_level": 0.95,
                    "region_type": "city_state"
                },
                "poorest_region": {
                    "name": "Barren Steppes",
                    "wealth_level": 0.15,
                    "region_type": "wasteland"
                },
                "wealth_by_region_type": {
                    "kingdom": 0.8,
                    "city_state": 0.85,
                    "wilderness": 0.2
                },
                "resource_distribution": {
                    "gold": 15,
                    "iron": 25,
                    "wood": 40
                }
            }
        }

# ============================================================================
# SEARCH & FILTER SCHEMAS
# ============================================================================

class RegionFilterSchema(BaseModel):
    """Schema for region filtering parameters using strings per Bible"""
    continent_id: Optional[UUID] = Field(None, description="Filter by continent ID")
    region_type: Optional[str] = Field(None, description="Filter by region type (string per Bible)")
    biome_type: Optional[str] = Field(None, description="Filter by biome type (string per Bible)")
    climate_type: Optional[str] = Field(None, description="Filter by climate type (string per Bible)")
    min_population: Optional[int] = Field(None, ge=0, description="Minimum population")
    max_population: Optional[int] = Field(None, ge=0, description="Maximum population")
    min_danger_level: Optional[int] = Field(None, ge=1, le=10, description="Minimum danger level")
    max_danger_level: Optional[int] = Field(None, ge=1, le=10, description="Maximum danger level")
    min_wealth_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum wealth level")
    max_wealth_level: Optional[float] = Field(None, ge=0.0, le=1.0, description="Maximum wealth level")
    name_search: Optional[str] = Field(None, description="Search in region names")
    
    @validator('region_type')
    def validate_region_type_filter(cls, v):
        """Validate region type filter (string per Bible)"""
        if v is not None and v not in VALID_REGION_TYPES:
            raise ValueError(f"Invalid region type: {v}. Must be one of: {VALID_REGION_TYPES}")
        return v
    
    @validator('biome_type')
    def validate_biome_type_filter(cls, v):
        """Validate biome type filter (string per Bible)"""
        if v is not None and v not in VALID_BIOME_TYPES:
            raise ValueError(f"Invalid biome type: {v}. Must be one of: {VALID_BIOME_TYPES}")
        return v
    
    @validator('climate_type')
    def validate_climate_type_filter(cls, v):
        """Validate climate type filter (string per Bible)"""
        if v is not None and v not in VALID_CLIMATE_TYPES:
            raise ValueError(f"Invalid climate type: {v}. Must be one of: {VALID_CLIMATE_TYPES}")
        return v

# ============================================================================
# WORLD GENERATION SCHEMAS
# ============================================================================

class WorldGenerationParametersSchema(BaseModel):
    """Schema for world generation parameters"""
    continent_count: int = Field(default=3, ge=1, le=10, description="Number of continents to generate")
    regions_per_continent: int = Field(default=20, ge=5, le=100, description="Average regions per continent")
    biome_diversity: float = Field(default=0.7, ge=0.0, le=1.0, description="Biome diversity factor")
    climate_zones: int = Field(default=5, ge=1, le=15, description="Number of distinct climate zones")
    political_complexity: float = Field(default=0.6, ge=0.0, le=1.0, description="Political complexity factor")
    magical_saturation: float = Field(default=0.3, ge=0.0, le=1.0, description="Magical saturation level")
    seed: Optional[int] = Field(None, description="Random seed for consistent generation")
    
    class Config:
        schema_extra = {
            "example": {
                "continent_count": 4,
                "regions_per_continent": 25,
                "biome_diversity": 0.8,
                "climate_zones": 6,
                "political_complexity": 0.7,
                "magical_saturation": 0.4,
                "seed": 12345
            }
        } 