"""
Tension State Domain Models

Pure business logic data structures for managing tension state, configuration,
and conflict triggers according to Development Bible standards.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass


@dataclass
class TensionModifier:
    """Domain model for temporary tension modifiers"""
    modifier_type: str
    value: float  # Can be positive (increase) or negative (decrease)
    expiration_time: datetime
    source: str  # What caused this modifier (event, festival, etc.)


@dataclass
class TensionState:
    """Domain model for current environmental tension state in a location"""
    current_level: float  # Current tension level (0.0 to 1.0) for environmental/local tension
    base_level: float     # Base tension for this location type
    last_updated: datetime
    recent_events: List[str]  # Recent event IDs that affected tension
    modifiers: Dict[str, TensionModifier]  # Active temporary modifiers


@dataclass
class FactionRelationship:
    """Domain model for faction-to-faction relationship tension (-100 to +100)"""
    faction_a_id: str     # First faction ID
    faction_b_id: str     # Second faction ID
    tension_level: int    # Tension level (-100 to +100, where 0 = neutral)
    last_updated: datetime
    relationship_type: str  # 'alliance', 'neutral', 'hostile', 'war'
    recent_events: List[str]  # Recent events affecting this relationship
    modifiers: Dict[str, TensionModifier]  # Active temporary modifiers
    war_threshold: int = 70    # Tension level that triggers war
    alliance_threshold: int = -50  # Tension level that indicates strong alliance


@dataclass
class TensionConfig:
    """Domain model for location-specific tension configuration"""
    base_tension: float          # Starting tension level (environmental)
    decay_rate: float           # How fast tension naturally decreases per hour
    max_tension: float          # Maximum tension level
    min_tension: float          # Minimum tension level
    player_impact: float        # Multiplier for player-caused events
    npc_impact: float          # Multiplier for NPC-caused events
    environmental_impact: float # Multiplier for environmental events


@dataclass
class FactionTensionConfig:
    """Domain model for faction relationship tension configuration"""
    base_decay_rate: int        # How much tension decays per day (towards 0)
    max_tension: int = 100      # Maximum tension level
    min_tension: int = -100     # Minimum tension level (strong alliance)
    neutral_point: int = 0      # Neutral relationship level
    war_threshold: int = 70     # Tension level that triggers war
    alliance_threshold: int = -50  # Strong alliance threshold
    event_impact_multiplier: float = 1.0  # Multiplier for faction events


@dataclass
class ConflictTrigger:
    """Domain model for conflict trigger conditions"""
    name: str                    # Name of the conflict type
    tension_threshold: int       # Faction tension level required to trigger (uses -100 to +100 scale)
    duration_hours: int         # How long the conflict lasts
    faction_requirements: Dict[str, Any]  # Requirements about factions present
    probability_modifier: float # Modifier for trigger probability


@dataclass
class RevoltConfig:
    """Domain model for revolt/uprising configuration"""
    base_probability_threshold: float      # Base environmental tension level for revolt possibility
    faction_influence_modifier: float      # How much faction presence affects revolt
    duration_range_hours: List[int]        # [min_hours, max_hours] for revolt duration
    casualty_multiplier: float            # Modifier for casualties during revolt
    economic_impact_factor: float         # Economic damage factor


@dataclass
class CalculationConstants:
    """Domain model for tension calculation constants"""
    high_tension_threshold: float         # When environmental tension is considered "high" (0.0-1.0)
    high_faction_tension_threshold: int   # When faction tension is considered "high" (-100 to +100)
    event_history_hours: int             # How many hours of events to consider
    modifier_expiration_check_hours: int # How often to check for expired modifiers
    severity_thresholds: Dict[str, float] # Thresholds for event severity levels
    revolt_probability: Dict[str, float]  # Parameters for revolt probability calculation
    environmental_tension_limits: Dict[str, float]  # Limits for environmental tension (0.0-1.0)
    faction_tension_limits: Dict[str, int]  # Limits for faction tension (-100 to +100) 