"""
Tension_War system schemas.
"""

from pydantic import BaseModel, ConfigDict
from typing import Optional


class Tension_WarBase(BaseModel):
    """Base schema for tension_war system."""
    name: str


class Tension_WarCreate(Tension_WarBase):
    """Schema for creating tension_war items."""
    pass


class Tension_WarResponse(Tension_WarBase):
    """Schema for tension_war response."""
    id: int
    
    model_config = ConfigDict(from_attributes=True)
