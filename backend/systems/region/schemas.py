"""
Region system schemas.

This module contains Pydantic schemas for the region system.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class CoordinateSchema(BaseModel):
    """Coordinate schema for location data."""
    x: float
    y: float


class PoiSchema(BaseModel):
    """Point of Interest schema."""
    type: str
    coordinates: CoordinateSchema
    size: float
    
    # Optional fields that might be present
    name: Optional[str] = None
    description: Optional[str] = None
    faction_control: Optional[str] = None
    tension: Optional[float] = None


class RegionSchema(BaseModel):
    """Region schema."""
    id: Optional[str] = None
    coordinates: CoordinateSchema
    size: float
    biome: str
    elevation: float
    temperature: float
    humidity: float
    features: List[str]
    resources: Dict[str, float]
    pois: List[PoiSchema]
    
    # Optional fields
    name: Optional[str] = None
    description: Optional[str] = None
    faction_control: Optional[Dict[str, float]] = None
    tension: Optional[float] = None
    last_updated: Optional[str] = None


class TileSchema(BaseModel):
    """Tile schema for region maps."""
    tags: List[str]
    poi: Optional[str] = None


class RegionMapSchema(BaseModel):
    """Region map schema."""
    tiles: Dict[str, TileSchema]


class RegionGenerationSchema(BaseModel):
    """Parameters for region generation."""
    seed_x: int = Field(0, description="X-coordinate seed for region generation")
    seed_y: int = Field(0, description="Y-coordinate seed for region generation")


class EventSchema(BaseModel):
    """Schema for world events."""
    type: str
    region: str
    poi_id: Optional[str] = None
    description: Optional[str] = None
    character_id: Optional[str] = None
    faction_id: Optional[str] = None
    timestamp: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class QuestSchema(BaseModel):
    """Schema for quests."""
    title: str
    description: str
    objectives: List[Dict[str, Any]]
    rewards: Dict[str, Any]
    faction_id: Optional[str] = None
    giver_id: Optional[str] = None
    status: str = "active"


class QuestlogEntrySchema(BaseModel):
    """Schema for questlog entries."""
    quest: QuestSchema
    timestamp: Optional[str] = None

class HexCoordinateSchema(BaseModel):
    """Schema for hex-based coordinates."""
    q: int
    r: int
    s: int # Optional, can be derived if q+r+s=0

class RegionCreationSchema(BaseModel):
    """Schema for creating a new region."""
    continent_id: Optional[str] = None
    coordinates: CoordinateSchema
    biome: Optional[str] = "Plains"

class RegionUpdateSchema(BaseModel):
    """Schema for updating an existing region."""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    biome: Optional[str] = None
    population: Optional[int] = None
    poi_ids: Optional[List[str]] = None 