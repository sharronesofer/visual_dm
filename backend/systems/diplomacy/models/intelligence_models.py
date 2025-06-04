"""
Pydantic models for diplomatic intelligence and espionage system.

This module defines the data structures for intelligence operations, espionage activities,
information warfare, and all related components of the diplomatic intelligence system.
"""

from enum import Enum
from typing import List, Dict, Optional, Union, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from pydantic import BaseModel, Field, validator


class IntelligenceType(str, Enum):
    """Types of intelligence that can be gathered."""
    DIPLOMATIC_RECONNAISSANCE = "diplomatic_reconnaissance"
    TREATY_INTELLIGENCE = "treaty_intelligence"
    MILITARY_INTELLIGENCE = "military_intelligence"
    ECONOMIC_INTELLIGENCE = "economic_intelligence"
    LEADERSHIP_INTELLIGENCE = "leadership_intelligence"
    FACTION_CAPABILITIES = "faction_capabilities"
    SECRET_NEGOTIATIONS = "secret_negotiations"
    ALLIANCE_PLANS = "alliance_plans"
    TRADE_ROUTE_INFO = "trade_route_info"
    RESOURCE_LOCATIONS = "resource_locations"


class EspionageOperationType(str, Enum):
    """Types of espionage operations."""
    INFILTRATION = "infiltration"
    COMMUNICATION_INTERCEPTION = "communication_interception"
    SABOTAGE = "sabotage"
    DISINFORMATION = "disinformation"
    COUNTER_INTELLIGENCE = "counter_intelligence"
    SURVEILLANCE = "surveillance"
    RECRUITMENT = "recruitment"
    EXTRACTION = "extraction"
    ASSASSINATION = "assassination"
    THEFT = "theft"


class InformationWarfareType(str, Enum):
    """Types of information warfare operations."""
    PROPAGANDA_CAMPAIGN = "propaganda_campaign"
    REPUTATION_ATTACK = "reputation_attack"
    ALLIANCE_DISRUPTION = "alliance_disruption"
    FALSE_FLAG_OPERATION = "false_flag_operation"
    DIPLOMATIC_BLACKMAIL = "diplomatic_blackmail"
    MEDIA_MANIPULATION = "media_manipulation"
    MISINFORMATION_SPREAD = "misinformation_spread"
    CULTURAL_SUBVERSION = "cultural_subversion"


class OperationStatus(str, Enum):
    """Status of intelligence operations."""
    PLANNING = "planning"
    APPROVED = "approved"
    ACTIVE = "active"
    INFILTRATING = "infiltrating"
    EXECUTING = "executing"
    EXTRACTING = "extracting"
    COMPLETED = "completed"
    COMPROMISED = "compromised"
    FAILED = "failed"
    CANCELLED = "cancelled"
    SUSPENDED = "suspended"


class IntelligenceQuality(str, Enum):
    """Quality/reliability ratings for intelligence."""
    CONFIRMED = "confirmed"          # Multiple reliable sources
    PROBABLE = "probable"            # Single reliable source
    POSSIBLE = "possible"            # Unconfirmed but plausible
    DOUBTFUL = "doubtful"           # Questionable reliability
    FABRICATED = "fabricated"       # Known to be false
    UNKNOWN = "unknown"             # Unable to verify


class AgentStatus(str, Enum):
    """Status of intelligence agents."""
    ACTIVE = "active"
    DEEP_COVER = "deep_cover"
    COMPROMISED = "compromised"
    EXTRACTED = "extracted"
    TURNED = "turned"              # Became double agent
    MISSING = "missing"
    CAPTURED = "captured"
    ELIMINATED = "eliminated"
    RETIRED = "retired"


class NetworkSecurityLevel(str, Enum):
    """Security levels for intelligence networks."""
    OPEN = "open"                  # Minimal security
    RESTRICTED = "restricted"      # Basic operational security
    CLASSIFIED = "classified"      # High security protocols
    TOP_SECRET = "top_secret"      # Maximum security
    COMPARTMENTALIZED = "compartmentalized"  # Need-to-know basis only


