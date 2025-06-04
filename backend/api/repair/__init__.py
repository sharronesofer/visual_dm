"""
Repair System API

FastAPI routers and endpoints for the repair and equipment system.
"""

from .routers.repair_router import router as repair_router
from .routers.equipment_router import router as equipment_router

__all__ = [
    "repair_router",
    "equipment_router"
] 