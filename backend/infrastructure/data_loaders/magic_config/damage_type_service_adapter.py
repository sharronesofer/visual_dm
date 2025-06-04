"""
Damage Type Service Adapter

This adapter implements the DamageTypeService protocol using the existing
damage type infrastructure, bridging business logic with technical infrastructure.
"""

from typing import List, Optional

from backend.systems.magic.services.magic_business_service import DamageTypeService
from backend.infrastructure.data.json_config_loader import (
    get_config_loader,
    validate_config_id,
    ConfigurationType
)


class DamageTypeServiceAdapter(DamageTypeService):
    """Adapter that implements DamageTypeService using existing infrastructure"""
    
    def __init__(self):
        self.config_loader = get_config_loader()
    
    def validate_damage_type(self, damage_type_id: str) -> bool:
        """Validate a damage type ID"""
        return validate_config_id(damage_type_id, ConfigurationType.DAMAGE_TYPE)
    
    def get_environmental_damage_modifier(self, damage_type_id: str, environment: str) -> float:
        """Get environmental damage modifier"""
        modifiers = self.config_loader.get_environmental_damage_modifiers()
        environment_mods = modifiers.get(environment, {})
        return environment_mods.get(damage_type_id, 1.0)
    
    def calculate_damage_interaction(self, attacker_type: str, defender_type: str) -> float:
        """Calculate damage interaction multiplier"""
        interactions = self.config_loader.get_damage_interactions()
        return interactions.get('type_interactions', {}).get(f"{attacker_type}_vs_{defender_type}", 1.0)
    
    def get_damage_resistances(self, damage_type_id: str) -> Optional[List[str]]:
        """Get damage resistances for a type"""
        damage_data = self.config_loader.get_damage_type(damage_type_id)
        return damage_data.get('resistances') if damage_data else None
    
    def get_damage_vulnerabilities(self, damage_type_id: str) -> Optional[List[str]]:
        """Get damage vulnerabilities for a type"""
        damage_data = self.config_loader.get_damage_type(damage_type_id)
        return damage_data.get('vulnerabilities') if damage_data else None


def create_damage_type_service() -> DamageTypeServiceAdapter:
    """Factory function to create damage type service adapter"""
    return DamageTypeServiceAdapter() 