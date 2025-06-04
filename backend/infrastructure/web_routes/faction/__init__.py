"""
Faction Web Routes

HTTP endpoints for faction system operations.
"""

from .enhanced_diplomacy_routes import router as diplomacy_router

__all__ = ["diplomacy_router"] 