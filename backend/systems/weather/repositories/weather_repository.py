"""
Weather System Repository - Data Access Layer

Handles persistence and retrieval of weather data according to Development Bible standards.
"""

from typing import Protocol, Optional, List
from datetime import datetime
from backend.systems.weather.models.weather_model import Weather
from backend.infrastructure.utils import load_json, save_json


class WeatherRepository(Protocol):
    """Protocol for weather data access - dependency injection interface"""
    
    def save_weather_state(self, weather: Weather) -> bool:
        """Save current weather state"""
        ...
    
    def load_weather_state(self) -> Optional[Weather]:
        """Load weather state from storage"""
        ...
    
    def get_weather_history(self, limit: int = 100) -> List[Weather]:
        """Get weather history with optional limit"""
        ...
    
    def clear_weather_history(self) -> bool:
        """Clear all weather history"""
        ...


class WeatherRepositoryImpl:
    """Implementation of weather repository using game state persistence"""
    
    def __init__(self, persistence_service=None):
        """Initialize with persistence service dependency"""
        self.persistence_service = persistence_service
        self._weather_history: List[Weather] = []
    
    def save_weather_state(self, weather: Weather) -> bool:
        """Save current weather state using existing game state system"""
        try:
            if self.persistence_service:
                return self.persistence_service.save_weather(weather)
            else:
                # Fallback to basic JSON persistence if no service provided
                weather_data = weather.to_dict()
                return save_json("weather_current.json", weather_data)
        except Exception:
            return False
    
    def load_weather_state(self) -> Optional[Weather]:
        """Load weather state from existing game state system"""
        try:
            if self.persistence_service:
                return self.persistence_service.load_weather()
            else:
                # Fallback to basic JSON loading
                weather_data = load_json("weather_current.json")
                if weather_data:
                    return Weather.from_dict(weather_data)
                return None
        except Exception:
            return None
    
    def get_weather_history(self, limit: int = 100) -> List[Weather]:
        """Get weather history with limit"""
        if limit <= 0:
            return self._weather_history.copy()
        return self._weather_history[-limit:].copy()
    
    def add_to_history(self, weather: Weather) -> None:
        """Add weather to history (used internally by service)"""
        self._weather_history.append(weather)
        # Keep only last 1000 entries to prevent unbounded growth
        if len(self._weather_history) > 1000:
            self._weather_history = self._weather_history[-1000:]
    
    def clear_weather_history(self) -> bool:
        """Clear all weather history"""
        try:
            self._weather_history.clear()
            return True
        except Exception:
            return False 