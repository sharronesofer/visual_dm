"""
Diplomacy System Schemas

This package contains all request and response schemas for the diplomacy system API.
"""

from .request_schemas import *
from .response_schemas import *
from .crisis_schemas import *
from .diplomacy_schemas import *
from .intelligence_schemas import *

__all__ = [
    # Core Request Schemas
    "CreateTreatyRequest",
    "UpdateRelationshipRequest", 
    "StartNegotiationRequest",
    "SubmitOfferRequest",
    "RespondToNegotiationRequest",
    "ReportIncidentRequest",
    "ResolveIncidentRequest",
    "IssueUltimatumRequest",
    "RespondToUltimatumRequest",
    "ImposeSanctionsRequest",
    "ReportTreatyViolationRequest",
    "EstablishRelationshipRequest",
    "RecordDiplomaticEventRequest",
    
    # Core Response Schemas
    "BaseResponse",
    "RelationshipResponse",
    "TreatyResponse",
    "NegotiationResponse",
    "OfferResponse",
    "IncidentResponse",
    "UltimatumResponse",
    "SanctionResponse",
    "TreatyViolationResponse",
    "DiplomaticEventResponse",
    "FactionSummaryResponse",
    "HealthCheckResponse",
    "PaginatedResponse",
    "ErrorResponse",
    "SuccessResponse",
    "NegotiationDetailsResponse",
    "TreatyDetailsResponse",
    "RelationshipHistoryResponse",
    "DiplomacyStatisticsResponse",
    
    # Crisis Management Request Schemas
    "CreateCrisisRequest",
    "UpdateCrisisRequest",
    "CreateResolutionAttemptRequest",
    "UpdateResolutionAttemptRequest",
    "CreateInterventionRequest",
    "CreateEscalationTriggerRequest",
    "RequestImpactAssessmentRequest",
    
    # Crisis Management Response Schemas
    "CrisisResponse",
    "ResolutionAttemptResponse",
    "InterventionResponse",
    "EscalationTriggerResponse",
    "ImpactAssessmentResponse",
    "CrisisListResponse",
    "CrisisDetailsResponse",
    "CrisisStatisticsResponse"
] 