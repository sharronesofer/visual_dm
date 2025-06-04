"""
Rumor System Infrastructure Components

This module contains all technical infrastructure for the rumor system,
separated from business logic in backend.systems.rumor.
"""

# Import technical services
from .services.validation_service import DefaultRumorValidationService, create_rumor_validation_service
from .repositories.rumor_repository import SQLAlchemyRumorRepository, create_rumor_repository
from .npc_rumor_service import NPCRumorDatabaseService, DatabaseInterface

__all__ = [
    "DefaultRumorValidationService",
    "create_rumor_validation_service",
    "SQLAlchemyRumorRepository",
    "create_rumor_repository",
    "NPCRumorDatabaseService",
    "DatabaseInterface"
]

# Note: Imports are available in submodules to avoid circular dependencies
# Use: from backend.infrastructure.systems.rumor.models.models import RumorEntity
# Use: from backend.infrastructure.systems.rumor.repositories.rumor_repository import SQLAlchemyRumorRepository
# etc. 