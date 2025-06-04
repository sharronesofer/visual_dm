"""
Inventory System Configuration Loader

This module provides configuration loading and management for the inventory system
according to the Development Bible infrastructure standards.
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

from backend.systems.inventory.models import InventoryType, InventoryStatus, EncumbranceLevel
from backend.systems.inventory.protocols import InventoryConfigurationService


class InventoryConfigurationLoader:
    """Configuration loader for inventory system JSON files"""
    
    def __init__(self, config_path: str = "data/systems/inventory"):
        self.config_path = Path(config_path)
        self._inventory_types: Dict[str, Any] = {}
        self._inventory_statuses: Dict[str, Any] = {}
        self._inventory_rules: Dict[str, Any] = {}
        self._loaded = False
    
    def load_configurations(self) -> None:
        """Load all configuration files"""
        try:
            # Load inventory types
            types_file = self.config_path / "inventory_types.json"
            if types_file.exists():
                with open(types_file, 'r', encoding='utf-8') as f:
                    self._inventory_types = json.load(f)
            else:
                self._inventory_types = self._get_default_types()
            
            # Load inventory statuses
            statuses_file = self.config_path / "inventory_statuses.json"
            if statuses_file.exists():
                with open(statuses_file, 'r', encoding='utf-8') as f:
                    self._inventory_statuses = json.load(f)
            else:
                self._inventory_statuses = self._get_default_statuses()
            
            # Load inventory rules
            rules_file = self.config_path / "inventory_rules.json"
            if rules_file.exists():
                with open(rules_file, 'r', encoding='utf-8') as f:
                    self._inventory_rules = json.load(f)
            else:
                self._inventory_rules = self._get_default_rules()
            
            self._loaded = True
            
        except Exception as e:
            raise RuntimeError(f"Failed to load inventory configurations: {e}")
    
    def _ensure_loaded(self) -> None:
        """Ensure configurations are loaded"""
        if not self._loaded:
            self.load_configurations()
    
    def get_inventory_types(self) -> Dict[str, Any]:
        """Get all inventory type configurations"""
        self._ensure_loaded()
        return self._inventory_types.copy()
    
    def get_inventory_type_config(self, inventory_type: str) -> Dict[str, Any]:
        """Get configuration for specific inventory type"""
        self._ensure_loaded()
        return self._inventory_types.get(inventory_type, {})
    
    def get_inventory_statuses(self) -> Dict[str, Any]:
        """Get all inventory status configurations"""
        self._ensure_loaded()
        return self._inventory_statuses.copy()
    
    def get_inventory_rules(self) -> Dict[str, Any]:
        """Get all inventory rules"""
        self._ensure_loaded()
        return self._inventory_rules.copy()
    
    def get_status_transitions(self) -> Dict[str, List[str]]:
        """Get allowed status transitions"""
        self._ensure_loaded()
        return self._inventory_statuses.get("transitions", self._get_default_transitions())
    
    def get_encumbrance_settings(self) -> Dict[str, Any]:
        """Get encumbrance level settings"""
        self._ensure_loaded()
        return self._inventory_rules.get("encumbrance", self._get_default_encumbrance_settings())
    
    def get_capacity_settings(self) -> Dict[str, Any]:
        """Get capacity management settings"""
        self._ensure_loaded()
        return self._inventory_rules.get("capacity", self._get_default_capacity_settings())
    
    def _get_default_types(self) -> Dict[str, Any]:
        """Get default inventory type configurations"""
        return {
            "character": {
                "default_capacity": 50,
                "default_weight_limit": 100.0,
                "allows_trading": True,
                "allows_sorting": True,
                "allows_filtering": True,
                "default_sort": "name",
                "available_filters": ["type", "rarity", "equipped", "category", "weight"],
                "description": "Personal character inventory"
            },
            "container": {
                "default_capacity": 20,
                "default_weight_limit": 500.0,
                "allows_trading": False,
                "allows_sorting": True,
                "allows_filtering": True,
                "default_sort": "date_added",
                "available_filters": ["type", "category", "weight"],
                "description": "Static world container (chest, barrel, etc.)"
            },
            "shop": {
                "default_capacity": 200,
                "default_weight_limit": None,
                "allows_trading": True,
                "allows_sorting": True,
                "allows_filtering": True,
                "default_sort": "value",
                "available_filters": ["type", "rarity", "category", "value", "weight"],
                "description": "Merchant shop inventory"
            },
            "bank": {
                "default_capacity": 100,
                "default_weight_limit": None,
                "allows_trading": False,
                "allows_sorting": True,
                "allows_filtering": True,
                "default_sort": "value",
                "available_filters": ["type", "rarity", "category", "value"],
                "description": "Player bank storage"
            },
            "quest": {
                "default_capacity": 10,
                "default_weight_limit": 50.0,
                "allows_trading": False,
                "allows_sorting": False,
                "allows_filtering": False,
                "default_sort": "quest_order",
                "available_filters": [],
                "description": "Quest-specific item container"
            }
        }
    
    def _get_default_statuses(self) -> Dict[str, Any]:
        """Get default inventory status configurations"""
        return {
            "statuses": {
                "active": {
                    "description": "Inventory is active and operational",
                    "allows_operations": True,
                    "allows_item_operations": True,
                    "allows_modifications": True
                },
                "inactive": {
                    "description": "Inventory is temporarily disabled",
                    "allows_operations": False,
                    "allows_item_operations": False,
                    "allows_modifications": True
                },
                "maintenance": {
                    "description": "Inventory is under maintenance",
                    "allows_operations": False,
                    "allows_item_operations": False,
                    "allows_modifications": False
                },
                "archived": {
                    "description": "Inventory is archived (read-only)",
                    "allows_operations": False,
                    "allows_item_operations": False,
                    "allows_modifications": False
                },
                "corrupted": {
                    "description": "Inventory data is corrupted",
                    "allows_operations": False,
                    "allows_item_operations": False,
                    "allows_modifications": False
                }
            },
            "transitions": self._get_default_transitions()
        }
    
    def _get_default_transitions(self) -> Dict[str, List[str]]:
        """Get default status transitions"""
        return {
            "active": ["inactive", "maintenance", "archived"],
            "inactive": ["active", "archived"],
            "maintenance": ["active", "inactive", "archived"],  # Allow maintenance -> archived
            "archived": [],  # Terminal state
            "corrupted": ["maintenance", "archived"]
        }
    
    def _get_default_rules(self) -> Dict[str, Any]:
        """Get default inventory rules"""
        return {
            "capacity": self._get_default_capacity_settings(),
            "encumbrance": self._get_default_encumbrance_settings(),
            "validation": {
                "min_name_length": 1,
                "max_name_length": 255,
                "max_description_length": 1000,
                "allowed_characters": "alphanumeric_spaces_punctuation"
            },
            "business_rules": {
                "allow_duplicate_names_per_player": False,
                "allow_duplicate_names_globally": True,
                "auto_cleanup_empty_inventories": False,
                "max_inventories_per_player": 50,
                "max_inventories_per_character": 10
            }
        }
    
    def _get_default_capacity_settings(self) -> Dict[str, Any]:
        """Get default capacity settings"""
        return {
            "weight_calculation": {
                "strength_multiplier": 10.0,
                "base_weight_limit": 100.0,
                "overload_threshold": 1.25  # 25% overload allowed
            },
            "warnings": {
                "capacity_warning_threshold": 0.8,  # 80%
                "weight_warning_threshold": 0.8,    # 80%
                "overload_warning_threshold": 1.0   # 100%
            },
            "limits": {
                "min_capacity": 1,
                "max_capacity": 1000,
                "min_weight_limit": 0.0,
                "max_weight_limit": 10000.0
            }
        }
    
    def _get_default_encumbrance_settings(self) -> Dict[str, Any]:
        """Get default encumbrance settings"""
        return {
            "thresholds": {
                "normal": 0.75,     # 0-75% of weight limit
                "heavy": 1.0,       # 75-100% of weight limit
                "encumbered": 1.25, # 100-125% of weight limit
                "overloaded": 999.0 # 125%+ of weight limit
            },
            "effects": {
                "normal": {
                    "movement_mp_multiplier": 1.0,
                    "stealth_penalty": 0,
                    "agility_penalty": 0,
                    "warning_message": None
                },
                "heavy": {
                    "movement_mp_multiplier": 1.2,
                    "stealth_penalty": -1,
                    "agility_penalty": -1,
                    "warning_message": "You are carrying a heavy load"
                },
                "encumbered": {
                    "movement_mp_multiplier": 1.5,
                    "stealth_penalty": -3,
                    "agility_penalty": -2,
                    "warning_message": "You are encumbered and moving slowly"
                },
                "overloaded": {
                    "movement_mp_multiplier": 2.0,
                    "stealth_penalty": -5,
                    "agility_penalty": -3,
                    "warning_message": "You are severely overloaded!"
                }
            }
        }


class ConfigurableInventoryService(InventoryConfigurationService):
    """Implementation of InventoryConfigurationService using the configuration loader"""
    
    def __init__(self, config_loader: Optional[InventoryConfigurationLoader] = None):
        self.config_loader = config_loader or InventoryConfigurationLoader()
    
    def get_inventory_type_config(self, inventory_type: InventoryType) -> Dict[str, Any]:
        """Get configuration for inventory type"""
        return self.config_loader.get_inventory_type_config(inventory_type.value)
    
    def get_status_transitions(self) -> Dict[str, List[str]]:
        """Get allowed status transitions"""
        return self.config_loader.get_status_transitions()
    
    def can_transition_status(self, from_status: InventoryStatus, to_status: InventoryStatus) -> bool:
        """Check if status transition is allowed"""
        transitions = self.get_status_transitions()
        return to_status.value in transitions.get(from_status.value, [])
    
    def calculate_movement_mp_multiplier(self, encumbrance_level: EncumbranceLevel) -> float:
        """Calculate movement MP multiplier for encumbrance level"""
        encumbrance_settings = self.config_loader.get_encumbrance_settings()
        effects = encumbrance_settings.get("effects", {})
        level_effects = effects.get(encumbrance_level.value, {})
        return level_effects.get("movement_mp_multiplier", 1.0)
    
    def get_encumbrance_effects(self, encumbrance_level: EncumbranceLevel) -> Dict[str, Any]:
        """Get all effects for an encumbrance level"""
        encumbrance_settings = self.config_loader.get_encumbrance_settings()
        effects = encumbrance_settings.get("effects", {})
        return effects.get(encumbrance_level.value, {})
    
    def calculate_max_weight_from_strength(self, strength: int) -> float:
        """Calculate max weight capacity from character strength"""
        capacity_settings = self.config_loader.get_capacity_settings()
        weight_calc = capacity_settings.get("weight_calculation", {})
        multiplier = weight_calc.get("strength_multiplier", 10.0)
        return float(strength * multiplier)
    
    def get_capacity_warning_thresholds(self) -> Dict[str, float]:
        """Get capacity warning thresholds"""
        capacity_settings = self.config_loader.get_capacity_settings()
        return capacity_settings.get("warnings", {})
    
    def validate_inventory_name(self, name: str) -> Dict[str, Any]:
        """Validate inventory name according to rules"""
        rules = self.config_loader.get_inventory_rules()
        validation = rules.get("validation", {})
        
        min_length = validation.get("min_name_length", 1)
        max_length = validation.get("max_name_length", 255)
        
        errors = []
        if len(name) < min_length:
            errors.append(f"Name must be at least {min_length} characters")
        if len(name) > max_length:
            errors.append(f"Name must be no more than {max_length} characters")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def get_business_rules(self) -> Dict[str, Any]:
        """Get business rules configuration"""
        rules = self.config_loader.get_inventory_rules()
        return rules.get("business_rules", {}) 