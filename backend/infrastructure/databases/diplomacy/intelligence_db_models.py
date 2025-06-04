"""
SQLAlchemy database models for diplomatic intelligence and espionage system.

This module contains the database table definitions that correspond to the
Pydantic models in intelligence_models.py.
"""

from uuid import uuid4
from datetime import datetime
from typing import List, Dict, Any, Optional, Union

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSON, ARRAY, ENUM as SQLEnum
from sqlalchemy.orm import relationship

from .diplomacy_models import Base  # Import Base from local diplomacy models
from backend.systems.diplomacy.models.intelligence_models import (
    IntelligenceType, EspionageOperationType, InformationWarfareType,
    OperationStatus, IntelligenceQuality, AgentStatus, NetworkSecurityLevel
)


class IntelligenceAgent(Base):
    """SQLAlchemy model for intelligence agents."""
    
    __tablename__ = "intelligence_agents"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    code_name = Column(String(100), nullable=False)
    faction_id = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Agent characteristics
    skill_level = Column(Integer, nullable=False, default=50)  # 0-100
    specialization = Column(SQLEnum(IntelligenceType), nullable=False)
    cover_identity = Column(Text, nullable=False)
    
    # Current assignment
    status = Column(SQLEnum(AgentStatus), nullable=False, default=AgentStatus.ACTIVE)
    current_assignment = Column(PGUUID(as_uuid=True), nullable=True)  # Current operation ID
    target_faction = Column(PGUUID(as_uuid=True), nullable=True)  # Faction being investigated
    location = Column(String(255), nullable=True)  # Current operational location
    
    # Operational history
    operations_completed = Column(Integer, nullable=False, default=0)
    successful_operations = Column(Integer, nullable=False, default=0)
    compromised_count = Column(Integer, nullable=False, default=0)
    
    # Attributes affecting performance
    loyalty = Column(Integer, nullable=False, default=80)  # 0-100
    stealth = Column(Integer, nullable=False, default=50)  # 0-100
    infiltration = Column(Integer, nullable=False, default=50)  # 0-100
    analysis = Column(Integer, nullable=False, default=50)  # 0-100
    
    # Security and risk
    security_clearance = Column(SQLEnum(NetworkSecurityLevel), nullable=False, default=NetworkSecurityLevel.RESTRICTED)
    cover_blown = Column(Boolean, nullable=False, default=False)
    last_contact = Column(DateTime, nullable=False, default=datetime.utcnow)
    burn_notice = Column(Boolean, nullable=False, default=False)
    
    # Timing
    recruited_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    last_mission_at = Column(DateTime, nullable=True)
    retirement_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class IntelligenceNetwork(Base):
    """SQLAlchemy model for intelligence networks."""
    
    __tablename__ = "intelligence_networks"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    controlling_faction = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Network composition
    agents = Column(ARRAY(String), nullable=True)  # Agent IDs in this network
    assets = Column(ARRAY(String), nullable=True)  # Non-agent intelligence sources
    safe_houses = Column(JSON, nullable=True)  # Array of secure locations
    
    # Network characteristics
    security_level = Column(SQLEnum(NetworkSecurityLevel), nullable=False, default=NetworkSecurityLevel.RESTRICTED)
    geographic_scope = Column(JSON, nullable=True)  # Array of regions of operation
    primary_targets = Column(ARRAY(String), nullable=True)  # Target faction IDs
    
    # Network health
    operational_status = Column(String(50), nullable=False, default="active")
    compromise_level = Column(Integer, nullable=False, default=0)  # 0-100
    effectiveness_rating = Column(Integer, nullable=False, default=50)  # 0-100
    
    # Operational metrics
    active_operations = Column(ARRAY(String), nullable=True)
    intelligence_gathered = Column(Integer, nullable=False, default=0)
    successful_missions = Column(Integer, nullable=False, default=0)
    blown_operations = Column(Integer, nullable=False, default=0)
    
    # Resources and funding
    budget = Column(Integer, nullable=False, default=10000)
    monthly_cost = Column(Integer, nullable=False, default=1000)
    equipment_level = Column(Integer, nullable=False, default=50)  # 0-100
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class IntelligenceOperation(Base):
    """SQLAlchemy model for intelligence operations."""
    
    __tablename__ = "intelligence_operations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    operation_name = Column(String(255), nullable=False)
    operation_type = Column(String(100), nullable=False)  # Union type stored as string
    
    # Operation details
    description = Column(Text, nullable=False)
    objectives = Column(JSON, nullable=False)  # Array of objective strings
    target_faction = Column(PGUUID(as_uuid=True), nullable=False)
    executing_faction = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Resources assigned
    assigned_agents = Column(ARRAY(String), nullable=True)  # Agent IDs
    assigned_network = Column(PGUUID(as_uuid=True), nullable=True)
    budget_allocated = Column(Integer, nullable=False, default=1000)
    
    # Operation parameters
    status = Column(SQLEnum(OperationStatus), nullable=False, default=OperationStatus.PLANNING)
    priority_level = Column(String(20), nullable=False, default="medium")
    security_classification = Column(SQLEnum(NetworkSecurityLevel), nullable=False, default=NetworkSecurityLevel.RESTRICTED)
    
    # Timing and planning
    planned_start = Column(DateTime, nullable=False, default=datetime.utcnow)
    planned_duration = Column(Integer, nullable=False, default=30)  # Days
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    deadline = Column(DateTime, nullable=True)
    
    # Success metrics
    success_probability = Column(Integer, nullable=False, default=50)  # 0-100
    detection_risk = Column(Integer, nullable=False, default=30)  # 0-100
    political_risk = Column(Integer, nullable=False, default=20)  # 0-100
    
    # Operation requirements
    required_skills = Column(JSON, nullable=True)  # Array of IntelligenceType strings
    required_clearance = Column(SQLEnum(NetworkSecurityLevel), nullable=False, default=NetworkSecurityLevel.RESTRICTED)
    cover_story = Column(Text, nullable=True)
    extraction_plan = Column(Text, nullable=True)
    
    # Results and outcomes
    intelligence_gathered = Column(ARRAY(String), nullable=True)  # Intelligence report IDs
    operation_result = Column(String(50), nullable=True)
    casualties = Column(Integer, nullable=False, default=0)
    collateral_damage = Column(Text, nullable=True)
    
    # Cost tracking
    actual_cost = Column(Integer, nullable=False, default=0)
    political_cost = Column(Integer, nullable=False, default=0)  # 0-100
    reputation_impact = Column(Integer, nullable=False, default=0)  # -50 to 50
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class IntelligenceReport(Base):
    """SQLAlchemy model for intelligence reports."""
    
    __tablename__ = "intelligence_reports"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    report_title = Column(String(255), nullable=False)
    intelligence_type = Column(SQLEnum(IntelligenceType), nullable=False)
    
    # Source information
    source_operation = Column(PGUUID(as_uuid=True), nullable=True)
    source_agent = Column(PGUUID(as_uuid=True), nullable=True)
    source_network = Column(PGUUID(as_uuid=True), nullable=True)
    source_faction = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Target information
    target_faction = Column(PGUUID(as_uuid=True), nullable=False)
    related_factions = Column(ARRAY(String), nullable=True)
    
    # Intelligence content
    content = Column(Text, nullable=False)
    supporting_evidence = Column(JSON, nullable=True)  # Array of evidence strings
    key_findings = Column(JSON, nullable=True)  # Array of finding strings
    actionable_insights = Column(JSON, nullable=True)  # Array of insight strings
    
    # Quality and reliability
    quality = Column(SQLEnum(IntelligenceQuality), nullable=False, default=IntelligenceQuality.UNKNOWN)
    confidence_level = Column(Integer, nullable=False, default=50)  # 0-100
    corroboration_sources = Column(Integer, nullable=False, default=1)
    
    # Timing and relevance
    intelligence_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    expiration_date = Column(DateTime, nullable=True)
    urgency_level = Column(String(20), nullable=False, default="normal")
    
    # Classification and sharing
    classification_level = Column(SQLEnum(NetworkSecurityLevel), nullable=False, default=NetworkSecurityLevel.RESTRICTED)
    shared_with = Column(ARRAY(String), nullable=True)  # Faction IDs with access
    sharing_restrictions = Column(JSON, nullable=True)  # Array of restriction strings
    
    # Impact assessment
    strategic_value = Column(Integer, nullable=False, default=50)  # 0-100
    operational_impact = Column(Text, nullable=True)
    recommended_actions = Column(JSON, nullable=True)  # Array of action strings
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class CounterIntelligenceOperation(Base):
    """SQLAlchemy model for counter-intelligence operations."""
    
    __tablename__ = "counter_intelligence_operations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    operation_name = Column(String(255), nullable=False)
    defending_faction = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Operation focus
    protection_scope = Column(JSON, nullable=True)  # Array of protection area strings
    suspected_threats = Column(ARRAY(String), nullable=True)  # Suspected hostile faction IDs
    threat_level = Column(String(20), nullable=False, default="medium")
    
    # Counter-intel methods
    security_measures = Column(JSON, nullable=True)  # Array of security measure strings
    surveillance_activities = Column(JSON, nullable=True)  # Array of surveillance activity strings
    deception_operations = Column(JSON, nullable=True)  # Array of deception operation strings
    
    # Status and results
    status = Column(SQLEnum(OperationStatus), nullable=False, default=OperationStatus.PLANNING)
    threats_detected = Column(ARRAY(String), nullable=True)  # Detected enemy operation IDs
    agents_caught = Column(ARRAY(String), nullable=True)  # Captured enemy agent IDs
    leaks_prevented = Column(Integer, nullable=False, default=0)
    
    # Resources
    assigned_personnel = Column(ARRAY(String), nullable=True)  # Personnel IDs
    budget = Column(Integer, nullable=False, default=5000)
    
    # Timing
    start_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class InformationWarfareOperation(Base):
    """SQLAlchemy model for information warfare operations."""
    
    __tablename__ = "information_warfare_operations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_name = Column(String(255), nullable=False)
    operation_type = Column(SQLEnum(InformationWarfareType), nullable=False)
    
    # Campaign details
    executing_faction = Column(PGUUID(as_uuid=True), nullable=False)
    target_factions = Column(ARRAY(String), nullable=False)  # Target faction IDs
    target_audience = Column(JSON, nullable=True)  # Array of audience descriptions
    
    # Campaign messaging
    primary_message = Column(Text, nullable=False)
    key_narratives = Column(JSON, nullable=True)  # Array of narrative strings
    propaganda_materials = Column(JSON, nullable=True)  # Array of material descriptions
    
    # Distribution channels
    media_channels = Column(JSON, nullable=True)  # Array of media channel strings
    social_networks = Column(JSON, nullable=True)  # Array of social network strings
    diplomatic_channels = Column(JSON, nullable=True)  # Array of diplomatic channel strings
    
    # Operation parameters
    status = Column(SQLEnum(OperationStatus), nullable=False, default=OperationStatus.PLANNING)
    intensity_level = Column(String(20), nullable=False, default="medium")
    duration = Column(Integer, nullable=False, default=60)  # Days
    
    # Metrics and effectiveness
    reach_estimate = Column(Integer, nullable=False, default=10000)
    effectiveness_score = Column(Integer, nullable=True)  # 0-100
    counter_narratives_encountered = Column(JSON, nullable=True)  # Array of counter-narrative strings
    
    # Impact tracking
    reputation_changes = Column(JSON, nullable=True)  # Dict mapping faction IDs to reputation deltas
    relationship_impacts = Column(JSON, nullable=True)  # Dict mapping relationship IDs to changes
    public_opinion_shifts = Column(JSON, nullable=True)  # Dict mapping topics to opinion changes
    
    # Resources and costs
    budget = Column(Integer, nullable=False, default=5000)
    personnel_assigned = Column(ARRAY(String), nullable=True)  # Personnel IDs
    
    # Timing
    launch_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    peak_activity_period = Column(JSON, nullable=True)  # Dict with start/end datetime strings
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class IntelligenceAssessment(Base):
    """SQLAlchemy model for intelligence assessments."""
    
    __tablename__ = "intelligence_assessments"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    assessment_title = Column(String(255), nullable=False)
    assessing_faction = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Assessment scope
    intelligence_reports = Column(ARRAY(String), nullable=False)  # Report IDs being analyzed
    assessment_focus = Column(JSON, nullable=True)  # Array of focus area strings
    time_period = Column(JSON, nullable=True)  # Dict with start/end datetime strings
    
    # Analysis results
    key_insights = Column(JSON, nullable=True)  # Array of insight strings
    threat_assessment = Column(JSON, nullable=True)  # Dict mapping faction IDs to threat levels
    opportunity_assessment = Column(JSON, nullable=True)  # Dict mapping opportunities to descriptions
    
    # Predictions and forecasts
    short_term_predictions = Column(JSON, nullable=True)  # Array of prediction strings (1-30 days)
    medium_term_predictions = Column(JSON, nullable=True)  # Array of prediction strings (1-6 months)
    long_term_predictions = Column(JSON, nullable=True)  # Array of prediction strings (6+ months)
    
    # Confidence and reliability
    overall_confidence = Column(Integer, nullable=False, default=50)  # 0-100
    intelligence_gaps = Column(JSON, nullable=True)  # Array of gap description strings
    contradicting_reports = Column(ARRAY(String), nullable=True)  # Report IDs that contradict
    
    # Recommendations
    strategic_recommendations = Column(JSON, nullable=True)  # Array of strategic recommendation strings
    tactical_recommendations = Column(JSON, nullable=True)  # Array of tactical recommendation strings
    intelligence_priorities = Column(JSON, nullable=True)  # Array of priority investigation strings
    
    # Classification and distribution
    classification_level = Column(SQLEnum(NetworkSecurityLevel), nullable=False, default=NetworkSecurityLevel.CLASSIFIED)
    distribution_list = Column(ARRAY(String), nullable=True)  # Faction decision-maker IDs
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class SecurityBreach(Base):
    """SQLAlchemy model for security breaches."""
    
    __tablename__ = "security_breaches"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    breach_type = Column(String(100), nullable=False)
    affected_faction = Column(PGUUID(as_uuid=True), nullable=False)
    
    # Breach details
    description = Column(Text, nullable=False)
    discovery_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    estimated_breach_date = Column(DateTime, nullable=True)
    
    # Impact assessment
    compromised_operations = Column(ARRAY(String), nullable=True)  # Operation IDs
    compromised_agents = Column(ARRAY(String), nullable=True)  # Agent IDs
    compromised_intelligence = Column(ARRAY(String), nullable=True)  # Intelligence report IDs
    compromised_networks = Column(ARRAY(String), nullable=True)  # Network IDs
    
    # Breach source
    perpetrating_faction = Column(PGUUID(as_uuid=True), nullable=True)
    breach_method = Column(String(255), nullable=True)
    insider_threat = Column(Boolean, nullable=False, default=False)
    
    # Response and mitigation
    containment_actions = Column(JSON, nullable=True)  # Array of containment action strings
    mitigation_measures = Column(JSON, nullable=True)  # Array of mitigation measure strings
    lessons_learned = Column(JSON, nullable=True)  # Array of lesson strings
    
    # Status tracking
    status = Column(String(50), nullable=False, default="investigating")
    damage_assessment = Column(Text, nullable=True)
    
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow) 