"""Economic Espionage System

This system handles economic espionage mechanics where NPCs and factions can:
- Steal trade secrets and pricing information
- Sabotage competitor operations
- Engage in market manipulation
- Build and operate spy networks
- Conduct counter-espionage operations

This module contains only business logic. Technical infrastructure (repositories, 
routers, database models, API schemas) has been moved to backend.infrastructure.
"""

from .models import *
from .services import *

__all__ = [
    # Business models and services are imported automatically
] 