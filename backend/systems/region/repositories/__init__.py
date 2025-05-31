"""Repositories for region system"""

from backend.systems.region.repositories.region_repository import (
    RegionRepository,
    ContinentRepository,
    get_region_repository,
    get_continent_repository
)

__all__ = [
    "RegionRepository",
    "ContinentRepository", 
    "get_region_repository",
    "get_continent_repository"
]

