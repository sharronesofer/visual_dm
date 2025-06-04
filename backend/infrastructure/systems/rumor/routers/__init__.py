"""Rumor routers module"""

from .rumor_router import router
# from .npc_rumor_routes import rumor_bp  # Legacy Flask router - disabled due to dependency issues

__all__ = ["router"]
