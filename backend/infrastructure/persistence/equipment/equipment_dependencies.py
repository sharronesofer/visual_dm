"""
Equipment System Dependencies

Provides simplified dependency resolution for equipment system components
without complex FastAPI dependency injection patterns that cause issues.
"""

from typing import Optional

# Import simplified repositories
from backend.infrastructure.persistence.equipment.equipment_template_repository import EquipmentTemplateRepository
from backend.infrastructure.persistence.equipment.equipment_instance_repository_simple import EquipmentInstanceRepositorySimple
from backend.systems.equipment.services.business_logic_service import EquipmentBusinessLogicService

# Type aliases for clarity
EquipmentInstanceRepoType = EquipmentInstanceRepositorySimple
EquipmentTemplateRepoType = EquipmentTemplateRepository
BusinessLogicServiceType = EquipmentBusinessLogicService

# Global instances (singleton pattern for simplicity)
_instance_repo: Optional[EquipmentInstanceRepositorySimple] = None
_template_repo: Optional[EquipmentTemplateRepository] = None
_business_logic: Optional[EquipmentBusinessLogicService] = None


def get_equipment_instance_repository() -> EquipmentInstanceRepositorySimple:
    """Get equipment instance repository (singleton)."""
    global _instance_repo
    if _instance_repo is None:
        _instance_repo = EquipmentInstanceRepositorySimple()
    return _instance_repo


def get_equipment_template_repository() -> EquipmentTemplateRepository:
    """Get equipment template repository (singleton)."""
    global _template_repo
    if _template_repo is None:
        _template_repo = EquipmentTemplateRepository()
    return _template_repo


def get_equipment_business_logic_service() -> EquipmentBusinessLogicService:
    """Get equipment business logic service (singleton)."""
    global _business_logic
    if _business_logic is None:
        _business_logic = EquipmentBusinessLogicService()
    return _business_logic


def reset_dependencies():
    """Reset all dependencies (useful for testing)."""
    global _instance_repo, _template_repo, _business_logic
    _instance_repo = None
    _template_repo = None
    _business_logic = None


# Additional type aliases for complex dependencies
CharacterEquipmentServiceType = object  # Placeholder for character equipment service
SetBonusServiceType = object  # Placeholder for set bonus service 