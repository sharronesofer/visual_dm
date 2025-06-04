"""Models for equipment system

DEPRECATED: This module has been moved to backend.infrastructure.equipment.models
Please update your imports to use the new location.

Example:
    # Old (deprecated):
    from backend.systems.equipment.models import EquipmentEntity
    
    # New (correct):
    from backend.infrastructure.systems.equipment.models import EquipmentEntity
"""

import warnings

# Import new quality system
from .equipment_quality import EquipmentQuality, QualityConfig, get_quality_stats

def __getattr__(name):
    """Provide deprecation warnings for old imports"""
    warnings.warn(
        f"Importing {name} from backend.systems.equipment.models is deprecated. "
        f"Please import from backend.infrastructure.systems.equipment.models instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    # Import and return the actual class from infrastructure
    from backend.infrastructure.systems.equipment.models import models as infra_models
    return getattr(infra_models, name)

# List of available classes for reference
__all__ = [
    # Infrastructure models (deprecated location)
    'EquipmentBaseModel',
    'EquipmentModel',
    'EquipmentEntity', 
    'Equipment',
    'EquipmentDurabilityLog',
    'EquipmentSet',
    'CreateEquipmentRequest',
    'UpdateEquipmentRequest',
    'EquipmentResponse',
    'EquipmentListResponse',
    
    # New quality system
    'EquipmentQuality',
    'QualityConfig', 
    'get_quality_stats'
]
