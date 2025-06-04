"""
Religion Data Repositories

Data access layer for religion system.
"""

from .repository import ReligionRepository, get_religion_repository

__all__ = [
    "ReligionRepository",
    "get_religion_repository",
]

