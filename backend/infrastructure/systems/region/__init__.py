"""
Region Infrastructure Module

Technical infrastructure for the region system including:
- Database migrations
- API routers and schemas
- Data repositories
- Utility functions for coordinate mapping
"""

# Re-export key infrastructure components
from .repositories import get_region_repository, get_continent_repository
from .routers import router as region_router
from .schemas import *

__all__ = [
    'get_region_repository',
    'get_continent_repository', 
    'region_router'
] 