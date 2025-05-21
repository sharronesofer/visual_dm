"""
Schemas for Tension and War Management System

This module defines the Pydantic models for the tension and war system,
including request and response schemas for API interactions.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator

# Tension schemas
class TensionLevelEnum(str, Enum):
    """Enumeration of tension levels between factions."""
    ALLIANCE = "alliance"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    RIVALRY = "rivalry"
    HOSTILE = "hostile"
    WAR = "war"


class TensionRequest(BaseModel):
    """Request schema for modifying tension"""
    faction: str = Field(..., description="Faction name for which to modify tension")
    value: int = Field(..., description="Amount to modify tension by (positive or negative)")
    reason: Optional[str] = Field(None, description="Reason for tension modification")


class TensionResponse(BaseModel):
    """Response schema for tension data"""
    region_id: str = Field(..., description="Region ID")
    tensions: Dict[str, int] = Field(..., description="Dictionary of faction tensions")
    last_updated: Dict[str, datetime] = Field(..., description="Dictionary of last updated timestamps per faction")
    history: Optional[List[Dict[str, Any]]] = Field(None, description="Optional tension history")


class TensionHistoryEntry(BaseModel):
    """Schema for a historical tension data point."""
    timestamp: datetime = Field(..., description="When the tension was recorded")
    value: float = Field(..., description="Tension value at this time")
    reason: Optional[str] = Field(None, description="Reason for tension change")


class TensionHistoryResponse(BaseModel):
    """Response schema for tension history endpoint."""
    faction_a_id: str = Field(..., description="ID of the first faction")
    faction_b_id: str = Field(..., description="ID of the second faction")
    current_tension: float = Field(..., description="Current tension value")
    history: List[TensionHistoryEntry] = Field(
        default_factory=list,
        description="Historical tension values"
    )


# War schemas
class WarOutcomeEnum(str, Enum):
    """Enumeration of possible war outcomes."""
    DECISIVE_VICTORY = "decisive_victory"
    VICTORY = "victory"
    STALEMATE = "stalemate"
    CEASEFIRE = "ceasefire"
    WHITE_PEACE = "white_peace"


class WarInitiationRequest(BaseModel):
    """Request schema for initializing a war"""
    region_a: str = Field(..., description="First region involved in war")
    region_b: str = Field(..., description="Second region involved in war")
    faction_a: str = Field(..., description="First faction involved in war")
    faction_b: str = Field(..., description="Second faction involved in war")


class WarStatusResponse(BaseModel):
    """Response schema for war status"""
    region_id: str = Field(..., description="Region ID")
    is_active: bool = Field(..., description="Whether war is active in this region")
    faction_a: Optional[str] = Field(None, description="First faction in war")
    faction_b: Optional[str] = Field(None, description="Second faction in war")
    start_date: Optional[datetime] = Field(None, description="War start date")
    day: Optional[int] = Field(None, description="Current war day")
    controlled_pois: Optional[Dict[str, List[str]]] = Field(None, description="POIs controlled by each faction")
    battle_log: Optional[List[Dict[str, Any]]] = Field(None, description="Log of battle events")


class WarAdvanceResponse(BaseModel):
    """Response schema for advancing war state"""
    region_id: str = Field(..., description="Region ID")
    day: int = Field(..., description="New day of the war")
    events: List[Dict[str, Any]] = Field(..., description="Events that occurred during the day")
    new_raids: Optional[List[Dict[str, Any]]] = Field(None, description="New raids generated this day")
    continues: bool = Field(..., description="Whether the war continues")
    end_reason: Optional[str] = Field(None, description="Reason war ended, if applicable")


class PoiConquestRequest(BaseModel):
    """Request schema for POI conquest"""
    region: str = Field(..., description="Region where POI is located")
    poi_id: str = Field(..., description="ID of the POI being conquered")
    faction: str = Field(..., description="Faction conquering the POI")


class BattleResult(BaseModel):
    """Schema for battle results"""
    victor: str = Field(..., description="Faction that won the battle")
    loser: str = Field(..., description="Faction that lost the battle")
    location: str = Field(..., description="POI or area where battle occurred")
    victor_losses: int = Field(..., description="Casualties suffered by victor")
    loser_losses: int = Field(..., description="Casualties suffered by loser")
    day: int = Field(..., description="War day when battle occurred")
    timestamp: datetime = Field(..., description="When the battle occurred")
    description: str = Field(..., description="Narrative description of battle")


class RaidEvent(BaseModel):
    """Schema for raid events"""
    attacker: str = Field(..., description="Faction conducting the raid")
    defender: str = Field(..., description="Faction defending against the raid")
    target: str = Field(..., description="POI being raided")
    success: bool = Field(..., description="Whether the raid was successful")
    losses: int = Field(..., description="Casualties from the raid")
    plunder: Optional[Dict[str, Any]] = Field(None, description="Resources captured")
    timestamp: datetime = Field(..., description="When the raid occurred")
    description: str = Field(..., description="Narrative description of raid")


class WarStateResponse(BaseModel):
    """Response schema for war state endpoint."""
    faction_a_id: str = Field(..., description="ID of the first faction")
    faction_b_id: str = Field(..., description="ID of the second faction")
    start_date: datetime = Field(..., description="When the war started")
    days_elapsed: int = Field(..., description="Days since war began")
    exhaustion_a: float = Field(..., description="Exhaustion level of faction A")
    exhaustion_b: float = Field(..., description="Exhaustion level of faction B")
    battles: List[BattleResult] = Field(default_factory=list, description="List of battles")
    disputed_regions: List[str] = Field(default_factory=list, description="Disputed region IDs")
    is_active: bool = Field(..., description="Whether the war is still active")


class WarDeclarationRequest(BaseModel):
    """Request schema for war declaration endpoint."""
    faction_a_id: str = Field(..., description="ID of declaring faction")
    faction_b_id: str = Field(..., description="ID of target faction")
    disputed_regions: Optional[List[str]] = Field(
        default_factory=list,
        description="Disputed region IDs"
    )
    reason: Optional[str] = Field(None, description="Reason for war declaration")

    @validator('faction_a_id', 'faction_b_id')
    def factions_must_be_different(cls, v, values):
        """Validate that factions are different entities."""
        if 'faction_a_id' in values and v == values['faction_a_id']:
            raise ValueError('Factions must be different entities')
        return v


class WarOutcomeResponse(BaseModel):
    """Response schema for war outcome endpoint."""
    war_id: str = Field(..., description="Unique identifier for the war")
    winner_id: Optional[str] = Field(None, description="ID of winning faction (if any)")
    loser_id: Optional[str] = Field(None, description="ID of losing faction (if any)")
    outcome_type: WarOutcomeEnum = Field(..., description="Type of war outcome")
    start_date: datetime = Field(..., description="When the war started")
    end_date: datetime = Field(..., description="When the war ended")
    duration: int = Field(..., description="Duration in days")
    battle_count: int = Field(..., description="Number of battles fought")
    territorial_changes: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of territorial changes"
    )
    casualties: Dict[str, int] = Field(
        default_factory=dict,
        description="Total casualties by faction"
    )


class PeaceOfferRequest(BaseModel):
    """Request schema for peace negotiation endpoint."""
    faction_id: str = Field(..., description="ID of faction making the offer")
    war_id: str = Field(..., description="ID of the active war")
    terms: Dict[str, Any] = Field(..., description="Peace terms being offered")
    concessions: bool = Field(False, description="Whether offering faction is making concessions")


class PeaceOfferResponse(BaseModel):
    """Response schema for peace offer status."""
    offer_id: str = Field(..., description="Unique identifier for the peace offer")
    war_id: str = Field(..., description="ID of the associated war")
    offering_faction: str = Field(..., description="ID of faction making the offer")
    receiving_faction: str = Field(..., description="ID of faction receiving the offer")
    terms: Dict[str, Any] = Field(..., description="Peace terms")
    status: str = Field(..., description="Status of peace offer (pending/accepted/rejected)")
    created_at: datetime = Field(..., description="When the offer was created") 