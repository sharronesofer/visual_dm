"""Domain Models Package."""

from .base import BaseModel
from backend.infrastructure.shared.models.base import BaseRepository

__all__ = [
    'BaseModel',
    'BaseRepository',
] 