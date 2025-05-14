"""
World-related data models and structures.
Defines the core world models and their relationships.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pydantic import BaseModel, Field, validator
from uuid import uuid4

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

class Region(BaseModel):
    """Represents a region in the world."""
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

    @validator("level_range")
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

    @validator("type")
    def validate_type(cls, v):
        """Validate the POI type."""
        valid_types = ["town", "city", "village", "dungeon", "landmark", "ruin", "fortress"]
        if v.lower() not in valid_types:
            raise ValueError(f"Invalid POI type. Must be one of: {valid_types}")
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

    @validator("weather")
    def validate_weather(cls, v):
        """Validate the weather type."""
        valid_weather = ["clear", "cloudy", "rainy", "stormy", "snowy", "foggy"]
        if v.lower() not in valid_weather:
            raise ValueError(f"Invalid weather type. Must be one of: {valid_weather}")
        return v.lower()

    @validator("season")
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