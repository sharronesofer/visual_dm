"""
Memory Infrastructure Module

This module contains the technical infrastructure components for the memory system:
- Data models and entities
- API routers and endpoints  
- Data access repositories
- Request/response schemas
- Data access services (imported separately to avoid circular dependencies)

Business logic remains in backend.systems.memory
"""

# Import infrastructure components
from . import models
from . import routers
from . import repositories
from . import schemas
# Note: services not imported here to avoid circular dependencies
# Import services directly: from backend.infrastructure.systems.memory.services import ...

__all__ = [
    "models",
    "routers", 
    "repositories",
    "schemas"
] 