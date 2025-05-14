from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class SkillBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    ability: Optional[str] = Field(None, max_length=50)

class SkillCreate(SkillBase):
    pass

class Skill(SkillBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CharacterBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    race: str = Field(..., max_length=50)
    character_class: str = Field(..., max_length=50)
    level: int = Field(default=1, ge=1, le=20)
    stats: Dict[str, int] = Field(
        ...,
        description="Character stats (strength, dexterity, etc.)"
    )
    background: Optional[str] = Field(None, max_length=100)
    alignment: Optional[str] = Field(None, max_length=50)
    equipment: List[Dict] = Field(default_factory=list)
    notes: List[str] = Field(default_factory=list)

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    race: Optional[str] = Field(None, max_length=50)
    character_class: Optional[str] = Field(None, max_length=50)
    level: Optional[int] = Field(None, ge=1, le=20)
    stats: Optional[Dict[str, int]] = None
    background: Optional[str] = Field(None, max_length=100)
    alignment: Optional[str] = Field(None, max_length=50)
    equipment: Optional[List[Dict]] = None
    notes: Optional[List[str]] = None

class Character(CharacterBase):
    id: int
    skills: List[Skill]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 