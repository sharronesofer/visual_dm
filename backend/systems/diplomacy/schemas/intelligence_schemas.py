"""
API request and response schemas for diplomatic intelligence and espionage system.

This module defines the Pydantic schemas used for REST API endpoints
related to intelligence operations, agents, networks, and reports.
"""

from typing import List, Dict, Optional, Any, Union
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field

from ..models.intelligence_models import (
    IntelligenceType, EspionageOperationType, InformationWarfareType,
    OperationStatus, IntelligenceQuality, AgentStatus, NetworkSecurityLevel
)


# Request Schemas

class RecruitAgentRequest(BaseModel):
    """Request schema for recruiting a new intelligence agent"""
    specialization: IntelligenceType = Field(..., description="Agent's area of expertise")
    skill_level: Optional[int] = Field(None, ge=0, le=100, description="Initial skill level (auto-generated if not provided)")
    
    class Config:
        schema_extra = {
            "example": {
                "specialization": "diplomatic_reconnaissance",
                "skill_level": 65
            }
        }


class CreateIntelligenceOperationRequest(BaseModel):
    """Request schema for creating an intelligence operation"""
    operation_type: Union[IntelligenceType, EspionageOperationType] = Field(..., description="Type of intelligence operation")
    target_faction: UUID = Field(..., description="Faction being targeted for intelligence gathering")
    objectives: List[str] = Field(..., min_items=1, description="Specific objectives of the operation")
    assigned_agents: Optional[List[UUID]] = Field(default=[], description="Agent IDs to assign to this operation")
    budget_allocated: Optional[int] = Field(default=1000, ge=0, description="Budget allocated for the operation")
    priority_level: Optional[str] = Field(default="medium", description="Priority level: low, medium, high, critical")
    
    class Config:
        schema_extra = {
            "example": {
                "operation_type": "diplomatic_reconnaissance",
                "target_faction": "123e4567-e89b-12d3-a456-426614174000",
                "objectives": [
                    "Gather intelligence on upcoming treaty negotiations",
                    "Identify key decision makers in target faction"
                ],
                "assigned_agents": ["987fcdeb-51a2-43d1-b345-426614174001"],
                "budget_allocated": 5000,
                "priority_level": "high"
            }
        }


class CreateCounterIntelligenceRequest(BaseModel):
    """Request schema for creating a counter-intelligence operation"""
    suspected_threats: List[UUID] = Field(..., description="Faction IDs suspected of hostile intelligence operations")
    protection_scope: List[str] = Field(..., description="Areas/assets to protect")
    threat_level: Optional[str] = Field(default="medium", description="Assessed threat level: low, medium, high, critical")
    
    class Config:
        schema_extra = {
            "example": {
                "suspected_threats": ["123e4567-e89b-12d3-a456-426614174000"],
                "protection_scope": [
                    "Diplomatic communications",
                    "Treaty negotiations",
                    "Military intelligence"
                ],
                "threat_level": "high"
            }
        }


class CreateInformationWarfareRequest(BaseModel):
    """Request schema for creating an information warfare campaign"""
    operation_type: InformationWarfareType = Field(..., description="Type of information warfare operation")
    target_factions: List[UUID] = Field(..., min_items=1, description="Factions being targeted by the campaign")
    primary_message: str = Field(..., min_length=1, description="Main message of the campaign")
    target_audience: Optional[List[str]] = Field(default=[], description="Specific audiences to target")
    intensity_level: Optional[str] = Field(default="medium", description="Campaign intensity: subtle, medium, aggressive, overwhelming")
    duration: Optional[int] = Field(default=60, ge=1, description="Campaign duration in days")
    
    class Config:
        schema_extra = {
            "example": {
                "operation_type": "reputation_attack",
                "target_factions": ["123e4567-e89b-12d3-a456-426614174000"],
                "primary_message": "Target faction's recent policies are destabilizing the region",
                "target_audience": ["Diplomatic community", "Allied nations"],
                "intensity_level": "aggressive",
                "duration": 30
            }
        }


class CreateIntelligenceNetworkRequest(BaseModel):
    """Request schema for creating an intelligence network"""
    name: str = Field(..., min_length=1, max_length=255, description="Name of the intelligence network")
    geographic_scope: List[str] = Field(..., description="Geographic regions where the network operates")
    security_level: Optional[NetworkSecurityLevel] = Field(default=NetworkSecurityLevel.RESTRICTED, description="Security classification level")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Northern Watch Network",
                "geographic_scope": ["Northern Territories", "Border Regions"],
                "security_level": "classified"
            }
        }


class GenerateAssessmentRequest(BaseModel):
    """Request schema for generating an intelligence assessment"""
    intelligence_reports: List[UUID] = Field(..., min_items=1, description="Intelligence report IDs to analyze")
    assessment_focus: Optional[List[str]] = Field(default=[], description="Specific areas to focus the assessment on")
    
    class Config:
        schema_extra = {
            "example": {
                "intelligence_reports": [
                    "123e4567-e89b-12d3-a456-426614174000",
                    "987fcdeb-51a2-43d1-b345-426614174001"
                ],
                "assessment_focus": ["Military capabilities", "Economic vulnerabilities"]
            }
        }


