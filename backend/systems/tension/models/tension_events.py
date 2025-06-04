"""
Tension Event Domain Models

Domain models and enums for tension-affecting events according to
Development Bible standards for pure business logic.
"""

from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass


class TensionEventType(Enum):
    """Types of events that can affect tension levels"""
    
    # Combat Events
    PLAYER_COMBAT = "player_combat"
    NPC_COMBAT = "npc_combat"
    FACTION_WARFARE = "faction_warfare"
    SIEGE_WARFARE = "siege_warfare"
    SKIRMISH = "skirmish"
    ASSASSINATION = "assassination"
    DUEL = "duel"
    
    # Death and Violence Events
    NPC_DEATH = "npc_death"
    MASS_CASUALTIES = "mass_casualties"
    EXECUTION = "execution"
    MURDER = "murder"
    SUICIDE = "suicide"
    
    # Environmental Events
    ENVIRONMENTAL_DISASTER = "environmental_disaster"
    NATURAL_DISASTER = "natural_disaster"
    PLAGUE_OUTBREAK = "plague_outbreak"
    FAMINE = "famine"
    FIRE_OUTBREAK = "fire_outbreak"
    FLOOD = "flood"
    EARTHQUAKE = "earthquake"
    MAGICAL_CATASTROPHE = "magical_catastrophe"
    
    # Political Events
    POLITICAL_CHANGE = "political_change"
    REGIME_CHANGE = "regime_change"
    REBELLION = "rebellion"
    COUP = "coup"
    ELECTION = "election"
    POLICY_CHANGE = "policy_change"
    TAXATION_CHANGE = "taxation_change"
    LAW_ENFORCEMENT = "law_enforcement"
    CORRUPTION_EXPOSED = "corruption_exposed"
    
    # Economic Events
    ECONOMIC_CRISIS = "economic_crisis"
    MARKET_CRASH = "market_crash"
    TRADE_EMBARGO = "trade_embargo"
    RESOURCE_SHORTAGE = "resource_shortage"
    INFLATION = "inflation"
    UNEMPLOYMENT = "unemployment"
    PROSPERITY_BOOM = "prosperity_boom"
    MERCHANT_ARRIVAL = "merchant_arrival"
    
    # Social Events
    FESTIVAL = "festival"
    RELIGIOUS_CEREMONY = "religious_ceremony"
    SOCIAL_UNREST = "social_unrest"
    PROTEST = "protest"
    RIOT = "riot"
    CULTURAL_EVENT = "cultural_event"
    WEDDING = "wedding"
    FUNERAL = "funeral"
    
    # Criminal Events
    THEFT = "theft"
    BURGLARY = "burglary"
    KIDNAPPING = "kidnapping"
    SMUGGLING = "smuggling"
    BANDITRY = "banditry"
    PIRACY = "piracy"
    DRUG_TRADE = "drug_trade"
    ORGANIZED_CRIME = "organized_crime"
    
    # Religious Events
    RELIGIOUS_CONFLICT = "religious_conflict"
    HERESY = "heresy"
    DIVINE_INTERVENTION = "divine_intervention"
    TEMPLE_DESECRATION = "temple_desecration"
    PILGRIMAGE = "pilgrimage"
    RELIGIOUS_PERSECUTION = "religious_persecution"
    
    # Magical Events
    MAGICAL_ACCIDENT = "magical_accident"
    SPELL_DISASTER = "spell_disaster"
    ARTIFACT_DISCOVERY = "artifact_discovery"
    MAGICAL_RESEARCH = "magical_research"
    SUMMONING_GONE_WRONG = "summoning_gone_wrong"
    PLANAR_INCURSION = "planar_incursion"
    
    # Military Events
    MILITARY_DEPLOYMENT = "military_deployment"
    MILITARY_RETREAT = "military_retreat"
    FORTIFICATION_BUILT = "fortification_built"
    FORTIFICATION_DESTROYED = "fortification_destroyed"
    WEAPONS_CACHE_FOUND = "weapons_cache_found"
    DESERTION = "desertion"
    
    # Diplomatic Events
    DIPLOMATIC_VISIT = "diplomatic_visit"
    TREATY_SIGNED = "treaty_signed"
    ALLIANCE_FORMED = "alliance_formed"
    ALLIANCE_BROKEN = "alliance_broken"
    DIPLOMATIC_INCIDENT = "diplomatic_incident"
    HOSTAGE_SITUATION = "hostage_situation"
    
    # Information Events
    RUMORS_SPREAD = "rumors_spread"
    PROPAGANDA = "propaganda"
    INFORMATION_LEAK = "information_leak"
    ESPIONAGE_DISCOVERED = "espionage_discovered"
    SECRET_REVEALED = "secret_revealed"
    
    # Infrastructure Events
    CONSTRUCTION_PROJECT = "construction_project"
    INFRASTRUCTURE_DAMAGE = "infrastructure_damage"
    BRIDGE_COLLAPSE = "bridge_collapse"
    ROAD_BLOCKADE = "road_blockade"
    SUPPLY_LINE_CUT = "supply_line_cut"


