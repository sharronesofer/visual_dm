"""
Authentication API routers.

This package contains FastAPI routers for authentication endpoints.
"""

# Import routers
# TODO: Implement these routers
# from .auth_router import router as auth_router
# from .user_router import router as user_router

# This router is implemented
from .auth_relationship_router import router as auth_relationship_router

__all__ = [
    # "auth_router",
    # "user_router",
    "auth_relationship_router"
] 