from sqlalchemy import Column, String, Float, Integer, Enum, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
from backend.app.models.base import BaseModel

class Season(enum.Enum):
    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"

class WeatherCondition(enum.Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"
    FOG = "fog"
    WINDY = "windy"

class World(BaseModel):
    """World model representing the game world state."""
    
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Time tracking
    current_time = Column(DateTime, default=datetime.utcnow)
    time_scale = Column(Float, default=1.0)  # How fast game time passes relative to real time
    
    # Season and weather tracking
    current_season = Column(Enum(Season), default=Season.SPRING)
    current_weather = Column(Enum(WeatherCondition), default=WeatherCondition.CLEAR)
    weather_duration = Column(Integer, default=24)  # Duration in in-game hours
    
    # World settings and features
    has_day_night_cycle = Column(Boolean, default=True)
    has_seasons = Column(Boolean, default=True)
    has_dynamic_weather = Column(Boolean, default=True)
    
    # World size and boundaries
    width = Column(Float)
    height = Column(Float)
    is_infinite = Column(Boolean, default=False)
    
    # Relationships
    locations = relationship("Location", back_populates="world")
    
    def __repr__(self):
        return f"<World {self.name}>" 