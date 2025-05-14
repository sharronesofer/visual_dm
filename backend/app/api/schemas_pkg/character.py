"""Character API schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, conint

class CharacterBase(BaseModel):
    """Base schema for character."""
    name: str = Field(..., description="Character name")
    race: str = Field(..., description="Character race")
    background: str = Field(..., description="Character background")
    strength: conint(ge=1, le=20) = Field(..., description="Strength score (1-20)")
    dexterity: conint(ge=1, le=20) = Field(..., description="Dexterity score (1-20)")
    constitution: conint(ge=1, le=20) = Field(..., description="Constitution score (1-20)")
    intelligence: conint(ge=1, le=20) = Field(..., description="Intelligence score (1-20)")
    wisdom: conint(ge=1, le=20) = Field(..., description="Wisdom score (1-20)")
    charisma: conint(ge=1, le=20) = Field(..., description="Charisma score (1-20)")

class CharacterCreate(CharacterBase):
    """Schema for creating a character."""
    pass

class CharacterUpdate(BaseModel):
    """Schema for updating a character."""
    name: Optional[str] = Field(None, description="Character name")
    race: Optional[str] = Field(None, description="Character race")
    background: Optional[str] = Field(None, description="Character background")
    strength: Optional[conint(ge=1, le=20)] = Field(None, description="Strength score (1-20)")
    dexterity: Optional[conint(ge=1, le=20)] = Field(None, description="Dexterity score (1-20)")
    constitution: Optional[conint(ge=1, le=20)] = Field(None, description="Constitution score (1-20)")
    intelligence: Optional[conint(ge=1, le=20)] = Field(None, description="Intelligence score (1-20)")
    wisdom: Optional[conint(ge=1, le=20)] = Field(None, description="Wisdom score (1-20)")
    charisma: Optional[conint(ge=1, le=20)] = Field(None, description="Charisma score (1-20)")

class CharacterResponse(CharacterBase):
    """Schema for character response."""
    id: int
    created_at: datetime
    updated_at: datetime
    quest_ids: List[int] = Field(default_factory=list, description="IDs of quests the character is involved in")
    faction_ids: List[int] = Field(default_factory=list, description="IDs of factions the character belongs to")
    led_faction_ids: List[int] = Field(default_factory=list, description="IDs of factions the character leads")

    class Config:
        """Pydantic config."""
        from_attributes = True 