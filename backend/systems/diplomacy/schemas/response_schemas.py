"""
Response Schemas for Diplomacy System

Pydantic schemas for API response validation and serialization.
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from backend.systems.diplomacy.models.core_models import (
    TreatyType, TreatyStatus, DiplomaticStatus, NegotiationStatus,
    DiplomaticIncidentType, DiplomaticIncidentSeverity,
    TreatyViolationType, UltimatumStatus, DiplomaticEventType
)


class BaseResponse(BaseModel):
    """Base response schema with common fields"""
    id: UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RelationshipResponse(BaseResponse):
    """Response schema for faction relationships"""
    faction_a_id: UUID
    faction_b_id: UUID
    status: DiplomaticStatus
    reputation_score: float
    last_interaction: Optional[datetime]
    notes: Optional[str]


class TreatyResponse(BaseResponse):
    """Response schema for treaties"""
    faction_a_id: UUID
    faction_b_id: UUID
    treaty_type: TreatyType
    status: TreatyStatus
    terms: Dict[str, Any]
    signed_date: Optional[datetime]
    expiry_date: Optional[datetime]
    ratified_by_a: bool
    ratified_by_b: bool


class NegotiationResponse(BaseResponse):
    """Response schema for negotiations"""
    initiator_faction_id: UUID
    target_faction_id: UUID
    topic: str
    status: NegotiationStatus
    current_offer: Optional[Dict[str, Any]]
    deadline: Optional[datetime]
    concluded_at: Optional[datetime]
    final_terms: Optional[Dict[str, Any]]


class OfferResponse(BaseResponse):
    """Response schema for negotiation offers"""
    negotiation_id: UUID
    offering_faction_id: UUID
    terms: Dict[str, Any]
    message: Optional[str]
    accepted: Optional[bool]
    response_message: Optional[str]


class IncidentResponse(BaseResponse):
    """Response schema for diplomatic incidents"""
    incident_type: DiplomaticIncidentType
    faction_a_id: UUID
    faction_b_id: Optional[UUID]
    severity: DiplomaticIncidentSeverity
    description: str
    location: Optional[str]
    evidence: Optional[Dict[str, Any]]
    resolved: bool
    resolution: Optional[str]
    resolved_at: Optional[datetime]


class UltimatumResponse(BaseResponse):
    """Response schema for ultimatums"""
    issuing_faction_id: UUID
    target_faction_id: UUID
    demands: Dict[str, Any]
    deadline: datetime
    status: UltimatumStatus
    consequences: Optional[Dict[str, Any]]
    response: Optional[str]
    responded_at: Optional[datetime]
    related_incident_id: Optional[UUID]


class SanctionResponse(BaseResponse):
    """Response schema for sanctions"""
    imposing_faction_id: UUID
    target_faction_id: UUID
    sanction_type: str
    restrictions: Dict[str, Any]
    reason: str
    active: bool
    expiry_date: Optional[datetime]


class TreatyViolationResponse(BaseResponse):
    """Response schema for treaty violations"""
    treaty_id: UUID
    violation_type: TreatyViolationType
    reporting_faction_id: UUID
    description: str
    evidence: Optional[Dict[str, Any]]
    verified: bool
    resolved: bool
    resolution: Optional[str]


class DiplomaticEventResponse(BaseResponse):
    """Response schema for diplomatic events"""
    event_type: DiplomaticEventType
    faction_a_id: UUID
    faction_b_id: Optional[UUID]
    description: str
    metadata: Optional[Dict[str, Any]]
    impact_score: Optional[float]


class FactionSummaryResponse(BaseModel):
    """Response schema for faction diplomatic summary"""
    faction_id: UUID
    total_relationships: int
    relationships_by_status: Dict[str, int]
    active_treaties: int
    pending_negotiations: int
    recent_incidents: int
    reputation_average: float
    
    # Detailed breakdowns
    allies: List[UUID]
    enemies: List[UUID]
    neutral_relations: List[UUID]
    
    # Recent activity
    recent_events: List[DiplomaticEventResponse]
    active_ultimatums_issued: int
    active_ultimatums_received: int
    active_sanctions_imposed: int
    active_sanctions_received: int


class HealthCheckResponse(BaseModel):
    """Response schema for health checks"""
    status: str
    system: str
    relationships_count: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper"""
    items: List[BaseResponse]
    total: int
    page: int
    size: int
    pages: int


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str
    detail: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class SuccessResponse(BaseModel):
    """Generic success response"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Specialized response types for complex operations
class NegotiationDetailsResponse(NegotiationResponse):
    """Extended negotiation response with offers"""
    offers: List[OfferResponse]
    offer_count: int


class TreatyDetailsResponse(TreatyResponse):
    """Extended treaty response with violations"""
    violations: List[TreatyViolationResponse]
    violation_count: int


class RelationshipHistoryResponse(RelationshipResponse):
    """Extended relationship response with history"""
    events: List[DiplomaticEventResponse]
    event_count: int
    relationship_timeline: List[Dict[str, Any]]


# Summary and statistics responses
class DiplomacyStatisticsResponse(BaseModel):
    """Overall diplomacy system statistics"""
    total_relationships: int
    total_treaties: int
    total_negotiations: int
    total_incidents: int
    
    # Status breakdowns
    relationships_by_status: Dict[str, int]
    treaties_by_status: Dict[str, int]
    negotiations_by_status: Dict[str, int]
    
    # Recent activity
    recent_activity_count: int
    most_active_factions: List[Dict[str, Any]]
    
    # System health
    system_uptime: str
    last_updated: datetime 