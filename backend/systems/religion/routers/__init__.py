"""Routers for religion system"""

# Import router components
try:
    from .religion_router import router as religion_router
except ImportError:
    # Router may have import issues
    religion_router = None

try:
    from .websocket_routes import religion_websocket_router
except ImportError:
    # WebSocket router may have import issues
    religion_websocket_router = None

__all__ = [
    "religion_router",
    "religion_websocket_router"
]

