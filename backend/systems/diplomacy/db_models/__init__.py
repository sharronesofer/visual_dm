"""Database Models for diplomacy system"""

# Import and re-export all database models
from backend.systems.diplomacy.models.db_models import (
    DiplomaticRelationship,
    Treaty,
    Negotiation,
    DiplomaticEvent,
    TreatyViolation,
    DiplomaticIncident,
    Ultimatum,
    Sanction
)

# Add alias for test compatibility
FactionRelationship = DiplomaticRelationship

__all__ = [
    'DiplomaticRelationship',
    'FactionRelationship',  # Alias for DiplomaticRelationship
    'Treaty',
    'Negotiation',
    'DiplomaticEvent',
    'TreatyViolation',
    'DiplomaticIncident',
    'Ultimatum',
    'Sanction'
]

