"""
World State Infrastructure Module

This module contains the technical infrastructure for the world state system,
including API endpoints, database models, repositories, and technical utilities.
"""

# API routers
from backend.infrastructure.systems.world_state.api import world_state_router, world_state_service_router
from backend.infrastructure.systems.world_state.api.websocket_routes import router as world_state_websocket_router
from backend.infrastructure.systems.world_state.api.metrics_routes import router as world_state_metrics_router

# Models
from backend.infrastructure.systems.world_state.models.models import (
    World_StateEntity,
    World_StateModel,
    CreateWorld_StateRequest,
    UpdateWorld_StateRequest,
    World_StateResponse,
    World_StateListResponse
)

# Utilities
from backend.infrastructure.systems.world_state.utils.terrain_generator import TerrainGenerator

__all__ = [
    # API components
    "world_state_router",
    "world_state_service_router",
    "world_state_websocket_router", 
    "world_state_metrics_router",
    
    # Data layer
    "World_StateEntity",
    "World_StateModel",
    "CreateWorld_StateRequest",
    "UpdateWorld_StateRequest", 
    "World_StateResponse",
    "World_StateListResponse",
    
    # Utilities
    "TerrainGenerator",
] 