@dataclass
class TensionEvent:
    """
    Represents an event that affects tension levels.
    Pure domain model with no external dependencies.
    """
    event_type: TensionEventType
    region_id: str
    poi_id: str
    timestamp: datetime
    data: Dict[str, Any]
    event_id: str
    description: Optional[str] = None
    severity: float = 1.0  # Multiplier for base impact (0.0-3.0)
    duration_hours: Optional[float] = None  # Some events have ongoing effects


class TensionEventFilter:
    """Filter for querying tension events."""
    region_id: Optional[str] = None
    poi_id: Optional[str] = None
    event_types: Optional[list] = None
    min_impact: Optional[float] = None
    max_impact: Optional[float] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    min_severity: Optional[str] = None


class EventSeverity(Enum):
    """Severity levels for events."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    EXTREME = "extreme"


class TensionEventBuilder:
    """Builder pattern for creating tension events with validation."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset builder to initial state."""
        self._event_type = None
        self._region_id = None
        self._poi_id = None
        self._impact = 0.0
        self._timestamp = datetime.utcnow()
        self._data = {}
        self._source = None
        self._duration_hours = None
        return self
    
    def event_type(self, event_type: TensionEventType):
        """Set the event type."""
        self._event_type = event_type
        return self
    
    def location(self, region_id: str, poi_id: str):
        """Set the location where the event occurred."""
        self._region_id = region_id
        self._poi_id = poi_id
        return self
    
    def impact(self, impact: float):
        """Set the tension impact."""
        self._impact = impact
        return self
    
    def timestamp(self, timestamp: datetime):
        """Set the event timestamp."""
        self._timestamp = timestamp
        return self
    
    def data(self, **kwargs):
        """Add event-specific data."""
        self._data.update(kwargs)
        return self
    
    def source(self, source: str):
        """Set the event source."""
        self._source = source
        return self
    
    def duration(self, hours: float):
        """Set effect duration in hours."""
        self._duration_hours = hours
        return self
    
    def build(self) -> TensionEvent:
        """Build and validate the tension event."""
        if not self._event_type:
            raise ValueError("Event type is required")
        if not self._region_id or not self._poi_id:
            raise ValueError("Region ID and POI ID are required")
        
        event = TensionEvent(
            event_type=self._event_type,
            region_id=self._region_id,
            poi_id=self._poi_id,
            timestamp=self._timestamp,
            data=self._data.copy()
        )
        
        self.reset()  # Reset for next use
        return event


# Factory functions for common event types

def create_player_combat_event(
    region_id: str,
    poi_id: str,
    lethal: bool = False,
    stealth: bool = False,
    enemies_defeated: int = None
) -> TensionEvent:
    """Create a player combat event using configurable parameters."""
    # Load configurable defaults
    try:
        from backend.infrastructure.config_loaders.tension_config import TensionConfigManager
        config_manager = TensionConfigManager()
        defaults = config_manager.get_event_factory_defaults().get("player_combat", {})
    except ImportError:
        defaults = {"base_impact": 0.15, "lethal_bonus": 0.3, "stealth_reduction": 0.1, "default_enemies_defeated": 1}
    
    base_impact = defaults.get("base_impact", 0.15)
    if lethal:
        base_impact += defaults.get("lethal_bonus", 0.3)
    if stealth:
        base_impact -= defaults.get("stealth_reduction", 0.1)
    
    if enemies_defeated is None:
        enemies_defeated = defaults.get("default_enemies_defeated", 1)
    
    return TensionEventBuilder()\
        .event_type(TensionEventType.PLAYER_COMBAT)\
        .location(region_id, poi_id)\
        .impact(base_impact)\
        .source("player_action")\
        .data(lethal=lethal, stealth=stealth, enemies_defeated=enemies_defeated)\
        .build()


