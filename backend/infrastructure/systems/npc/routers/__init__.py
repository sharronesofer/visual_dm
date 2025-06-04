"""NPC Routers

FastAPI routers for NPC system API endpoints.
"""

from .npc_router import router as npc_router
from .barter_router import router as barter_router
from .npc_location_router import router as npc_location_router
from .npc_character_routes import router as npc_character_router

__all__ = [
    'npc_router',
    'barter_router', 
    'npc_location_router',
    'npc_character_router'
]
