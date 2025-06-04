"""
Equipment Quality Service

Handles quality progression, durability scaling, and quality-based modifiers
for the equipment system.
"""

from typing import Dict, Any, Optional, List
from enum import Enum
import json
import os
from pathlib import Path

class EquipmentQuality(str, Enum):
    """Equipment quality levels."""
    BASIC = "basic"
    MILITARY = "military" 
    NOBLE = "noble"

class EquipmentQualityService:
    """Service for managing equipment quality mechanics."""
    
    def __init__(self):
        self._quality_data = None
        self._load_quality_data()
    
    def _load_quality_data(self):
        """Load quality tier data from JSON configuration."""
        try:
            # Get the path to the moved data directory
            project_root = Path(__file__).parent.parent.parent.parent
            data_dir = project_root / "data" / "systems" / "equipment"
            quality_file = data_dir / "quality_tiers.json"
            
            if quality_file.exists():
                with open(quality_file, 'r') as f:
                    self._quality_data = json.load(f)
            else:
                # Fallback default quality data
                self._quality_data = {
                    "basic": {
                        "name": "Basic",
                        "description": "Standard quality equipment",
                        "durability_multiplier": 1.0,
                        "stat_multiplier": 1.0,
                        "enchantment_slots": 1,
                        "max_enchantment_rarity": "rare"
                    },
                    "military": {
                        "name": "Military",
                        "description": "Military-grade equipment",
                        "durability_multiplier": 1.5,
                        "stat_multiplier": 1.3,
                        "enchantment_slots": 2,
                        "max_enchantment_rarity": "epic"
                    },
                    "noble": {
                        "name": "Noble",
                        "description": "Luxury equipment for nobility",
                        "durability_multiplier": 2.0,
                        "stat_multiplier": 1.6,
                        "enchantment_slots": 3,
                        "max_enchantment_rarity": "legendary"
                    }
                }
        except Exception as e:
            print(f"Warning: Could not load quality data: {e}")
            self._quality_data = {}
    
    def get_quality_info(self, quality: str) -> Optional[Dict[str, Any]]:
        """Get complete information about a quality tier."""
        return self._quality_data.get(quality.lower())
    
    def get_durability_multiplier(self, quality: str) -> float:
        """Get the durability multiplier for a quality tier."""
        quality_info = self.get_quality_info(quality)
        return quality_info.get('durability_multiplier', 1.0) if quality_info else 1.0
    
    def get_stat_multiplier(self, quality: str) -> float:
        """Get the stat multiplier for a quality tier."""
        quality_info = self.get_quality_info(quality)
        return quality_info.get('stat_multiplier', 1.0) if quality_info else 1.0
    
    def get_enchantment_slots(self, quality: str) -> int:
        """Get the number of enchantment slots for a quality tier."""
        quality_info = self.get_quality_info(quality)
        return quality_info.get('enchantment_slots', 1) if quality_info else 1
    
    def get_max_enchantment_rarity(self, quality: str) -> str:
        """Get the maximum enchantment rarity this quality can support."""
        quality_info = self.get_quality_info(quality)
        return quality_info.get('max_enchantment_rarity', 'common') if quality_info else 'common'
    
    def get_all_qualities(self) -> List[str]:
        """Get list of all available quality tiers."""
        return list(self._quality_data.keys())
    
    def is_valid_quality(self, quality: str) -> bool:
        """Check if a quality tier exists."""
        return quality.lower() in self._quality_data
    
    def can_support_enchantment_rarity(self, quality: str, enchantment_rarity: str) -> bool:
        """Check if a quality tier can support a specific enchantment rarity."""
        max_rarity = self.get_max_enchantment_rarity(quality)
        
        # Define rarity hierarchy
        rarity_order = ['common', 'rare', 'epic', 'legendary']
        
        try:
            max_index = rarity_order.index(max_rarity.lower())
            enchant_index = rarity_order.index(enchantment_rarity.lower())
            return enchant_index <= max_index
        except ValueError:
            return False
    
    def get_upgrade_path(self, current_quality: str) -> Optional[str]:
        """Get the next quality tier in the upgrade path."""
        qualities = ['basic', 'military', 'noble']
        try:
            current_index = qualities.index(current_quality.lower())
            if current_index < len(qualities) - 1:
                return qualities[current_index + 1]
        except ValueError:
            pass
        return None
    
    def get_quality_modifier_for_stat(self, quality: str, base_value: float) -> float:
        """Apply quality modifier to a base stat value."""
        multiplier = self.get_stat_multiplier(quality)
        return base_value * multiplier
    
    def get_quality_modified_durability(self, quality: str, base_durability: int) -> int:
        """Apply quality modifier to base durability."""
        multiplier = self.get_durability_multiplier(quality)
        return int(base_durability * multiplier)
    
    def get_repair_cost_modifier(self, quality: str) -> float:
        """Get repair cost modifier based on quality."""
        # Higher quality equipment costs more to repair
        quality_modifiers = {
            'basic': 1.0,
            'military': 1.5, 
            'noble': 2.0
        }
        return quality_modifiers.get(quality.lower(), 1.0)
    
    def get_quality_description(self, quality: str) -> str:
        """Get a human-readable description of the quality tier."""
        quality_info = self.get_quality_info(quality)
        if quality_info:
            return f"{quality_info.get('name', quality.title())}: {quality_info.get('description', 'No description available.')}"
        return f"Unknown quality: {quality}" 