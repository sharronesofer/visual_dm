"""
Player routes module - aggregates character routes under player namespace.
This file serves purely as a router aggregator, re-registering character router under a broader player router namespace.
"""

from fastapi import APIRouter
from backend.infrastructure.api.character.routers.character_router import router as character_router

# Create player router that includes character routes
player_router = APIRouter(prefix="/player", tags=["player"])
player_router.include_router(character_router)

