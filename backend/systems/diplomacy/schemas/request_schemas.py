"""
Request Schemas for Diplomacy System

Pydantic schemas for validating incoming API requests.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from backend.systems.diplomacy.models.core_models import (
    TreatyType, DiplomaticStatus, NegotiationStatus,
    DiplomaticIncidentType, DiplomaticIncidentSeverity,
    TreatyViolationType, UltimatumStatus
)


class CreateTreatyRequest(BaseModel):
    """Request schema for creating a new treaty"""
    faction_a_id: UUID = Field(..., description="First faction involved in the treaty")
    faction_b_id: UUID = Field(..., description="Second faction involved in the treaty")
    treaty_type: TreatyType = Field(..., description="Type of treaty being created")
    terms: Dict[str, Any] = Field(..., description="Treaty terms and conditions")
    duration_days: Optional[int] = Field(None, description="Duration of treaty in days")
    
    @validator('terms')
    def validate_terms(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError("Terms must be a non-empty dictionary")
        return v


class UpdateRelationshipRequest(BaseModel):
    """Request schema for updating faction relationship status"""
    new_status: DiplomaticStatus = Field(..., description="New diplomatic status")
    reason: Optional[str] = Field(None, description="Reason for status change")


class StartNegotiationRequest(BaseModel):
    """Request schema for starting a new negotiation"""
    initiator_faction_id: UUID = Field(..., description="Faction starting the negotiation")
    target_faction_id: UUID = Field(..., description="Target faction for negotiation")
    topic: str = Field(..., min_length=1, description="Topic of negotiation")
    initial_offer: Dict[str, Any] = Field(..., description="Initial negotiation offer")
    deadline_days: Optional[int] = Field(None, ge=1, description="Negotiation deadline in days")
    
    @validator('initial_offer')
    def validate_initial_offer(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError("Initial offer must be a non-empty dictionary")
        return v


class SubmitOfferRequest(BaseModel):
    """Request schema for submitting negotiation offers"""
    offering_faction_id: UUID = Field(..., description="Faction making the offer")
    terms: Dict[str, Any] = Field(..., description="Offer terms")
    message: Optional[str] = Field(None, description="Message accompanying the offer")
    
    @validator('terms')
    def validate_terms(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError("Terms must be a non-empty dictionary")
        return v


class RespondToNegotiationRequest(BaseModel):
    """Request schema for responding to negotiations"""
    responding_faction_id: UUID = Field(..., description="Faction responding")
    response: str = Field(..., pattern="^(accept|reject|counter)$", description="Response type")
    counter_offer: Optional[Dict[str, Any]] = Field(None, description="Counter offer if response is 'counter'")
    message: Optional[str] = Field(None, description="Response message")


class ReportIncidentRequest(BaseModel):
    """Request schema for reporting diplomatic incidents"""
    incident_type: DiplomaticIncidentType = Field(..., description="Type of incident")
    faction_a_id: UUID = Field(..., description="Primary faction involved")
    faction_b_id: Optional[UUID] = Field(None, description="Secondary faction (if applicable)")
    severity: DiplomaticIncidentSeverity = Field(
        DiplomaticIncidentSeverity.MINOR, 
        description="Severity of the incident"
    )
    description: str = Field(..., min_length=1, description="Incident description")
    location: Optional[str] = Field(None, description="Location where incident occurred")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Supporting evidence")


class ResolveIncidentRequest(BaseModel):
    """Request schema for resolving incidents"""
    resolution: str = Field(..., min_length=1, description="Resolution details")
    resolved_by_faction_id: Optional[UUID] = Field(None, description="Faction resolving the incident")
    compensation: Optional[Dict[str, Any]] = Field(None, description="Compensation offered")


class IssueUltimatumRequest(BaseModel):
    """Request schema for issuing ultimatums"""
    issuing_faction_id: UUID = Field(..., description="Faction issuing the ultimatum")
    target_faction_id: UUID = Field(..., description="Target faction")
    demands: Dict[str, Any] = Field(..., description="Ultimatum demands")
    deadline_hours: int = Field(24, ge=1, le=168, description="Deadline in hours (1-168)")
    consequences: Optional[Dict[str, Any]] = Field(None, description="Consequences if demands not met")
    related_incident_id: Optional[UUID] = Field(None, description="Related incident ID")
    
    @validator('demands')
    def validate_demands(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError("Demands must be a non-empty dictionary")
        return v


class RespondToUltimatumRequest(BaseModel):
    """Request schema for responding to ultimatums"""
    response: str = Field(..., pattern="^(accept|reject|negotiate)$", description="Response type")
    responding_faction_id: UUID = Field(..., description="Faction responding")
    counter_proposal: Optional[Dict[str, Any]] = Field(None, description="Counter proposal if negotiating")


class ImposeSanctionsRequest(BaseModel):
    """Request schema for imposing sanctions"""
    imposing_faction_id: UUID = Field(..., description="Faction imposing sanctions")
    target_faction_id: UUID = Field(..., description="Target faction")
    sanction_type: str = Field(..., min_length=1, description="Type of sanctions")
    restrictions: Dict[str, Any] = Field(..., description="Specific restrictions")
    duration_days: Optional[int] = Field(None, ge=1, description="Duration in days")
    reason: str = Field("", description="Reason for sanctions")
    
    @validator('restrictions')
    def validate_restrictions(cls, v):
        if not v or not isinstance(v, dict):
            raise ValueError("Restrictions must be a non-empty dictionary")
        return v


class ReportTreatyViolationRequest(BaseModel):
    """Request schema for reporting treaty violations"""
    violation_type: TreatyViolationType = Field(..., description="Type of violation")
    reporting_faction_id: UUID = Field(..., description="Faction reporting the violation")
    description: str = Field(..., min_length=1, description="Violation description")
    evidence: Optional[Dict[str, Any]] = Field(None, description="Supporting evidence")


class EstablishRelationshipRequest(BaseModel):
    """Request schema for establishing new relationships"""
    initial_status: DiplomaticStatus = Field(
        DiplomaticStatus.NEUTRAL, 
        description="Initial diplomatic status"
    )


class RecordDiplomaticEventRequest(BaseModel):
    """Request schema for recording diplomatic events"""
    event_type: str = Field(..., min_length=1, description="Type of event")
    faction_a_id: UUID = Field(..., description="Primary faction")
    faction_b_id: Optional[UUID] = Field(None, description="Secondary faction")
    description: str = Field("", description="Event description")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional event data") 