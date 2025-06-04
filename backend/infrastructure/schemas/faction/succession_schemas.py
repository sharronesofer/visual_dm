"""
Faction Succession Schemas

This module defines schemas for succession crisis API validation and data transfer
according to Task 69 requirements.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, validator

# Define enums locally to avoid circular imports with domain models
class SuccessionType(str, Enum):
    """Types of faction succession systems"""
    HEREDITARY = "hereditary"
    ELECTORAL = "electoral"
    APPOINTED = "appointed"
    MERITOCRATIC = "meritocratic"
    COUNCIL = "council"
    AUTOCRATIC = "autocratic"

class SuccessionCrisisStatus(str, Enum):
    """Status of succession crisis"""
    PENDING = "pending"
    ACTIVE = "active"
    RESOLVED = "resolved"
    FAILED = "failed"

class SuccessionTrigger(str, Enum):
    """Triggers for succession crisis"""
    LEADER_DEATH_NATURAL = "leader_death_natural"
    LEADER_DEATH_VIOLENT = "leader_death_violent"
    LEADER_ABDICATION = "leader_abdication"
    EXTERNAL_PRESSURE = "external_pressure"
    INTERNAL_REVOLT = "internal_revolt"
    SUCCESSION_DISPUTE = "succession_dispute"

class SuccessionCandidateModel(BaseModel):
    """Schema for succession candidate"""
    id: UUID
    name: str
    legitimacy_score: float
    support_base: float
    claim_strength: float
    political_connections: int
    military_backing: float


class SuccessionAnalysisRequest(BaseModel):
    """Request for analyzing faction succession vulnerability"""
    
    faction_id: UUID = Field(..., description="ID of faction to analyze")
    simulate_triggers: Optional[List[SuccessionTrigger]] = Field(
        default_factory=list, 
        description="Triggers to simulate"
    )
    include_candidates: bool = Field(default=True, description="Include potential candidates")


class SuccessionAnalysisResponse(BaseModel):
    """Response for succession vulnerability analysis"""
    
    faction_id: UUID
    faction_name: str
    succession_type: SuccessionType
    vulnerability_score: float = Field(..., description="Succession vulnerability (0-1)")
    potential_triggers: List[Dict[str, Any]] = Field(default_factory=list)
    potential_candidates: List[SuccessionCandidateModel] = Field(default_factory=list)
    stability_factors: Dict[str, Any] = Field(default_factory=dict)
    
    # Faction type specific analysis
    succession_rules: Dict[str, Any] = Field(default_factory=dict)
    leadership_structure: Dict[str, Any] = Field(default_factory=dict)


class TriggerSuccessionCrisisRequest(BaseModel):
    """Request to trigger a succession crisis"""
    
    faction_id: UUID = Field(..., description="ID of faction")
    trigger: SuccessionTrigger = Field(..., description="Crisis trigger")
    previous_leader_id: Optional[UUID] = Field(None, description="Previous leader if applicable")
    external_pressure_source: Optional[UUID] = Field(None, description="Source of external pressure")
    trigger_details: Optional[Dict[str, Any]] = Field(default_factory=dict)
    
    @validator('trigger_details')
    def validate_trigger_details(cls, v, values):
        """Validate trigger details based on trigger type"""
        trigger = values.get('trigger')
        if trigger == SuccessionTrigger.LEADER_DEATH_VIOLENT:
            if 'killer_id' not in v and 'assassination_details' not in v:
                raise ValueError("Violent death requires killer_id or assassination_details")
        elif trigger == SuccessionTrigger.EXTERNAL_PRESSURE:
            if 'pressure_source' not in v:
                raise ValueError("External pressure requires pressure_source")
        return v


class AdvanceSuccessionCrisisRequest(BaseModel):
    """Request to advance succession crisis by one step"""
    
    crisis_id: UUID = Field(..., description="ID of succession crisis")
    time_days: Optional[int] = Field(1, description="Days to advance", ge=1, le=30)
    external_events: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="External events affecting the crisis"
    )


class ResolveSuccessionCrisisRequest(BaseModel):
    """Request to manually resolve succession crisis"""
    
    crisis_id: UUID = Field(..., description="ID of succession crisis")
    winner_id: UUID = Field(..., description="ID of winning candidate")
    resolution_method: str = Field(..., description="How crisis was resolved")
    force_resolution: bool = Field(default=False, description="Force resolution ignoring rules")


class InterferenceRequest(BaseModel):
    """Request for external faction interference in succession"""
    
    crisis_id: UUID = Field(..., description="ID of succession crisis")
    interfering_faction_id: UUID = Field(..., description="ID of interfering faction")
    interference_type: str = Field(..., description="Type of interference")
    candidate_id: Optional[UUID] = Field(None, description="Candidate being supported")
    resources_committed: float = Field(default=0.0, description="Resources committed")
    interference_details: Optional[Dict[str, Any]] = Field(default_factory=dict)


class SuccessionEventSchema(BaseModel):
    """Schema for succession-related events"""
    
    event_type: str = Field(..., description="Type of succession event")
    crisis_id: UUID = Field(..., description="Related succession crisis")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    event_data: Dict[str, Any] = Field(default_factory=dict)
    affected_characters: List[UUID] = Field(default_factory=list)
    affected_factions: List[UUID] = Field(default_factory=list)


class CandidateActionRequest(BaseModel):
    """Request for candidate action during succession"""
    
    crisis_id: UUID = Field(..., description="ID of succession crisis")
    candidate_id: UUID = Field(..., description="ID of candidate")
    action_type: str = Field(..., description="Type of action")
    action_details: Dict[str, Any] = Field(default_factory=dict)
    resources_spent: float = Field(default=0.0, description="Resources spent on action")


class SuccessionMetricsResponse(BaseModel):
    """Response with succession crisis metrics"""
    
    total_crises: int = Field(..., description="Total succession crises")
    active_crises: int = Field(..., description="Currently active crises") 
    resolved_crises: int = Field(..., description="Resolved crises")
    failed_crises: int = Field(..., description="Failed crises")
    faction_splits: int = Field(..., description="Crises that resulted in faction splits")
    
    # Breakdown by faction type
    crisis_by_faction_type: Dict[str, int] = Field(default_factory=dict)
    crisis_by_trigger: Dict[str, int] = Field(default_factory=dict)
    crisis_by_succession_type: Dict[str, int] = Field(default_factory=dict)
    
    # Average metrics
    average_duration_days: float = Field(..., description="Average crisis duration")
    average_candidates: float = Field(..., description="Average number of candidates")
    average_stability_impact: float = Field(..., description="Average stability impact")


class FactionStabilityRequest(BaseModel):
    """Request to update faction stability during succession"""
    
    faction_id: UUID = Field(..., description="ID of faction")
    stability_change: float = Field(..., description="Change in stability (-1 to 1)")
    stability_factors: Optional[Dict[str, Any]] = Field(default_factory=dict)
    duration_days: Optional[int] = Field(None, description="Duration of instability")


class SuccessionSimulationRequest(BaseModel):
    """Request to simulate succession scenarios"""
    
    faction_id: UUID = Field(..., description="ID of faction")
    scenarios: List[Dict[str, Any]] = Field(..., description="Scenarios to simulate")
    simulation_depth: int = Field(default=10, ge=1, le=50, description="Simulation steps")
    include_external_factors: bool = Field(default=True)


class SuccessionSimulationResponse(BaseModel):
    """Response for succession simulation"""
    
    faction_id: UUID
    scenarios_tested: int
    simulation_results: List[Dict[str, Any]] = Field(default_factory=list)
    stability_projections: Dict[str, float] = Field(default_factory=dict)
    recommended_actions: List[str] = Field(default_factory=list)


# Batch operation schemas
class BatchSuccessionAnalysisRequest(BaseModel):
    """Request for analyzing multiple factions"""
    
    faction_ids: List[UUID] = Field(..., description="IDs of factions to analyze")
    analysis_depth: str = Field(default="standard", description="Analysis depth")
    include_cross_faction_effects: bool = Field(default=True)


class BatchSuccessionAnalysisResponse(BaseModel):
    """Response for batch succession analysis"""
    
    faction_analyses: List[SuccessionAnalysisResponse] = Field(default_factory=list)
    cross_faction_effects: Dict[str, Any] = Field(default_factory=dict)
    global_stability_impact: float = Field(..., description="Overall stability impact")
    crisis_probability_matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict) 