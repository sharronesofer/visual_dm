"""
Crisis Management Models for the Diplomacy System

This module defines models for diplomatic crisis detection, escalation, and resolution:
- DiplomaticCrisis: Core crisis entity with escalation mechanics
- CrisisEscalationLevel: Enum for crisis severity levels
- CrisisResolutionPath: Different ways crises can be resolved
- CrisisIntervention: Third-party interventions in crises
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, validator


class CrisisType(str, Enum):
    """Types of diplomatic crises that can occur."""
    BORDER_DISPUTE = "border_dispute"
    TRADE_WAR = "trade_war"
    SUCCESSION_CRISIS = "succession_crisis"
    HUMANITARIAN_CRISIS = "humanitarian_crisis"
    MILITARY_STANDOFF = "military_standoff"
    RESOURCE_CONFLICT = "resource_conflict"
    TERRITORIAL_CLAIM = "territorial_claim"
    ALLIANCE_BREAKDOWN = "alliance_breakdown"
    TREATY_CRISIS = "treaty_crisis"
    ESPIONAGE_REVELATION = "espionage_revelation"
    ECONOMIC_WARFARE = "economic_warfare"
    PROXY_CONFLICT = "proxy_conflict"
    REFUGEE_CRISIS = "refugee_crisis"
    ENVIRONMENTAL_DISPUTE = "environmental_dispute"
    CULTURAL_CONFLICT = "cultural_conflict"


class CrisisEscalationLevel(str, Enum):
    """Escalation levels for diplomatic crises."""
    TENSION = "tension"              # Early warning signs
    INCIDENT = "incident"            # Specific triggering event
    DISPUTE = "dispute"              # Formal diplomatic disagreement
    CRISIS = "crisis"                # Active crisis requiring intervention
    SEVERE_CRISIS = "severe_crisis"  # High risk of military action
    CRITICAL = "critical"            # Imminent threat of war/breakdown
    BREAKDOWN = "breakdown"          # Complete diplomatic failure


class CrisisStatus(str, Enum):
    """Current status of a crisis."""
    DEVELOPING = "developing"        # Crisis is forming
    ACTIVE = "active"               # Crisis is ongoing
    ESCALATING = "escalating"       # Crisis is getting worse
    DE_ESCALATING = "de_escalating" # Crisis is improving
    STABILIZED = "stabilized"       # Crisis is under control
    RESOLVED = "resolved"           # Crisis has been resolved
    DORMANT = "dormant"             # Crisis is paused but could resume
    FAILED_RESOLUTION = "failed_resolution"  # Resolution attempts failed


class ResolutionType(str, Enum):
    """Types of crisis resolution approaches."""
    DIPLOMATIC_MEDIATION = "diplomatic_mediation"
    ECONOMIC_INCENTIVES = "economic_incentives"
    MILITARY_DETERRENCE = "military_deterrence"
    THIRD_PARTY_ARBITRATION = "third_party_arbitration"
    FACE_SAVING_COMPROMISE = "face_saving_compromise"
    INTERNATIONAL_PRESSURE = "international_pressure"
    TREATY_REVISION = "treaty_revision"
    COMPENSATION_PACKAGE = "compensation_package"
    STATUS_QUO_RESTORATION = "status_quo_restoration"
    PARTITION_SOLUTION = "partition_solution"
    TEMPORARY_CEASEFIRE = "temporary_ceasefire"
    COALITION_INTERVENTION = "coalition_intervention"


class InterventionType(str, Enum):
    """Types of third-party interventions."""
    MEDIATION = "mediation"          # Neutral party helps negotiate
    ARBITRATION = "arbitration"      # Neutral party makes binding decision
    PEACEKEEPING = "peacekeeping"    # Military presence to maintain peace
    ECONOMIC_SANCTIONS = "economic_sanctions"  # Economic pressure
    DIPLOMATIC_PRESSURE = "diplomatic_pressure"  # Political influence
    HUMANITARIAN_AID = "humanitarian_aid"  # Assistance to affected populations
    MILITARY_SUPPORT = "military_support"  # Military aid to one side
    COALITION_BUILDING = "coalition_building"  # Organizing multiple interventions


class DiplomaticCrisis(BaseModel):
    """A diplomatic crisis requiring management and resolution."""
    id: UUID = Field(default_factory=uuid4)
    crisis_type: CrisisType
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    
    # Primary parties in the crisis
    primary_factions: List[UUID] = Field(..., min_items=2)
    affected_factions: List[UUID] = Field(default_factory=list)  # Indirectly affected
    neutral_observers: List[UUID] = Field(default_factory=list)  # Watching but not involved
    
    # Crisis state
    status: CrisisStatus = CrisisStatus.DEVELOPING
    escalation_level: CrisisEscalationLevel = CrisisEscalationLevel.TENSION
    severity_score: int = Field(default=30, ge=0, le=100)  # Overall crisis severity
    
    # Timing
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    last_escalation_at: Optional[datetime] = None
    deadline: Optional[datetime] = None  # Point of no return
    resolved_at: Optional[datetime] = None
    
    # Root causes and triggers
    root_causes: List[str] = Field(default_factory=list)
    triggering_events: List[UUID] = Field(default_factory=list)  # Related incident/event IDs
    contributing_factors: Dict[str, Union[str, int, bool]] = Field(default_factory=dict)
    
    # Escalation tracking
    escalation_history: List[Dict[str, Union[str, datetime, int]]] = Field(default_factory=list)
    escalation_triggers: List[str] = Field(default_factory=list)
    de_escalation_opportunities: List[str] = Field(default_factory=list)
    
    # Stakes and consequences
    potential_consequences: Dict[str, Union[str, int, List]] = Field(default_factory=dict)
    economic_impact: int = Field(default=0, ge=0, le=100)
    stability_impact: int = Field(default=0, ge=0, le=100)
    humanitarian_impact: int = Field(default=0, ge=0, le=100)
    
    # Resolution tracking
    active_resolution_attempts: List[UUID] = Field(default_factory=list)
    failed_resolution_attempts: List[UUID] = Field(default_factory=list)
    successful_resolutions: List[UUID] = Field(default_factory=list)
    
    # International involvement
    active_interventions: List[UUID] = Field(default_factory=list)
    potential_mediators: List[UUID] = Field(default_factory=list)
    coalition_against: List[UUID] = Field(default_factory=list)
    coalition_support: List[UUID] = Field(default_factory=list)
    
    # Metadata
    public_awareness: int = Field(default=50, ge=0, le=100)  # How widely known the crisis is
    media_coverage: int = Field(default=50, ge=0, le=100)  # Level of media attention
    international_concern: int = Field(default=50, ge=0, le=100)  # Global worry level
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('primary_factions')
    def validate_primary_factions(cls, v):
        if len(v) < 2:
            raise ValueError("Crisis must involve at least 2 primary factions")
        return v
    
    @validator('deadline')
    def validate_deadline(cls, v, values):
        if v and 'detected_at' in values and v <= values['detected_at']:
            raise ValueError("Deadline must be after detection time")
        return v


class CrisisResolutionAttempt(BaseModel):
    """An attempt to resolve a diplomatic crisis."""
    id: UUID = Field(default_factory=uuid4)
    crisis_id: UUID
    resolution_type: ResolutionType
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    
    # Parties involved in resolution
    proposing_faction: Optional[UUID] = None  # Who proposed this resolution
    mediating_factions: List[UUID] = Field(default_factory=list)  # Third-party mediators
    supporting_factions: List[UUID] = Field(default_factory=list)  # Factions supporting this approach
    opposing_factions: List[UUID] = Field(default_factory=list)  # Factions opposing this approach
    
    # Resolution details
    proposed_terms: Dict[str, Union[str, int, bool, List]] = Field(default_factory=dict)
    concessions_required: Dict[UUID, List[str]] = Field(default_factory=dict)  # What each faction must give up
    benefits_offered: Dict[UUID, List[str]] = Field(default_factory=dict)  # What each faction gains
    
    # Implementation details
    implementation_timeline: Optional[int] = None  # Days to implement
    monitoring_mechanism: Optional[str] = None  # How compliance is verified
    enforcement_measures: List[str] = Field(default_factory=list)
    
    # Success factors
    success_probability: int = Field(default=50, ge=0, le=100)
    estimated_cost: int = Field(default=0, ge=0)  # Economic cost to implement
    political_cost: int = Field(default=0, ge=0, le=100)  # Political capital required
    
    # Status tracking
    status: str = Field(default="proposed")  # proposed, under_consideration, accepted, rejected, implemented, failed
    acceptance_votes: Dict[UUID, bool] = Field(default_factory=dict)  # Faction acceptance
    implementation_progress: int = Field(default=0, ge=0, le=100)
    
    # Timing
    proposed_at: datetime = Field(default_factory=datetime.utcnow)
    deadline_for_response: Optional[datetime] = None
    accepted_at: Optional[datetime] = None
    implemented_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    
    # Results
    actual_effectiveness: Optional[int] = None  # 0-100, how well it worked
    unintended_consequences: List[str] = Field(default_factory=list)
    lessons_learned: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CrisisIntervention(BaseModel):
    """Third-party intervention in a diplomatic crisis."""
    id: UUID = Field(default_factory=uuid4)
    crisis_id: UUID
    intervening_faction: UUID
    intervention_type: InterventionType
    title: str = Field(..., min_length=1, max_length=255)
    
    # Intervention details
    objectives: List[str] = Field(default_factory=list)
    methods: List[str] = Field(default_factory=list)
    resources_committed: Dict[str, Union[str, int]] = Field(default_factory=dict)
    conditions_for_success: List[str] = Field(default_factory=list)
    
    # Authorization and legitimacy
    legal_basis: Optional[str] = None  # Treaty, international law, etc.
    supporting_factions: List[UUID] = Field(default_factory=list)
    opposing_factions: List[UUID] = Field(default_factory=list)
    international_mandate: bool = False
    
    # Timeline and scope
    start_date: datetime = Field(default_factory=datetime.utcnow)
    planned_duration: Optional[int] = None  # Days
    actual_end_date: Optional[datetime] = None
    scope_limitations: List[str] = Field(default_factory=list)
    
    # Effectiveness tracking
    status: str = Field(default="active")  # active, suspended, completed, failed, withdrawn
    success_metrics: List[str] = Field(default_factory=list)
    progress_indicators: Dict[str, Union[str, int, bool]] = Field(default_factory=dict)
    effectiveness_score: Optional[int] = None  # 0-100, how effective the intervention was
    
    # Costs and consequences
    economic_cost: int = Field(default=0, ge=0)
    political_cost: int = Field(default=0, ge=0, le=100)
    reputation_impact: int = Field(default=0, ge=-50, le=50)  # Impact on intervening faction's reputation
    
    # Side effects
    positive_outcomes: List[str] = Field(default_factory=list)
    negative_outcomes: List[str] = Field(default_factory=list)
    regional_impact: Dict[str, Union[str, int]] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CrisisEscalationTrigger(BaseModel):
    """Events or conditions that can escalate a crisis."""
    id: UUID = Field(default_factory=uuid4)
    crisis_id: UUID
    trigger_type: str = Field(..., min_length=1)  # Type of escalating event
    description: str = Field(..., min_length=1)
    
    # Trigger conditions
    triggering_event_id: Optional[UUID] = None  # Related diplomatic event
    threshold_conditions: Dict[str, Union[str, int, bool]] = Field(default_factory=dict)
    faction_actions: Dict[UUID, List[str]] = Field(default_factory=dict)
    
    # Escalation effects
    escalation_increase: int = Field(default=10, ge=0, le=50)  # How much this escalates the crisis
    affected_relationships: List[UUID] = Field(default_factory=list)  # Relationship IDs affected
    trigger_deadline: Optional[datetime] = None  # When this trigger expires
    
    # Mitigation
    prevention_actions: List[str] = Field(default_factory=list)
    mitigation_cost: int = Field(default=0, ge=0)
    responsible_factions: List[UUID] = Field(default_factory=list)
    
    triggered: bool = False
    triggered_at: Optional[datetime] = None
    prevented: bool = False
    prevented_by: Optional[UUID] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CrisisImpactAssessment(BaseModel):
    """Assessment of crisis impact on various systems and factions."""
    id: UUID = Field(default_factory=uuid4)
    crisis_id: UUID
    assessment_date: datetime = Field(default_factory=datetime.utcnow)
    assessor_faction: Optional[UUID] = None  # Who conducted this assessment
    
    # Impact categories
    economic_impact: Dict[UUID, int] = Field(default_factory=dict)  # Impact per faction (0-100)
    political_impact: Dict[UUID, int] = Field(default_factory=dict)  # Political stability impact
    military_impact: Dict[UUID, int] = Field(default_factory=dict)  # Military readiness impact
    social_impact: Dict[UUID, int] = Field(default_factory=dict)  # Population morale impact
    
    # Regional effects
    trade_disruption: int = Field(default=0, ge=0, le=100)
    refugee_displacement: int = Field(default=0, ge=0)
    infrastructure_damage: int = Field(default=0, ge=0, le=100)
    environmental_impact: int = Field(default=0, ge=0, le=100)
    
    # Projections
    short_term_outlook: str = Field(default="uncertain")  # 1-30 days
    medium_term_outlook: str = Field(default="uncertain")  # 1-6 months
    long_term_outlook: str = Field(default="uncertain")  # 6+ months
    
    # Risk factors
    risk_of_escalation: int = Field(default=50, ge=0, le=100)
    risk_of_spillover: int = Field(default=30, ge=0, le=100)  # Risk of affecting other regions
    probability_of_resolution: int = Field(default=50, ge=0, le=100)
    
    # Recommendations
    recommended_actions: List[str] = Field(default_factory=list)
    priority_interventions: List[str] = Field(default_factory=list)
    resources_needed: Dict[str, Union[str, int]] = Field(default_factory=dict)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 