class ExecuteOperationRequest(BaseModel):
    """Request schema for executing an operation"""
    operation_id: UUID = Field(..., description="ID of the operation to execute")
    
    class Config:
        schema_extra = {
            "example": {
                "operation_id": "123e4567-e89b-12d3-a456-426614174000"
            }
        }


# Response Schemas

class AgentResponse(BaseModel):
    """Response schema for intelligence agent data"""
    id: UUID
    code_name: str
    faction_id: UUID
    specialization: IntelligenceType
    skill_level: int
    cover_identity: str
    status: AgentStatus
    current_assignment: Optional[UUID]
    target_faction: Optional[UUID]
    location: Optional[str]
    operations_completed: int
    successful_operations: int
    compromised_count: int
    loyalty: int
    stealth: int
    infiltration: int
    analysis: int
    security_clearance: NetworkSecurityLevel
    cover_blown: bool
    burn_notice: bool
    recruited_at: datetime
    last_mission_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IntelligenceOperationResponse(BaseModel):
    """Response schema for intelligence operations"""
    id: UUID
    operation_name: str
    operation_type: str
    description: str
    objectives: List[str]
    target_faction: UUID
    executing_faction: UUID
    assigned_agents: List[UUID]
    assigned_network: Optional[UUID]
    budget_allocated: int
    status: OperationStatus
    priority_level: str
    security_classification: NetworkSecurityLevel
    planned_start: datetime
    planned_duration: int
    actual_start: Optional[datetime]
    actual_end: Optional[datetime]
    deadline: Optional[datetime]
    success_probability: int
    detection_risk: int
    political_risk: int
    intelligence_gathered: List[UUID]
    operation_result: Optional[str]
    casualties: int
    actual_cost: int
    political_cost: int
    reputation_impact: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IntelligenceReportResponse(BaseModel):
    """Response schema for intelligence reports"""
    id: UUID
    report_title: str
    intelligence_type: IntelligenceType
    source_operation: Optional[UUID]
    source_agent: Optional[UUID]
    source_network: Optional[UUID]
    source_faction: UUID
    target_faction: UUID
    related_factions: List[UUID]
    content: str
    supporting_evidence: List[str]
    key_findings: List[str]
    actionable_insights: List[str]
    quality: IntelligenceQuality
    confidence_level: int
    corroboration_sources: int
    intelligence_date: datetime
    expiration_date: Optional[datetime]
    urgency_level: str
    classification_level: NetworkSecurityLevel
    shared_with: List[UUID]
    sharing_restrictions: List[str]
    strategic_value: int
    operational_impact: Optional[str]
    recommended_actions: List[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CounterIntelligenceOperationResponse(BaseModel):
    """Response schema for counter-intelligence operations"""
    id: UUID
    operation_name: str
    defending_faction: UUID
    protection_scope: List[str]
    suspected_threats: List[UUID]
    threat_level: str
    security_measures: List[str]
    surveillance_activities: List[str]
    deception_operations: List[str]
    status: OperationStatus
    threats_detected: List[UUID]
    agents_caught: List[UUID]
    leaks_prevented: int
    assigned_personnel: List[UUID]
    budget: int
    start_date: datetime
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InformationWarfareOperationResponse(BaseModel):
    """Response schema for information warfare operations"""
    id: UUID
    campaign_name: str
    operation_type: InformationWarfareType
    executing_faction: UUID
    target_factions: List[UUID]
    target_audience: List[str]
    primary_message: str
    key_narratives: List[str]
    propaganda_materials: List[str]
    media_channels: List[str]
    social_networks: List[str]
    diplomatic_channels: List[str]
    status: OperationStatus
    intensity_level: str
    duration: int
    reach_estimate: int
    effectiveness_score: Optional[int]
    counter_narratives_encountered: List[str]
    reputation_changes: Dict[UUID, int]
    relationship_impacts: Dict[str, int]
    public_opinion_shifts: Dict[str, int]
    budget: int
    personnel_assigned: List[UUID]
    launch_date: datetime
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IntelligenceNetworkResponse(BaseModel):
    """Response schema for intelligence networks"""
    id: UUID
    name: str
    controlling_faction: UUID
    agents: List[UUID]
    assets: List[UUID]
    safe_houses: List[str]
    security_level: NetworkSecurityLevel
    geographic_scope: List[str]
    primary_targets: List[UUID]
    operational_status: str
    compromise_level: int
    effectiveness_rating: int
    active_operations: List[UUID]
    intelligence_gathered: int
    successful_missions: int
    blown_operations: int
    budget: int
    monthly_cost: int
    equipment_level: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IntelligenceAssessmentResponse(BaseModel):
    """Response schema for intelligence assessments"""
    id: UUID
    assessment_title: str
    assessing_faction: UUID
    intelligence_reports: List[UUID]
    assessment_focus: List[str]
    time_period: Dict[str, datetime]
    key_insights: List[str]
    threat_assessment: Dict[UUID, str]
    opportunity_assessment: Dict[str, str]
    short_term_predictions: List[str]
    medium_term_predictions: List[str]
    long_term_predictions: List[str]
    overall_confidence: int
    intelligence_gaps: List[str]
    contradicting_reports: List[UUID]
    strategic_recommendations: List[str]
    tactical_recommendations: List[str]
    intelligence_priorities: List[str]
    classification_level: NetworkSecurityLevel
    distribution_list: List[UUID]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SecurityBreachResponse(BaseModel):
    """Response schema for security breaches"""
    id: UUID
    breach_type: str
    affected_faction: UUID
    description: str
    discovery_date: datetime
    estimated_breach_date: Optional[datetime]
    compromised_operations: List[UUID]
    compromised_agents: List[UUID]
    compromised_intelligence: List[UUID]
    compromised_networks: List[UUID]
    perpetrating_faction: Optional[UUID]
    breach_method: Optional[str]
    insider_threat: bool
    containment_actions: List[str]
    mitigation_measures: List[str]
    lessons_learned: List[str]
    status: str
    damage_assessment: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# List Response Schemas

class AgentListResponse(BaseModel):
    """Response schema for list of agents"""
    agents: List[AgentResponse]
    total_count: int
    active_count: int
    compromised_count: int
    available_count: int


class OperationListResponse(BaseModel):
    """Response schema for list of operations"""
    operations: List[IntelligenceOperationResponse]
    total_count: int
    active_count: int
    completed_count: int
    successful_count: int


class ReportListResponse(BaseModel):
    """Response schema for list of intelligence reports"""
    reports: List[IntelligenceReportResponse]
    total_count: int
    recent_count: int
    high_value_count: int


class NetworkListResponse(BaseModel):
    """Response schema for list of intelligence networks"""
    networks: List[IntelligenceNetworkResponse]
    total_count: int
    active_count: int
    compromised_count: int


# Statistics and Summary Schemas

class IntelligenceStatisticsResponse(BaseModel):
    """Response schema for intelligence statistics"""
    total_agents: int
    active_agents: int
    total_operations: int
    successful_operations: int
    success_rate: float
    total_intelligence_reports: int
    agent_utilization: float
    operations_by_type: Dict[str, int]
    reports_by_quality: Dict[str, int]
    network_effectiveness: Dict[UUID, int]
    recent_activity_summary: Dict[str, Any]


class OperationExecutionResponse(BaseModel):
    """Response schema for operation execution results"""
    operation_id: UUID
    result: str  # success, failure, compromised
    intelligence_report: Optional[IntelligenceReportResponse]
    agents_affected: List[UUID]
    political_consequences: Optional[str]
    reputation_impact: int
    execution_timestamp: datetime


class InformationCampaignResultResponse(BaseModel):
    """Response schema for information warfare campaign results"""
    campaign_id: UUID
    success: bool
    effectiveness: int
    reputation_impacts: Dict[str, int]
    reach_achieved: int
    counter_narratives_detected: List[str]
    execution_timestamp: datetime


# Error Response Schemas

class IntelligenceErrorResponse(BaseModel):
    """Error response for intelligence operations"""
    error: str
    detail: str
    operation_id: Optional[UUID] = None
    agent_id: Optional[UUID] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Success Response Schemas

class IntelligenceSuccessResponse(BaseModel):
    """Generic success response for intelligence operations"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Detailed Response Schemas with Related Data

class AgentDetailsResponse(AgentResponse):
    """Extended agent response with operational history"""
    recent_operations: List[IntelligenceOperationResponse]
    intelligence_reports_generated: List[IntelligenceReportResponse]
    performance_metrics: Dict[str, Any]
    risk_assessment: Dict[str, Any]


class OperationDetailsResponse(IntelligenceOperationResponse):
    """Extended operation response with related data"""
    assigned_agent_details: List[AgentResponse]
    intelligence_reports: List[IntelligenceReportResponse]
    related_counter_operations: List[CounterIntelligenceOperationResponse]
    risk_factors: Dict[str, Any]


class NetworkDetailsResponse(IntelligenceNetworkResponse):
    """Extended network response with detailed information"""
    agent_details: List[AgentResponse]
    recent_operations: List[IntelligenceOperationResponse]
    intelligence_summary: Dict[str, Any]
    security_assessment: Dict[str, Any]


class FactionIntelligenceSummaryResponse(BaseModel):
    """Comprehensive intelligence summary for a faction"""
    faction_id: UUID
    total_agents: int
    active_operations: int
    intelligence_reports: int
    networks: int
    recent_activities: List[Dict[str, Any]]
    threat_assessment: Dict[str, Any]
    opportunities: List[str]
    recommendations: List[str]
    security_status: str
    generated_at: datetime = Field(default_factory=datetime.utcnow) 