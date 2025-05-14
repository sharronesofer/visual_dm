"""
Arc-related data models and structures.
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

class ArcStage(BaseModel):
    """Represents a stage in a character arc."""
    id: int
    title: str
    description: str
    completed: bool = False
    events: List[Dict] = Field(default_factory=list)

class PlayerArc(BaseModel):
    """Represents a player's story arc."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    character_id: str
    title: str
    theme: str
    current_stage: int = 1
    total_stages: int
    completed_stages: List[int] = Field(default_factory=list)
    stages: List[ArcStage] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # active, completed, failed 