class IntelligenceAgent(BaseModel):
    """An intelligence agent working for a faction."""
    id: UUID = Field(default_factory=uuid4)
    code_name: str = Field(..., min_length=1, max_length=100)
    faction_id: UUID  # Controlling faction
    
    # Agent characteristics
    skill_level: int = Field(default=50, ge=0, le=100)  # Overall competence
    specialization: IntelligenceType = Field(...) # Primary expertise area
    cover_identity: str = Field(..., min_length=1)  # False identity/role
    
    # Current assignment
    status: AgentStatus = AgentStatus.ACTIVE
    current_assignment: Optional[UUID] = None  # Current operation ID
    target_faction: Optional[UUID] = None  # Faction being investigated/infiltrated
    location: Optional[str] = None  # Current operational location
    
    # Operational history
    operations_completed: int = Field(default=0, ge=0)
    successful_operations: int = Field(default=0, ge=0)
    compromised_count: int = Field(default=0, ge=0)
    
    # Attributes affecting performance
    loyalty: int = Field(default=80, ge=0, le=100)  # Likelihood to defect
    stealth: int = Field(default=50, ge=0, le=100)  # Ability to avoid detection
    infiltration: int = Field(default=50, ge=0, le=100)  # Ability to gain access
    analysis: int = Field(default=50, ge=0, le=100)  # Intelligence evaluation skill
    
    # Security and risk
    security_clearance: NetworkSecurityLevel = NetworkSecurityLevel.RESTRICTED
    cover_blown: bool = False
    last_contact: datetime = Field(default_factory=datetime.utcnow)
    burn_notice: bool = False  # Agent marked for elimination/disavowal
    
    # Timing
    recruited_at: datetime = Field(default_factory=datetime.utcnow)
    last_mission_at: Optional[datetime] = None
    retirement_date: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IntelligenceNetwork(BaseModel):
    """A network of intelligence assets and agents."""
    id: UUID = Field(default_factory=uuid4)
    name: str = Field(..., min_length=1, max_length=255)
    controlling_faction: UUID
    
    # Network composition
    agents: List[UUID] = Field(default_factory=list)  # Agent IDs in this network
    assets: List[UUID] = Field(default_factory=list)  # Non-agent intelligence sources
    safe_houses: List[str] = Field(default_factory=list)  # Secure locations
    
    # Network characteristics
    security_level: NetworkSecurityLevel = NetworkSecurityLevel.RESTRICTED
    geographic_scope: List[str] = Field(default_factory=list)  # Regions of operation
    primary_targets: List[UUID] = Field(default_factory=list)  # Target faction IDs
    
    # Network health
    operational_status: str = Field(default="active")  # active, compromised, dormant, disbanded
    compromise_level: int = Field(default=0, ge=0, le=100)  # How much is blown
    effectiveness_rating: int = Field(default=50, ge=0, le=100)
    
    # Operational metrics
    active_operations: List[UUID] = Field(default_factory=list)
    intelligence_gathered: int = Field(default=0, ge=0)
    successful_missions: int = Field(default=0, ge=0)
    blown_operations: int = Field(default=0, ge=0)
    
    # Resources and funding
    budget: int = Field(default=10000, ge=0)  # Operating budget
    monthly_cost: int = Field(default=1000, ge=0)  # Maintenance cost
    equipment_level: int = Field(default=50, ge=0, le=100)  # Quality of tools/tech
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IntelligenceOperation(BaseModel):
    """A specific intelligence gathering or espionage operation."""
    id: UUID = Field(default_factory=uuid4)
    operation_name: str = Field(..., min_length=1, max_length=255)
    operation_type: Union[IntelligenceType, EspionageOperationType, InformationWarfareType]
    
    # Operation details
    description: str = Field(..., min_length=1)
    objectives: List[str] = Field(..., min_items=1)
    target_faction: UUID
    executing_faction: UUID
    
    # Resources assigned
    assigned_agents: List[UUID] = Field(default_factory=list)
    assigned_network: Optional[UUID] = None
    budget_allocated: int = Field(default=1000, ge=0)
    
    # Operation parameters
    status: OperationStatus = OperationStatus.PLANNING
    priority_level: str = Field(default="medium")  # low, medium, high, critical
    security_classification: NetworkSecurityLevel = NetworkSecurityLevel.RESTRICTED
    
    # Timing and planning
    planned_start: datetime = Field(default_factory=datetime.utcnow)
    planned_duration: int = Field(default=30, ge=1)  # Days
    actual_start: Optional[datetime] = None
    actual_end: Optional[datetime] = None
    deadline: Optional[datetime] = None
    
    # Success metrics
    success_probability: int = Field(default=50, ge=0, le=100)
    detection_risk: int = Field(default=30, ge=0, le=100)
    political_risk: int = Field(default=20, ge=0, le=100)  # Diplomatic consequences
    
    # Operation requirements
    required_skills: List[IntelligenceType] = Field(default_factory=list)
    required_clearance: NetworkSecurityLevel = NetworkSecurityLevel.RESTRICTED
    cover_story: Optional[str] = None
    extraction_plan: Optional[str] = None
    
    # Results and outcomes
    intelligence_gathered: List[UUID] = Field(default_factory=list)  # Intelligence report IDs
    operation_result: Optional[str] = None  # success, partial_success, failure, compromised
    casualties: int = Field(default=0, ge=0)  # Agents lost/compromised
    collateral_damage: Optional[str] = None
    
    # Cost tracking
    actual_cost: int = Field(default=0, ge=0)
    political_cost: int = Field(default=0, ge=0, le=100)  # Diplomatic fallout
    reputation_impact: int = Field(default=0, ge=-50, le=50)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IntelligenceReport(BaseModel):
    """A piece of intelligence gathered from operations."""
    id: UUID = Field(default_factory=uuid4)
    report_title: str = Field(..., min_length=1, max_length=255)
    intelligence_type: IntelligenceType
    
    # Source information
    source_operation: Optional[UUID] = None  # Operation that gathered this
    source_agent: Optional[UUID] = None  # Agent who gathered this
    source_network: Optional[UUID] = None  # Network that provided this
    source_faction: UUID  # Faction that gathered the intelligence
    
    # Target information
    target_faction: UUID  # Faction this intelligence is about
    related_factions: List[UUID] = Field(default_factory=list)  # Other involved factions
    
    # Intelligence content
    content: str = Field(..., min_length=1)  # The actual intelligence information
    supporting_evidence: List[str] = Field(default_factory=list)
    key_findings: List[str] = Field(default_factory=list)
    actionable_insights: List[str] = Field(default_factory=list)
    
    # Quality and reliability
    quality: IntelligenceQuality = IntelligenceQuality.UNKNOWN
    confidence_level: int = Field(default=50, ge=0, le=100)
    corroboration_sources: int = Field(default=1, ge=1)  # Number of confirming sources
    
    # Timing and relevance
    intelligence_date: datetime = Field(default_factory=datetime.utcnow)  # When info was current
    expiration_date: Optional[datetime] = None  # When info becomes stale
    urgency_level: str = Field(default="normal")  # immediate, urgent, normal, routine
    
    # Classification and sharing
    classification_level: NetworkSecurityLevel = NetworkSecurityLevel.RESTRICTED
    shared_with: List[UUID] = Field(default_factory=list)  # Faction IDs that have access
    sharing_restrictions: List[str] = Field(default_factory=list)
    
    # Impact assessment
    strategic_value: int = Field(default=50, ge=0, le=100)
    operational_impact: Optional[str] = None
    recommended_actions: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @validator('expiration_date')
    def validate_expiration_after_intelligence_date(cls, v, values):
        if v and 'intelligence_date' in values and v <= values['intelligence_date']:
            raise ValueError('Expiration date must be after intelligence date')
        return v


