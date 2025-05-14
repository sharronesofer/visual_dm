from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class NPCTraitBase(BaseModel):
    trait_type: str
    value: float

class NPCTraitCreate(NPCTraitBase):
    pass

class NPCTraitRead(NPCTraitBase):
    id: int
    npc_id: str

    class Config:
        orm_mode = True

class NPCRelationshipBase(BaseModel):
    target_id: str
    relationship_type: str
    value: float

class NPCRelationshipCreate(NPCRelationshipBase):
    pass

class NPCRelationshipRead(NPCRelationshipBase):
    id: int
    npc_id: str

    class Config:
        orm_mode = True

class NPCBase(BaseModel):
    name: str
    is_active: Optional[bool] = True

class NPCCreate(NPCBase):
    traits: Optional[List[NPCTraitCreate]] = None

class NPCRead(NPCBase):
    id: str
    created_at: datetime
    updated_at: datetime
    traits: List[NPCTraitRead] = []
    relationships: List[NPCRelationshipRead] = []

    class Config:
        orm_mode = True
