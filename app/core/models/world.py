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