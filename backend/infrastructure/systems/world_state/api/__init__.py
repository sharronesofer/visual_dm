"""
API endpoints for the World State system.

This module handles FastAPI routes and endpoints for accessing and manipulating
world state through HTTP interfaces.
"""

from backend.infrastructure.systems.world_state.api.world_routes import router as world_state_router
from backend.infrastructure.systems.world_state.api.service_routes import router as world_state_service_router

__all__ = ['world_state_router', 'world_state_service_router'] 