class CounterIntelligenceOperation(BaseModel):
    """Operations to protect against enemy espionage."""
    id: UUID = Field(default_factory=uuid4)
    operation_name: str = Field(..., min_length=1, max_length=255)
    defending_faction: UUID
    
    # Operation focus
    protection_scope: List[str] = Field(default_factory=list)  # What is being protected
    suspected_threats: List[UUID] = Field(default_factory=list)  # Suspected hostile factions
    threat_level: str = Field(default="medium")  # low, medium, high, critical
    
    # Counter-intel methods
    security_measures: List[str] = Field(default_factory=list)
    surveillance_activities: List[str] = Field(default_factory=list)
    deception_operations: List[str] = Field(default_factory=list)
    
    # Status and results
    status: OperationStatus = OperationStatus.PLANNING
    threats_detected: List[UUID] = Field(default_factory=list)  # Detected enemy operations
    agents_caught: List[UUID] = Field(default_factory=list)  # Captured enemy agents
    leaks_prevented: int = Field(default=0, ge=0)
    
    # Resources
    assigned_personnel: List[UUID] = Field(default_factory=list)
    budget: int = Field(default=5000, ge=0)
    
    # Timing
    start_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InformationWarfareOperation(BaseModel):
    """Information warfare and propaganda operations."""
    id: UUID = Field(default_factory=uuid4)
    campaign_name: str = Field(..., min_length=1, max_length=255)
    operation_type: InformationWarfareType
    
    # Campaign details
    executing_faction: UUID
    target_factions: List[UUID] = Field(..., min_items=1)
    target_audience: List[str] = Field(default_factory=list)  # Who is being influenced
    
    # Campaign messaging
    primary_message: str = Field(..., min_length=1)
    key_narratives: List[str] = Field(default_factory=list)
    propaganda_materials: List[str] = Field(default_factory=list)
    
    # Distribution channels
    media_channels: List[str] = Field(default_factory=list)
    social_networks: List[str] = Field(default_factory=list)
    diplomatic_channels: List[str] = Field(default_factory=list)
    
    # Operation parameters
    status: OperationStatus = OperationStatus.PLANNING
    intensity_level: str = Field(default="medium")  # subtle, medium, aggressive, overwhelming
    duration: int = Field(default=60, ge=1)  # Days
    
    # Metrics and effectiveness
    reach_estimate: int = Field(default=10000, ge=0)  # Number of people reached
    effectiveness_score: Optional[int] = None  # 0-100 based on results
    counter_narratives_encountered: List[str] = Field(default_factory=list)
    
    # Impact tracking
    reputation_changes: Dict[UUID, int] = Field(default_factory=dict)  # Faction reputation deltas
    relationship_impacts: Dict[str, int] = Field(default_factory=dict)  # Relationship changes
    public_opinion_shifts: Dict[str, int] = Field(default_factory=dict)
    
    # Resources and costs
    budget: int = Field(default=5000, ge=0)
    personnel_assigned: List[UUID] = Field(default_factory=list)
    
    # Timing
    launch_date: datetime = Field(default_factory=datetime.utcnow)
    end_date: Optional[datetime] = None
    peak_activity_period: Optional[Dict[str, datetime]] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class IntelligenceAssessment(BaseModel):
    """Analysis and assessment of gathered intelligence."""
    id: UUID = Field(default_factory=uuid4)
    assessment_title: str = Field(..., min_length=1, max_length=255)
    assessing_faction: UUID
    
    # Assessment scope
    intelligence_reports: List[UUID] = Field(..., min_items=1)  # Reports being analyzed
    assessment_focus: List[str] = Field(default_factory=list)  # Specific areas of focus
    time_period: Dict[str, datetime] = Field(default_factory=dict)  # start/end dates
    
    # Analysis results
    key_insights: List[str] = Field(default_factory=list)
    threat_assessment: Dict[UUID, str] = Field(default_factory=dict)  # Faction threat levels
    opportunity_assessment: Dict[str, str] = Field(default_factory=dict)
    
    # Predictions and forecasts
    short_term_predictions: List[str] = Field(default_factory=list)  # 1-30 days
    medium_term_predictions: List[str] = Field(default_factory=list)  # 1-6 months
    long_term_predictions: List[str] = Field(default_factory=list)  # 6+ months
    
    # Confidence and reliability
    overall_confidence: int = Field(default=50, ge=0, le=100)
    intelligence_gaps: List[str] = Field(default_factory=list)  # Missing information
    contradicting_reports: List[UUID] = Field(default_factory=list)
    
    # Recommendations
    strategic_recommendations: List[str] = Field(default_factory=list)
    tactical_recommendations: List[str] = Field(default_factory=list)
    intelligence_priorities: List[str] = Field(default_factory=list)  # What to investigate next
    
    # Classification and distribution
    classification_level: NetworkSecurityLevel = NetworkSecurityLevel.CLASSIFIED
    distribution_list: List[UUID] = Field(default_factory=list)  # Faction decision-makers
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class SecurityBreach(BaseModel):
    """Record of security breaches and intelligence compromises."""
    id: UUID = Field(default_factory=uuid4)
    breach_type: str = Field(..., min_length=1)  # Type of security failure
    affected_faction: UUID
    
    # Breach details
    description: str = Field(..., min_length=1)
    discovery_date: datetime = Field(default_factory=datetime.utcnow)
    estimated_breach_date: Optional[datetime] = None  # When breach actually occurred
    
    # Impact assessment
    compromised_operations: List[UUID] = Field(default_factory=list)
    compromised_agents: List[UUID] = Field(default_factory=list)
    compromised_intelligence: List[UUID] = Field(default_factory=list)
    compromised_networks: List[UUID] = Field(default_factory=list)
    
    # Breach source
    perpetrating_faction: Optional[UUID] = None  # If known who did it
    breach_method: Optional[str] = None  # How the breach occurred
    insider_threat: bool = False  # Whether it was an inside job
    
    # Response and mitigation
    containment_actions: List[str] = Field(default_factory=list)
    mitigation_measures: List[str] = Field(default_factory=list)
    lessons_learned: List[str] = Field(default_factory=list)
    
    # Status tracking
    status: str = Field(default="investigating")  # investigating, contained, mitigated, closed
    damage_assessment: Optional[str] = None  # Overall impact evaluation
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow) 