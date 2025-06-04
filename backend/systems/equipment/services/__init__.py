"""
Equipment System Services - Pure Business Logic

This module provides business logic services for the equipment system
according to the Development Bible standards.

Only contains pure business logic - no infrastructure dependencies to avoid circular imports.
"""

# Local business logic services (systems layer only)
from .enchanting_service import EnchantingService
from .business_logic_service import (
    EquipmentBusinessLogicService, 
    EquipmentInstanceData, 
    EquipmentBaseTemplate, 
    QualityTierData,
    create_equipment_business_service
)
from .character_equipment_service import (
    CharacterEquipmentService,
    CharacterEquipmentSlot,
    CharacterEquipmentLoadout,
    CharacterEquipmentRepository,
    EquipmentTemplateRepository,
    create_character_equipment_service
)

__all__ = [
    # Business logic services (systems layer)
    'EnchantingService',
    'EquipmentBusinessLogicService',
    'EquipmentInstanceData',
    'EquipmentBaseTemplate', 
    'QualityTierData',
    'create_equipment_business_service',
    
    # Character integration services
    'CharacterEquipmentService',
    'CharacterEquipmentSlot',
    'CharacterEquipmentLoadout', 
    'CharacterEquipmentRepository',
    'EquipmentTemplateRepository',
    'create_character_equipment_service'
] 