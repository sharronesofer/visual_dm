"""NPC Repositories

Data access layer for NPC system operations.
"""

from .npc_repository import NPCRepository
from .npc_memory_repository import NPCMemoryRepository
from .npc_location_repository import NPCLocationRepository

__all__ = [
    'NPCRepository',
    'NPCMemoryRepository', 
    'NPCLocationRepository'
]
