"""
Infrastructure Repository Implementations for Region System

Concrete repository implementations that provide data persistence
for region and continent business logic.
"""

from .region_repository import RegionRepository, get_region_repository
from .continent_repository import ContinentRepository, get_continent_repository

__all__ = [
    'RegionRepository',
    'ContinentRepository',
    'get_region_repository',
    'get_continent_repository'
]

