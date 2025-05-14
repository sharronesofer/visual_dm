"""
World state and related models.
"""

# NOTE: No SQLAlchemy World class is currently defined.

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, func, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.core.db_base import Base, db
from app.core.models.region import Region
from app.core.enums import WorldType
from random import random, choices
from app.core.models.resource import Resource
from app.core.models.trade_route import TradeRoute
from app.core.models.world_event import WorldEvent
# from app.core.schemas.base import BaseSchema  # Uncomment or fix this import if available
from dataclasses import dataclass, field
import logging
import uuid
import json
import copy

from app.core.models.entity import Entity
from app.core.models.character import Character
from app.core.models.location import Location
from app.core.models.item import Item
from app.core.models.world_state import WorldState
from app.core.persistence.world_persistence import WorldPersistenceManager, FileSystemStorageStrategy
from app.core.persistence.serialization import serialize, deserialize
from app.core.persistence.transaction import Transaction

logger = logging.getLogger(__name__)

class Season(str, Enum):
    SPRING = "spring"
    SUMMER = "summer"
    FALL = "fall"
    WINTER = "winter"

class Weather(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"
    FOG = "fog"

class WorldState(Enum):
    """Possible states of a game world."""
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"
    CORRUPTED = "corrupted"

# class WorldSchema(BaseSchema):
#     """Pydantic schema for world data validation."""
#     id: int
#     name: str
#     description: str
#     is_active: bool
#     game_time: WorldTime
#     world_type: WorldType
#     created_at: datetime
#     updated_at: datetime

class WorldTime(BaseModel):
    """Model for tracking world time and season."""
    hour: int = 0
    day: int = 1
    month: int = 1
    year: int = 1
    season: Season = Season.SPRING

    def advance(self, hours: int = 1):
        HOURS_PER_DAY = 24
        DAYS_PER_MONTH = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}
        MONTHS_PER_YEAR = 12
        SEASON_TRANSITIONS = {3: Season.SPRING, 6: Season.SUMMER, 9: Season.FALL, 12: Season.WINTER}

        self.hour += hours
        while self.hour >= HOURS_PER_DAY:
            self.hour -= HOURS_PER_DAY
            self.day += 1
        while self.day > DAYS_PER_MONTH[self.month]:
            self.day -= DAYS_PER_MONTH[self.month]
            self.month += 1
            if self.month > MONTHS_PER_YEAR:
                self.month = 1
                self.year += 1
        # Update season if month matches a transition
        if self.month in SEASON_TRANSITIONS:
            self.season = SEASON_TRANSITIONS[self.month]

    def to_string(self) -> str:
        return f"{self.year:04d}-{self.month:02d}-{self.day:02d} {self.hour:02d}:00 ({self.season.value})"

    @classmethod
    def from_string(cls, s: str):
        # Example: '2025-03-15 14:00 (spring)'
        import re
        m = re.match(r"(\d+)-(\d+)-(\d+) (\d+):00 \((\w+)\)", s)
        if not m:
            raise ValueError(f"Invalid time string: {s}")
        year, month, day, hour, season = m.groups()
        return cls(hour=int(hour), day=int(day), month=int(month), year=int(year), season=Season(season))

    def format(self, fmt: str = "%Y-%m-%d %H:00 (%S)") -> str:
        # Custom formatter, %Y=year, %m=month, %d=day, %H=hour, %S=season
        return fmt.replace("%Y", str(self.year)).replace("%m", f"{self.month:02d}") \
            .replace("%d", f"{self.day:02d}").replace("%H", f"{self.hour:02d}") \
            .replace("%S", self.season.value)

