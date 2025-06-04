"""
Magic Configuration Repository Adapter

This adapter implements the MagicConfigRepository protocol using the technical
magic configuration loader, bridging business logic with technical infrastructure.
"""

from typing import Dict, List, Optional, Any

from backend.systems.magic.services.magic_business_service import MagicConfigRepository
from .magic_config_loader import MagicConfigLoader, get_magic_config_loader


class MagicConfigRepositoryAdapter(MagicConfigRepository):
    """Adapter that implements MagicConfigRepository using MagicConfigLoader"""
    
    def __init__(self, config_loader: Optional[MagicConfigLoader] = None):
        self.config_loader = config_loader or get_magic_config_loader()
    
    def get_spells(self) -> Dict[str, Any]:
        """Get all spell configurations"""
        return self.config_loader.load_spells()
    
    def get_spell(self, spell_name: str) -> Optional[Dict[str, Any]]:
        """Get specific spell configuration"""
        return self.config_loader.get_spell(spell_name)
    
    def get_magic_domains(self) -> Dict[str, Any]:
        """Get all magic domain configurations"""
        return self.config_loader.load_magic_domains()
    
    def get_domain(self, domain_name: str) -> Optional[Dict[str, Any]]:
        """Get specific domain configuration"""
        return self.config_loader.get_domain(domain_name)
    
    def get_combat_rules(self) -> Dict[str, Any]:
        """Get spell school combat rules"""
        return self.config_loader.load_combat_rules()
    
    def get_concentration_rules(self) -> Dict[str, Any]:
        """Get concentration rules"""
        return self.config_loader.load_concentration_rules()


def create_magic_config_repository() -> MagicConfigRepositoryAdapter:
    """Factory function to create magic config repository adapter"""
    return MagicConfigRepositoryAdapter() 