"""
POI models for representing Points of Interest in the game world.
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from uuid import uuid4
from enum import Enum

class POIType(str, Enum):
    """
    Types of POI locations in the game world, consolidating all POI types referenced
    in the system into a canonical list.
    """
    CITY = "city"
    TOWN = "town"
    VILLAGE = "village"
    DUNGEON = "dungeon"
    RUINS = "ruins"
    TEMPLE = "temple"
    CASTLE = "castle"
    FORTRESS = "fortress"
    TOWER = "tower"
    CAMP = "camp"
    TAVERN = "tavern"
    SHOP = "shop"
    FARM = "farm"
    MINE = "mine"
    GROVE = "grove"
    CAVE = "cave"
    LANDMARK = "landmark"
    OUTPOST = "outpost"
    VAULT = "vault"
    OTHER = "other"
    # Future POI types can be added here

class POIState(str, Enum):
    """
    Canonical POI states as described in the Development Bible.
    These represent the possible states a POI can be in, which affects
    its behavior, appearance, and available interactions.
    """
    NORMAL = "normal"          # Fully populated, functional POI
    DECLINING = "declining"    # Population dropping, at risk of abandonment
    ABANDONED = "abandoned"    # No active population, not yet ruins
    RUINS = "ruins"            # Destroyed/abandoned, hostile or neutral
    DUNGEON = "dungeon"        # Hostile, repopulated by monsters
    REPOPULATING = "repopulating"  # Population returning, transitioning to Normal
    SPECIAL = "special"        # Custom/narrative state (e.g., festival, siege)

class PointOfInterest(BaseModel):
    """
    Canonical POI model, consolidating attributes from multiple POI classes
    throughout the codebase into a single, comprehensive model.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: str
    region_id: str
    
    # Position data
    coordinates: Tuple[float, float] = Field(default=(0.0, 0.0))
    position: Dict[str, int] = Field(default_factory=lambda: {"x": 0, "y": 0})
    claimed_region_hex_ids: List[str] = [] # IDs of region-scale hexes claimed by this POI
    
    # Type and state information
    poi_type: str = Field(..., description="Type of POI (city, dungeon, etc.)")
    current_state: str = Field(default=POIState.NORMAL, description="Current state of the POI")
    tags: List[str] = [] # Biome/environmental tags
    
    # Demographics
    population: int = 0
    max_population: Optional[int] = None
    npcs: List[str] = Field(default_factory=list, description="IDs of NPCs in this POI")
    
    # Gameplay and narrative elements
    level: int = Field(default=1, ge=1, le=20)
    quests: List[str] = Field(default_factory=list)
    faction_id: Optional[str] = None
    resources: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # Configuration
    model_config = ConfigDict(arbitrary_types_allowed=True, use_enum_values=True)
    
    @field_validator("poi_type")
    @classmethod
    def validate_poi_type(cls, v):
        """Validate POI type against canonical types."""
        try:
            return POIType(v.lower())
        except ValueError:
            # For backward compatibility with legacy data
            # or custom POI types not in the enum
            return v.lower()
    
    @field_validator("current_state")
    @classmethod
    def validate_current_state(cls, v):
        """Validate POI state against canonical states."""
        try:
            return POIState(v.lower())
        except ValueError:
            # For backward compatibility with legacy data
            return v.lower()
    
    def update_timestamp(self) -> None:
        """Update the POI's updated_at timestamp."""
        self.updated_at = datetime.utcnow()
    
    def add_npc(self, npc_id: str) -> None:
        """Add an NPC to the POI."""
        if npc_id not in self.npcs:
            self.npcs.append(npc_id)
            self.update_timestamp()
    
    def remove_npc(self, npc_id: str) -> None:
        """Remove an NPC from the POI."""
        if npc_id in self.npcs:
            self.npcs.remove(npc_id)
            self.update_timestamp()
    
    def add_quest(self, quest_id: str) -> None:
        """Add a quest to the POI."""
        if quest_id not in self.quests:
            self.quests.append(quest_id)
            self.update_timestamp()
    
    def remove_quest(self, quest_id: str) -> None:
        """Remove a quest from the POI."""
        if quest_id in self.quests:
            self.quests.remove(quest_id)
            self.update_timestamp()
    
    def add_claimed_hex(self, hex_id: str) -> None:
        """Add a region hex to the POI's claimed hexes."""
        if hex_id not in self.claimed_region_hex_ids:
            self.claimed_region_hex_ids.append(hex_id)
            self.update_timestamp()
    
    def remove_claimed_hex(self, hex_id: str) -> None:
        """Remove a region hex from the POI's claimed hexes."""
        if hex_id in self.claimed_region_hex_ids:
            self.claimed_region_hex_ids.remove(hex_id)
            self.update_timestamp()
    
    def update_resource(self, resource_id: str, value: Any) -> None:
        """Update a resource value for the POI."""
        self.resources[resource_id] = value
        self.update_timestamp() 