"""
POI schemas for API request/response models.
Consolidates all POI-related schemas into a single, coherent module.
"""

from typing import Dict, List, Optional, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime

class HexCoordinateSchema(BaseModel):
    """
    A hexagonal grid coordinate using the cube coordinate system.
    In a cube coordinate system for hexagons, q + r + s = 0.
    """
    q: int
    r: int
    s: Optional[int] = None  # Can be derived if q+r+s=0

    def __post_init__(self):
        """Derive s if not provided."""
        if self.s is None:
            self.s = -self.q - self.r

class POISchema(BaseModel):
    """
    Schema for POI data, representing a Point of Interest in the game world.
    Used for API responses and general POI representation.
    """
    poi_id: str
    name: str
    description: Optional[str] = None
    region_id: str  # The main region this POI belongs to
    
    # Grid coordinates of the POI's anchor point within its region
    position: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0})

    poi_type: str  # e.g., "City", "Metropolis", "Dungeon", "Ruins"
    tags: List[str] = []  # Biome/environmental tags, e.g., from land_types.json
    
    # List of IDs/coords of *region-scale* hexes claimed by this POI
    claimed_region_hex_ids: List[str] = []
    
    population: int = 0
    max_population: Optional[int] = None
    current_state: str = "normal"  # e.g., Normal, Declining, Abandoned, Ruins, Dungeon

    # Other POI specific details
    faction_id: Optional[str] = None
    resources: Dict[str, Any] = Field(default_factory=dict)
    level: Optional[int] = None
    npcs: List[str] = []
    quests: List[str] = []
    
    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        schema_extra = {
            "example": {
                "poi_id": "poi_12345",
                "name": "Eldervale",
                "description": "A bustling trade city nestled between forested hills.",
                "region_id": "region_678",
                "position": {"x": 120, "y": 85},
                "poi_type": "city",
                "tags": ["forest", "hills", "temperate"],
                "claimed_region_hex_ids": ["hex_123", "hex_124"],
                "population": 500,
                "max_population": 800,
                "current_state": "normal",
                "faction_id": "faction_mercantile_union",
                "resources": {"gold": 5000, "wood": 3000, "stone": 2000},
                "level": 3,
                "npcs": ["npc_123", "npc_124", "npc_125"],
                "quests": ["quest_52", "quest_53"]
            }
        }

class POICreationSchema(BaseModel):
    """
    Schema for creating a new POI.
    Simplified version of POISchema with only required fields.
    """
    name: str
    region_id: str
    position: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0})
    poi_type: str
    tags: List[str] = []
    claimed_region_hex_ids: List[str] = []
    population: int = 0
    max_population: Optional[int] = None
    current_state: str = "normal"
    faction_id: Optional[str] = None
    description: Optional[str] = None
    level: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Stormhold Outpost",
                "description": "A frontier outpost guarding the mountain pass.",
                "region_id": "region_678",
                "position": {"x": 150, "y": 210},
                "poi_type": "outpost",
                "tags": ["mountains", "frontier", "military"],
                "claimed_region_hex_ids": ["hex_345"],
                "population": 50,
                "max_population": 100,
                "current_state": "normal",
                "faction_id": "faction_imperial_guard",
                "level": 2
            }
        }

class POIUpdateSchema(BaseModel):
    """
    Schema for updating an existing POI.
    All fields are optional since updates can be partial.
    """
    name: Optional[str] = None
    description: Optional[str] = None
    position: Optional[Dict[str, int]] = None
    poi_type: Optional[str] = None
    tags: Optional[List[str]] = None
    claimed_region_hex_ids: Optional[List[str]] = None
    population: Optional[int] = None
    max_population: Optional[int] = None
    current_state: Optional[str] = None
    faction_id: Optional[str] = None
    resources: Optional[Dict[str, Any]] = None
    level: Optional[int] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Stormhold Fortress",
                "description": "A reinforced fortress guarding the mountain pass.",
                "population": 75,
                "current_state": "normal",
                "resources": {"gold": 2000, "wood": 1000, "stone": 3000}
            }
        }

class POIStateTransitionSchema(BaseModel):
    """
    Schema for transitioning a POI's state.
    """
    new_state: str
    reason: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "new_state": "ruins",
                "reason": "Destroyed by dragon attack"
            }
        }

class POIQueryResponse(BaseModel):
    """
    Schema for POI query responses, including pagination info.
    """
    items: List[POISchema]
    total: int
    page: int
    size: int
    
    class Config:
        schema_extra = {
            "example": {
                "items": [
                    {
                        "poi_id": "poi_12345",
                        "name": "Eldervale",
                        "description": "A bustling trade city nestled between forested hills.",
                        "region_id": "region_678",
                        "position": {"x": 120, "y": 85},
                        "poi_type": "city",
                        "tags": ["forest", "hills", "temperate"],
                        "claimed_region_hex_ids": ["hex_123", "hex_124"],
                        "population": 500,
                        "max_population": 800,
                        "current_state": "normal",
                        "faction_id": "faction_mercantile_union"
                    }
                ],
                "total": 42,
                "page": 1,
                "size": 10
            }
        } 