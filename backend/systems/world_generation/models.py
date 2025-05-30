"""
Models for the world generation system.

This file contains Pydantic models used for data validation and serialization across the world generation system.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class CoordinateSchema(BaseModel):
    """Represents a 2D coordinate in the world grid."""
    x: int
    y: int


class ContinentBoundarySchema(BaseModel):
    """Represents the rectangular boundary of a continent."""
    min_x: int
    max_x: int
    min_y: int
    max_y: int


class ContinentSchema(BaseModel):
    """Represents a continent in the world."""
    continent_id: str
    name: Optional[str] = None  # e.g., "Eldoria", "Terra Nova"
    seed: Optional[str] = None
    region_coordinates: List[CoordinateSchema] = []  # List of coordinates of all regions in this continent
    region_ids: List[str] = []  # List of IDs of all regions in this continent
    origin_coordinate: Optional[CoordinateSchema] = None  # The starting point of generation for this continent
    boundary: Optional[ContinentBoundarySchema] = None
    creation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    # Metadata for number of regions, as per 2025 update (50-70 regions)
    num_regions: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ContinentCreationRequestSchema(BaseModel):
    """Request schema for creating a new continent."""
    name: Optional[str] = None
    seed: Optional[str] = None
    num_regions_target: int = Field(default=60, ge=50, le=70)  # Target between 50-70
    metadata: Dict[str, Any] = Field(default_factory=dict) 