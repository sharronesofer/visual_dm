"""
World-related data models and structures.
Defines the core world models and their relationships.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import uuid4
from backend.data.modding.loaders.game_data_registry import GameDataRegistry
from enum import Enum

class TerrainType(BaseModel):
    """Represents a type of terrain in the world."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    movement_cost: float = Field(..., ge=1.0)
    visibility_modifier: float = Field(..., ge=0.0, le=1.0)
    resources: List[str] = Field(default_factory=list)
    features: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class Region(BaseModel):
    """
    Canonical Region model for world/narrative/mechanical logic.
    
    Represents a region in the world, including all narrative and mechanical properties required by the Q&A and consolidation requirements.

    Fields:
        id: Unique region identifier (UUID string)
        name: Name of the region
        description: Description of the region
        level_range: Tuple of (min_level, max_level) for the region
        terrain_types: List of terrain type IDs
        points_of_interest: List of POI IDs in the region
        factions: List of faction IDs present in the region
        climate: Climate description
        created_at: UTC timestamp of creation
        updated_at: UTC timestamp of last update
        metadata: Arbitrary metadata for extensibility
        primary_capitol_id: ID of the original (birth) capitol city (historical)
        secondary_capitol_id: ID of the current controlling capitol city (changes with conquest/revolt)
        metropolis_type: Type of metropolis (Arcane, Industrial, Sacred, Ruined, Natural)
        motif_pool: List of 3 unique active motif IDs (narrative drivers, hidden from player)
        motif_history: List of motif IDs previously assigned to this region
        memory: List of memory/core memory objects for major events (summarized at intervals)
        arc: ID of the current active arc (meta-quest) for the region
        arc_history: List of arc IDs (resolved/failed) for this region
        history: List of major region events (capitol changes, arc failures, tension spikes, etc.)
        population: Total population of the region (used for city/POI generation)
        tension_level: Current tension level (0-100) between factions in the region

    Example usage:
        region = Region(
            name="The Verdant Expanse",
            description="A lush, wild region teeming with life.",
            level_range=(1, 5),
            terrain_types=["forest", "river"],
            points_of_interest=["poi_1", "poi_2"],
            factions=["faction_1"],
            climate="temperate",
            primary_capitol_id="city_1",
            metropolis_type="Natural",
            motif_pool=["motif_growth", "motif_conflict", "motif_renewal"],
            population=12000,
            tension_level=15
        )
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    level_range: Tuple[int, int] = Field(..., ge=1, le=20)
    terrain_types: List[str] = Field(default_factory=list)
    points_of_interest: List[str] = Field(default_factory=list)
    factions: List[str] = Field(default_factory=list)
    climate: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # --- Consolidation/Q&A fields ---
    primary_capitol_id: Optional[str] = Field(None, description="ID of the original (birth) capitol city. Never changes; historical note.")
    secondary_capitol_id: Optional[str] = Field(None, description="ID of the current controlling capitol city. Changes with conquest or revolt.")
    metropolis_type: Optional[str] = Field(None, description="Type of metropolis: Arcane, Industrial, Sacred, Ruined, Natural. Assigned at creation, never changes.")
    motif_pool: List[str] = Field(default_factory=list, description="List of 3 unique active motif IDs for the region. Motifs are narrative drivers, hidden from the player.")
    motif_history: List[str] = Field(default_factory=list, description="History of motifs previously assigned to this region.")
    memory: List[Dict[str, Any]] = Field(default_factory=list, description="List of memory/core memory objects for major events. Summarized at daily, weekly, monthly, annual intervals.")
    arc: Optional[str] = Field(None, description="ID of the current active arc (meta-quest) for the region. Only one at a time.")
    arc_history: List[str] = Field(default_factory=list, description="History of arcs (resolved/failed) for this region.")
    history: List[Dict[str, Any]] = Field(default_factory=list, description="List of major region events, including capitol changes, arc failures, tension spikes, etc.")
    population: int = Field(0, description="Total population of the region, used for city/POI generation.")
    tension_level: int = Field(0, description="Current tension level (0-100) between factions in the region.")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("level_range")
    @classmethod
    def validate_level_range(cls, v):
        """Validate that the level range is valid."""
        min_level, max_level = v
        if min_level > max_level:
            raise ValueError("Minimum level cannot be greater than maximum level")
        return v

class PointOfInterest(BaseModel):
    """Represents a point of interest in the world."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    type: str  # e.g., "town", "dungeon", "landmark"
    region_id: str
    coordinates: Tuple[float, float]
    level: int = Field(..., ge=1, le=20)
    npcs: List[str] = Field(default_factory=list)
    quests: List[str] = Field(default_factory=list)
    resources: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """Validate the POI type using registry."""
        registry = GameDataRegistry("backend/data/modding")
        registry.load_all()
        valid_types = [poi['id'] for poi in getattr(registry, 'poi_types', [])] + [poi['name'] for poi in getattr(registry, 'poi_types', [])]
        if v.lower() not in [t.lower() for t in valid_types]:
            # Fallback for legacy data
            return v.lower()
        return v.lower()

