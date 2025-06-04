"""
Models for the Diplomacy System

This module provides all the Pydantic models used throughout the diplomacy system.
"""

# Import Pydantic models (these are the main business logic models)
from .core_models import (
    # Status and Type Enums
    DiplomaticStatus,
    TreatyType,
    TreatyStatus,
    NegotiationStatus,
    DiplomaticEventType,
    TreatyViolationType,
    DiplomaticIncidentType,
    DiplomaticIncidentSeverity,
    UltimatumStatus,
    SanctionType,
    SanctionStatus,
    
    # Core Models
    Treaty,
    Negotiation,
    NegotiationOffer,
    DiplomaticEvent,
    TreatyViolation,
    DiplomaticIncident,
    Ultimatum,
    Sanction,
    FactionRelationship
)

from .crisis_models import (
    # Crisis Type Enums
    CrisisType,
    CrisisEscalationLevel,
    CrisisStatus,
    ResolutionType,
    InterventionType,
    
    # Crisis Models
    DiplomaticCrisis,
    CrisisResolutionAttempt,
    CrisisIntervention,
    CrisisEscalationTrigger,
    CrisisImpactAssessment
)

from .intelligence_models import (
    # Intelligence models
    IntelligenceAgent, AgentStatus, IntelligenceNetwork, NetworkSecurityLevel,
    IntelligenceOperation, OperationStatus, IntelligenceReport, IntelligenceQuality,
    CounterIntelligenceOperation, InformationWarfareOperation, IntelligenceAssessment,
    SecurityBreach, IntelligenceType, EspionageOperationType, InformationWarfareType
)

# Export all models
__all__ = [
    # Core diplomatic enums
    "DiplomaticStatus", "TreatyType", "TreatyStatus", "NegotiationStatus",
    "DiplomaticEventType", "TreatyViolationType", "DiplomaticIncidentType", 
    "DiplomaticIncidentSeverity", "UltimatumStatus", "SanctionType", "SanctionStatus",
    
    # Core diplomatic models
    "Treaty", "Negotiation", "NegotiationOffer", "DiplomaticEvent", "TreatyViolation",
    "DiplomaticIncident", "Ultimatum", "Sanction", "FactionRelationship",
    
    # Crisis management enums
    "CrisisType", "CrisisEscalationLevel", "CrisisStatus", "ResolutionType", "InterventionType",
    
    # Crisis management models
    "DiplomaticCrisis", "CrisisResolutionAttempt", "CrisisIntervention", 
    "CrisisEscalationTrigger", "CrisisImpactAssessment",
    
    # Intelligence enums
    "AgentStatus", "NetworkSecurityLevel", "OperationStatus", "IntelligenceQuality",
    "IntelligenceType", "EspionageOperationType", "InformationWarfareType",
    
    # Intelligence models
    "IntelligenceAgent", "IntelligenceNetwork", "IntelligenceOperation", "IntelligenceReport",
    "CounterIntelligenceOperation", "InformationWarfareOperation", "IntelligenceAssessment",
    "SecurityBreach"
]
