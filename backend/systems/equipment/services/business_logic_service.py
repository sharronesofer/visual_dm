"""
Equipment Business Logic Service - Pure Business Rules

This service contains pure business logic for equipment management according to
Development Bible standards. Handles unique equipment instances with:
- Base type (shared stats like damage, crit, reach)
- Quality tier (3 types: basic, military, masterwork) - affects durability
- Rarity tier (4 types: common, rare, epic, legendary) - affects number of effects
- 3-20+ magical effects (mostly unique per item)
- Character ownership tracking
- Durability management (usage-based, not time-based)
- Set bonus calculations (12 equipment slots total)
"""

from typing import Dict, Any, List, Optional, Tuple
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging

from backend.systems.equipment.models.equipment_models import EquipmentSlot
from backend.systems.equipment.models.equipment_quality import EquipmentQuality, QualityConfig

logger = logging.getLogger(__name__)

class DurabilityStatus(Enum):
    """Durability condition states"""
    EXCELLENT = "excellent"    # 90-100%
    GOOD = "good"             # 75-89%
    WORN = "worn"             # 50-74%
    DAMAGED = "damaged"       # 25-49%
    VERY_DAMAGED = "very_damaged"  # 10-24%
    BROKEN = "broken"         # 0-9%

# Business Domain Models
@dataclass
class EquipmentInstanceData:
    """Business domain model for unique equipment instances"""
    id: UUID
    character_id: UUID
    template_id: str
    slot: EquipmentSlot
    current_durability: int
    max_durability: int
    usage_count: int
    quality_tier: str  # basic, military, masterwork - affects durability
    rarity_tier: str   # common, rare, epic, legendary - affects enchantment slots
    equipment_set: Optional[str]
    is_equipped: bool
    enchantments: List[Dict[str, Any]]
    effective_stats: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_repaired: Optional[datetime] = None
    location: str = "inventory"
    
    def counts_for_set_bonus(self) -> bool:
        """Equipment counts for set bonus only if durability >= 30%"""
        return self.current_durability >= (self.max_durability * 0.3)


@dataclass
class EquipmentBaseTemplate:
    """Business domain model for base equipment templates"""
    template_id: str
    name: str
    slot: EquipmentSlot
    base_stats: Dict[str, Any]
    requirements: Dict[str, Any]
    max_durability: int
    description: str
    equipment_set: Optional[str]
    allowed_quality_tiers: List[str]
    allowed_rarity_tiers: List[str]


@dataclass
class EquipmentSetData:
    """Business domain model for equipment sets"""
    set_id: str
    name: str
    required_slots: set[EquipmentSlot]
    set_bonuses: Dict[str, str]
    lore_description: str


@dataclass
class EnchantmentData:
    """Business domain model for equipment enchantments"""
    enchantment_type: str
    magnitude: float
    target_attribute: Optional[str]
    is_active: bool


