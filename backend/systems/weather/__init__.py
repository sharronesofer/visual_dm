"""
Weather System - Independent weather simulation system

This system handles weather simulation and provides weather data
to other systems via events, ensuring loose coupling per Development Bible.
"""

from .services.weather_service import WeatherService
from .models.weather_model import Weather, WeatherCondition

__all__ = [
    'WeatherService',
    'Weather', 
    'WeatherCondition'
] 