"""
Models module.
"""

# Import models from the parent models.py file
try:
    from ..models import (
        PointOfInterest,
        POIType,
        POIState,
        POIInteractionType
    )
except ImportError:
    # Create fallback classes
    from enum import Enum
    
    class POIType(str, Enum):
        CITY = "city"
        VILLAGE = "village"
        TOWN = "town"
        SETTLEMENT = "settlement"
        OUTPOST = "outpost"
        FORTRESS = "fortress"
        TEMPLE = "temple"
        MARKET = "market"
        OTHER = "other"
    
    class POIState(str, Enum):
        ACTIVE = "active"
        INACTIVE = "inactive"
        ABANDONED = "abandoned"
        RUINED = "ruined"
        UNDER_CONSTRUCTION = "under_construction"
        DECLINING = "declining"
        GROWING = "growing"
        NORMAL = "normal"
        RUINS = "ruins"
        DUNGEON = "dungeon"
        REPOPULATING = "repopulating"
        SPECIAL = "special"
    
    class POIInteractionType(str, Enum):
        TRADE = "trade"
        DIPLOMACY = "diplomacy"
        COMBAT = "combat"
        EXPLORATION = "exploration"
        QUEST = "quest"
        SOCIAL = "social"
        NEUTRAL = "neutral"
    
    class PointOfInterest:
        def __init__(self, **kwargs):
            for key, value in kwargs.items():
                setattr(self, key, value)

__all__ = [
    "PointOfInterest",
    "POIType", 
    "POIState",
    "POIInteractionType"
] 