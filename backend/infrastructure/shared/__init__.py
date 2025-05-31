"""
Shared business logic components for all Visual DM systems.

This module contains shared domain models, repositories, schemas, and business rules
that are used across multiple systems in the Visual DM backend.
"""

# Import shared database components
from . import database

__all__ = [
    'database',
] 