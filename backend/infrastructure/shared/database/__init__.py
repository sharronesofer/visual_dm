"""
Shared database components for business logic systems.

This module provides database access and session management for business logic
systems, using local base implementations.
"""

# Import from local base module to avoid circular imports
from .base import Base, BaseModel
from .session import get_db

# Re-export for compatibility
__all__ = [
    'Base',
    'BaseModel',
    'get_db',
] 