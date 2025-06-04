"""
Infrastructure - Persistence Layer

Handles file I/O, data serialization, and state persistence for various systems.
"""

from .game_time_persistence import PersistenceService as GameTimePersistenceService

__all__ = [
    "GameTimePersistenceService"
] 