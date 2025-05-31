"""
API endpoints for the World State system.

This module handles FastAPI routes and endpoints for accessing and manipulating
world state through HTTP interfaces.
"""

from backend.systems.world_state.router import router as world_state_router

__all__ = ['world_state_router'] 