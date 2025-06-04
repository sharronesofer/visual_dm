"""
Weather System Models

Core data structures for weather simulation.
"""

from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WeatherCondition(Enum):
    """Enumeration of possible weather conditions."""
    CLEAR = "clear"
    PARTLY_CLOUDY = "partly_cloudy"
    CLOUDY = "cloudy"
    OVERCAST = "overcast"
    LIGHT_RAIN = "light_rain"
    RAIN = "rain"
    HEAVY_RAIN = "heavy_rain"
    DRIZZLE = "drizzle"
    MIST = "mist"
    FOG = "fog"
    LIGHT_SNOW = "light_snow"
    SNOW = "snow"
    HEAVY_SNOW = "heavy_snow"
    BLIZZARD = "blizzard"
    THUNDERSTORM = "thunderstorm"
    WINDY = "windy"
    SCORCHING = "scorching"
    HAIL = "hail"
    HURRICANE = "hurricane"
    SANDSTORM = "sandstorm"


class Weather(BaseModel):
    """
    Represents current weather conditions.
    """
    condition: WeatherCondition = WeatherCondition.CLEAR
    temperature: float = 65.0  # Temperature in Fahrenheit
    humidity: float = 50.0  # Humidity percentage (0-100)
    wind_speed: float = 5.0  # Wind speed in mph
    pressure: float = 29.92  # Atmospheric pressure in inches of mercury
    visibility: float = 10.0  # Visibility in miles
    last_changed: datetime = Field(default_factory=datetime.utcnow)
    timestamp: datetime = Field(default_factory=datetime.utcnow)  # For event compatibility
    duration_hours: int = 4  # How long this weather should last
    
    def __str__(self) -> str:
        return f"{self.condition.value.replace('_', ' ').title()}, {self.temperature:.1f}°F"
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "condition": self.condition.value,
            "temperature": self.temperature,
            "humidity": self.humidity,
            "wind_speed": self.wind_speed,
            "pressure": self.pressure,
            "visibility": self.visibility,
            "last_changed": self.last_changed.isoformat() if self.last_changed else None,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "duration_hours": self.duration_hours
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Weather':
        """Create Weather instance from dictionary."""
        # Convert datetime strings back to datetime objects
        if 'last_changed' in data and data['last_changed']:
            data['last_changed'] = datetime.fromisoformat(data['last_changed'])
        
        if 'timestamp' in data and data['timestamp']:
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        # Convert condition string to enum
        if 'condition' in data:
            data['condition'] = WeatherCondition(data['condition'])
        
        return cls(**data) 