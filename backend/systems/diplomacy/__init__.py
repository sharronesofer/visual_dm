"""
Diplomacy System

This module provides functionality for managing diplomatic relations between factions,
including treaties, negotiations, diplomatic events, and tension/war management.
"""

from backend.systems.diplomacy.models import (
    DiplomaticEvent,
    DiplomaticEventType,
    DiplomaticStatus,
    FactionRelationship,
    Negotiation,
    NegotiationOffer,
    NegotiationStatus,
    Treaty,
    TreatyStatus,
    TreatyType
)

from backend.systems.diplomacy.services import DiplomacyService, TensionService
from backend.systems.diplomacy.repository import DiplomacyRepository

# Convenience re-exports
diplomatic_status = {
    "NEUTRAL": DiplomaticStatus.NEUTRAL,
    "FRIENDLY": DiplomaticStatus.FRIENDLY,
    "ALLIED": DiplomaticStatus.ALLIED,
    "HOSTILE": DiplomaticStatus.HOSTILE,
    "WAR": DiplomaticStatus.WAR
}

treaty_types = {
    "PEACE": TreatyType.PEACE,
    "ALLIANCE": TreatyType.ALLIANCE,
    "TRADE": TreatyType.TRADE,
    "NON_AGGRESSION": TreatyType.NON_AGGRESSION,
    "MUTUAL_DEFENSE": TreatyType.MUTUAL_DEFENSE
}

# Create global service instances
diplomacy_service = DiplomacyService()
tension_service = TensionService()

__all__ = [
    "DiplomaticEvent",
    "DiplomaticEventType",
    "DiplomaticStatus",
    "FactionRelationship",
    "Negotiation",
    "NegotiationOffer",
    "NegotiationStatus",
    "Treaty",
    "TreatyStatus",
    "TreatyType",
    "DiplomacyService",
    "TensionService",
    "DiplomacyRepository",
    "diplomatic_status",
    "treaty_types",
    "diplomacy_service",
    "tension_service"
]
