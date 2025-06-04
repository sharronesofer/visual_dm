"""
Motif API routers and endpoints.
"""

# Import all routers
from .router import router

# Temporarily commented out until motif_engine_class is implemented
# from .motif_routes import motif_router

__all__ = [
    "router",
    # "motif_router"
]
