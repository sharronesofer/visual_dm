"""
Diplomatic HTTP/API Infrastructure

HTTP routers and API endpoints for the diplomacy system.
"""

from .main_router import diplomacy_router
from .treaty_router import treaty_router
from .negotiation_router import negotiation_router
from .relationship_router import relationship_router
from .incident_router import incident_router

__all__ = [
    'diplomacy_router',
    "treaty_router", 
    "negotiation_router",
    "relationship_router", 
    "incident_router"
] 