def create_npc_death_event(
    region_id: str,
    poi_id: str,
    npc_importance: str = None,
    cause: str = "unknown"
) -> TensionEvent:
    """Create an NPC death event using configurable parameters."""
    # Load configurable defaults
    try:
        from backend.infrastructure.config_loaders.tension_config import TensionConfigManager
        config_manager = TensionConfigManager()
        defaults = config_manager.get_event_factory_defaults().get("npc_death", {})
    except ImportError:
        defaults = {"base_impact": 0.1, "important_bonus": 0.3, "civilian_bonus": 0.2, "default_importance": "normal"}
    
    if npc_importance is None:
        npc_importance = defaults.get("default_importance", "normal")
    
    base_impact = defaults.get("base_impact", 0.1)
    
    if npc_importance == "important":
        base_impact += defaults.get("important_bonus", 0.3)
    elif npc_importance == "civilian":
        base_impact += defaults.get("civilian_bonus", 0.2)
    
    return TensionEventBuilder()\
        .event_type(TensionEventType.NPC_DEATH)\
        .location(region_id, poi_id)\
        .impact(base_impact)\
        .source("npc_system")\
        .data(importance=npc_importance, cause=cause)\
        .build()


def create_environmental_disaster_event(
    region_id: str,
    poi_id: str,
    disaster_type: str,
    severity: float = None
) -> TensionEvent:
    """Create an environmental disaster event using configurable parameters."""
    # Load configurable defaults
    try:
        from backend.infrastructure.config_loaders.tension_config import TensionConfigManager
        config_manager = TensionConfigManager()
        defaults = config_manager.get_event_factory_defaults().get("environmental_disaster", {})
    except ImportError:
        defaults = {"base_impact": 0.3, "default_severity": 1.0, "default_duration_multiplier": 24}
    
    if severity is None:
        severity = defaults.get("default_severity", 1.0)
    
    base_impact = defaults.get("base_impact", 0.3) * severity
    duration = defaults.get("default_duration_multiplier", 24) * severity
    
    return TensionEventBuilder()\
        .event_type(TensionEventType.ENVIRONMENTAL_DISASTER)\
        .location(region_id, poi_id)\
        .impact(base_impact)\
        .source("environment")\
        .duration(duration)\
        .data(disaster_type=disaster_type, severity=severity)\
        .build()


def create_political_change_event(
    region_id: str,
    poi_id: str,
    change_type: str = "minor",
    peaceful: bool = True
) -> TensionEvent:
    """Create a political change event using configurable parameters."""
    # Load configurable defaults
    try:
        from backend.infrastructure.config_loaders.tension_config import TensionConfigManager
        config_manager = TensionConfigManager()
        defaults = config_manager.get_event_factory_defaults().get("political_change", {})
    except ImportError:
        defaults = {
            "base_impact": 0.2, "regime_change_bonus": 0.5, "major_change_bonus": 0.2,
            "peaceful_reduction": 0.1, "default_duration_minor": 24, "default_duration_regime": 72
        }
    
    base_impact = defaults.get("base_impact", 0.2)
    
    # Modify impact based on change type
    if change_type == "regime_change":
        base_impact += defaults.get("regime_change_bonus", 0.5)
        duration = defaults.get("default_duration_regime", 72)
    elif change_type == "major":
        base_impact += defaults.get("major_change_bonus", 0.2)
        duration = defaults.get("default_duration_minor", 24) * 2
    else:  # minor
        duration = defaults.get("default_duration_minor", 24)
    
    # Reduce impact if peaceful
    if peaceful:
        base_impact -= defaults.get("peaceful_reduction", 0.1)
    
    return TensionEventBuilder()\
        .event_type(TensionEventType.POLITICAL_CHANGE)\
        .location(region_id, poi_id)\
        .impact(base_impact)\
        .source("political_system")\
        .duration(duration)\
        .data(change_type=change_type, peaceful=peaceful)\
        .build()


def create_festival_event(
    region_id: str,
    poi_id: str,
    festival_size: str = "local"
) -> TensionEvent:
    """Create a festival event using configurable parameters."""
    # Load configurable defaults
    try:
        from backend.infrastructure.config_loaders.tension_config import TensionConfigManager
        config_manager = TensionConfigManager()
        defaults = config_manager.get_event_factory_defaults().get("festival", {})
    except ImportError:
        defaults = {
            "local_impact": -0.1, "regional_impact": -0.2, "major_impact": -0.3, "default_duration": 24
        }
    
    # Set impact based on festival size (negative = tension reduction)
    if festival_size == "major":
        impact = defaults.get("major_impact", -0.3)
    elif festival_size == "regional":
        impact = defaults.get("regional_impact", -0.2)
    else:  # local
        impact = defaults.get("local_impact", -0.1)
    
    duration = defaults.get("default_duration", 24)
    
    return TensionEventBuilder()\
        .event_type(TensionEventType.FESTIVAL)\
        .location(region_id, poi_id)\
        .impact(impact)\
        .source("social_system")\
        .duration(duration)\
        .data(size=festival_size)\
        .build() 