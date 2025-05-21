"""
Character API Schemas
-------------------
Pydantic models for character-related API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import UUID

class CharacterBase(BaseModel):
    """Base schema for character data."""
    name: str = Field(..., description="The character's name")
    race: str = Field(..., description="The character's race")
    level: int = Field(1, description="The character's level")
    stats: Dict[str, Any] = Field(
        default_factory=dict,
        description="Character statistics (STR, DEX, etc.)"
    )
    skills: List[str] = Field(
        default_factory=list,
        description="List of character skills"
    )
    
class CharacterCreate(CharacterBase):
    """Schema for creating a new character."""
    name: str = Field(..., alias="character_name")
    attributes: Dict[str, int] = Field(
        default_factory=dict,
        description="Character attributes (STR, DEX, etc.)"
    )
    feats: List[str] = Field(
        default_factory=list,
        description="List of character feats"
    )
    background: Optional[str] = Field(
        None,
        description="Character background story"
    )
    kit: Optional[str] = Field(
        None,
        description="The starter kit name"
    )
    
    class Config:
        allow_population_by_field_name = True

class CharacterUpdate(BaseModel):
    """Schema for updating a character."""
    name: Optional[str] = None
    race: Optional[str] = None
    level: Optional[int] = None
    stats: Optional[Dict[str, Any]] = None
    skills: Optional[List[str]] = None
    background: Optional[str] = None
    
    class Config:
        arbitrary_types_allowed = True

class CharacterResponse(CharacterBase):
    """Schema for character responses."""
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class CharacterList(BaseModel):
    """Schema for character list responses."""
    id: UUID
    name: str
    race: str
    level: int

    class Config:
        orm_mode = True

# Add schemas for party/player if needed
class PartyMember(BaseModel):
    """Schema for a party member."""
    character_id: UUID
    joined_at: datetime

class Party(BaseModel):
    """Schema for a party."""
    id: UUID
    members: List[PartyMember]
    created_at: datetime

class RumorEvent(BaseModel):
    event_id: str
    description: str
    timestamp: datetime
    involved_npcs: List[str] = Field(default_factory=list)

class Rumor(BaseModel):
    rumor_id: str
    event_id: str
    content: str
    source_npc: str
    truth_value: float
    retellings: int = 0
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    heard_by: List[str] = Field(default_factory=list)
    decay: float = 1.0

class RumorTransformationRequest(BaseModel):
    event: str
    rumor: str
    traits: str
    distortion_level: float

class RumorTransformationResponse(BaseModel):
    transformed_rumor: str
    new_truth_value: float 
