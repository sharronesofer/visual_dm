"""
Crisis Management Request and Response Schemas

This module defines Pydantic schemas for crisis management API endpoints,
including request validation and response formatting.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field, validator

from backend.systems.diplomacy.models.crisis_models import (
    CrisisType, CrisisEscalationLevel, CrisisStatus, ResolutionType, InterventionType
)


# Request Schemas

class CreateCrisisRequest(BaseModel):
    """Request schema for creating a new diplomatic crisis"""
    crisis_type: CrisisType = Field(..., description="Type of crisis being created")
    title: str = Field(..., min_length=1, max_length=255, description="Title for the crisis")
    description: str = Field(..., min_length=1, description="Detailed description of the crisis")
    primary_factions: List[UUID] = Field(..., min_items=2, description="Primary factions involved in the crisis")
    affected_factions: Optional[List[UUID]] = Field(default=[], description="Factions indirectly affected")
    root_causes: Optional[List[str]] = Field(default=[], description="Root causes of the crisis")
    severity_score: Optional[int] = Field(default=30, ge=0, le=100, description="Initial severity score")
    deadline: Optional[datetime] = Field(None, description="Crisis deadline (point of no return)")
    
    @validator('primary_factions')
    def validate_primary_factions(cls, v):
        if len(v) < 2:
            raise ValueError("Crisis must involve at least 2 primary factions")
        return v


class UpdateCrisisRequest(BaseModel):
    """Request schema for updating crisis status and details"""
    status: Optional[CrisisStatus] = Field(None, description="New crisis status")
    escalation_level: Optional[CrisisEscalationLevel] = Field(None, description="New escalation level")
    severity_score: Optional[int] = Field(None, ge=0, le=100, description="Updated severity score")
    description: Optional[str] = Field(None, description="Updated crisis description")
    deadline: Optional[datetime] = Field(None, description="Updated crisis deadline")


class CreateResolutionAttemptRequest(BaseModel):
    """Request schema for creating a crisis resolution attempt"""
    resolution_type: ResolutionType = Field(..., description="Type of resolution approach")
    title: str = Field(..., min_length=1, max_length=255, description="Title for the resolution attempt")
    description: str = Field(..., min_length=1, description="Detailed description of the resolution approach")
    proposing_faction: Optional[UUID] = Field(None, description="Faction proposing this resolution")
    mediating_factions: Optional[List[UUID]] = Field(default=[], description="Third-party mediator factions")
    proposed_terms: Optional[Dict[str, Any]] = Field(default={}, description="Specific terms of the resolution")
    implementation_timeline: Optional[int] = Field(None, ge=1, description="Days required for implementation")
    estimated_cost: Optional[int] = Field(default=0, ge=0, description="Economic cost to implement")


class UpdateResolutionAttemptRequest(BaseModel):
    """Request schema for updating resolution attempt status"""
    status: str = Field(..., description="New status of the resolution attempt")
    acceptance_votes: Optional[Dict[UUID, bool]] = Field(None, description="Faction votes on acceptance")
    implementation_progress: Optional[int] = Field(None, ge=0, le=100, description="Implementation progress percentage")
    actual_effectiveness: Optional[int] = Field(None, ge=0, le=100, description="Actual effectiveness rating")


class CreateInterventionRequest(BaseModel):
    """Request schema for creating a crisis intervention"""
    intervening_faction: UUID = Field(..., description="Faction making the intervention")
    intervention_type: InterventionType = Field(..., description="Type of intervention")
    title: str = Field(..., min_length=1, max_length=255, description="Title for the intervention")
    objectives: Optional[List[str]] = Field(default=[], description="Intervention objectives")
    methods: Optional[List[str]] = Field(default=[], description="Methods to be used")
    planned_duration: Optional[int] = Field(None, ge=1, description="Planned duration in days")
    legal_basis: Optional[str] = Field(None, description="Legal justification for intervention")


class CreateEscalationTriggerRequest(BaseModel):
    """Request schema for creating an escalation trigger"""
    trigger_type: str = Field(..., min_length=1, description="Type of escalation trigger")
    description: str = Field(..., min_length=1, description="Description of the trigger")
    escalation_increase: int = Field(default=10, ge=0, le=50, description="How much this escalates the crisis")
    threshold_conditions: Optional[Dict[str, Any]] = Field(default={}, description="Conditions that activate this trigger")
    prevention_actions: Optional[List[str]] = Field(default=[], description="Actions that could prevent this trigger")
    trigger_deadline: Optional[datetime] = Field(None, description="When this trigger expires")


class RequestImpactAssessmentRequest(BaseModel):
    """Request schema for requesting a crisis impact assessment"""
    assessor_faction: Optional[UUID] = Field(None, description="Faction requesting the assessment")
    assessment_focus: Optional[List[str]] = Field(default=[], description="Specific areas to focus the assessment on")


# Response Schemas

class CrisisResponse(BaseModel):
    """Response schema for diplomatic crisis data"""
    id: UUID
    crisis_type: CrisisType
    title: str
    description: str
    primary_factions: List[UUID]
    affected_factions: List[UUID]
    neutral_observers: List[UUID]
    status: CrisisStatus
    escalation_level: CrisisEscalationLevel
    severity_score: int
    detected_at: datetime
    last_escalation_at: Optional[datetime]
    deadline: Optional[datetime]
    resolved_at: Optional[datetime]
    root_causes: List[str]
    escalation_history: List[Dict[str, Any]]
    de_escalation_opportunities: List[str]
    economic_impact: int
    stability_impact: int
    humanitarian_impact: int
    public_awareness: int
    media_coverage: int
    international_concern: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResolutionAttemptResponse(BaseModel):
    """Response schema for crisis resolution attempts"""
    id: UUID
    crisis_id: UUID
    resolution_type: ResolutionType
    title: str
    description: str
    proposing_faction: Optional[UUID]
    mediating_factions: List[UUID]
    supporting_factions: List[UUID]
    opposing_factions: List[UUID]
    proposed_terms: Dict[str, Any]
    implementation_timeline: Optional[int]
    monitoring_mechanism: Optional[str]
    success_probability: int
    estimated_cost: int
    political_cost: int
    status: str
    acceptance_votes: Dict[UUID, bool]
    implementation_progress: int
    proposed_at: datetime
    deadline_for_response: Optional[datetime]
    accepted_at: Optional[datetime]
    implemented_at: Optional[datetime]
    failed_at: Optional[datetime]
    actual_effectiveness: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InterventionResponse(BaseModel):
    """Response schema for crisis interventions"""
    id: UUID
    crisis_id: UUID
    intervening_faction: UUID
    intervention_type: InterventionType
    title: str
    objectives: List[str]
    methods: List[str]
    resources_committed: Dict[str, Any]
    legal_basis: Optional[str]
    supporting_factions: List[UUID]
    opposing_factions: List[UUID]
    international_mandate: bool
    start_date: datetime
    planned_duration: Optional[int]
    actual_end_date: Optional[datetime]
    status: str
    success_metrics: List[str]
    effectiveness_score: Optional[int]
    economic_cost: int
    political_cost: int
    reputation_impact: int
    positive_outcomes: List[str]
    negative_outcomes: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class EscalationTriggerResponse(BaseModel):
    """Response schema for escalation triggers"""
    id: UUID
    crisis_id: UUID
    trigger_type: str
    description: str
    triggering_event_id: Optional[UUID]
    threshold_conditions: Dict[str, Any]
    escalation_increase: int
    trigger_deadline: Optional[datetime]
    prevention_actions: List[str]
    mitigation_cost: int
    responsible_factions: List[UUID]
    triggered: bool
    triggered_at: Optional[datetime]
    prevented: bool
    prevented_by: Optional[UUID]
    created_at: datetime
    
    class Config:
        from_attributes = True


class ImpactAssessmentResponse(BaseModel):
    """Response schema for crisis impact assessments"""
    id: UUID
    crisis_id: UUID
    assessment_date: datetime
    assessor_faction: Optional[UUID]
    economic_impact: Dict[UUID, int]
    political_impact: Dict[UUID, int]
    military_impact: Dict[UUID, int]
    social_impact: Dict[UUID, int]
    trade_disruption: int
    refugee_displacement: int
    infrastructure_damage: int
    environmental_impact: int
    short_term_outlook: str
    medium_term_outlook: str
    long_term_outlook: str
    risk_of_escalation: int
    risk_of_spillover: int
    probability_of_resolution: int
    recommended_actions: List[str]
    priority_interventions: List[str]
    resources_needed: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CrisisListResponse(BaseModel):
    """Response schema for list of crises"""
    crises: List[CrisisResponse]
    total_count: int
    active_count: int
    critical_count: int
    resolved_count: int


class CrisisDetailsResponse(CrisisResponse):
    """Extended crisis response with related data"""
    resolution_attempts: List[ResolutionAttemptResponse]
    interventions: List[InterventionResponse]
    escalation_triggers: List[EscalationTriggerResponse]
    impact_assessments: List[ImpactAssessmentResponse]


class CrisisStatisticsResponse(BaseModel):
    """Response schema for crisis management statistics"""
    total_crises: int
    active_crises: int
    resolved_crises: int
    crises_by_type: Dict[str, int]
    crises_by_escalation_level: Dict[str, int]
    average_resolution_time: Optional[float]  # Days
    resolution_success_rate: float  # Percentage
    most_effective_resolution_types: List[Dict[str, Any]]
    faction_involvement_stats: Dict[UUID, Dict[str, int]]
    recent_crisis_trends: List[Dict[str, Any]]


class SuccessResponse(BaseModel):
    """Generic success response for crisis management operations"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ErrorResponse(BaseModel):
    """Error response for crisis management operations"""
    error: str
    detail: str
    crisis_id: Optional[UUID] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow) 