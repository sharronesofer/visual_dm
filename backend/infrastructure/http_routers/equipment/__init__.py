"""
Infrastructure HTTP routers for the equipment system.

Contains FastAPI routers and HTTP-related technical infrastructure.
"""

from .equipment_router import router as equipment_router
from .enchanting_router import router as enchanting_router  
from .character_equipment_router import router as character_equipment_router
from .combat_equipment_router import router as combat_equipment_router

__all__ = [
    'equipment_router',
    'enchanting_router',
    'character_equipment_router', 
    'combat_equipment_router'
]

# Note: Combat and character integration routers are available but temporarily
# disabled due to circular import resolution. They will be re-enabled once
# the character system imports are restructured.

# Note: The old router system has been replaced with the new hybrid system
# All old router code has been removed to prevent conflicts

