from sqlalchemy import Column, String, Integer, Float, Enum, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
import enum
from backend.infrastructure.models import BaseModel
from backend.infrastructure.shared.models.world import WeatherCondition

class LocationType(enum.Enum):
    CITY = "city"
    TOWN = "town"
    VILLAGE = "village"
    DUNGEON = "dungeon"
    CAVE = "cave"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    LAKE = "lake"
    RIVER = "river"
    OCEAN = "ocean"
    DESERT = "desert"
    RUIN = "ruin"
    TEMPLE = "temple"
    CASTLE = "castle"
    CAMP = "camp"
    SHOP = "shop"
    INN = "inn"
    HOUSE = "house"
    CUSTOM = "custom"

class Location(BaseModel):
    """Location model representing places in the game world."""
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Location type and characteristics
    type = Column(Enum(LocationType), nullable=False)
    size = Column(Float)  # Size in square units (kilometers, miles, etc.)
    
    # World positioning
    world_id = Column(Integer, ForeignKey('world.id'))
    world = relationship("World", back_populates="locations")
    x_coordinate = Column(Float)
    y_coordinate = Column(Float)
    z_coordinate = Column(Float)
    
    # Environment properties
    local_weather = Column(Enum(WeatherCondition))
    has_custom_weather = Column(Boolean, default=False)
    temperature = Column(Float)
    
    # Status and access
    is_discovered = Column(Boolean, default=False)
    is_accessible = Column(Boolean, default=True)
    discovery_requirements = Column(JSON)  # Requirements to discover this location
    access_requirements = Column(JSON)  # Requirements to access this location
    
    # Connected entities
    npcs = relationship("NPC", back_populates="location")
    resources = Column(JSON)  # Available resources and their states
    
    # Connected locations
    parent_id = Column(Integer, ForeignKey('location.id'), nullable=True)
    parent = relationship("Location", remote_side="Location.id", backref="sublocations")
    
    def __repr__(self):
        return f"<Location {self.name} ({self.type.name})>" 