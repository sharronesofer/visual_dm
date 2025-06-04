"""
Crisis Management Database Models

SQLAlchemy models for crisis management system.
"""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, JSON, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, ARRAY
from sqlalchemy.orm import relationship

from .diplomacy_models import Base
from backend.systems.diplomacy.models.crisis_models import (
    CrisisType, CrisisEscalationLevel, CrisisStatus, ResolutionType, InterventionType
)


class DiplomaticCrisis(Base):
    """SQLAlchemy model for diplomatic crises."""
    
    __tablename__ = "diplomatic_crises"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    crisis_type = Column(SQLEnum(CrisisType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Primary parties in the crisis
    primary_factions = Column(ARRAY(String), nullable=False)  # Array of faction UUIDs as strings
    affected_factions = Column(ARRAY(String), nullable=True)  # Indirectly affected factions
    neutral_observers = Column(ARRAY(String), nullable=True)  # Watching but not involved
    
    # Crisis state
    status = Column(SQLEnum(CrisisStatus), nullable=False, default=CrisisStatus.DEVELOPING)
    escalation_level = Column(SQLEnum(CrisisEscalationLevel), nullable=False, default=CrisisEscalationLevel.TENSION)
    severity_score = Column(Integer, nullable=False, default=30)  # 0-100
    
    # Timing
    detected_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_escalation_at = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)  # Point of no return
    resolved_at = Column(DateTime, nullable=True)
    
    # Root causes and triggers
    root_causes = Column(JSON, nullable=True)  # Array of strings
    triggering_events = Column(ARRAY(String), nullable=True)  # Related incident/event IDs
    contributing_factors = Column(JSON, nullable=True)  # Dict of factors
    
    # Escalation tracking
    escalation_history = Column(JSON, nullable=True)  # Array of escalation events
    escalation_triggers = Column(JSON, nullable=True)  # Array of trigger descriptions
    de_escalation_opportunities = Column(JSON, nullable=True)  # Array of opportunity descriptions
    
    # Stakes and consequences
    potential_consequences = Column(JSON, nullable=True)  # Dict of potential outcomes
    economic_impact = Column(Integer, nullable=False, default=0)  # 0-100
    stability_impact = Column(Integer, nullable=False, default=0)  # 0-100
    humanitarian_impact = Column(Integer, nullable=False, default=0)  # 0-100
    
    # Resolution tracking
    active_resolution_attempts = Column(ARRAY(String), nullable=True)  # Resolution attempt IDs
    failed_resolution_attempts = Column(ARRAY(String), nullable=True)  # Failed resolution IDs
    successful_resolutions = Column(ARRAY(String), nullable=True)  # Successful resolution IDs
    
    # International involvement
    active_interventions = Column(ARRAY(String), nullable=True)  # Intervention IDs
    potential_mediators = Column(ARRAY(String), nullable=True)  # Potential mediator faction IDs
    coalition_against = Column(ARRAY(String), nullable=True)  # Faction IDs opposed to crisis parties
    coalition_support = Column(ARRAY(String), nullable=True)  # Faction IDs supporting crisis parties
    
    # Metadata
    public_awareness = Column(Integer, nullable=False, default=50)  # 0-100
    media_coverage = Column(Integer, nullable=False, default=50)  # 0-100
    international_concern = Column(Integer, nullable=False, default=50)  # 0-100
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class CrisisResolutionAttempt(Base):
    """SQLAlchemy model for crisis resolution attempts."""
    
    __tablename__ = "crisis_resolution_attempts"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    crisis_id = Column(PGUUID(as_uuid=True), ForeignKey("diplomatic_crises.id"), nullable=False)
    resolution_type = Column(SQLEnum(ResolutionType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Parties involved in resolution
    proposing_faction = Column(PGUUID(as_uuid=True), nullable=True)  # Who proposed this resolution
    mediating_factions = Column(ARRAY(String), nullable=True)  # Third-party mediator faction IDs
    supporting_factions = Column(ARRAY(String), nullable=True)  # Supporting faction IDs
    opposing_factions = Column(ARRAY(String), nullable=True)  # Opposing faction IDs
    
    # Resolution details
    proposed_terms = Column(JSON, nullable=True)  # Dict of proposed terms
    concessions_required = Column(JSON, nullable=True)  # Dict mapping faction IDs to concession lists
    benefits_offered = Column(JSON, nullable=True)  # Dict mapping faction IDs to benefit lists
    
    # Implementation details
    implementation_timeline = Column(Integer, nullable=True)  # Days to implement
    monitoring_mechanism = Column(String(500), nullable=True)  # How compliance is verified
    enforcement_measures = Column(JSON, nullable=True)  # Array of enforcement mechanisms
    
    # Success factors
    success_probability = Column(Integer, nullable=False, default=50)  # 0-100
    estimated_cost = Column(Integer, nullable=False, default=0)  # Economic cost
    political_cost = Column(Integer, nullable=False, default=0)  # Political capital required (0-100)
    
    # Status tracking
    status = Column(String(50), nullable=False, default="proposed")
    acceptance_votes = Column(JSON, nullable=True)  # Dict mapping faction IDs to boolean votes
    implementation_progress = Column(Integer, nullable=False, default=0)  # 0-100
    
    # Timing
    proposed_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    deadline_for_response = Column(DateTime, nullable=True)
    accepted_at = Column(DateTime, nullable=True)
    implemented_at = Column(DateTime, nullable=True)
    failed_at = Column(DateTime, nullable=True)
    
    # Results
    actual_effectiveness = Column(Integer, nullable=True)  # 0-100, how well it worked
    unintended_consequences = Column(JSON, nullable=True)  # Array of consequence descriptions
    lessons_learned = Column(JSON, nullable=True)  # Array of lesson descriptions
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    crisis = relationship("DiplomaticCrisis", backref="resolution_attempts")


class CrisisIntervention(Base):
    """SQLAlchemy model for crisis interventions."""
    
    __tablename__ = "crisis_interventions"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    crisis_id = Column(PGUUID(as_uuid=True), ForeignKey("diplomatic_crises.id"), nullable=False)
    intervening_faction = Column(PGUUID(as_uuid=True), nullable=False)
    intervention_type = Column(SQLEnum(InterventionType), nullable=False)
    title = Column(String(255), nullable=False)
    
    # Intervention details
    objectives = Column(JSON, nullable=True)  # Array of objective strings
    methods = Column(JSON, nullable=True)  # Array of method strings
    resources_committed = Column(JSON, nullable=True)  # Dict of resource commitments
    conditions_for_success = Column(JSON, nullable=True)  # Array of condition strings
    
    # Authorization and legitimacy
    legal_basis = Column(String(500), nullable=True)  # Treaty, international law, etc.
    supporting_factions = Column(ARRAY(String), nullable=True)  # Supporting faction IDs
    opposing_factions = Column(ARRAY(String), nullable=True)  # Opposing faction IDs
    international_mandate = Column(Boolean, nullable=False, default=False)
    
    # Timeline and scope
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    planned_duration = Column(Integer, nullable=True)  # Days
    actual_end_date = Column(DateTime, nullable=True)
    scope_limitations = Column(JSON, nullable=True)  # Array of limitation strings
    
    # Effectiveness tracking
    status = Column(String(50), nullable=False, default="active")
    success_metrics = Column(JSON, nullable=True)  # Array of metric strings
    progress_indicators = Column(JSON, nullable=True)  # Dict of progress indicators
    effectiveness_score = Column(Integer, nullable=True)  # 0-100
    
    # Costs and consequences
    economic_cost = Column(Integer, nullable=False, default=0)
    political_cost = Column(Integer, nullable=False, default=0)  # 0-100
    reputation_impact = Column(Integer, nullable=False, default=0)  # -50 to 50
    
    # Side effects
    positive_outcomes = Column(JSON, nullable=True)  # Array of outcome strings
    negative_outcomes = Column(JSON, nullable=True)  # Array of outcome strings
    regional_impact = Column(JSON, nullable=True)  # Dict of regional impact metrics
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    crisis = relationship("DiplomaticCrisis", backref="interventions")


class CrisisEscalationTrigger(Base):
    """SQLAlchemy model for crisis escalation triggers."""
    
    __tablename__ = "crisis_escalation_triggers"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    crisis_id = Column(PGUUID(as_uuid=True), ForeignKey("diplomatic_crises.id"), nullable=False)
    trigger_type = Column(String(100), nullable=False)  # Type of escalating event
    description = Column(Text, nullable=False)
    
    # Trigger conditions
    triggering_event_id = Column(PGUUID(as_uuid=True), nullable=True)  # Related diplomatic event
    threshold_conditions = Column(JSON, nullable=True)  # Dict of threshold conditions
    faction_actions = Column(JSON, nullable=True)  # Dict mapping faction IDs to action arrays
    
    # Escalation effects
    escalation_increase = Column(Integer, nullable=False, default=10)  # 0-50
    affected_relationships = Column(ARRAY(String), nullable=True)  # Relationship IDs affected
    trigger_deadline = Column(DateTime, nullable=True)  # When this trigger expires
    
    # Mitigation
    prevention_actions = Column(JSON, nullable=True)  # Array of prevention action strings
    mitigation_cost = Column(Integer, nullable=False, default=0)
    responsible_factions = Column(ARRAY(String), nullable=True)  # Responsible faction IDs
    
    triggered = Column(Boolean, nullable=False, default=False)
    triggered_at = Column(DateTime, nullable=True)
    prevented = Column(Boolean, nullable=False, default=False)
    prevented_by = Column(PGUUID(as_uuid=True), nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationship
    crisis = relationship("DiplomaticCrisis", backref="escalation_triggers")


class CrisisImpactAssessment(Base):
    """SQLAlchemy model for crisis impact assessments."""
    
    __tablename__ = "crisis_impact_assessments"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    crisis_id = Column(PGUUID(as_uuid=True), ForeignKey("diplomatic_crises.id"), nullable=False)
    assessment_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    assessor_faction = Column(PGUUID(as_uuid=True), nullable=True)  # Who conducted this assessment
    
    # Impact categories (JSON dicts mapping faction IDs to impact scores 0-100)
    economic_impact = Column(JSON, nullable=True)  # Impact per faction
    political_impact = Column(JSON, nullable=True)  # Political stability impact per faction
    military_impact = Column(JSON, nullable=True)  # Military readiness impact per faction
    social_impact = Column(JSON, nullable=True)  # Population morale impact per faction
    
    # Regional effects
    trade_disruption = Column(Integer, nullable=False, default=0)  # 0-100
    refugee_displacement = Column(Integer, nullable=False, default=0)  # Number of refugees
    infrastructure_damage = Column(Integer, nullable=False, default=0)  # 0-100
    environmental_impact = Column(Integer, nullable=False, default=0)  # 0-100
    
    # Projections
    short_term_outlook = Column(String(100), nullable=False, default="uncertain")  # 1-30 days
    medium_term_outlook = Column(String(100), nullable=False, default="uncertain")  # 1-6 months
    long_term_outlook = Column(String(100), nullable=False, default="uncertain")  # 6+ months
    
    # Risk factors
    risk_of_escalation = Column(Integer, nullable=False, default=50)  # 0-100
    risk_of_spillover = Column(Integer, nullable=False, default=30)  # 0-100
    probability_of_resolution = Column(Integer, nullable=False, default=50)  # 0-100
    
    # Recommendations
    recommended_actions = Column(JSON, nullable=True)  # Array of action strings
    priority_interventions = Column(JSON, nullable=True)  # Array of intervention strings
    resources_needed = Column(JSON, nullable=True)  # Dict of resource requirements
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    crisis = relationship("DiplomaticCrisis", backref="impact_assessments") 