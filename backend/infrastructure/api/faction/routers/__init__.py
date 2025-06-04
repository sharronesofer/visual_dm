"""Faction routers module"""

# Import all routers
from .faction_router import *
# Temporarily disabled due to import issues
# from .faction_routes import *
# from .expansion_router import *
# from .succession_router import succession_router

__all__ = [
    # Router instances
    "faction_router",
    # "faction_routes",
    # "expansion_router", 
    # "succession_router",
    
    # Router functions
    "get_db_session"
]
