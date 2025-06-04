"""
Religion API Routers

FastAPI routers for religion system endpoints.
"""

from .religion_router import router as religion_router
from .websocket_routes import religion_websocket_router

__all__ = [
    "religion_router",
    "religion_websocket_router",
]

