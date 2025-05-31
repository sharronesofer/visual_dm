"""Character schemas module."""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict

class CharacterSchema(BaseModel):
    """Character schema for validation."""
    id: str
    name: str
    level: int = 1
    health: int = 100
    attributes: Dict[str, int] = {}
    
    model_config = ConfigDict()        extra = "allow"

class CharacterCreateSchema(BaseModel):
    """Schema for creating characters."""
    name: str
    level: int = 1
    attributes: Dict[str, int] = {}

class CharacterUpdateSchema(BaseModel):
    """Schema for updating characters."""
    name: Optional[str] = None
    level: Optional[int] = None
    health: Optional[int] = None
    attributes: Optional[Dict[str, int]] = None

# Export schemas
__all__ = ['CharacterSchema', 'CharacterCreateSchema', 'CharacterUpdateSchema']
