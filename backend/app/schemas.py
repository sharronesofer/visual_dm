from pydantic import BaseModel
from typing import List, Optional

class WorldData(BaseModel):
    id: int
    name: str
    seed: int
    size: int
    created_at: Optional[str]

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

class Event(BaseModel):
    id: int
    type: str
    payload: dict
    timestamp: Optional[str]