class EquipmentBusinessLogicService:
    """Pure business logic for equipment management"""
    
    def __init__(self):
        # Business constants based on user requirements
        self.QUALITY_TIERS = ['basic', 'military', 'noble']
        self.RARITY_TIERS = ['common', 'rare', 'epic', 'legendary']
        self.MIN_MAGICAL_EFFECTS = 1
        self.MAX_MAGICAL_EFFECTS = 4  # Based on legendary rarity tier
        
        # Durability constants (usage-based, not time-based)
        # These represent the number of uses before items are likely to break
        self.QUALITY_DURABILITY_USES = {
            'basic': 168,      # Break after ~168 uses (1 week daily use, ~24 uses per day)
            'military': 336,   # Break after ~336 uses (2 weeks daily use)  
            'masterwork': 672  # Break after ~672 uses (4 weeks daily use)
        }
        
        # Utilization-based decay parameters
        self.UTILIZATION_DECAY_RATES = {
            'basic': {
                'base_decay_per_use': 0.595,  # 100/168 = ~0.595% per use
                'variance_factor': 0.3,        # ±30% variance for realism
                'critical_multiplier': 2.0,    # Critical usage causes more wear
                'failure_threshold': 5.0       # Items start failing below 5% durability
            },
            'military': {
                'base_decay_per_use': 0.298,  # 100/336 = ~0.298% per use
                'variance_factor': 0.25,       # ±25% variance (more consistent)
                'critical_multiplier': 1.8,    # Less critical wear than basic
                'failure_threshold': 3.0       # More reliable at low durability
            },
            'masterwork': {
                'base_decay_per_use': 0.149,  # 100/672 = ~0.149% per use
                'variance_factor': 0.2,        # ±20% variance (most consistent)
                'critical_multiplier': 1.5,    # Least critical wear
                'failure_threshold': 1.0       # Most reliable at low durability
            }
        }
        
        # Usage type multipliers for different activities
        self.USAGE_TYPE_MULTIPLIERS = {
            'light_use': 0.5,      # Casual activities, light combat
            'normal_use': 1.0,     # Regular combat, standard activities
            'heavy_use': 1.5,      # Intense combat, demanding activities
            'extreme_use': 2.0,    # Boss fights, dangerous environments
            'critical_hit': 2.5,   # Critical strikes cause extra wear
            'blocking': 1.2,       # Shields take extra wear when blocking
            'parrying': 1.3,       # Weapons wear more when parrying
            'environmental': 0.8    # Passive environmental wear
        }

        # Set bonus minimum durability threshold
        self.SET_BONUS_MIN_DURABILITY = 30.0
        
        # All 12 equipment slots for set calculations
        self.ALL_EQUIPMENT_SLOTS = list(EquipmentSlot)
        
        # Legacy support for tests
        self.DAILY_USE_HOURS = 8  # Expected daily usage hours for durability calculations
        self.MAX_MAGICAL_EFFECTS_LEGACY = 20  # For backward compatibility with tests
    
    # === CORE BUSINESS RULES ===
    
    def create_equipment_instance(self, character_id: UUID, template: EquipmentBaseTemplate, 
                                quality_tier: str, rarity_tier: str) -> EquipmentInstanceData:
        """
        Business rule: Create a new equipment instance with quality and rarity
        """
        # Calculate max durability based on quality tier
        quality_enum = EquipmentQuality(quality_tier)
        durability_multiplier = QualityConfig.VALUE_MULTIPLIERS.get(quality_enum, 1.0)
        max_durability = template.max_durability * durability_multiplier
        
        # Generate unique equipment ID
        equipment_id = uuid4()
        
        # Create equipment instance
        equipment_data = EquipmentInstanceData(
            id=equipment_id,
            character_id=character_id,
            template_id=template.template_id,
            slot=template.slot,
            current_durability=int(max_durability),
            max_durability=int(max_durability),
            usage_count=0,
            quality_tier=quality_tier,
            rarity_tier=rarity_tier,
            equipment_set=template.equipment_set,
            is_equipped=False,
            enchantments=[],  # Will be populated separately
            effective_stats=template.base_stats.copy(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        logger.info(f"Created equipment instance {equipment_id} for character {character_id}")
        return equipment_data
    
    def equip_item_to_slot(self, character_id: UUID, item: EquipmentInstanceData, slot: EquipmentSlot) -> Dict[str, Any]:
        """
        Business rule: Equip an item to a specific character slot
        """
        try:
            # Validate item can be equipped to this slot
            if item.slot != slot:
                return {
                    "success": False,
                    "error": f"Item cannot be equipped to {slot.value} slot (item is for {item.slot.value})"
                }
            
            # Check if item is functional
            if not self.is_equipment_functional(item.current_durability):
                return {
                    "success": False,
                    "error": "Item is too damaged to be equipped"
                }
            
            # Get dependencies to check for existing item in slot
            from backend.infrastructure.persistence.equipment.equipment_dependencies import (
                get_equipment_instance_repository
            )
            
            instance_repo = get_equipment_instance_repository()
            
            # Check if there's already an item in that slot
            existing_item = instance_repo.get_equipped_item_in_slot(character_id, slot)
            if existing_item:
                # Unequip existing item first
                unequip_result = self.unequip_item_from_slot(character_id, slot)
                if not unequip_result["success"]:
                    return {
                        "success": False,
                        "error": f"Failed to unequip existing item: {unequip_result['error']}"
                    }
            
            # Equip the new item
            item.is_equipped = True
            item.equipment_slot = slot.value
            item.updated_at = datetime.utcnow()
            
            # Update in repository
            updated_item = instance_repo.update_equipment(item)
            
            return {
                "success": True,
                "equipped_item": {
                    "id": updated_item.id,
                    "template_id": updated_item.template_id,
                    "slot": slot.value,
                    "current_durability": updated_item.current_durability,
                    "max_durability": updated_item.max_durability
                },
                "message": f"Item equipped to {slot.value} slot successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to equip item {item.id} to slot {slot.value}: {str(e)}")
            return {
                "success": False,
                "error": f"Equipment operation failed: {str(e)}"
            }
    
    def unequip_item_from_slot(self, character_id: UUID, slot: EquipmentSlot) -> Dict[str, Any]:
        """
        Business rule: Unequip an item from a specific character slot
        """
        try:
            # Get dependencies
            from backend.infrastructure.persistence.equipment.equipment_dependencies import (
                get_equipment_instance_repository
            )
            
            instance_repo = get_equipment_instance_repository()
            
            # Find the equipped item in that slot
            equipped_item = instance_repo.get_equipped_item_in_slot(character_id, slot)
            if not equipped_item:
                return {
                    "success": False,
                    "error": f"No item equipped in {slot.value} slot"
                }
            
            # Unequip the item
            equipped_item.is_equipped = False
            equipped_item.equipment_slot = None
            equipped_item.location = "inventory"
            equipped_item.updated_at = datetime.utcnow()
            
            # Update in repository
            updated_item = instance_repo.update_equipment(equipped_item)
            
            return {
                "success": True,
                "unequipped_item": {
                    "id": updated_item.id,
                    "template_id": updated_item.template_id,
                    "slot": slot.value
                },
                "message": f"Item unequipped from {slot.value} slot successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to unequip item from slot {slot.value}: {str(e)}")
            return {
                "success": False,
                "error": f"Unequip operation failed: {str(e)}"
            }
    
    def swap_equipment_in_slot(self, character_id: UUID, new_item: EquipmentInstanceData, slot: EquipmentSlot) -> Dict[str, Any]:
        """
        Business rule: Swap an equipped item with a new item in one operation
        """
        try:
            # Validate new item can be equipped to this slot
            if new_item.slot != slot:
                return {
                    "success": False,
                    "error": f"Item cannot be equipped to {slot.value} slot (item is for {new_item.slot.value})"
                }
            
            # Check if new item is functional
            if not self.is_equipment_functional(new_item.current_durability):
                return {
                    "success": False,
                    "error": "Item is too damaged to be equipped"
                }
            
            # Get dependencies
            from backend.infrastructure.persistence.equipment.equipment_dependencies import (
                get_equipment_instance_repository
            )
            
            instance_repo = get_equipment_instance_repository()
            
            # Get currently equipped item
            old_item = instance_repo.get_equipped_item_in_slot(character_id, slot)
            
            # Perform the swap
            if old_item:
                # Unequip old item
                old_item.is_equipped = False
                old_item.equipment_slot = None
                old_item.location = "inventory"
                old_item.updated_at = datetime.utcnow()
                instance_repo.update_equipment(old_item)
            
            # Equip new item
            new_item.is_equipped = True
            new_item.equipment_slot = slot.value
            new_item.location = "equipped"
            new_item.updated_at = datetime.utcnow()
            updated_new_item = instance_repo.update_equipment(new_item)
            
            return {
                "success": True,
                "equipped_item": {
                    "id": updated_new_item.id,
                    "template_id": updated_new_item.template_id,
                    "slot": slot.value
                },
                "unequipped_item": {
                    "id": old_item.id,
                    "template_id": old_item.template_id
                } if old_item else None,
                "message": f"Equipment swapped in {slot.value} slot successfully"
            }
            
        except Exception as e:
            logger.error(f"Failed to swap equipment in slot {slot.value}: {str(e)}")
            return {
                "success": False,
                "error": f"Swap operation failed: {str(e)}"
            }
    
    def calculate_character_total_stats(self, equipped_items: List[EquipmentInstanceData]) -> Dict[str, Any]:
        """
        Business rule: Calculate total character stats from equipped items
        """
        total_stats = {}
        
        for item in equipped_items:
            if not item.is_equipped or not self.is_equipment_functional(item.current_durability):
                continue
            
            # Apply durability penalties to stats
            adjusted_stats = self.apply_stat_adjustments_for_durability(item.effective_stats, item.current_durability)
            
            # Add to total stats
            for stat_name, value in adjusted_stats.items():
                if isinstance(value, (int, float)):
                    total_stats[stat_name] = total_stats.get(stat_name, 0) + value
                elif isinstance(value, str) and "%" in value:
                    # Handle percentage bonuses
                    percent_value = float(value.replace("%", ""))
                    total_stats[f"{stat_name}_percent"] = total_stats.get(f"{stat_name}_percent", 0) + percent_value
        
        return total_stats
    
    def calculate_character_set_bonuses(self, equipped_items: List[EquipmentInstanceData]) -> List[Dict[str, Any]]:
        """
        Business rule: Calculate active set bonuses for character
        Set bonuses activate from 3 pieces up to 12 pieces (full set)
        """
        # Group items by equipment set
        set_counts = {}
        for item in equipped_items:
            if (item.is_equipped and 
                item.equipment_set and 
                self.counts_for_set_bonus(item.current_durability)):
                set_counts[item.equipment_set] = set_counts.get(item.equipment_set, 0) + 1
        
        # Load set bonus configurations
        set_bonus_configs = self._load_set_bonus_configurations()
        
        # Calculate active bonuses
        active_bonuses = []
        for set_name, count in set_counts.items():
            if count >= 3:  # Minimum for set bonus is 3 pieces
                set_config = set_bonus_configs.get(set_name)
                if not set_config:
                    continue
                    
                bonus = {
                    "set_name": set_name,
                    "set_display_name": set_config.get("name", set_name),
                    "description": set_config.get("description", ""),
                    "pieces_equipped": count,
                    "total_pieces": 12,  # Always 12 slots total
                    "active_bonuses": [],
                    "total_stats": {},
                    "total_effects": []
                }
                
                # Apply bonuses for each tier the character qualifies for
                set_bonuses = set_config.get("set_bonuses", {})
                for piece_count in range(3, min(count + 1, 13)):  # 3 to current count, max 12
                    piece_str = str(piece_count)
                    if piece_str in set_bonuses:
                        tier_bonus = set_bonuses[piece_str]
                        bonus["active_bonuses"].append({
                            "tier": piece_count,
                            "name": tier_bonus.get("name", f"{piece_count}-piece bonus"),
                            "description": tier_bonus.get("description", ""),
                            "stats": tier_bonus.get("stats", {}),
                            "effects": tier_bonus.get("effects", [])
                        })
                        
                        # Accumulate total stats
                        for stat, value in tier_bonus.get("stats", {}).items():
                            if isinstance(value, (int, float)):
                                bonus["total_stats"][stat] = bonus["total_stats"].get(stat, 0) + value
                            else:
                                bonus["total_stats"][stat] = value  # For boolean values like immunity
                        
                        # Accumulate effects
                        bonus["total_effects"].extend(tier_bonus.get("effects", []))
                
                active_bonuses.append(bonus)
        
        return active_bonuses
    
    def _load_set_bonus_configurations(self) -> Dict[str, Any]:
        """Load set bonus configurations from JSON file"""
        try:
            import json
            import os
            
            # Look for set bonus config file
            config_path = os.path.join("data", "systems", "equipment", "set_bonuses.json")
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config_data = json.load(f)
                    return config_data.get("equipment_sets", {})
            else:
                logger.warning(f"Set bonus configuration not found at {config_path}")
                return {}
        except Exception as e:
            logger.error(f"Failed to load set bonus configurations: {e}")
            return {}
    
    def get_set_bonus_preview(self, set_name: str, current_pieces: int) -> Dict[str, Any]:
        """
        Business rule: Preview what bonuses would be available with more set pieces
        Useful for showing players what they could achieve
        """
        set_configs = self._load_set_bonus_configurations()
        set_config = set_configs.get(set_name)
        
        if not set_config:
            return {"error": f"Set '{set_name}' not found"}
        
        preview = {
            "set_name": set_name,
            "set_display_name": set_config.get("name", set_name),
            "description": set_config.get("description", ""),
            "current_pieces": current_pieces,
            "current_bonuses": [],
            "next_bonus": None,
            "all_bonuses": []
        }
        
        set_bonuses = set_config.get("set_bonuses", {})
        
        # Get current active bonuses
        for piece_count in range(3, min(current_pieces + 1, 13)):
            piece_str = str(piece_count)
            if piece_str in set_bonuses:
                preview["current_bonuses"].append({
                    "tier": piece_count,
                    "name": set_bonuses[piece_str].get("name", f"{piece_count}-piece bonus"),
                    "description": set_bonuses[piece_str].get("description", "")
                })
        
        # Get next available bonus
        for piece_count in range(current_pieces + 1, 13):
            piece_str = str(piece_count)
            if piece_str in set_bonuses:
                preview["next_bonus"] = {
                    "tier": piece_count,
                    "name": set_bonuses[piece_str].get("name", f"{piece_count}-piece bonus"),
                    "description": set_bonuses[piece_str].get("description", ""),
                    "pieces_needed": piece_count - current_pieces
                }
                break
        
        # Get all possible bonuses for reference
        for piece_count in range(3, 13):
            piece_str = str(piece_count)
            if piece_str in set_bonuses:
                preview["all_bonuses"].append({
                    "tier": piece_count,
                    "name": set_bonuses[piece_str].get("name", f"{piece_count}-piece bonus"),
                    "description": set_bonuses[piece_str].get("description", ""),
                    "is_active": piece_count <= current_pieces
                })
        
        return preview
    
    def validate_equipment_creation(self, template_or_id, quality_tier: str, 
                                  rarity_tier_or_effects=None) -> Dict[str, Any]:
        """
        Business rule: Validate equipment creation parameters
        
        Supports both new template-based validation and legacy string-based validation
        for backward compatibility with tests.
        """
        # Handle legacy test format: validate_equipment_creation(template_id, quality_tier, magical_effects)
        if isinstance(template_or_id, str) and isinstance(rarity_tier_or_effects, list):
            return self._validate_equipment_creation_legacy(
                template_or_id, quality_tier, rarity_tier_or_effects
            )
        
        # Handle new template-based format: validate_equipment_creation(template, quality_tier, rarity_tier)
        template = template_or_id
        rarity_tier = rarity_tier_or_effects
        
        errors = []
        
        # Validate quality tier is allowed for this template
        if quality_tier not in template.allowed_quality_tiers:
            errors.append(f"Quality tier '{quality_tier}' not allowed for template '{template.template_id}'")
        
        # Validate rarity tier is allowed for this template  
        if rarity_tier not in template.allowed_rarity_tiers:
            errors.append(f"Rarity tier '{rarity_tier}' not allowed for template '{template.template_id}'")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    def _validate_equipment_creation_legacy(self, template_id: str, quality_tier: str, 
                                          magical_effects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Legacy business rule validation for backward compatibility with tests
        """
        errors = []
        
        # Business rule: Quality tier must be valid
        if quality_tier not in self.QUALITY_TIERS:
            errors.append(f"Invalid quality tier: {quality_tier}. Must be one of {self.QUALITY_TIERS}")
        
        # Business rule: Equipment can have 0-20+ magical effects (legacy limit)
        if len(magical_effects) > self.MAX_MAGICAL_EFFECTS_LEGACY:
            errors.append(f"Too many magical effects: {len(magical_effects)}. Maximum is {self.MAX_MAGICAL_EFFECTS_LEGACY}")
        
        # Business rule: Each magical effect must have required fields
        for i, effect in enumerate(magical_effects):
            if 'effect_type' not in effect or 'power_level' not in effect:
                errors.append(f"Magical effect {i} missing required fields: effect_type, power_level")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    # === UTILIZATION-BASED DURABILITY SYSTEM ===
    
    def calculate_utilization_based_durability_loss(self, current_durability: int, quality_tier: str,
                                                  usage_type: str, usage_count: int = 1,
                                                  environmental_factor: float = 1.0,
                                                  is_critical: bool = False) -> tuple[int, Dict[str, Any]]:
        """
        Business rule: Calculate durability loss from equipment usage (combat, etc.)
        """
        # Usage type damage multipliers
        usage_multipliers = {
            "light_use": 0.5,
            "normal_use": 1.0,
            "heavy_use": 1.5,
            "critical_hit": 2.0,
            "defensive": 0.8,
            "crafting": 0.3
        }
        
        base_damage = usage_multipliers.get(usage_type, 1.0)
        
        # Critical hits cause extra damage
        if is_critical:
            base_damage *= 1.5
        
        # Apply environmental factor and quality resistance
        quality_config = self.equipment_config_service.get_quality_tier_config(quality_tier)
        quality_resistance = quality_config.get("durability_multiplier", 1.0) if quality_config else 1.0
        
        # Higher quality = more resistance to damage
        damage_resistance = min(0.8, quality_resistance * 0.1)  # Cap at 80% resistance
        final_damage = int(base_damage * environmental_factor * (1 - damage_resistance) * usage_count)
        
        new_durability = max(0, current_durability - final_damage)
        
        damage_details = {
            "usage_type": usage_type,
            "usage_count": usage_count,
            "environmental_factor": environmental_factor,
            "is_critical": is_critical,
            "damage_amount": final_damage,
            "quality_resistance": damage_resistance
        }
        
        return new_durability, damage_details

    def calculate_expected_item_lifespan(
        self, 
        quality_tier: str,
        daily_usage_frequency: int = 24,
        usage_type: str = 'normal_use',
        environmental_factor: float = 1.0
    ) -> Dict[str, Any]:
        """
        Calculate the expected lifespan of an item based on usage patterns.
        
        Args:
            quality_tier: Item quality tier
            daily_usage_frequency: How many times per day the item is used
            usage_type: Primary usage type
            environmental_factor: Environmental wear factor
            
        Returns:
            Dictionary with lifespan statistics
        """
        decay_params = self.UTILIZATION_DECAY_RATES.get(quality_tier, self.UTILIZATION_DECAY_RATES['basic'])
        usage_multiplier = self.USAGE_TYPE_MULTIPLIERS.get(usage_type, 1.0)
        
        # Calculate effective decay rate
        effective_decay_per_use = (
            decay_params['base_decay_per_use'] * 
            usage_multiplier * 
            environmental_factor
        )
        
        # Expected uses until breakage (when durability reaches 0)
        expected_total_uses = 100.0 / effective_decay_per_use
        
        # Convert to days based on usage frequency
        expected_days = expected_total_uses / daily_usage_frequency
        
        # Calculate variance bounds
        variance = decay_params['variance_factor']
        min_uses = expected_total_uses * (1 - variance)
        max_uses = expected_total_uses * (1 + variance)
        min_days = min_uses / daily_usage_frequency
        max_days = max_uses / daily_usage_frequency
        
        return {
            'quality_tier': quality_tier,
            'daily_usage_frequency': daily_usage_frequency,
            'usage_type': usage_type,
            'environmental_factor': environmental_factor,
            'expected_total_uses': int(expected_total_uses),
            'expected_days': round(expected_days, 1),
            'expected_weeks': round(expected_days / 7, 1),
            'min_days': round(min_days, 1),
            'max_days': round(max_days, 1),
            'variance_range_days': round(max_days - min_days, 1),
            'effective_decay_per_use': round(effective_decay_per_use, 4)
        }

    def simulate_item_usage_lifecycle(
        self,
        quality_tier: str,
        daily_usage_frequency: int = 24,
        usage_pattern: List[str] = None,
        environmental_factor: float = 1.0,
        simulation_days: int = 30
    ) -> Dict[str, Any]:
        """
        Simulate the complete usage lifecycle of an item to validate decay rates.
        
        This is useful for testing whether a basic item used every day for a week
        will indeed be likely to break as per the requirements.
        
        Args:
            quality_tier: Item quality tier
            daily_usage_frequency: Uses per day
            usage_pattern: List of usage types for variation
            environmental_factor: Environmental conditions
            simulation_days: How many days to simulate
            
        Returns:
            Detailed simulation results
        """
        import random
        
        if usage_pattern is None:
            usage_pattern = ['normal_use'] * 20 + ['heavy_use'] * 3 + ['critical_hit'] * 1
        
        # Start with full durability
        current_durability = 100.0
        simulation_log = []
        day_by_day_durability = []
        
        for day in range(1, simulation_days + 1):
            daily_durability_loss = 0.0
            daily_usage_events = []
            
            for use_num in range(daily_usage_frequency):
                if current_durability <= 0:
                    break
                    
                # Select usage type from pattern
                usage_type = random.choice(usage_pattern)
                is_critical = usage_type == 'critical_hit' or random.random() < 0.05
                
                # Calculate durability loss for this use
                new_durability, breakdown = self.calculate_utilization_based_durability_loss(
                    current_durability=current_durability,
                    quality_tier=quality_tier,
                    usage_type=usage_type,
                    usage_count=1,
                    environmental_factor=environmental_factor,
                    is_critical=is_critical
                )
                
                durability_lost = current_durability - new_durability
                daily_durability_loss += durability_lost
                current_durability = new_durability
                
                daily_usage_events.append({
                    'use_number': use_num + 1,
                    'usage_type': usage_type,
                    'is_critical': is_critical,
                    'durability_lost': round(durability_lost, 3),
                    'durability_after': round(current_durability, 2),
                    'broke': breakdown.get('broke_this_use', False)
                })
                
                if current_durability <= 0:
                    break
            
            day_summary = {
                'day': day,
                'starting_durability': round(100.0 - sum(day_by_day_durability), 2),
                'daily_durability_loss': round(daily_durability_loss, 2),
                'ending_durability': round(current_durability, 2),
                'total_uses_this_day': len(daily_usage_events),
                'is_broken': current_durability <= 0,
                'usage_events': daily_usage_events
            }
            
            simulation_log.append(day_summary)
            day_by_day_durability.append(daily_durability_loss)
            
            if current_durability <= 0:
                break
        
        # Calculate summary statistics
        total_uses = sum(len(day['usage_events']) for day in simulation_log)
        days_until_broken = len(simulation_log) if current_durability <= 0 else None
        
        return {
            'simulation_parameters': {
                'quality_tier': quality_tier,
                'daily_usage_frequency': daily_usage_frequency,
                'environmental_factor': environmental_factor,
                'simulation_days': simulation_days
            },
            'results': {
                'total_uses': total_uses,
                'days_simulated': len(simulation_log),
                'days_until_broken': days_until_broken,
                'final_durability': round(current_durability, 2),
                'item_broke': current_durability <= 0,
                'average_daily_durability_loss': round(sum(day_by_day_durability) / len(day_by_day_durability), 3) if day_by_day_durability else 0
            },
            'day_by_day_log': simulation_log,
            'durability_curve': [round(100.0 - sum(day_by_day_durability[:i+1]), 2) for i in range(len(day_by_day_durability))]
        }

    # === LEGACY METHOD UPDATES FOR COMPATIBILITY ===
    
    def calculate_durability_loss_on_use(self, equipment_data: EquipmentInstanceData, 
                                       usage_type: str = "general", 
                                       base_damage: int = 1) -> int:
        """
        Business rule: Calculate durability loss when equipment is used
        Quality affects how much durability is lost per use
        """
        # Base durability loss
        durability_loss = base_damage
        
        # Quality affects degradation rate
        quality_multipliers = {
            'basic': 1.0,      # Standard degradation
            'military': 0.7,   # 30% less degradation  
            'masterwork': 0.4  # 60% less degradation
        }
        
        multiplier = quality_multipliers.get(equipment_data.quality_tier, 1.0)
        return max(1, int(durability_loss * multiplier))
    
    def calculate_repair_cost(self, current_durability: int, max_durability: int, quality_tier: str) -> int:
        """
        Business rule: Calculate repair cost based on Bible specification
        Formula: total_cost = base_repair_cost + (durability_lost * per_point_repair_cost)
        """
        # Load quality tier data
        quality_config = self.equipment_config_service.get_quality_tier_config(quality_tier)
        if not quality_config:
            logger.warning(f"Unknown quality tier: {quality_tier}, using basic defaults")
            # Default to basic quality costs
            base_repair_cost = 500
            per_point_repair_cost = 5
        else:
            base_repair_cost = quality_config.get("base_repair_cost", 500)
            per_point_repair_cost = quality_config.get("per_point_repair_cost", 5)
        
        # Calculate durability lost
        durability_lost = max_durability - current_durability
        
        # Apply formula
        total_cost = base_repair_cost + (durability_lost * per_point_repair_cost)
        
        return int(total_cost)
    
    def calculate_durability_damage_on_use(self, current_durability: float, 
                                         quality_tier: str, usage_type: str,
                                         is_critical: bool = False,
                                         environmental_factor: float = 1.0) -> Tuple[float, Dict[str, Any]]:
        """
        Business rule: Calculate durability loss when equipment is USED
        - Weapons lose durability when attacking and hitting
        - Armor loses durability when being hit (potentially by body part)
        - Usage-based, not time-based per user requirements
        
        UPDATED: Now uses the new utilization-based durability system
        
        Args:
            current_durability: Current durability 0-100
            quality_tier: basic, military, masterwork
            usage_type: 'attack', 'defend', 'block', etc.
            is_critical: Critical hits cause more durability damage
            environmental_factor: Environmental degradation multiplier
            
        Returns:
            Tuple of (new_durability, calculation_details)
        """
        # Map legacy usage types to new system
        usage_type_mapping = {
            'attack': 'normal_use',
            'defend': 'normal_use', 
            'block': 'blocking',
            'critical_hit': 'critical_hit',
            'general': 'normal_use'
        }
        
        mapped_usage_type = usage_type_mapping.get(usage_type, 'normal_use')
        
        # Use the new utilization-based system
        new_durability, breakdown = self.calculate_utilization_based_durability_loss(
            current_durability=current_durability,
            quality_tier=quality_tier,
            usage_type=mapped_usage_type,
            usage_count=1,
            environmental_factor=environmental_factor,
            is_critical=is_critical
        )
        
        # Transform breakdown to match legacy format for backward compatibility
        legacy_breakdown = {
            'usage_type': usage_type,
            'total_possible_uses': self.QUALITY_DURABILITY_USES.get(quality_tier, 168),
            'base_degradation_per_use': breakdown['base_decay_per_use'],
            'usage_multiplier': breakdown['usage_multiplier'],
            'is_critical': is_critical,
            'environmental_factor': environmental_factor,
            'total_degradation': breakdown['total_durability_loss'],
            # New fields from utilization system
            'variance_applied': breakdown['variance_multiplier'],
            'degradation_accelerated': breakdown['degradation_accelerated'],
            'breakage_risk': breakdown['breakage_risk'],
            'broke_this_use': breakdown['broke_this_use'],
            'expected_uses_remaining': breakdown['expected_uses_remaining']
        }
        
        return new_durability, legacy_breakdown
    
    def get_durability_status(self, current_durability: int) -> str:
        """
        Business rule: Get descriptive durability status
        """
        if current_durability <= 0:
            return "broken"
        elif current_durability <= 10:
            return "critically_damaged"
        elif current_durability <= 25:
            return "heavily_damaged"
        elif current_durability <= 50:
            return "damaged"
        elif current_durability <= 75:
            return "worn"
        else:
            return "good"
    
    def calculate_stat_penalties(self, current_durability: int) -> float:
        """
        Business rule: Calculate stat penalty multiplier based on durability
        """
        if current_durability <= 0:
            return 1.0  # 100% penalty (no stats)
        elif current_durability <= 10:
            return 0.5  # 50% penalty
        elif current_durability <= 25:
            return 0.3  # 30% penalty
        elif current_durability <= 50:
            return 0.15  # 15% penalty
        else:
            return 0.0  # No penalty
    
    def is_equipment_functional(self, durability: float) -> bool:
        """
        Business rule: Equipment is non-functional when broken
        """
        return durability > 0.0
    
    def counts_for_set_bonus(self, durability: float) -> bool:
        """
        Business rule: Equipment below 30% durability doesn't count for set bonuses
        Per user requirements
        """
        return durability >= self.SET_BONUS_MIN_DURABILITY
    
    def apply_stat_adjustments_for_durability(self, base_stats: Dict[str, Any], 
                                           durability: float) -> Dict[str, Any]:
        """
        Business rule: Adjust equipment stats based on durability
        Affects damage dealt per user requirements
        """
        # Make a copy to avoid modifying the original
        adjusted_stats = base_stats.copy()
        
        # Broken items provide no benefits
        if durability <= 0:
            for stat in adjusted_stats:
                if isinstance(adjusted_stats[stat], (int, float)):
                    adjusted_stats[stat] = 0
            return adjusted_stats
        
        # Apply stat penalties based on durability
        penalty = self.calculate_stat_penalties(durability)
        if penalty > 0:
            for stat in adjusted_stats:
                if isinstance(adjusted_stats[stat], (int, float)) and adjusted_stats[stat] > 0:
                    adjusted_stats[stat] = round(adjusted_stats[stat] * (1 - penalty), 2)
        
        return adjusted_stats
    
    # === SET BONUS CALCULATIONS ===
    
    def calculate_set_bonuses(self, equipped_items: List[EquipmentInstanceData], 
                            available_sets: List[EquipmentSetData]) -> Dict[str, Any]:
        """
        Business rule: Calculate active set bonuses for equipped items
        Equipment sets are mandatory for all equipment types per user requirements
        Only equipment with >= 30% durability counts for set bonuses
        """
        active_sets = {}
        
        # Group equipped items by set ID
        set_item_counts = {}
        for item in equipped_items:
            # Only count items that meet durability requirement
            if not item.counts_for_set_bonus():
                continue
                
            # Find which set this item belongs to (would need template lookup)
            # For now, assume we can get set_id from item
            if hasattr(item, 'set_id') and item.set_id:
                set_id = item.set_id
                if set_id not in set_item_counts:
                    set_item_counts[set_id] = []
                set_item_counts[set_id].append(item)
        
        # Calculate bonuses for each set
        for set_data in available_sets:
            set_id = set_data.set_id
            if set_id not in set_item_counts:
                continue
                
            equipped_count = len(set_item_counts[set_id])
            
            # Find which bonuses are active based on equipped count
            active_bonuses = {}
            for pieces_required, bonuses in set_data.set_bonuses.items():
                if equipped_count >= pieces_required:
                    active_bonuses[pieces_required] = bonuses
            
            if active_bonuses:
                active_sets[set_id] = {
                    'name': set_data.name,
                    'pieces_equipped': equipped_count,
                    'total_pieces': len(set_data.equipment_slots),
                    'active_bonuses': active_bonuses
                }
        
        return {
            'active_sets': active_sets,
            'total_sets_active': len(active_sets)
        }
    
    def apply_set_bonuses_to_stats(self, base_stats: Dict[str, Any], 
                                  set_bonuses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Business rule: Apply set bonuses to character/equipment stats
        Multiple sets can be active simultaneously per user requirements
        """
        # Make a copy of the stats to avoid modifying the original
        updated_stats = base_stats.copy()
        
        # Track applied bonuses for reporting
        applied_bonuses = []
        
        # Apply bonuses from each active set
        for set_id, set_info in set_bonuses.get('active_sets', {}).items():
            for pieces_required, bonuses in set_info.get('active_bonuses', {}).items():
                # Apply stat bonuses
                for attribute, value in bonuses.get('stats', {}).items():
                    if attribute in updated_stats:
                        updated_stats[attribute] += value
                    else:
                        updated_stats[attribute] = value
                        
                    applied_bonuses.append({
                        'set': set_info['name'],
                        'pieces': pieces_required,
                        'bonus': f"{attribute} +{value}"
                    })
                    
                # Apply special effects
                for effect in bonuses.get('effects', []):
                    if 'effects' not in updated_stats:
                        updated_stats['effects'] = []
                    updated_stats['effects'].append({
                        'id': f"set_bonus_{set_id}_{pieces_required}",
                        'name': effect.get('name', 'Set Bonus'),
                        'description': effect.get('description', ''),
                        'source': set_info['name'],
                        'is_set_bonus': True
                    })
                    
                    applied_bonuses.append({
                        'set': set_info['name'],
                        'pieces': pieces_required,
                        'bonus': effect.get('name', 'Special Effect')
                    })
        
        # Add the applied bonuses to the stats for reference
        updated_stats['applied_set_bonuses'] = applied_bonuses
        
        return updated_stats
    
    # === EXISTING METHODS ===
    
    def calculate_equipment_uniqueness_score(self, magical_effects: List[Dict[str, Any]]) -> float:
        """
        Business rule: Calculate how unique this equipment is
        Based on number and power of magical effects
        """
        if not magical_effects:
            return 0.0
        
        # Base uniqueness from effect count
        effect_count_score = min(len(magical_effects) / self.MAX_MAGICAL_EFFECTS, 1.0)
        
        # Bonus uniqueness from effect power levels
        total_power = sum(effect.get('power_level', 0) for effect in magical_effects)
        max_possible_power = len(magical_effects) * 100  # Assuming max power is 100
        
        if max_possible_power > 0:
            power_score = total_power / max_possible_power
        else:
            power_score = 0.0
        
        # Combine scores with weighting
        final_score = (effect_count_score * 0.6) + (power_score * 0.4)
        
        return min(final_score, 1.0)
    
    def generate_equipment_display_name(self, base_name: str, quality_tier: str, 
                                      magical_effects: List[Dict[str, Any]],
                                      custom_name: Optional[str] = None) -> str:
        """
        Business rule: Generate display name for equipment
        Priority: custom_name > quality + magical + base_name > base_name
        """
        if custom_name:
            return custom_name
        
        name_parts = []
        
        # Add quality prefix for military/noble
        if quality_tier == 'military':
            name_parts.append('Military-Grade')
        elif quality_tier == 'masterwork':
            name_parts.append('Mastercrafted')
        
        # Add magical indicator if has effects
        if magical_effects:
            if len(magical_effects) >= 5:
                name_parts.append('Heavily Enchanted')
            elif len(magical_effects) >= 3:
                name_parts.append('Enchanted')
            else:
                name_parts.append('Magical')
        
        name_parts.append(base_name)
        
        return ' '.join(name_parts)
    
    def validate_character_ownership(self, character_id: UUID, 
                                   equipment_instances: List[EquipmentInstanceData]) -> Dict[str, Any]:
        """
        Business rule: Validate character can own/use these equipment pieces
        """
        issues = []
        
        for equipment in equipment_instances:
            if equipment.character_id != character_id:
                issues.append(f"Equipment {equipment.id} is not owned by character {character_id}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'equipment_count': len(equipment_instances)
        }
    
    def calculate_repair_urgency(self, equipment_instances: List[EquipmentInstanceData]) -> List[Dict[str, Any]]:
        """
        Business rule: Calculate which equipment needs repair most urgently
        """
        urgency_list = []
        
        for equipment in equipment_instances:
            status = self.get_durability_status(equipment.current_durability / equipment.max_durability)
            penalty = self.calculate_stat_penalties(equipment.current_durability / equipment.max_durability)
            
            urgency_score = penalty * 100  # Convert to 0-100 scale
            
            urgency_list.append({
                'equipment_id': equipment.id,
                'custom_name': equipment.name,
                'template_id': equipment.template_id,
                'durability': equipment.current_durability / equipment.max_durability,
                'status': status,
                'penalty_percentage': penalty * 100,
                'urgency_score': urgency_score,
                'counts_for_set_bonus': equipment.counts_for_set_bonus()
            })
        
        # Sort by urgency score (highest first)
        urgency_list.sort(key=lambda x: x['urgency_score'], reverse=True)
        
        return urgency_list

    def calculate_durability_degradation(self, current_durability: int, quality_tier: str, 
                                       time_worn: float, environmental_factor: float) -> tuple[int, Dict[str, Any]]:
        """
        Business rule: Calculate gradual durability loss from wearing equipment
        """
        # Load quality tier configuration
        quality_config = self.equipment_config_service.get_quality_tier_config(quality_tier)
        degradation_rate = quality_config.get("degradation_rate", 1.0) if quality_config else 1.0
        
        # Calculate base wear
        base_wear = time_worn * degradation_rate * environmental_factor
        
        # Random variation (±20%)
        import random
        variation = random.uniform(0.8, 1.2)
        actual_wear = int(base_wear * variation)
        
        new_durability = max(0, current_durability - actual_wear)
        
        damage_details = {
            "wear_type": "environmental",
            "time_worn": time_worn,
            "environmental_factor": environmental_factor,
            "degradation_rate": degradation_rate,
            "damage_amount": actual_wear
        }
        
        return new_durability, damage_details


def create_equipment_business_service() -> EquipmentBusinessLogicService:
    """Factory function to create equipment business service"""
    return EquipmentBusinessLogicService() 