class WorldMap(BaseModel):
    """Represents the world map and its properties."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    regions: List[str] = Field(default_factory=list)
    width: int = Field(..., ge=1)
    height: int = Field(..., ge=1)
    scale: float = Field(..., gt=0.0)  # meters per unit
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    def get_region_at(self, x: int, y: int) -> Optional[str]:
        """Get the region ID at the specified coordinates."""
        # This would be implemented based on the actual map data structure
        pass

    def get_pois_in_region(self, region_id: str) -> List[str]:
        """Get all POIs in a specific region."""
        # This would be implemented based on the actual map data structure
        pass

    def calculate_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """Calculate the distance between two points on the map."""
        dx = x2 - x1
        dy = y2 - y1
        return (dx * dx + dy * dy) ** 0.5 * self.scale

class WorldState(BaseModel):
    """Represents the current state of the world."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    current_time: datetime = Field(default_factory=datetime.utcnow)
    weather: str
    season: str
    active_events: List[str] = Field(default_factory=list)
    active_quests: List[str] = Field(default_factory=list)
    active_npcs: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

    @field_validator("weather")
    @classmethod
    def validate_weather(cls, v):
        """Validate the weather type using registry."""
        registry = GameDataRegistry("backend/data/modding")
        registry.load_all()
        valid_weather = [w['id'] for w in getattr(registry, 'weather_types', [])] + [w['name'] for w in getattr(registry, 'weather_types', [])]
        if v.lower() not in [w.lower() for w in valid_weather]:
            # Fallback for legacy data
            return v.lower()
        return v.lower()

    @field_validator("season")
    @classmethod
    def validate_season(cls, v):
        """Validate the season."""
        valid_seasons = ["spring", "summer", "autumn", "winter"]
        if v.lower() not in valid_seasons:
            raise ValueError(f"Invalid season. Must be one of: {valid_seasons}")
        return v.lower()

    def advance_time(self, hours: int = 1) -> None:
        """Advance the world time by the specified number of hours."""
        self.current_time = self.current_time + datetime.timedelta(hours=hours)
        self.updated_at = datetime.utcnow()

    def update_weather(self, new_weather: str) -> None:
        """Update the current weather."""
        self.weather = new_weather
        self.updated_at = datetime.utcnow()

    def add_event(self, event_id: str) -> None:
        """Add an active event to the world state."""
        if event_id not in self.active_events:
            self.active_events.append(event_id)
            self.updated_at = datetime.utcnow()

    def remove_event(self, event_id: str) -> None:
        """Remove an active event from the world state."""
        if event_id in self.active_events:
            self.active_events.remove(event_id)
            self.updated_at = datetime.utcnow()

class LevelRange(BaseModel):
    """Range of character levels for an area."""
    min_level: int
    max_level: int

