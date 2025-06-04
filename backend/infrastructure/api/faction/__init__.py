"""Faction API module"""

from .routers.faction_router import faction_router
# Temporarily disabled due to import issues
# from .routers.faction_routes import *
# from .routers.alliance_routes import *
# from .routers.expansion_router import *
# from .routers.succession_router import *

__all__ = [
    "faction_router",
] 