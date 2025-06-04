"""
Disease System Repositories

Database access layer for disease system entities following 
repository pattern with protocol-based dependency injection.
"""

from .disease_repository import (
    DiseaseRepository,
    get_disease_repository
)
from .disease_outbreak_repository import (
    DiseaseOutbreakRepository, 
    get_disease_outbreak_repository
)

__all__ = [
    'DiseaseRepository',
    'get_disease_repository',
    'DiseaseOutbreakRepository',
    'get_disease_outbreak_repository'
] 