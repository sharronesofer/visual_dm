"""
Models for the religion system.

These models represent religions, religion types, and membership associations
between entities and religions.
"""

from enum import IntEnum
from typing import Dict, List, Optional, Any, Set, Union
from pydantic import BaseModel, Field
from datetime import datetime
import uuid


class ReligionType(IntEnum):
    """
    Canonical religion types as defined in the Development Bible.
    
    1: Polytheistic - Multiple deities, pantheon-based
    2: Monotheistic - Single deity, centralized doctrine
    3: Animistic - Spirits inhabit natural objects/phenomena
    4: Ancestor - Ancestor worship, lineage-based
    5: Cult - Small, secretive, or heretical group
    6: Syncretic - Blends elements from multiple religions
    7: Custom - User/system-defined religion type
    """
    POLYTHEISTIC = 1
    MONOTHEISTIC = 2
    ANIMISTIC = 3
    ANCESTOR = 4
    CULT = 5
    SYNCRETIC = 6
    CUSTOM = 7


def religiontype_to_string(religion_type: ReligionType) -> str:
    """Convert a ReligionType enum to a readable string."""
    mapping = {
        ReligionType.POLYTHEISTIC: "Polytheistic",
        ReligionType.MONOTHEISTIC: "Monotheistic",
        ReligionType.ANIMISTIC: "Animistic",
        ReligionType.ANCESTOR: "Ancestor",
        ReligionType.CULT: "Cult",
        ReligionType.SYNCRETIC: "Syncretic",
        ReligionType.CUSTOM: "Custom",
    }
    return mapping.get(religion_type, "Unknown")


def string_to_religiontype(type_str: str) -> ReligionType:
    """Convert a string to a ReligionType enum."""
    mapping = {
        "polytheistic": ReligionType.POLYTHEISTIC,
        "monotheistic": ReligionType.MONOTHEISTIC,
        "animistic": ReligionType.ANIMISTIC,
        "ancestor": ReligionType.ANCESTOR,
        "cult": ReligionType.CULT,
        "syncretic": ReligionType.SYNCRETIC,
        "custom": ReligionType.CUSTOM,
    }
    return mapping.get(type_str.lower(), ReligionType.CUSTOM)


class Religion(BaseModel):
    """
    A religion entity in the game world.
    
    Represents a specific religion with its type, name, description, and
    various metadata for integration with other systems.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    type: ReligionType
    tags: List[str] = Field(default_factory=list)
    tenets: List[str] = Field(default_factory=list)
    holy_places: List[str] = Field(default_factory=list)
    sacred_texts: List[str] = Field(default_factory=list)
    region_ids: List[str] = Field(default_factory=list)
    faction_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def get_type_string(self) -> str:
        """Get the string representation of this religion's type."""
        return religiontype_to_string(self.type)


class ReligionMembership(BaseModel):
    """
    Association between an entity (character, NPC) and a religion.
    
    Tracks membership details including devotion level, status, and
    role within the religion.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_id: str  # Character or NPC ID
    religion_id: str
    devotion_level: int = 0  # 0-100 scale of devotion/reputation
    status: str = "member"  # member, leader, priest, outcast, etc.
    joined_date: datetime = Field(default_factory=datetime.utcnow)
    role: Optional[str] = None  # specific role within the religion
    is_public: bool = True  # Whether membership is known publicly
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        orm_mode = True 