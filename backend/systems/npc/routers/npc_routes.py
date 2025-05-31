"""
NPC Routes Module
-----------------
Master router aggregator for NPC system, combining all NPC-related routes.
Uses FastAPI APIRouter instead of Flask Blueprints.
"""

from fastapi import APIRouter

# Import existing routers
from .npc_router import router as main_npc_router
from .npc_character_routes import router as character_router
from .npc_location_router import router as location_router

# Create master NPC router
npc_routes_router = APIRouter(prefix="/npc", tags=["npc-system"])

# Include all sub-routers
npc_routes_router.include_router(main_npc_router)
npc_routes_router.include_router(character_router)
npc_routes_router.include_router(location_router)

# Export the router
__all__ = ["npc_routes_router"]

