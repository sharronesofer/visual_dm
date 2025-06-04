"""
Equipment Quality Configuration

Defines quality tiers and their impacts on durability, repair costs, and value.
Updated to match Development Bible specification using "masterwork" terminology.
"""

from enum import Enum
from typing import Dict, Any, Tuple
from datetime import timedelta

class EquipmentQuality(Enum):
    """Equipment quality levels per Development Bible"""
    BASIC = "basic"
    MILITARY = "military" 
    SUPERIOR = "superior"
    ELITE = "elite"
    MASTERWORK = "masterwork"

class QualityConfig:
    """Configuration for equipment quality tiers"""
    
    # Durability periods per quality tier (weeks)
    DURABILITY_PERIODS = {
        EquipmentQuality.BASIC: timedelta(weeks=1),         # 1 week
        EquipmentQuality.MILITARY: timedelta(weeks=2),      # 2 weeks
        EquipmentQuality.SUPERIOR: timedelta(weeks=3),      # 3 weeks
        EquipmentQuality.ELITE: timedelta(weeks=4),         # 4 weeks
        EquipmentQuality.MASTERWORK: timedelta(weeks=5)     # 5 weeks
    }
    
    # Repair cost multipliers per Bible specification
    BASE_REPAIR_COST = 500
    REPAIR_COST_MULTIPLIERS = {
        EquipmentQuality.BASIC: 1.0,        # 500 gold base
        EquipmentQuality.MILITARY: 1.5,     # 750 gold base
        EquipmentQuality.SUPERIOR: 2.0,     # 1000 gold base
        EquipmentQuality.ELITE: 2.5,        # 1500 gold base
        EquipmentQuality.MASTERWORK: 3.0    # 2000 gold base
    }
    
    # Value multipliers per Bible specification  
    VALUE_MULTIPLIERS = {
        EquipmentQuality.BASIC: 1.0,
        EquipmentQuality.MILITARY: 1.5,
        EquipmentQuality.SUPERIOR: 2.0,
        EquipmentQuality.ELITE: 2.5,
        EquipmentQuality.MASTERWORK: 3.0
    }
    
    # Sprite suffixes for visual differentiation
    SPRITE_SUFFIXES = {
        EquipmentQuality.BASIC: "",
        EquipmentQuality.MILITARY: "_military",
        EquipmentQuality.SUPERIOR: "_superior", 
        EquipmentQuality.ELITE: "_elite",
        EquipmentQuality.MASTERWORK: "_masterwork"
    }
    
    @classmethod
    def get_durability_period(cls, quality: EquipmentQuality) -> timedelta:
        """Get the durability period for a quality level"""
        return cls.DURABILITY_PERIODS[quality]
    
    @classmethod
    def get_repair_cost(cls, quality: EquipmentQuality, base_item_value: float = None) -> float:
        """Calculate repair cost for a quality level"""
        if base_item_value:
            # Use item value as base if provided
            base_cost = base_item_value * 0.1  # 10% of item value
        else:
            # Use standard base cost
            base_cost = cls.BASE_REPAIR_COST
            
        return base_cost * cls.REPAIR_COST_MULTIPLIERS[quality]
    
    @classmethod
    def get_item_value(cls, base_value: float, quality: EquipmentQuality) -> float:
        """Calculate item value based on quality"""
        return base_value * cls.VALUE_MULTIPLIERS[quality]
    
    @classmethod
    def get_sprite_path(cls, base_sprite: str, quality: EquipmentQuality) -> str:
        """Get sprite path for quality level"""
        if '.' in base_sprite:
            name, ext = base_sprite.rsplit('.', 1)
            return f"{name}{cls.SPRITE_SUFFIXES[quality]}.{ext}"
        else:
            return f"{base_sprite}{cls.SPRITE_SUFFIXES[quality]}"
    
    @classmethod
    def calculate_decay_rate(cls, quality: EquipmentQuality) -> float:
        """Calculate daily durability decay rate for quality level"""
        period = cls.get_durability_period(quality)
        # Assuming 100% durability decays over the period
        # Return daily decay rate
        return 100.0 / period.days

def get_quality_stats(quality: EquipmentQuality, base_item_value: float = 100.0) -> Dict[str, Any]:
    """Get comprehensive stats for an equipment quality level"""
    return {
        "quality": quality.value,
        "durability_period_days": QualityConfig.get_durability_period(quality).days,
        "repair_cost": QualityConfig.get_repair_cost(quality, base_item_value),
        "value_multiplier": QualityConfig.VALUE_MULTIPLIERS[quality],
        "item_value": QualityConfig.get_item_value(base_item_value, quality),
        "daily_decay_rate": QualityConfig.calculate_decay_rate(quality),
        "sprite_suffix": QualityConfig.SPRITE_SUFFIXES[quality]
    } 