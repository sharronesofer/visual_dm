"""
Loot Configuration Interface - Business Logic Layer

This module provides business logic interfaces for loot configuration,
delegating technical file operations to the infrastructure layer.
"""

from typing import Dict, Any, Optional
from backend.infrastructure.config_loaders.loot_config_loader import (
    config_loader as infrastructure_config_loader,
    DEFAULT_RARITY_CHANCES,
    DEFAULT_RARITY_MULTIPLIERS
)


class LootConfigInterface:
    """Business logic interface for loot configuration access."""
    
    def __init__(self, infrastructure_loader=None):
        """
        Initialize the config interface.
        
        Args:
            infrastructure_loader: Optional infrastructure config loader for dependency injection
        """
        self.infrastructure_loader = infrastructure_loader or infrastructure_config_loader
    
    def get_rarity_config(self) -> Dict[str, Any]:
        """Get item rarity configuration."""
        return self.infrastructure_loader.get_rarity_config()
    
    def get_economic_config(self) -> Dict[str, Any]:
        """Get economic factors and pricing configuration."""
        return self.infrastructure_loader.get_economic_config()
    
    def get_shop_config(self) -> Dict[str, Any]:
        """Get shop types and specializations configuration."""
        return self.infrastructure_loader.get_shop_config()
    
    def get_environmental_config(self) -> Dict[str, Any]:
        """Get biome and motif effects configuration."""
        return self.infrastructure_loader.get_environmental_config()
    
    def get_rarity_chances(self) -> Dict[str, float]:
        """Get just the rarity chance values."""
        return self.infrastructure_loader.get_rarity_chances()
    
    def get_rarity_multipliers(self) -> Dict[str, float]:
        """Get just the rarity value multipliers."""
        return self.infrastructure_loader.get_rarity_multipliers()
    
    def get_shop_type_config(self, shop_type: str) -> Dict[str, Any]:
        """
        Get configuration for a specific shop type.
        
        Args:
            shop_type: The shop type to get config for
            
        Returns:
            Configuration dict for the shop type
        """
        return self.infrastructure_loader.get_shop_type_config(shop_type)
    
    def get_biome_effects(self, biome: str) -> Dict[str, Any]:
        """
        Get biome-specific loot effects.
        
        Args:
            biome: The biome name to get effects for
            
        Returns:
            Biome effects configuration
        """
        return self.infrastructure_loader.get_biome_effects(biome)
    
    def get_motif_effects(self, motif: str) -> Dict[str, Any]:
        """
        Get motif-specific loot effects.
        
        Args:
            motif: The motif name to get effects for
            
        Returns:
            Motif effects configuration
        """
        return self.infrastructure_loader.get_motif_effects(motif)
    
    def get_economic_factors(self) -> Dict[str, Any]:
        """Get economic factor configuration."""
        return self.infrastructure_loader.get_economic_factors()
    
    def get_supply_demand_config(self) -> Dict[str, Any]:
        """Get supply and demand configuration."""
        return self.infrastructure_loader.get_supply_demand_config()


# Global instance for business logic
config_loader = LootConfigInterface()


# Convenience functions for backward compatibility
def get_rarity_chances() -> Dict[str, float]:
    """Get item rarity chances."""
    return config_loader.get_rarity_chances()


def get_rarity_multipliers() -> Dict[str, float]:
    """Get item rarity value multipliers."""
    return config_loader.get_rarity_multipliers()


def get_shop_config(shop_type: str) -> Dict[str, Any]:
    """Get configuration for a specific shop type."""
    return config_loader.get_shop_type_config(shop_type)


def get_biome_effects(biome: str) -> Dict[str, Any]:
    """Get biome-specific loot effects."""
    return config_loader.get_biome_effects(biome)


def get_motif_effects(motif: str) -> Dict[str, Any]:
    """Get motif-specific loot effects."""
    return config_loader.get_motif_effects(motif)


def get_economic_factors() -> Dict[str, Any]:
    """Get economic factor configuration."""
    return config_loader.get_economic_factors() 