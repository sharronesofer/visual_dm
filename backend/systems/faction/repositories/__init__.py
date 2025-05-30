"""
Faction system repositories module.

This module provides data access layer components for the faction system.
"""

from backend.systems.faction.repositories.faction_repository import (
    FactionRepository,
    FactionRelationshipRepository
)

__all__ = [
    'FactionRepository',
    'FactionRelationshipRepository'
]
