"""
Schema definitions for faction-related data structures.
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

class FactionType(str, Enum):
    """Types of factions in the game world."""
    KINGDOM = "kingdom"
    CITY_STATE = "city_state"
    MERCHANT_GUILD = "merchant_guild"
    THIEVES_GUILD = "thieves_guild"
    RELIGIOUS_ORDER = "religious_order"
    ARCANE_SOCIETY = "arcane_society"
    MERCENARY_COMPANY = "mercenary_company"
    MONSTROUS_HORDE = "monstrous_horde"
    NOBLE_HOUSE = "noble_house"
    TRIBAL_CONFEDERATION = "tribal_confederation"
    CULT = "cult"
    OTHER = "other"

class FactionAlignment(str, Enum):
    """Alignment categories for factions."""
    LAWFUL_GOOD = "lawful_good"
    LAWFUL_NEUTRAL = "lawful_neutral"
    LAWFUL_EVIL = "lawful_evil"
    NEUTRAL_GOOD = "neutral_good"
    TRUE_NEUTRAL = "true_neutral"
    NEUTRAL_EVIL = "neutral_evil"
    CHAOTIC_GOOD = "chaotic_good"
    CHAOTIC_NEUTRAL = "chaotic_neutral"
    CHAOTIC_EVIL = "chaotic_evil"

class DiplomaticStance(str, Enum):
    """Diplomatic stances between factions."""
    ALLIED = "allied"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    UNFRIENDLY = "unfriendly"
    HOSTILE = "hostile"
    AT_WAR = "at_war"

class FactionSchema(BaseModel):
    """
    Schema for faction data.
    
    Factions are organized groups with shared goals, interests, and identities
    that interact with each other and the world.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: FactionType = FactionType.OTHER
    description: str
    alignment: Optional[FactionAlignment] = None
    influence: float = 50.0  # 0-100 scale
    headquarters: Optional[str] = None  # Location ID
    leader_id: Optional[str] = None  # NPC/Character ID
    territories: List[str] = Field(default_factory=list)  # List of location IDs
    members: List[str] = Field(default_factory=list)  # List of character IDs
    resources: Dict[str, float] = Field(default_factory=dict)  # Resource name -> amount
    diplomatic_relations: Dict[str, DiplomaticStance] = Field(default_factory=dict)  # Faction ID -> stance
    traits: List[str] = Field(default_factory=list)  # Descriptive traits
    goals: List[str] = Field(default_factory=list)  # Current faction goals
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    custom_data: Dict[str, Any] = Field(default_factory=dict)  # For extensibility 