"""
Landmark Models for POI System

Data models and enums for landmarks, monuments, and significant locations.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class LandmarkType(str, Enum):
    """Types of landmarks"""
    ANCIENT_RUINS = "ancient_ruins"
    MAGICAL_SITE = "magical_site"
    NATURAL_WONDER = "natural_wonder"
    HISTORICAL_SITE = "historical_site"
    RELIGIOUS_SHRINE = "religious_shrine"
    STRATEGIC_LOCATION = "strategic_location"
    RESOURCE_NODE = "resource_node"
    PORTAL = "portal"
    DUNGEON = "dungeon"
    MONUMENT = "monument"
    BATTLEFIELD = "battlefield"
    GRAVEYARD = "graveyard"
    LIBRARY = "library"
    ACADEMY = "academy"
    OBSERVATORY = "observatory"


class LandmarkRarity(str, Enum):
    """Rarity levels for landmarks"""
    COMMON = "common"           # Found relatively frequently
    UNCOMMON = "uncommon"       # Moderately rare
    RARE = "rare"              # Quite rare
    EPIC = "epic"              # Very rare
    LEGENDARY = "legendary"     # Extremely rare
    MYTHIC = "mythic"          # Almost unique


class LandmarkStatus(str, Enum):
    """Status of landmarks"""
    UNDISCOVERED = "undiscovered"    # Not yet found
    DISCOVERED = "discovered"        # Found but not explored
    EXPLORED = "explored"           # Partially explored
    FULLY_MAPPED = "fully_mapped"   # Completely explored
    CLAIMED = "claimed"             # Claimed by faction
    CONTESTED = "contested"         # Multiple claims
    ABANDONED = "abandoned"         # Previously claimed, now empty
    CORRUPTED = "corrupted"         # Magically corrupted
    SEALED = "sealed"              # Magically or physically sealed


class LandmarkEffect(str, Enum):
    """Types of effects landmarks can provide"""
    RESOURCE_BONUS = "resource_bonus"
    DEFENSE_BONUS = "defense_bonus"
    MAGIC_AMPLIFICATION = "magic_amplification"
    KNOWLEDGE_ACCESS = "knowledge_access"
    TRAVEL_NETWORK = "travel_network"
    POPULATION_ATTRACTION = "population_attraction"
    TRADE_BONUS = "trade_bonus"
    CULTURAL_INFLUENCE = "cultural_influence"
    MILITARY_TRAINING = "military_training"
    HEALING = "healing"
    VISION = "vision"
    PROTECTION = "protection"
    CURSE = "curse"
    TRANSFORMATION = "transformation"


@dataclass
class LandmarkFeature:
    """Represents a special feature of a landmark"""
    id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    effect_type: LandmarkEffect = LandmarkEffect.RESOURCE_BONUS
    magnitude: float = 1.0  # Effect strength multiplier
    radius: float = 0.0  # Area of effect (0 = landmark only)
    duration: Optional[int] = None  # Duration in days (None = permanent)
    activation_requirements: List[str] = field(default_factory=list)
    active: bool = True
    discovered: bool = False
    
    def can_activate(self, context: Dict[str, Any]) -> bool:
        """Check if feature can be activated given context"""
        if not self.active or not self.discovered:
            return False
        
        for requirement in self.activation_requirements:
            if not self._check_requirement(requirement, context):
                return False
        
        return True
    
    def _check_requirement(self, requirement: str, context: Dict[str, Any]) -> bool:
        """Check if a specific requirement is met"""
        # Parse requirement string (simplified)
        if requirement.startswith("population:"):
            required_pop = int(requirement.split(":")[1])
            return context.get("population", 0) >= required_pop
        elif requirement.startswith("faction:"):
            required_faction = requirement.split(":")[1]
            return context.get("controlling_faction") == required_faction
        elif requirement.startswith("season:"):
            required_season = requirement.split(":")[1]
            return context.get("current_season") == required_season
        elif requirement.startswith("time:"):
            required_time = requirement.split(":")[1]
            return context.get("time_of_day") == required_time
        
        return True


@dataclass
class Landmark:
    """Represents a landmark POI with special properties"""
    id: UUID = field(default_factory=uuid4)
    poi_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    landmark_type: LandmarkType = LandmarkType.ANCIENT_RUINS
    rarity: LandmarkRarity = LandmarkRarity.COMMON
    status: LandmarkStatus = LandmarkStatus.UNDISCOVERED
    
    # Properties
    age: int = 1000  # Age in years
    origin_culture: str = "unknown"
    historical_significance: str = ""
    magical_resonance: float = 0.0  # 0.0 to 1.0
    
    # Features and effects
    features: List[LandmarkFeature] = field(default_factory=list)
    unique_resources: Dict[str, int] = field(default_factory=dict)
    
    # Discovery and exploration
    discovery_date: Optional[datetime] = None
    discovered_by: Optional[UUID] = None  # Faction or character ID
    exploration_progress: float = 0.0  # 0.0 to 1.0
    required_exploration_points: int = 100
    
    # Control and claims
    controlling_faction: Optional[UUID] = None
    contested_by: List[UUID] = field(default_factory=list)
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)
    
    def get_discovery_difficulty(self) -> float:
        """Calculate how difficult this landmark is to discover"""
        base_difficulty = {
            LandmarkRarity.COMMON: 0.2,
            LandmarkRarity.UNCOMMON: 0.4,
            LandmarkRarity.RARE: 0.6,
            LandmarkRarity.EPIC: 0.8,
            LandmarkRarity.LEGENDARY: 0.9,
            LandmarkRarity.MYTHIC: 0.95
        }.get(self.rarity, 0.5)
        
        # Modify based on type
        type_modifier = {
            LandmarkType.NATURAL_WONDER: -0.1,  # Easier to spot
            LandmarkType.ANCIENT_RUINS: 0.1,   # Hidden by time
            LandmarkType.MAGICAL_SITE: 0.2,    # Hidden by magic
            LandmarkType.DUNGEON: 0.3,         # Deliberately hidden
            LandmarkType.PORTAL: 0.25          # Unstable/hard to find
        }.get(self.landmark_type, 0.0)
        
        return min(0.99, max(0.01, base_difficulty + type_modifier))
    
    def get_active_effects(self, context: Dict[str, Any] = None) -> List[LandmarkFeature]:
        """Get currently active landmark effects"""
        context = context or {}
        return [f for f in self.features if f.can_activate(context)]


@dataclass
class LandmarkQuest:
    """Represents a quest or challenge associated with a landmark"""
    id: UUID = field(default_factory=uuid4)
    landmark_id: UUID = field(default_factory=uuid4)
    name: str = ""
    description: str = ""
    objectives: List[str] = field(default_factory=list)
    rewards: Dict[str, Any] = field(default_factory=dict)
    time_limit: Optional[int] = None  # Days
    prerequisites: List[str] = field(default_factory=list)
    status: str = "available"  # available, active, completed, failed
    assigned_to: Optional[UUID] = None  # Faction or character
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def is_available_to(self, faction_id: UUID, context: Dict[str, Any] = None) -> bool:
        """Check if quest is available to a faction"""
        if self.status != "available":
            return False
        
        # Check prerequisites
        context = context or {}
        for prerequisite in self.prerequisites:
            if not self._check_prerequisite(prerequisite, faction_id, context):
                return False
        
        return True
    
    def _check_prerequisite(self, prerequisite: str, faction_id: UUID, context: Dict[str, Any]) -> bool:
        """Check if a prerequisite is met"""
        # This would be expanded with actual prerequisite checking logic
        return True 