class WeatherState(str, Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    SNOW = "snow"
    STORM = "storm"
    FOG = "fog"

class WeatherData(BaseModel):
    condition: WeatherState = WeatherState.CLEAR
    temperature: float = 20.0
    wind_speed: float = 0.0
    precipitation: float = 0.0
    visibility: float = 100.0
    last_update: datetime = Field(default_factory=datetime.utcnow)

# --- TEMPORARY: Minimal SQLAlchemy World model for Alembic migration and tick_world_day ---
class World(db.Model):
    __tablename__ = 'worlds'
    id = db.Column(Integer, primary_key=True)
    name = db.Column(String(100), nullable=False)
    description = db.Column(Text)
    is_active = db.Column(Boolean, default=True)
    game_time = db.Column(JSON)
    world_type = db.Column(String(50), default='fantasy')
    created_at = db.Column(DateTime, default=datetime.utcnow)
    updated_at = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    weather = db.Column(JSON, default=dict)
    regions = relationship('Region', back_populates='world', cascade='all, delete-orphan')
    factions = relationship('Faction', back_populates='world', cascade='all, delete-orphan')
# --- TEMPORARY: Comment out hybrid World(BaseModel) for Alembic migration ---
# class World(BaseModel):
#     """Model for managing the game world state."""
#     __tablename__ = 'worlds'
#     __table_args__ = {'extend_existing': True}
#
#     id: Mapped[int] = mapped_column(Integer, primary_key=True)
#     name: Mapped[str] = mapped_column(String(100), nullable=False)
#     description: Mapped[str] = mapped_column(Text)
#     is_active: Mapped[bool] = mapped_column(Boolean, default=True)
#     game_time: Mapped[Dict[str, int]] = mapped_column(JSON)
#     world_type: Mapped[WorldType] = mapped_column(SQLEnum(WorldType), default=WorldType.FANTASY)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
#     updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
#     weather: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict)  # region_id -> WeatherData dict
#
#     def to_dict(self) -> Dict[str, Any]:
#         ...
#     # (rest of methods omitted for migration)

class WorldMap(BaseModel):
    """Model for the game world map."""
    id: int
    name: str = Field(description="Name of the map")
    description: str = Field(description="Description of the map")
    width: int = Field(default=100, description="Width of the map in tiles")
    height: int = Field(default=100, description="Height of the map in tiles")
    scale: float = Field(default=1.0, description="Scale of the map")
    regions: List[str] = Field(default_factory=list, description="List of region IDs")
    connections: List[Dict] = Field(default_factory=list, description="List of region connections")
    tiles: List[List[Dict]] = Field(default_factory=lambda: [[]])
    points_of_interest: List[Dict] = Field(default_factory=list)
    terrain_features: List[Dict] = Field(default_factory=list)
    navigation_data: Dict = Field(default_factory=dict)

    def get_region_at(self, x: int, y: int) -> Optional[Dict]:
        """Get the region at the specified coordinates."""
        for region in self.regions:
            if region.get("bounds", {}).get("contains", lambda x, y: False)(x, y):
                return region
        return None

    def add_point_of_interest(self, poi: Dict):
        """Add a new point of interest to the map."""
        self.points_of_interest.append(poi)

class TerrainType(BaseModel):
    """Model for terrain types."""
    id: int
    name: str
    description: str = Field(default="", description="Description of the terrain type")
    movement_cost: float = Field(default=1.0, description="Movement cost multiplier")
    visibility_modifier: float = Field(default=1.0, description="Visibility modifier")
    combat_modifier: float = Field(default=1.0, description="Combat modifier")
    combat_effects: Dict = Field(default_factory=dict)
    resource_types: List[str] = Field(default_factory=list)
    hazards: List[Dict] = Field(default_factory=list)
    properties: Dict = Field(default_factory=dict)

class Region(BaseModel):
    """Region model."""
    
    id: int
    name: str
    description: str = Field(default="", description="Description of the region")
    climate: str = Field(default="temperate", description="Climate type")
    level_range: List[int] = Field(default=[1, 20], description="Level range for the region")
    terrain_types: List[str] = Field(default_factory=list, description="List of terrain type IDs")
    points_of_interest: List[str] = Field(default_factory=list, description="List of POI IDs")

class PointOfInterest(BaseModel):
    """Model for points of interest on the map."""
    id: int
    name: str
    description: str = Field(default="", description="Description of the POI")
    type: str = Field(default="location", description="Type of POI")
    region_id: int = Field(description="ID of the region containing this POI")
    level: int = Field(default=1, description="Level of the POI")
    coordinates: List[float] = Field(default=[0.0, 0.0], description="Coordinates within the region")
    properties: Dict = Field(default_factory=dict, description="Additional properties")
    connected_to: List[int] = Field(default_factory=list)
    requirements: Dict = Field(default_factory=dict)
    rewards: Dict = Field(default_factory=dict)

    def update_weather(self, new_weather: Weather):
        """Update the current weather."""
        self.weather = new_weather
        self.last_update = datetime.utcnow()

    def advance_season(self):
        """Move to the next season."""
        seasons = list(Season)
        current_index = seasons.index(self.season)
        next_index = (current_index + 1) % len(seasons)
        self.season = seasons[next_index]
        self.last_update = datetime.utcnow()

    def add_event(self, event: Dict):
        """Add a new world event."""
        self.current_events.append(event)
        self.last_update = datetime.utcnow()

    def update_faction(self, faction_id: str, new_state: Dict):
        """Update the state of a faction."""
        self.faction_states[faction_id] = new_state
        self.last_update = datetime.utcnow()

    def get_current_season(self) -> str:
        """
        Get the current season based on world time
        """
        month = self.current_time.month
        if month in (12, 1, 2):
            return 'winter'
        elif month in (3, 4, 5):
            return 'spring'
        elif month in (6, 7, 8):
            return 'summer'
        else:
            return 'autumn'

    def get_weather(self, region_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Get current weather conditions, optionally for a specific region
        """
        if region_id:
            return self.state.get('weather_conditions', {}).get(str(region_id), {})
        return self.state.get('weather_conditions', {})

    def set_weather(self, conditions: Dict[str, Any], region_id: Optional[int] = None) -> None:
        """
        Set weather conditions, optionally for a specific region
        """
        if 'weather_conditions' not in self.state:
            self.state['weather_conditions'] = {}
        
        if region_id:
            self.state['weather_conditions'][str(region_id)] = conditions
        else:
            self.state['weather_conditions'] = conditions
    
    def get_trade_routes(self) -> List[Dict[str, Any]]:
        """
        Get all active trade routes
        """
        return self.state.get('trade_routes', [])
    
    def add_trade_route(self, route: Dict[str, Any]) -> None:
        """
        Add a new trade route
        """
        if 'trade_routes' not in self.state:
            self.state['trade_routes'] = []
        
        route['established_date'] = datetime.utcnow().isoformat()
        self.state['trade_routes'].append(route)
    
    def remove_trade_route(self, route_id: str) -> None:
        """
        Remove a trade route
        """
        routes = self.state.get('trade_routes', [])
        self.state['trade_routes'] = [r for r in routes if r.get('id') != route_id]

# Unit tests for WorldTime (to be moved to tests/ later)
if __name__ == "__main__":
    def test_advance_time():
        wt = WorldTime(hour=23, day=30, month=2, year=2025, season=Season.WINTER)
        wt.advance(2)  # Should roll over to day 1, month 3, and season SPRING
        assert wt.hour == 1
        assert wt.day == 1
        assert wt.month == 3
        assert wt.year == 2025
        assert wt.season == Season.SPRING
        print("test_advance_time passed")

    def test_to_string_and_from_string():
        wt = WorldTime(hour=14, day=15, month=3, year=2025, season=Season.SPRING)
        s = wt.to_string()
        wt2 = WorldTime.from_string(s)
        assert wt2.hour == 14
        assert wt2.day == 15
        assert wt2.month == 3
        assert wt2.year == 2025
        assert wt2.season == Season.SPRING
        print("test_to_string_and_from_string passed")

    test_advance_time()
    test_to_string_and_from_string()

    def test_weather_system():
        w = World(id=1, name="TestWorld", description="desc", is_active=True, game_time=WorldTime().dict(), world_type=WorldType.FANTASY, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        w.advance_time(24*30*2)  # Move to spring
        w.update_weather()
        weather = w.get_weather()
        assert isinstance(weather, WeatherData)
        assert weather.condition in WeatherState
        print(f"Weather: {weather.condition}, Temp: {weather.temperature}")
        print("test_weather_system passed")

    test_weather_system()

    def test_economic_system():
        # Mock session with in-memory objects
        class DummySession:
            def __init__(self):
                self._regions = []
                self._factions = []
                self._resources = []
                self._trade_routes = []
            def query(self, model):
                if model.__name__ == 'Region':
                    return self._regions
                if model.__name__ == 'Faction':
                    return self._factions
                if model.__name__ == 'Resource':
                    return self._resources
                if model.__name__ == 'TradeRoute':
                    return self._trade_routes
            def commit(self):
                pass
            def add(self, obj):
                if isinstance(obj, Resource):
                    self._resources.append(obj)
                elif isinstance(obj, TradeRoute):
                    self._trade_routes.append(obj)
        # Setup
        session = DummySession()
        from types import SimpleNamespace
        region = SimpleNamespace(resources=[])
        faction = SimpleNamespace(resources=[])
        resource = Resource(id=1, name="Wheat", type="food", amount=100, price=1.0)
        region.resources.append(resource)
        session._regions.append(region)
        session._resources.append(resource)
        # Test production
        w = World(id=1, name="TestWorld", description="desc", is_active=True, game_time=WorldTime().dict(), world_type=WorldType.FANTASY, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        w.produce_resources(session)
        assert resource.amount > 100
        # Test consumption
        faction.resources.append(resource)
        session._factions.append(faction)
        w.consume_resources(session)
        assert resource.amount < 110  # After production and consumption
        # Test price update
        w.update_resource_prices(session)
        assert resource.price > 0
        print("test_economic_system passed")

    test_economic_system()

    def test_event_system():
        class DummySession:
            def __init__(self):
                self._events = []
            def add(self, obj):
                self._events.append(obj)
            def commit(self):
                pass
            def query(self, model):
                class Q:
                    def filter(self, *args, **kwargs):
                        return [e for e in self._events if e.status == 'active']
                    def filter_by(self, **kwargs):
                        return [e for e in self._events if all(getattr(e, k) == v for k, v in kwargs.items())]
                return Q()
        session = DummySession()
        w = World(id=1, name="TestWorld", description="desc", is_active=True, game_time=WorldTime().dict(), world_type=WorldType.FANTASY, created_at=datetime.utcnow(), updated_at=datetime.utcnow())
        event = w.generate_random_event(session)
        assert event in session._events
        w.schedule_event(session, event, datetime.utcnow())
        assert event.status == 'scheduled'
        event.end_time = datetime.utcnow()
        event.status = 'active'
        w.resolve_events(session)
        assert event.status == 'resolved'
        w.notify_players(event)
        print("test_event_system passed")

    test_event_system()

@dataclass
class World:
    """
    Represents a complete game world.
    
    The World class encapsulates all entities, state, and behavior of the game world.
    It provides methods for managing entities, running simulations, and persisting state.
    """
    name: str
    description: str = ""
    world_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    state: WorldState = field(default_factory=WorldState)
    persistence_manager: Optional[WorldPersistenceManager] = None
    _is_loaded_from_storage: bool = False
    _metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize the world after creation."""
        # Set up any required connections or resources
        self.state.attach_world(self)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert world to dictionary for serialization.
        
        Returns:
            Dictionary representation of the world
        """
        return {
            "world_id": self.world_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at,
            "metadata": self._metadata,
            "state": self.state.to_dict(),
            "last_modified": datetime.utcnow().isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'World':
        """
        Create a world from a dictionary representation.
        
        Args:
            data: Dictionary representation of the world
            
        Returns:
            World instance
        """
        world_id = data.get("world_id", str(uuid.uuid4()))
        name = data.get("name", "Untitled World")
        description = data.get("description", "")
        created_at = data.get("created_at", datetime.utcnow().isoformat())
        metadata = data.get("metadata", {})
        
        # Create world with basic properties
        world = cls(
            world_id=world_id,
            name=name,
            description=description,
            created_at=created_at
        )
        
        # Set metadata
        world._metadata = metadata
        
        # Initialize state from dict if available
        if "state" in data:
            world.state = WorldState.from_dict(data["state"])
            world.state.attach_world(world)
        
        # Mark as loaded from storage
        world._is_loaded_from_storage = True
        
        return world
    
    def initialize_persistence(self, storage_root: str) -> None:
        """
        Initialize persistence for this world.
        
        Args:
            storage_root: Root directory for storage
        """
        storage = FileSystemStorageStrategy(storage_root)
        self.persistence_manager = WorldPersistenceManager(storage)
    
    def save(self, create_snapshot: bool = False, description: Optional[str] = None) -> bool:
        """
        Save the world to storage.
        
        Args:
            create_snapshot: Whether to create a version snapshot
            description: Description for the snapshot
            
        Returns:
            True if successful, False otherwise
        """
        if self.persistence_manager is None:
            logger.error("Cannot save world: persistence not initialized")
            return False
        
        # Convert world to dict format
        world_dict = self.to_dict()
        
        # If not already loaded from storage, create in storage
        if not self._is_loaded_from_storage:
            if self.persistence_manager.load_world(self.world_id) is None:
                # Create new world in storage
                self.persistence_manager.create_world(self.world_id, self._metadata)
                self._is_loaded_from_storage = True
        
        # Update cache
        self.persistence_manager.worlds_cache[self.world_id] = world_dict
        
        # Save to storage
        return self.persistence_manager.save_world(
            self.world_id, 
            create_snapshot=create_snapshot,
            description=description
        )
    
    @classmethod
    def load(cls, world_id: str, storage_root: str, version_id: Optional[str] = None) -> Optional['World']:
        """
        Load a world from storage.
        
        Args:
            world_id: ID of the world to load
            storage_root: Root directory for storage
            version_id: Specific version to load (latest if None)
            
        Returns:
            Loaded world, or None if not found
        """
        # Initialize storage and persistence manager
        storage = FileSystemStorageStrategy(storage_root)
        persistence_manager = WorldPersistenceManager(storage)
        
        # Load world data
        world_data = persistence_manager.load_world(world_id, version_id)
        
        if world_data is None:
            logger.error(f"Failed to load world {world_id}")
            return None
        
        # Create world from data
        world = cls.from_dict(world_data)
        
        # Attach persistence manager
        world.persistence_manager = persistence_manager
        
        return world
    
    def create_snapshot(self, description: Optional[str] = None) -> Optional[str]:
        """
        Create a version snapshot of the world.
        
        Args:
            description: Description for the snapshot
            
        Returns:
            ID of the created version, or None if failed
        """
        if self.persistence_manager is None:
            logger.error("Cannot create snapshot: persistence not initialized")
            return None
        
        # Save first to ensure latest state
        self.save()
        
        # Create snapshot
        return self.persistence_manager.create_snapshot(self.world_id, description)
    
    def rollback_to_version(self, version_id: str) -> bool:
        """
        Roll back to a previous version.
        
        Args:
            version_id: ID of the version to roll back to
            
        Returns:
            True if successful, False otherwise
        """
        if self.persistence_manager is None:
            logger.error("Cannot roll back: persistence not initialized")
            return False
        
        # Roll back
        world_data = self.persistence_manager.rollback_to_version(self.world_id, version_id)
        
        if world_data is None:
            logger.error(f"Failed to roll back to version {version_id}")
            return False
        
        # Update world from data
        loaded_world = self.from_dict(world_data)
        
        # Update this world's properties
        self.name = loaded_world.name
        self.description = loaded_world.description
        self._metadata = loaded_world._metadata
        self.state = loaded_world.state
        self.state.attach_world(self)
        
        return True
    
    def begin_transaction(self, name: Optional[str] = None) -> Optional[Transaction]:
        """
        Begin a new transaction for batching changes.
        
        Args:
            name: Optional name for the transaction
            
        Returns:
            Transaction object, or None if persistence not initialized
        """
        if self.persistence_manager is None:
            logger.error("Cannot begin transaction: persistence not initialized")
            return None
        
        # Get transaction manager
        transaction_manager = self.persistence_manager.get_transaction_manager(self.world_id)
        
        if transaction_manager is None:
            logger.error("Transaction manager not found")
            return None
        
        # Create transaction
        return transaction_manager.begin_transaction(name)
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """
        List all versions of this world.
        
        Returns:
            List of version metadata
        """
        if self.persistence_manager is None:
            logger.error("Cannot list versions: persistence not initialized")
            return []
        
        # Get version control
        version_control = self.persistence_manager.get_version_control(self.world_id)
        
        if version_control is None:
            logger.error("Version control not found")
            return []
        
        # Get versions
        return version_control.list_versions()
    
    def add_entity(self, entity: Entity) -> bool:
        """
        Add an entity to the world.
        
        Args:
            entity: Entity to add
            
        Returns:
            True if added, False if already exists
        """
        return self.state.add_entity(entity)
    
    def remove_entity(self, entity_id: str) -> bool:
        """
        Remove an entity from the world.
        
        Args:
            entity_id: ID of the entity to remove
            
        Returns:
            True if removed, False if not found
        """
        return self.state.remove_entity(entity_id)
    
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """
        Get an entity by ID.
        
        Args:
            entity_id: ID of the entity
            
        Returns:
            Entity if found, None otherwise
        """
        return self.state.get_entity(entity_id)
    
    def get_all_entities(self) -> List[Entity]:
        """
        Get all entities in the world.
        
        Returns:
            List of all entities
        """
        return self.state.get_all_entities()
    
    def get_characters(self) -> List[Character]:
        """
        Get all characters in the world.
        
        Returns:
            List of all characters
        """
        return self.state.get_characters()
    
    def get_locations(self) -> List[Location]:
        """
        Get all locations in the world.
        
        Returns:
            List of all locations
        """
        return self.state.get_locations()
    
    def get_items(self) -> List[Item]:
        """
        Get all items in the world.
        
        Returns:
            List of all items
        """
        return self.state.get_items()
    
    def update_metadata(self, key: str, value: Any) -> None:
        """
        Update metadata for the world.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self._metadata[key] = value
        
        # Mark as dirty
        if self.persistence_manager is not None:
            self.persistence_manager.mark_world_dirty(self.world_id)
    
    def get_metadata(self, key: str) -> Optional[Any]:
        """
        Get metadata value.
        
        Args:
            key: Metadata key
            
        Returns:
            Metadata value if exists, None otherwise
        """
        return self._metadata.get(key)
    
    def get_all_metadata(self) -> Dict[str, Any]:
        """
        Get all metadata.
        
        Returns:
            Dictionary of all metadata
        """
        return copy.deepcopy(self._metadata)
    
    def __str__(self) -> str:
        """
        Get string representation of the world.
        
        Returns:
            String representation
        """
        entity_count = len(self.state.get_all_entities())
        character_count = len(self.state.get_characters())
        location_count = len(self.state.get_locations())
        item_count = len(self.state.get_items())
        
        return (
            f"World: {self.name} (ID: {self.world_id})\n"
            f"Description: {self.description}\n"
            f"Created: {self.created_at}\n"
            f"Entities: {entity_count} total ({character_count} characters, "
            f"{location_count} locations, {item_count} items)"
        ) 