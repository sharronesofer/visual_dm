"""
Tension and War Models

This module defines the data models for tension and war management, including:
- TensionLevel: Enum for tension levels between factions
- WarOutcomeType: Enum for the types of war outcomes
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class TensionLevel(str, Enum):
    """Tension level between factions."""
    ALLIANCE = "alliance"  # -100 to -76: Strong alliance
    FRIENDLY = "friendly"  # -75 to -26: Friendly relations
    NEUTRAL = "neutral"    # -25 to 25: Neutral relations
    RIVALRY = "rivalry"    # 26 to 50: Rivalry/competition
    HOSTILE = "hostile"    # 51 to 99: Hostility/conflict
    WAR = "war"            # 100: Active state of war


class WarOutcomeType(str, Enum):
    """Type of war outcome."""
    DECISIVE_VICTORY = "decisive_victory"  # Complete victory, major concessions
    VICTORY = "victory"                    # Victory, moderate concessions
    STALEMATE = "stalemate"                # Neither side gains clear advantage
    CEASEFIRE = "ceasefire"                # Temporary end to fighting
    WHITE_PEACE = "white_peace"            # War ends with no changes


class TensionConfig(BaseModel):
    """Configuration for tension system."""
    base_tension: float = Field(default=0.0, description="Base tension value between factions")
    decay_rate: float = Field(default=0.1, description="Daily tension decay rate")
    max_tension: float = Field(default=100.0, description="Maximum tension value")
    min_tension: float = Field(default=-100.0, description="Minimum tension value (alliance)")
    faction_impact: float = Field(default=0.5, description="Impact of faction traits on tension")
    border_impact: float = Field(default=0.3, description="Impact of bordering regions on tension")
    event_impact: float = Field(default=0.2, description="Impact of events on tension")


class WarConfig(BaseModel):
    """Configuration for war system."""
    default_war_duration: int = Field(default=30, description="Default war duration in days")
    exhaustion_rate: float = Field(default=2.0, description="Daily exhaustion increase rate")
    max_exhaustion: float = Field(default=100.0, description="Maximum exhaustion level")
    min_peace_duration: int = Field(default=7, description="Minimum days of peace after war")
    attrition_factor: float = Field(default=1.5, description="Attrition multiplier for losses")
    battle_frequency: float = Field(default=5.0, description="Average days between battles")
    outcome_weights: Dict[str, float] = Field(default_factory=dict, description="Probability weights for outcomes")


class WarOutcome(BaseModel):
    """Outcome of a war."""
    winner_id: Optional[str] = Field(default=None, description="ID of winning faction (if any)")
    loser_id: Optional[str] = Field(default=None, description="ID of losing faction (if any)")
    outcome_type: WarOutcomeType = Field(..., description="Type of war outcome")
    territorial_changes: List[Dict[str, Any]] = Field(default_factory=list, description="Territorial changes")
    resource_transfers: Dict[str, Dict[str, float]] = Field(default_factory=dict, description="Resource transfers")
    reputation_changes: Dict[str, float] = Field(default_factory=dict, description="Reputation changes")
    tension_changes: float = Field(default=0.0, description="Change in tension due to outcome")
    casualties: Dict[str, int] = Field(default_factory=dict, description="Casualties by faction")
    duration: int = Field(..., description="Duration of war in days")


class WarState(BaseModel):
    """Current state of a war between factions."""
    faction_a_id: str = Field(..., description="ID of the first faction")
    faction_b_id: str = Field(..., description="ID of the second faction")
    start_date: datetime = Field(..., description="When the war started")
    exhaustion_a: float = Field(default=0.0, description="Exhaustion level of faction A")
    exhaustion_b: float = Field(default=0.0, description="Exhaustion level of faction B")
    battles: List[Dict[str, Any]] = Field(default_factory=list, description="List of battles")
    current_peace_offer: Optional[Dict[str, Any]] = Field(default=None, description="Current peace offer")
    disputed_regions: List[str] = Field(default_factory=list, description="List of disputed region IDs")
    is_active: bool = Field(default=True, description="Whether the war is active") 