"""
Faction Expansion System Schemas

Pydantic schemas for faction expansion API endpoints and data validation.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class ExpansionStrategy(Enum):
    """Types of faction expansion strategies"""
    MILITARY = "military"
    ECONOMIC = "economic"
    CULTURAL = "cultural"


class ExpansionStrategyType(str, Enum):
    """Expansion strategy enum for API"""
    MILITARY = "military"
    ECONOMIC = "economic" 
    CULTURAL = "cultural"


class ExpansionAttemptRequest(BaseModel):
    """Request to attempt faction expansion"""
    
    faction_id: UUID = Field(..., description="ID of the faction attempting expansion")
    target_region_id: UUID = Field(..., description="ID of the target region for expansion")
    strategy: Optional[ExpansionStrategyType] = Field(
        None, 
        description="Expansion strategy to use (if not provided, will be determined by faction personality)"
    )
    force_attempt: bool = Field(
        False,
        description="Force expansion attempt even if faction personality suggests otherwise"
    )


class ExpansionAttemptResponse(BaseModel):
    """Response from expansion attempt"""
    
    success: bool = Field(..., description="Whether the expansion attempt succeeded")
    strategy_used: ExpansionStrategyType = Field(..., description="Strategy that was used")
    target_region_id: UUID = Field(..., description="ID of the target region")
    faction_id: UUID = Field(..., description="ID of the expanding faction")
    cost: float = Field(..., description="Cost of the expansion attempt (0.0 to 1.0)")
    effectiveness: float = Field(..., description="Effectiveness of the attempt (0.0 to 1.0)")
    reason: str = Field(..., description="Detailed reason for success or failure")
    consequences: Dict[str, Any] = Field(..., description="Consequences of the expansion attempt")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the attempt occurred")


class FactionExpansionProfileRequest(BaseModel):
    """Request to get faction expansion profile"""
    
    faction_id: UUID = Field(..., description="ID of the faction to analyze")


class FactionExpansionProfileResponse(BaseModel):
    """Response with faction expansion analysis"""
    
    faction_id: UUID = Field(..., description="ID of the faction")
    faction_name: str = Field(..., description="Name of the faction")
    primary_strategy: ExpansionStrategyType = Field(..., description="Primary expansion strategy")
    aggressiveness: float = Field(..., description="Expansion aggressiveness (0.0 to 1.0)")
    should_expand: bool = Field(..., description="Whether faction should attempt expansion")
    strategy_scores: Dict[str, float] = Field(
        ..., 
        description="Scores for each expansion strategy"
    )
    hidden_attributes: Dict[str, int] = Field(
        ..., 
        description="Hidden personality attributes driving expansion behavior"
    )


class RegionExpansionOpportunitiesRequest(BaseModel):
    """Request to analyze expansion opportunities for a region"""
    
    region_id: UUID = Field(..., description="ID of the region to analyze")
    max_factions: int = Field(5, description="Maximum number of potential expanding factions to return")


class RegionExpansionOpportunity(BaseModel):
    """Information about a faction's expansion opportunity into a region"""
    
    faction_id: UUID = Field(..., description="ID of the faction")
    faction_name: str = Field(..., description="Name of the faction")
    expansion_strategy: ExpansionStrategyType = Field(..., description="Preferred expansion strategy")
    likelihood: float = Field(..., description="Likelihood of expansion attempt (0.0 to 1.0)")
    predicted_effectiveness: float = Field(..., description="Predicted effectiveness (0.0 to 1.0)")
    aggressiveness: float = Field(..., description="Faction aggressiveness (0.0 to 1.0)")


class RegionExpansionOpportunitiesResponse(BaseModel):
    """Response with expansion opportunities for a region"""
    
    region_id: UUID = Field(..., description="ID of the analyzed region")
    opportunities: List[RegionExpansionOpportunity] = Field(
        ..., 
        description="List of potential expansion opportunities, ordered by likelihood"
    )
    total_factions_analyzed: int = Field(..., description="Total number of factions analyzed")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the analysis was performed")


class BulkExpansionSimulationRequest(BaseModel):
    """Request to simulate expansion attempts for multiple factions"""
    
    faction_ids: List[UUID] = Field(..., description="List of faction IDs to simulate expansion for")
    simulation_steps: int = Field(1, ge=1, le=10, description="Number of expansion simulation steps")
    allow_concurrent_expansion: bool = Field(
        True, 
        description="Whether multiple factions can expand into the same region simultaneously"
    )


class BulkExpansionSimulationResponse(BaseModel):
    """Response from bulk expansion simulation"""
    
    simulation_id: UUID = Field(..., description="ID of this simulation run")
    steps_completed: int = Field(..., description="Number of simulation steps completed")
    total_attempts: int = Field(..., description="Total expansion attempts made")
    successful_attempts: int = Field(..., description="Number of successful expansions")
    expansion_results: List[ExpansionAttemptResponse] = Field(
        ..., 
        description="Results from all expansion attempts"
    )
    final_faction_territories: Dict[str, List[UUID]] = Field(
        ..., 
        description="Final territorial control after simulation (faction_id -> region_ids)"
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the simulation was run")


class ExpansionHistoryRequest(BaseModel):
    """Request to get expansion history"""
    
    faction_id: Optional[UUID] = Field(None, description="Filter by specific faction (optional)")
    region_id: Optional[UUID] = Field(None, description="Filter by specific region (optional)")
    strategy: Optional[ExpansionStrategyType] = Field(None, description="Filter by expansion strategy (optional)")
    limit: int = Field(50, ge=1, le=500, description="Maximum number of records to return")
    offset: int = Field(0, ge=0, description="Number of records to skip")


class ExpansionHistoryResponse(BaseModel):
    """Response with expansion history"""
    
    expansion_attempts: List[ExpansionAttemptResponse] = Field(
        ..., 
        description="List of historical expansion attempts"
    )
    total_count: int = Field(..., description="Total number of expansion attempts in database")
    filtered_count: int = Field(..., description="Number of attempts matching the filter criteria")
    has_more: bool = Field(..., description="Whether there are more records available") 