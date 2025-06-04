"""
Weather System Validation Service

Handles validation and configuration for weather system according to Development Bible standards.
"""

from typing import Protocol, Dict, Any, Optional
import random
from backend.systems.weather.models.weather_model import WeatherCondition
from backend.infrastructure.utils import load_json


class WeatherValidationService(Protocol):
    """Protocol for weather validation and configuration"""
    
    def load_weather_config(self) -> Dict[str, Any]:
        """Load weather configuration"""
        ...
    
    def load_weather_types(self) -> Dict[str, Any]:
        """Load weather types configuration"""
        ...
    
    def validate_weather_condition(self, condition: str) -> WeatherCondition:
        """Validate and convert weather condition"""
        ...
    
    def get_seasonal_weights(self, season: str) -> Dict[WeatherCondition, float]:
        """Get weather weights for a season"""
        ...


class WeatherValidationServiceImpl:
    """Implementation of weather validation service"""
    
    def __init__(self):
        self._config_cache: Optional[Dict[str, Any]] = None
        self._types_cache: Optional[Dict[str, Any]] = None
    
    def load_weather_config(self) -> Dict[str, Any]:
        """Load weather configuration from JSON"""
        if self._config_cache is None:
            try:
                self._config_cache = load_json("data/systems/weather/weather_config.json")
            except Exception:
                # Fallback default configuration
                self._config_cache = {
                    "weather_system": {
                        "enabled": True,
                        "randomness_factor": 0.5,
                        "seasonal_influence": 0.8,
                    },
                    "default_weather": {
                        "condition": "clear",
                        "temperature": 65.0,
                        "humidity": 50.0,
                        "wind_speed": 5.0,
                        "pressure": 29.92,
                        "visibility": 10.0,
                        "duration_hours": 4
                    }
                }
        
        return self._config_cache
    
    def load_weather_types(self) -> Dict[str, Any]:
        """Load weather types configuration from JSON"""
        if self._types_cache is None:
            try:
                self._types_cache = load_json("data/systems/weather/weather_types.json")
            except Exception:
                # Fallback to empty dict - use hardcoded values
                self._types_cache = {}
        
        return self._types_cache
    
    def validate_weather_condition(self, condition: str) -> WeatherCondition:
        """Validate and convert weather condition string to enum"""
        try:
            return WeatherCondition(condition.lower())
        except ValueError:
            # Return default if invalid
            return WeatherCondition.CLEAR
    
    def get_seasonal_weights(self, season: str) -> Dict[WeatherCondition, float]:
        """Get weather weights for a season from configuration or fallback"""
        weather_types = self.load_weather_types()
        season_key = season.lower()
        
        weights = {}
        
        # If we have JSON configuration, use it
        if weather_types:
            for condition_key, data in weather_types.items():
                try:
                    condition = WeatherCondition(condition_key)
                    probability = data.get("seasonal_probability", {}).get(season_key, 0.1)
                    weights[condition] = probability
                except (ValueError, KeyError):
                    continue
        
        # If no weights found, use hardcoded fallback
        if not weights:
            weights = self._get_fallback_seasonal_weights(season_key)
        
        return weights
    
    def _get_fallback_seasonal_weights(self, season: str) -> Dict[WeatherCondition, float]:
        """Fallback hardcoded seasonal weights"""
        seasonal_weights = {
            'spring': {
                WeatherCondition.CLEAR: 0.25,
                WeatherCondition.PARTLY_CLOUDY: 0.20,
                WeatherCondition.CLOUDY: 0.15,
                WeatherCondition.LIGHT_RAIN: 0.15,
                WeatherCondition.RAIN: 0.10,
                WeatherCondition.DRIZZLE: 0.10,
                WeatherCondition.FOG: 0.05,
            },
            'summer': {
                WeatherCondition.CLEAR: 0.40,
                WeatherCondition.PARTLY_CLOUDY: 0.25,
                WeatherCondition.CLOUDY: 0.10,
                WeatherCondition.SCORCHING: 0.10,
                WeatherCondition.THUNDERSTORM: 0.08,
                WeatherCondition.RAIN: 0.05,
                WeatherCondition.WINDY: 0.02,
            },
            'autumn': {
                WeatherCondition.CLEAR: 0.20,
                WeatherCondition.PARTLY_CLOUDY: 0.20,
                WeatherCondition.CLOUDY: 0.20,
                WeatherCondition.OVERCAST: 0.15,
                WeatherCondition.RAIN: 0.10,
                WeatherCondition.LIGHT_RAIN: 0.08,
                WeatherCondition.FOG: 0.05,
                WeatherCondition.WINDY: 0.02,
            },
            'winter': {
                WeatherCondition.CLOUDY: 0.25,
                WeatherCondition.OVERCAST: 0.20,
                WeatherCondition.SNOW: 0.15,
                WeatherCondition.LIGHT_SNOW: 0.12,
                WeatherCondition.CLEAR: 0.10,
                WeatherCondition.HEAVY_SNOW: 0.08,
                WeatherCondition.BLIZZARD: 0.05,
                WeatherCondition.FOG: 0.03,
                WeatherCondition.MIST: 0.02,
            }
        }
        
        return seasonal_weights.get(season, seasonal_weights['spring'])
    
    def get_temperature_range(self, season: str) -> tuple[float, float]:
        """Get temperature range for a season"""
        config = self.load_weather_config()
        seasonal_prefs = config.get("seasonal_preferences", {})
        season_data = seasonal_prefs.get(season.lower(), {})
        
        return tuple(season_data.get("temperature_range", [45, 75])) 