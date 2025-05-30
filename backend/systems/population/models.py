from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Literal
from datetime import datetime
from enum import Enum

class POIType(str, Enum):
    """Types of Points of Interest (POIs)"""
    CITY = "City"
    TOWN = "Town"
    VILLAGE = "Village"
    RUINS = "Ruins"
    DUNGEON = "Dungeon"
    RELIGIOUS = "Religious"
    EMBASSY = "Embassy"
    OUTPOST = "Outpost"
    MARKET = "Market"
    CUSTOM = "Custom"

class POIState(str, Enum):
    """Possible states for Points of Interest (POIs)"""
    NORMAL = "Normal"
    DECLINING = "Declining"
    ABANDONED = "Abandoned"
    RUINS = "Ruins"
    DUNGEON = "Dungeon"
    REPOPULATING = "Repopulating"
    SPECIAL = "Special"

class PopulationConfig(BaseModel):
    """Global configuration for population control system"""
    global_multiplier: float = Field(1.0, description="System-wide adjustment factor")
    base_rates: Dict[POIType, float] = Field(
        default_factory=lambda: {
            POIType.CITY: 10.0,
            POIType.TOWN: 5.0,
            POIType.VILLAGE: 2.0,
            POIType.RUINS: 0.0,
            POIType.DUNGEON: 0.0,
            POIType.RELIGIOUS: 3.0,
            POIType.EMBASSY: 4.0,
            POIType.OUTPOST: 3.0,
            POIType.MARKET: 6.0,
            POIType.CUSTOM: 1.0
        },
        description="Base birth rates per POI type"
    )
    state_transition_thresholds: Dict[str, float] = Field(
        default_factory=lambda: {
            "normal_to_declining": 0.6,  # Below 60% of target
            "declining_to_abandoned": 0.3,  # Below 30% of target
            "abandoned_to_ruins": 0.1,  # Below 10% of target
            "repopulating_to_normal": 0.7  # Above 70% of target
        },
        description="Thresholds for POI state transitions based on population ratio"
    )
    soft_cap_threshold: float = Field(0.9, description="Threshold for soft population cap as ratio of target population")
    soft_cap_multiplier: float = Field(0.5, description="Growth rate multiplier applied at soft cap")

class POIPopulation(BaseModel):
    """Population data for a specific POI"""
    poi_id: str = Field(..., description="Unique identifier for the POI")
    name: str = Field(..., description="Name of the POI")
    poi_type: POIType = Field(..., description="Type of the POI")
    current_population: int = Field(0, description="Current population count")
    target_population: int = Field(100, description="Target/maximum population count")
    min_population: int = Field(0, description="Minimum population threshold")
    base_rate: float = Field(1.0, description="Base birth rate for this POI")
    state: POIState = Field(POIState.NORMAL, description="Current state of the POI")
    resource_impact: Dict[str, float] = Field(
        default_factory=dict,
        description="Impact of this population on resources (resource_type: consumption_rate)"
    )
    last_updated: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

class PopulationChangedEvent(BaseModel):
    """Event emitted when a POI's population changes"""
    poi_id: str
    old_population: int
    new_population: int
    old_state: Optional[POIState] = None
    new_state: Optional[POIState] = None
    change_type: Literal["growth", "decline", "manual", "migration", "catastrophe", "war"] = "growth"
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class PopulationChangeRequest(BaseModel):
    """Request to manually change a POI's population"""
    new_population: int = Field(..., description="New population value to set")
    change_type: Literal["manual", "migration", "catastrophe", "war"] = "manual"
    reason: Optional[str] = None

class GlobalMultiplierRequest(BaseModel):
    """Request to update the global multiplier"""
    value: float = Field(..., description="New global multiplier value")

class BaseRateRequest(BaseModel):
    """Request to update the base rate for a POI type"""
    poi_type: POIType
    value: float = Field(..., description="New base rate value") 