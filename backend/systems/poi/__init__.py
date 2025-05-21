"""
Point of Interest (POI) System Module

This module provides a centralized system for managing POIs in the game world.
POIs represent significant locations such as cities, towns, dungeons, ruins, etc.
"""

from .models import PointOfInterest, POIState, POIType
from .schemas import POISchema, POICreationSchema, HexCoordinateSchema
from .services import POIService, POIStateService
from .utils import calculate_poi_distance

__all__ = [
    # Models
    "PointOfInterest",
    "POIState",
    "POIType",
    
    # Schemas
    "POISchema",
    "POICreationSchema",
    "HexCoordinateSchema",
    
    # Services
    "POIService",
    "POIStateService",
    
    # Utilities
    "calculate_poi_distance",
]
