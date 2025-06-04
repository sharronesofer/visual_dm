"""
Diplomacy System Database Models

This package contains SQLAlchemy database models for the diplomacy system.
These models were moved from the infrastructure layer to improve system encapsulation.
"""

from .diplomacy_models import (
    DiplomaticRelationship,
    Treaty,
    Negotiation,
    NegotiationOffer,
    DiplomaticEvent,
    TreatyViolation,
    DiplomaticIncident,
    Ultimatum,
    Sanction,
    Base
)

from .crisis_db_models import (
    DiplomaticCrisis,
    CrisisResolutionAttempt,
    CrisisIntervention,
    CrisisEscalationTrigger,
    CrisisImpactAssessment
)

from .intelligence_db_models import *

# Database adapters
from .intelligence_database_adapter import IntelligenceDatabaseAdapter
from .core_database_adapter import CoreDiplomacyDatabaseAdapter
from .crisis_database_adapter import CrisisDatabaseAdapter

__all__ = [
    # Core diplomatic models
    "DiplomaticRelationship",
    "Treaty", 
    "Negotiation",
    "NegotiationOffer",
    "DiplomaticEvent",
    "TreatyViolation",
    "DiplomaticIncident",
    "Ultimatum",
    "Sanction",
    # Crisis management models
    "DiplomaticCrisis",
    "CrisisResolutionAttempt",
    "CrisisIntervention", 
    "CrisisEscalationTrigger",
    "CrisisImpactAssessment",
    # Database adapters
    "IntelligenceDatabaseAdapter",
    "CoreDiplomacyDatabaseAdapter",
    "CrisisDatabaseAdapter",
    # Base for all models
    "Base"
] 