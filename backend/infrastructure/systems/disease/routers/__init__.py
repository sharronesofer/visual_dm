"""
Disease System API Routers

FastAPI routers for disease system endpoints.
"""

from .disease_router import router as disease_router
from .outbreak_router import router as outbreak_router
from .profile_router import router as profile_router
from .config_router import router as config_router

__all__ = [
    'disease_router',
    'outbreak_router', 
    'profile_router',
    'config_router'
] 