"""
Equipment System Repository Interfaces - Business Logic Layer

This module defines repository abstractions for equipment data access
according to the Development Bible standards. Contains ONLY business logic
interfaces - actual implementations belong in /backend/infrastructure/.

Key Components:
- Repository protocols/interfaces for dependency injection
- Business domain abstractions
- No database or file I/O implementations
"""

from typing import Protocol, List, Optional, Dict, Any
from uuid import UUID

from backend.systems.equipment.services.business_logic_service import (
    EquipmentInstanceData, EquipmentBaseTemplate, EquipmentSetData, EquipmentSlot,
    QualityTierData, RarityTierData
)


class IEquipmentInstanceRepository(Protocol):
    """Business logic interface for equipment instance persistence"""
    
    def create_equipment(self, equipment_data: EquipmentInstanceData) -> EquipmentInstanceData:
        """Create a new equipment instance"""
        ...
    
    def get_equipment_by_id(self, equipment_id: UUID) -> Optional[EquipmentInstanceData]:
        """Get equipment instance by ID"""
        ...
    
    def get_character_equipment(self, character_id: UUID, 
                              equipped_only: bool = False) -> List[EquipmentInstanceData]:
        """Get all equipment for a character"""
        ...
    
    def list_equipment(self, character_id: Optional[UUID] = None, slot: Optional[EquipmentSlot] = None,
                      equipment_set: Optional[str] = None, quality_tier: Optional[str] = None,
                      limit: int = 100, offset: int = 0) -> List[EquipmentInstanceData]:
        """List equipment with optional filters"""
        ...
    
    def update_equipment(self, equipment_id: UUID, updates: Dict[str, Any]) -> EquipmentInstanceData:
        """Update equipment instance"""
        ...
    
    def delete_equipment(self, equipment_id: UUID) -> bool:
        """Delete equipment instance"""
        ...


class IEquipmentTemplateRepository(Protocol):
    """Business logic interface for equipment template access"""
    
    def get_template(self, template_id: str) -> Optional[EquipmentBaseTemplate]:
        """Get equipment base template by ID"""
        ...
    
    def get_all_templates(self) -> List[EquipmentBaseTemplate]:
        """Get all available equipment templates"""
        ...
    
    def get_templates_by_slot(self, slot: EquipmentSlot) -> List[EquipmentBaseTemplate]:
        """Get templates for specific equipment slot"""
        ...
    
    def get_templates_by_set(self, equipment_set: str) -> List[EquipmentBaseTemplate]:
        """Get templates for specific equipment set"""
        ...
    
    def get_quality_tier(self, tier_id: str) -> Optional[QualityTierData]:
        """Get quality tier data"""
        ...
    
    def get_all_quality_tiers(self) -> List[QualityTierData]:
        """Get all quality tiers"""
        ...
    
    def get_rarity_tier(self, tier_id: str) -> Optional[RarityTierData]:
        """Get rarity tier data"""
        ...
    
    def get_all_rarity_tiers(self) -> List[RarityTierData]:
        """Get all rarity tiers"""
        ...
    
    def get_equipment_set(self, set_id: str) -> Optional[EquipmentSetData]:
        """Get equipment set data"""
        ...
    
    def get_all_equipment_sets(self) -> List[EquipmentSetData]:
        """Get all equipment sets"""
        ...


__all__ = [
    'IEquipmentInstanceRepository',
    'IEquipmentTemplateRepository'
] 