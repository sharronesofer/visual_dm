"""
NPC System
------------------
Module for managing non-player characters, their locations, behaviors, and relationships.
"""

from backend.systems.npc.npc_location_service import NpcLocationService
from backend.systems.npc.routers.npc_location_router import router as npc_location_router

__all__ = [
    # Services
    'NpcLocationService',
    
    # Routers
    'npc_location_router'
] 