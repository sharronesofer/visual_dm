"""
Equipment System API Routers

This module provides REST API endpoints for the equipment system according to
Development Bible standards. Implements the missing infrastructure layer for
equipment management.

Available Routers:
- equipment_router: CRUD operations for equipment instances
- equipment_management_router: Equipment management and character interaction
- set_bonus_router: Equipment set bonus calculations and previews
"""

from .equipment_router import router as equipment_router
from .equipment_router import character_router
from .equipment_management_router import router as equipment_management_router  
from .set_bonus_router import router as set_bonus_router

__all__ = [
    "equipment_router",
    "character_router",
    "equipment_management_router", 
    "set_bonus_router"
] 