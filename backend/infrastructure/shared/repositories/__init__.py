"""Repositories for shared system"""

from backend.infrastructure.repositories import BaseRepository
from backend.infrastructure.shared.exceptions import RepositoryError

__all__ = [
    "BaseRepository",
    "RepositoryError"
]

