"""Repositories for religion system"""

# Import repository components
try:
    from .repository import (
        ReligionRepository,
        create_religion_repository,
        get_religion_repository
    )
except ImportError:
    # Repository may have import issues
    pass

__all__ = [
    "ReligionRepository",
    "create_religion_repository", 
    "get_religion_repository"
]

