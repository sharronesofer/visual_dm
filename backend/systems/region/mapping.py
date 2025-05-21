"""
Region Mapping Utilities

This module contains utilities for mapping region coordinates to real-world lat/lon coordinates
and fetching weather data for those coordinates.
"""

from typing import Tuple, Dict, Any
from random import uniform

# Constants for mapping region coordinates to lat/lon
ORIGIN_LAT = -54.8019  # Ushuaia, Argentina
ORIGIN_LON = -68.3030
REGION_LATLON_SCALE = 0.5  # Degrees per region unit

def map_region_to_latlon(coordinates) -> Tuple[float, float]:
    """
    Map region grid coordinates to real-world latitude/longitude.
    
    Args:
        coordinates: The region coordinates
        
    Returns:
        Tuple of (latitude, longitude)
    """
    # Extract x, y from CoordinateSchema or dict
    x = getattr(coordinates, 'x', coordinates.get('x', 0))
    y = getattr(coordinates, 'y', coordinates.get('y', 0))
    
    # Calculate lat/lon
    lat = ORIGIN_LAT + (y * REGION_LATLON_SCALE)
    lon = ORIGIN_LON + (x * REGION_LATLON_SCALE)
    
    return lat, lon

def fetch_weather_for_latlon(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetch weather data for a specific lat/lon.
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        Weather data dict
    """
    # In a real implementation, this would call a weather API
    # For now, return simulated data
    
    # Random temperature between -10 and 30 Celsius
    temperature = round(uniform(-10, 30), 1)
    
    # Random conditions
    conditions = ['clear', 'cloudy', 'rain', 'snow', 'fog']
    condition = conditions[int(uniform(0, len(conditions)))]
    
    # Random wind
    wind_speed = round(uniform(0, 30), 1)
    wind_direction = round(uniform(0, 360))
    
    # Random precipitation
    precipitation = round(uniform(0, 25), 1)
    
    return {
        'latitude': lat,
        'longitude': lon,
        'temperature': temperature,
        'condition': condition,
        'wind_speed': wind_speed,
        'wind_direction': wind_direction,
        'precipitation': precipitation,
        'timestamp': 'simulated'  # Would be a real timestamp in production
    } 