from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

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