class LocationType(str, Enum):
    """Types of locations in the game world."""
    CITY = "city"
    TOWN = "town"
    VILLAGE = "village"
    DUNGEON = "dungeon"
    RUINS = "ruins"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    COASTAL = "coastal"
    DESERT = "desert"
    CAVE = "cave"
    TEMPLE = "temple"
    CASTLE = "castle"
    FORTRESS = "fortress"
    TOWER = "tower"
    CAMP = "camp"
    TAVERN = "tavern"
    SHOP = "shop"
    HOUSE = "house"
    FARM = "farm"
    MINE = "mine"
    VAULT = "vault"
    OTHER = "other"

class Weather(str, Enum):
    """Weather conditions in the game world."""
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    THUNDERSTORM = "thunderstorm"
    SNOW = "snow"
    BLIZZARD = "blizzard"
    FOG = "fog"
    WINDY = "windy"
    STORMY = "stormy"
    HAIL = "hail"
    SLEET = "sleet"
    HURRICANE = "hurricane"
    TORNADO = "tornado"
    SANDSTORM = "sandstorm"
    HEATWAVE = "heatwave"
    DROUGHT = "drought"
    FLOOD = "flood"

class Season(str, Enum):
    """Seasons in the game world."""
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"

class WorldRegion(BaseModel):
    """
    Represents a geographical region in the game world.
    """
    id: str
    name: str
    description: str
    level_range: LevelRange
    type: LocationType
    climate: str
    culture: str
    government: str
    population: int
    notable_npcs: List[str] = []
    points_of_interest: List[str] = []
    dangers: List[str] = []
    rumors: List[str] = []
    treasures: List[str] = []
    quests: List[str] = []
    
    @field_validator("level_range")
    @classmethod
    def validate_level_range(cls, v):
        """Validate level range."""
        if v.min_level > v.max_level:
            raise ValueError(f"Min level {v.min_level} cannot be greater than max level {v.max_level}")
        if v.min_level < 1:
            raise ValueError(f"Min level cannot be less than 1, got {v.min_level}")
        return v
    
    @field_validator("type")
    @classmethod
    def validate_type(cls, v):
        """Validate location type."""
        if v not in LocationType.__members__.values():
            raise ValueError(f"Invalid location type: {v}")
        return v

class WorldLocation(BaseModel):
    """
    Represents a specific location in the game world.
    """
    id: str
    name: str
    description: str
    region_id: str
    type: LocationType
    size: str
    importance: int
    population: Optional[int] = None
    rulers: List[str] = []
    factions: List[str] = []
    services: List[str] = []
    plot_hooks: List[str] = []
    secrets: List[str] = []
    encounters: List[str] = []
    npcs: List[str] = []
    
    @field_validator("type")
    @classmethod
    def validate_location_type(cls, v):
        """Validate location type."""
        if v not in LocationType.__members__.values():
            raise ValueError(f"Invalid location type: {v}")
        return v

class WorldConditions(BaseModel):
    """
    Represents the current environmental conditions in a location.
    """
    location_id: str
    weather: Weather
    season: Season
    time_of_day: str
    light_level: str
    temperature: str
    special_conditions: List[str] = []
    affects_gameplay: bool = True
    
    @field_validator("weather")
    @classmethod
    def validate_weather(cls, v):
        """Validate weather type."""
        if v not in Weather.__members__.values():
            raise ValueError(f"Invalid weather type: {v}")
        return v
    
    @field_validator("season")
    @classmethod
    def validate_season(cls, v):
        """Validate season."""
        if v not in Season.__members__.values():
            raise ValueError(f"Invalid season: {v}")
        return v

class WorldEvent(BaseModel):
    """
    Represents a significant event in the game world.
    """
    id: str
    name: str
    description: str
    location_ids: List[str]
    start_time: str
    end_time: Optional[str] = None
    participating_npcs: List[str] = []
    participating_factions: List[str] = []
    consequences: List[str] = []
    player_involvement: bool = False
    recurring: bool = False
    hidden: bool = False 