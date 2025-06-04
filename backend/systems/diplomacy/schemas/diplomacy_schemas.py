"""
API Schemas for the Diplomacy System

This module defines Pydantic models used for API validation and serialization/deserialization
of diplomatic data objects.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from backend.systems.diplomacy.models.core_models import (
    DiplomaticEventType, 
    DiplomaticIncidentSeverity,
    DiplomaticIncidentType,
    DiplomaticStatus, 
    NegotiationStatus, 
    SanctionStatus,
    SanctionType,
    TreatyType,
    TreatyViolationType,
    UltimatumStatus
)


class TreatyCreate(BaseModel):
    """Schema for creating a new treaty."""
    name: str
    type: TreatyType
    parties: List[UUID]
    terms: Dict[str, Union[str, int, bool, Dict, List]] = {}
    end_date: Optional[datetime] = None
    is_public: bool = True
    negotiation_id: Optional[UUID] = None


class TreatyUpdate(BaseModel):
    """Schema for updating an existing treaty."""
    name: Optional[str] = None
    terms: Optional[Dict[str, Union[str, int, bool, Dict, List]]] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_public: Optional[bool] = None


class TreatySchema(BaseModel):
    """Schema for representing a treaty in API responses."""
    id: UUID
    name: str
    type: TreatyType
    parties: List[UUID]
    terms: Dict[str, Union[str, int, bool, Dict, List]] = {}
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool
    is_public: bool
    created_at: datetime
    updated_at: datetime
    negotiation_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class NegotiationOfferCreate(BaseModel):
    """Schema for creating a new negotiation offer."""
    faction_id: UUID
    terms: Dict[str, Union[str, int, bool, Dict, List]] = {}
    counter_offer_id: Optional[UUID] = None


class NegotiationOfferSchema(BaseModel):
    """Schema for representing a negotiation offer in API responses."""
    faction_id: UUID
    timestamp: datetime
    terms: Dict[str, Union[str, int, bool, Dict, List]] = {}
    accepted: Optional[bool] = None
    counter_offer_id: Optional[UUID] = None

    model_config = ConfigDict(from_attributes=True)


class NegotiationCreate(BaseModel):
    """Schema for creating a new negotiation."""
    parties: List[UUID]
    initiator_id: UUID
    treaty_type: Optional[TreatyType] = None
    initial_offer: Optional[NegotiationOfferCreate] = None
    metadata: Dict[str, Union[str, int, bool, Dict, List]] = {}


class NegotiationUpdate(BaseModel):
    """Schema for updating an existing negotiation."""
    status: Optional[NegotiationStatus] = None
    current_offer_id: Optional[UUID] = None
    end_date: Optional[datetime] = None
    result_treaty_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Union[str, int, bool, Dict, List]]] = None


class NegotiationSchema(BaseModel):
    """Schema for representing a negotiation in API responses."""
    id: UUID
    parties: List[UUID]
    initiator_id: UUID
    status: NegotiationStatus
    offers: List[NegotiationOfferSchema] = []
    current_offer_id: Optional[UUID] = None
    treaty_type: Optional[TreatyType] = None
    start_date: datetime
    end_date: Optional[datetime] = None
    result_treaty_id: Optional[UUID] = None
    metadata: Dict[str, Union[str, int, bool, Dict, List]] = {}

    model_config = ConfigDict(from_attributes=True)


class DiplomaticEventCreate(BaseModel):
    """Schema for creating a new diplomatic event."""
    event_type: DiplomaticEventType
    factions: List[UUID]
    description: str
    severity: int = 0
    public: bool = True
    related_treaty_id: Optional[UUID] = None
    related_negotiation_id: Optional[UUID] = None
    metadata: Dict[str, Union[str, int, bool, Dict, List]] = {}
    tension_change: Dict[str, int] = {}


class DiplomaticEventSchema(BaseModel):
    """Schema for representing a diplomatic event in API responses."""
    id: UUID
    event_type: DiplomaticEventType
    factions: List[UUID]
    timestamp: datetime
    description: str
    severity: int
    public: bool
    related_treaty_id: Optional[UUID] = None
    related_negotiation_id: Optional[UUID] = None
    metadata: Dict[str, Union[str, int, bool, Dict, List]] = {}
    tension_change: Dict[str, int] = {}

    model_config = ConfigDict(from_attributes=True)


class FactionRelationshipSchema(BaseModel):
    """Schema for representing the diplomatic relationship between two factions."""
    faction_a_id: UUID
    faction_b_id: UUID
    status: DiplomaticStatus
    tension: int  # -100 to 100, negative for alliance, positive for conflict
    treaties: List[UUID] = []  # IDs of active treaties between these factions
    last_status_change: datetime
    negotiations: List[UUID] = []  # IDs of ongoing negotiations

    model_config = ConfigDict(from_attributes=True)


class TreatyViolationCreate(BaseModel):
    """Schema for creating a new treaty violation."""
    treaty_id: UUID
    violator_id: UUID
    violation_type: TreatyViolationType
    description: str
    evidence: Dict[str, Union[str, int, bool, Dict, List]] = {}
    reported_by: UUID
    severity: int = 50


class TreatyViolationUpdate(BaseModel):
    """Schema for updating a treaty violation."""
    acknowledged: Optional[bool] = None
    resolved: Optional[bool] = None
    resolution_details: Optional[str] = None


class TreatyViolationSchema(BaseModel):
    """Schema for representing a treaty violation in API responses."""
    id: UUID
    treaty_id: UUID
    violator_id: UUID
    violation_type: TreatyViolationType
    description: str
    evidence: Dict[str, Union[str, int, bool, Dict, List]] = {}
    reported_by: UUID
    timestamp: datetime
    severity: int
    acknowledged: bool
    resolved: bool
    resolution_details: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DiplomaticIncidentCreate(BaseModel):
    """Schema for creating a new diplomatic incident."""
    incident_type: DiplomaticIncidentType
    perpetrator_id: UUID
    victim_id: UUID
    description: str
    evidence: Dict[str, Union[str, int, bool, Dict, List]] = {}
    severity: DiplomaticIncidentSeverity = DiplomaticIncidentSeverity.MODERATE
    tension_impact: int = 20
    public: bool = True
    witnessed_by: List[UUID] = []
    related_event_id: Optional[UUID] = None
    related_treaty_id: Optional[UUID] = None


class DiplomaticIncidentUpdate(BaseModel):
    """Schema for updating an existing diplomatic incident."""
    severity: Optional[DiplomaticIncidentSeverity] = None
    resolved: Optional[bool] = None
    resolution_details: Optional[str] = None
    resolution_date: Optional[datetime] = None


class DiplomaticIncidentSchema(BaseModel):
    """Schema for representing a diplomatic incident in API responses."""
    id: UUID
    incident_type: DiplomaticIncidentType
    perpetrator_id: UUID
    victim_id: UUID
    description: str
    evidence: Dict[str, Union[str, int, bool, Dict, List]] = {}
    severity: DiplomaticIncidentSeverity
    tension_impact: int
    public: bool
    timestamp: datetime
    witnessed_by: List[UUID] = []
    related_event_id: Optional[UUID] = None
    related_treaty_id: Optional[UUID] = None
    resolved: bool
    resolution_details: Optional[str] = None
    resolution_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UltimatumCreate(BaseModel):
    """Schema for creating a new ultimatum."""
    issuer_id: UUID
    recipient_id: UUID
    demands: Dict[str, Union[str, int, bool, Dict, List]] = {}
    consequences: Dict[str, Union[str, int, bool, Dict, List]] = {}
    deadline: datetime
    justification: str
    public: bool = True
    witnessed_by: List[UUID] = []
    related_incident_id: Optional[UUID] = None
    related_treaty_id: Optional[UUID] = None
    related_event_id: Optional[UUID] = None
    tension_change_on_issue: int = 20
    tension_change_on_accept: int = -10
    tension_change_on_reject: int = 40


class UltimatumUpdate(BaseModel):
    """Schema for updating an existing ultimatum."""
    status: Optional[UltimatumStatus] = None
    deadline: Optional[datetime] = None
    response_date: Optional[datetime] = None
    demands: Optional[Dict[str, Union[str, int, bool, Dict, List]]] = None
    consequences: Optional[Dict[str, Union[str, int, bool, Dict, List]]] = None


class UltimatumSchema(BaseModel):
    """Schema for representing an ultimatum in API responses."""
    id: UUID
    issuer_id: UUID
    recipient_id: UUID
    demands: Dict[str, Union[str, int, bool, Dict, List]] = {}
    consequences: Dict[str, Union[str, int, bool, Dict, List]] = {}
    status: UltimatumStatus
    issue_date: datetime
    deadline: datetime
    response_date: Optional[datetime] = None
    justification: str
    public: bool
    witnessed_by: List[UUID] = []
    related_incident_id: Optional[UUID] = None
    related_treaty_id: Optional[UUID] = None
    related_event_id: Optional[UUID] = None
    tension_change_on_issue: int
    tension_change_on_accept: int
    tension_change_on_reject: int

    model_config = ConfigDict(from_attributes=True)


class SanctionCreate(BaseModel):
    """Schema for creating a new diplomatic sanction."""
    imposer_id: UUID
    target_id: UUID
    sanction_type: SanctionType
    description: str
    justification: str
    end_date: Optional[datetime] = None
    conditions_for_lifting: Dict[str, Union[str, int, bool, Dict, List]] = {}
    severity: int = 50
    economic_impact: int = 50
    diplomatic_impact: int = 50
    enforcement_measures: Dict[str, Union[str, int, bool, Dict, List]] = {}
    supporting_factions: List[UUID] = []
    opposing_factions: List[UUID] = []
    is_public: bool = True


class SanctionUpdate(BaseModel):
    """Schema for updating an existing sanction."""
    status: Optional[SanctionStatus] = None
    end_date: Optional[datetime] = None
    lifted_date: Optional[datetime] = None
    conditions_for_lifting: Optional[Dict[str, Union[str, int, bool, Dict, List]]] = None
    enforcement_measures: Optional[Dict[str, Union[str, int, bool, Dict, List]]] = None
    supporting_factions: Optional[List[UUID]] = None
    opposing_factions: Optional[List[UUID]] = None
    violations: Optional[List[Dict]] = None


class SanctionViolationRecord(BaseModel):
    """Schema for recording a sanction violation."""
    violation_date: datetime
    description: str
    evidence: Dict[str, Union[str, int, bool, Dict, List]] = {}
    reported_by: UUID
    severity: int = 50


class SanctionSchema(BaseModel):
    """Schema for representing a sanction in API responses."""
    id: UUID
    imposer_id: UUID
    target_id: UUID
    sanction_type: SanctionType
    description: str
    status: SanctionStatus
    justification: str
    imposed_date: datetime
    end_date: Optional[datetime] = None
    lifted_date: Optional[datetime] = None
    conditions_for_lifting: Dict[str, Union[str, int, bool, Dict, List]] = {}
    severity: int
    economic_impact: int
    diplomatic_impact: int
    enforcement_measures: Dict[str, Union[str, int, bool, Dict, List]] = {}
    supporting_factions: List[UUID] = []
    opposing_factions: List[UUID] = []
    violations: List[Dict] = []
    is_public: bool

    model_config = ConfigDict(from_attributes=True) 