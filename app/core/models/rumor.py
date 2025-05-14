"""
Rumor engine model for NPC interactions.
"""

from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from enum import Enum

class RumorType(str, Enum):
    """Types of rumors that can spread."""
    FACT = "fact"
    GOSSIP = "gossip"
    LIE = "lie"
    SECRET = "secret"
    WARNING = "warning"
    RUMOR = "rumor"

class RumorState(str, Enum):
    """States a rumor can be in."""
    NEW = "new"
    SPREADING = "spreading"
    WIDESPREAD = "widespread"
    FADING = "fading"
    FORGOTTEN = "forgotten"

class Rumor(BaseModel):
    """Base rumor model."""
    id: str
    type: RumorType
    content: Dict
    source_npc_id: str
    origin_time: datetime = Field(default_factory=datetime.utcnow)
    last_spread: datetime = Field(default_factory=datetime.utcnow)
    state: RumorState = Field(default=RumorState.NEW)
    spread_count: int = Field(default=0)
    heard_by: Set[str] = Field(default_factory=set)
    tags: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)

    def should_spread(self) -> bool:
        """Determine if this rumor should spread further."""
        if self.state == RumorState.FORGOTTEN:
            return False
            
        time_since_last_spread = datetime.utcnow() - self.last_spread
        if self.state == RumorState.NEW and time_since_last_spread >= timedelta(hours=1):
            return True
        elif self.state == RumorState.SPREADING and time_since_last_spread >= timedelta(hours=4):
            return True
        elif self.state == RumorState.WIDESPREAD and time_since_last_spread >= timedelta(hours=12):
            return True
        elif self.state == RumorState.FADING and time_since_last_spread >= timedelta(hours=24):
            return True
        return False

    def update_state(self):
        """Update the rumor's state based on spread count."""
        if self.spread_count >= 50:
            self.state = RumorState.WIDESPREAD
        elif self.spread_count >= 20:
            self.state = RumorState.SPREADING
        elif self.spread_count >= 5:
            self.state = RumorState.NEW
        elif self.spread_count == 0:
            self.state = RumorState.FORGOTTEN

class RumorEngine(BaseModel):
    """Engine for managing rumor spread and evolution."""
    active_rumors: Dict[str, Rumor] = Field(default_factory=dict)
    npc_relationships: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    last_update: datetime = Field(default_factory=datetime.utcnow)

    def add_rumor(self, rumor: Rumor):
        """Add a new rumor to the engine."""
        self.active_rumors[rumor.id] = rumor
        self.last_update = datetime.utcnow()

    def spread_rumor(self, rumor_id: str, npc_id: str) -> bool:
        """Attempt to spread a rumor to an NPC."""
        if rumor_id not in self.active_rumors:
            return False
            
        rumor = self.active_rumors[rumor_id]
        if not rumor.should_spread():
            return False
            
        # Check if NPC has already heard the rumor
        if npc_id in rumor.heard_by:
            return False
            
        # Calculate spread chance based on relationships
        spread_chance = self._calculate_spread_chance(rumor, npc_id)
        if spread_chance < 0.3:  # Minimum chance to spread
            return False
            
        # Update rumor state
        rumor.spread_count += 1
        rumor.heard_by.add(npc_id)
        rumor.last_spread = datetime.utcnow()
        rumor.update_state()
        
        return True

    def _calculate_spread_chance(self, rumor: Rumor, npc_id: str) -> float:
        """Calculate the chance of a rumor spreading to an NPC."""
        base_chance = 0.5
        
        # Adjust based on rumor type
        if rumor.type == RumorType.GOSSIP:
            base_chance += 0.2
        elif rumor.type == RumorType.SECRET:
            base_chance -= 0.2
            
        # Adjust based on relationship with source
        if npc_id in self.npc_relationships.get(rumor.source_npc_id, {}):
            relationship = self.npc_relationships[rumor.source_npc_id][npc_id]
            base_chance += relationship * 0.3
            
        return max(0.0, min(1.0, base_chance))

    def evolve_rumor(self, rumor_id: str) -> Optional[Rumor]:
        """Evolve a rumor based on its spread and state."""
        if rumor_id not in self.active_rumors:
            return None
            
        rumor = self.active_rumors[rumor_id]
        
        # Rumors can evolve when they reach widespread state
        if rumor.state != RumorState.WIDESPREAD:
            return None
            
        # Create evolved version of the rumor
        evolved = Rumor(
            id=f"{rumor.id}_evolved",
            type=rumor.type,
            content=self._evolve_content(rumor.content),
            source_npc_id=rumor.source_npc_id,
            origin_time=datetime.utcnow(),
            tags=rumor.tags + ["evolved"]
        )
        
        return evolved

    def _evolve_content(self, content: Dict) -> Dict:
        """Evolve the content of a rumor."""
        # This would be where we call GPT to evolve the rumor content
        # For now, return a simple modification
        evolved = content.copy()
        if "details" in evolved:
            evolved["details"] = f"EVOLVED: {evolved['details']}"
        return evolved 