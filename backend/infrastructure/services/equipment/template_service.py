"""
Equipment Template Service for Visual DM.

Manages loading and caching of equipment templates from JSON configuration files.
Works in conjunction with SQLAlchemy models for equipment instances.

Hybrid Pattern Implementation:
- This service handles the static template definitions (JSON)
- Equipment instances are managed via SQLAlchemy models
- Templates define base properties, instances track unique state
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from functools import lru_cache

logger = logging.getLogger(__name__)

@dataclass
class EquipmentTemplate:
    """Equipment template loaded from JSON configuration."""
    id: str
    name: str
    description: str
    item_type: str  # weapon, armor, accessory, etc.
    quality_tier: str  # basic, military, mastercraft
    rarity: str  # common, rare, epic, legendary
    base_value: int
    equipment_slots: List[str]  # Valid slots this can be equipped to
    stat_modifiers: Dict[str, int]
    abilities: List[Dict[str, Any]]  # Intrinsic abilities
    material: str
    weight: float
    durability_multiplier: float  # Modifier to base quality durability
    compatible_enchantments: List[str]  # Which enchantment schools work
    thematic_tags: List[str]  # For AI-driven set detection
    restrictions: Dict[str, Any]  # Level, ability, quest requirements
    visual_description: str
    lore_text: str
    crafting_requirements: Optional[Dict[str, Any]] = None


@dataclass 
class EnchantmentTemplate:
    """Enchantment definition loaded from JSON configuration."""
    id: str
    name: str
    description: str
    school: str  # elemental, protective, enhancement, etc.
    rarity: str  # basic, military, noble, legendary
    min_arcane_manipulation: int
    base_cost: int
    min_item_quality: str
    compatible_item_types: List[str]
    power_scaling: Dict[str, float]
    thematic_tags: List[str]
    application_time_hours: int
    stability_base: float
    mastery_effects: Dict[str, Any]


@dataclass
class QualityTierTemplate:
    """Quality tier definition with durability and value settings."""
    tier: str
    durability_weeks: int
    repair_cost: int
    value_multiplier: float
    description: str
    degradation_rate: float


class EquipmentTemplateService:
    """Service for loading and managing equipment templates from JSON."""
    
    def __init__(self, templates_dir: str = None):
        """Initialize template service with configuration directory."""
        if templates_dir is None:
            # Default to moved data directory
            project_root = Path(__file__).parent.parent.parent.parent
            templates_dir = project_root / "data" / "systems" / "equipment"
        
        self.templates_dir = Path(templates_dir)
        self._equipment_templates: Dict[str, EquipmentTemplate] = {}
        self._enchantment_templates: Dict[str, EnchantmentTemplate] = {}
        self._quality_tiers: Dict[str, QualityTierTemplate] = {}
        self._loaded = False
        
        logger.info(f"Initialized EquipmentTemplateService with templates at: {self.templates_dir}")
    
    def load_all_templates(self) -> bool:
        """Load all equipment, enchantment, and quality templates."""
        try:
            success = True
            success &= self._load_quality_tiers()
            success &= self._load_equipment_templates()
            success &= self._load_enchantment_templates()
            
            if success:
                self._loaded = True
                logger.info("Successfully loaded all equipment templates")
            else:
                logger.error("Failed to load some equipment templates")
            
            return success
        except Exception as e:
            logger.error(f"Error loading equipment templates: {e}")
            return False
    
    def _load_quality_tiers(self) -> bool:
        """Load quality tier definitions."""
        quality_file = self.templates_dir / "quality_tiers.json"
        
        if not quality_file.exists():
            logger.warning(f"Quality tiers file not found: {quality_file}")
            self._load_default_quality_tiers()
            return True
        
        try:
            with open(quality_file, 'r') as f:
                data = json.load(f)
            
            for tier_name, tier_data in data.get("quality_tiers", {}).items():
                template = QualityTierTemplate(
                    tier=tier_name,
                    durability_weeks=tier_data.get("durability_weeks", 1),
                    repair_cost=tier_data.get("repair_cost", 500),
                    value_multiplier=tier_data.get("value_multiplier", 1.0),
                    description=tier_data.get("description", ""),
                    degradation_rate=tier_data.get("degradation_rate", 1.0)
                )
                self._quality_tiers[tier_name] = template
            
            logger.info(f"Loaded {len(self._quality_tiers)} quality tiers")
            return True
            
        except Exception as e:
            logger.error(f"Error loading quality tiers: {e}")
            self._load_default_quality_tiers()
            return True  # Don't fail completely on quality tier issues
    
    def _load_equipment_templates(self) -> bool:
        """Load equipment template definitions."""
        equipment_file = self.templates_dir / "equipment_templates.json"
        
        if not equipment_file.exists():
            logger.error(f"Equipment templates file not found: {equipment_file}")
            return False
        
        try:
            with open(equipment_file, 'r') as f:
                data = json.load(f)
            
            for eq_id, eq_data in data.get("equipment", {}).items():
                template = EquipmentTemplate(
                    id=eq_id,
                    name=eq_data.get("name", eq_id),
                    description=eq_data.get("description", ""),
                    item_type=eq_data.get("item_type", "weapon"),
                    quality_tier=eq_data.get("quality_tier", "basic"),
                    rarity=eq_data.get("rarity", "common"),
                    base_value=eq_data.get("base_value", 100),
                    equipment_slots=eq_data.get("equipment_slots", ["main_hand"]),
                    stat_modifiers=eq_data.get("stat_modifiers", {}),
                    abilities=eq_data.get("abilities", []),
                    material=eq_data.get("material", "iron"),
                    weight=eq_data.get("weight", 1.0),
                    durability_multiplier=eq_data.get("durability_multiplier", 1.0),
                    compatible_enchantments=eq_data.get("compatible_enchantments", []),
                    thematic_tags=eq_data.get("thematic_tags", []),
                    restrictions=eq_data.get("restrictions", {}),
                    visual_description=eq_data.get("visual_description", ""),
                    lore_text=eq_data.get("lore_text", ""),
                    crafting_requirements=eq_data.get("crafting_requirements")
                )
                self._equipment_templates[eq_id] = template
            
            logger.info(f"Loaded {len(self._equipment_templates)} equipment templates")
            return True
            
        except Exception as e:
            logger.error(f"Error loading equipment templates: {e}")
            return False
    
    def _load_enchantment_templates(self) -> bool:
        """Load enchantment template definitions."""
        enchantment_file = self.templates_dir / "sample_enchantments.json"
        
        if not enchantment_file.exists():
            logger.warning(f"Enchantment templates file not found: {enchantment_file}")
            return True  # Not critical for basic operation
        
        try:
            with open(enchantment_file, 'r') as f:
                data = json.load(f)
            
            for ench_id, ench_data in data.get("enchantments", {}).items():
                template = EnchantmentTemplate(
                    id=ench_id,
                    name=ench_data.get("name", ench_id),
                    description=ench_data.get("description", ""),
                    school=ench_data.get("school", "enhancement"),
                    rarity=ench_data.get("rarity", "basic"),
                    min_arcane_manipulation=ench_data.get("min_arcane_manipulation", 1),
                    base_cost=ench_data.get("base_cost", 100),
                    min_item_quality=ench_data.get("min_item_quality", "basic"),
                    compatible_item_types=ench_data.get("compatible_item_types", []),
                    power_scaling=ench_data.get("power_scaling", {}),
                    thematic_tags=ench_data.get("thematic_tags", []),
                    application_time_hours=ench_data.get("application_time_hours", 2),
                    stability_base=ench_data.get("stability_base", 90.0),
                    mastery_effects=ench_data.get("mastery_effects", {})
                )
                self._enchantment_templates[ench_id] = template
            
            logger.info(f"Loaded {len(self._enchantment_templates)} enchantment templates")
            return True
            
        except Exception as e:
            logger.error(f"Error loading enchantment templates: {e}")
            return True  # Not critical for basic operation
    
    def _load_default_quality_tiers(self):
        """Load default quality tiers if config file is missing."""
        defaults = {
            "basic": QualityTierTemplate("basic", 1, 500, 1.0, "Basic quality equipment", 1.0),
            "military": QualityTierTemplate("military", 2, 750, 3.0, "Military grade equipment", 0.7), 
            "mastercraft": QualityTierTemplate("mastercraft", 4, 1500, 6.0, "Mastercrafted equipment", 0.5)
        }
        self._quality_tiers.update(defaults)
        logger.info("Loaded default quality tiers")
    
    # Public API methods
    
    def get_equipment_template(self, template_id: str) -> Optional[EquipmentTemplate]:
        """Get equipment template by ID."""
        if not self._loaded:
            self.load_all_templates()
        return self._equipment_templates.get(template_id)
    
    def get_enchantment_template(self, template_id: str) -> Optional[EnchantmentTemplate]:
        """Get enchantment template by ID."""
        if not self._loaded:
            self.load_all_templates()
        return self._enchantment_templates.get(template_id)
    
    def get_quality_tier(self, tier_name: str) -> Optional[QualityTierTemplate]:
        """Get quality tier definition."""
        if not self._loaded:
            self.load_all_templates()
        return self._quality_tiers.get(tier_name)
    
    def list_equipment_templates(self) -> List[EquipmentTemplate]:
        """Get all equipment templates."""
        if not self._loaded:
            self.load_all_templates()
        return list(self._equipment_templates.values())
    
    def list_enchantment_templates(self) -> List[EnchantmentTemplate]:
        """Get all enchantment templates."""
        if not self._loaded:
            self.load_all_templates()
        return list(self._enchantment_templates.values())
    
    def find_equipment_by_type(self, item_type: str) -> List[EquipmentTemplate]:
        """Find equipment templates by type."""
        if not self._loaded:
            self.load_all_templates()
        return [eq for eq in self._equipment_templates.values() if eq.item_type == item_type]
    
    def find_equipment_by_quality(self, quality_tier: str) -> List[EquipmentTemplate]:
        """Find equipment templates by quality tier."""
        if not self._loaded:
            self.load_all_templates()
        return [eq for eq in self._equipment_templates.values() if eq.quality_tier == quality_tier]
    
    def find_enchantments_by_school(self, school: str) -> List[EnchantmentTemplate]:
        """Find enchantment templates by school."""
        if not self._loaded:
            self.load_all_templates()
        return [ench for ench in self._enchantment_templates.values() if ench.school == school]
    
    def get_compatible_enchantments(self, equipment_template_id: str) -> List[EnchantmentTemplate]:
        """Get enchantments compatible with a specific equipment template."""
        equipment = self.get_equipment_template(equipment_template_id)
        if not equipment:
            return []
        
        compatible = []
        for enchantment in self.list_enchantment_templates():
            # Check if enchantment school is in equipment's compatible list
            if enchantment.school in equipment.compatible_enchantments:
                # Check if equipment type is supported by enchantment
                if equipment.item_type in enchantment.compatible_item_types:
                    compatible.append(enchantment)
        
        return compatible
    
    def validate_equipment_instance_data(self, template_id: str, instance_data: Dict[str, Any]) -> bool:
        """Validate that instance data is compatible with template requirements."""
        template = self.get_equipment_template(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return False
        
        # Validate equipment slot
        if instance_data.get("equipment_slot") not in template.equipment_slots:
            logger.error(f"Invalid equipment slot for {template_id}")
            return False
        
        # Additional validation logic could go here
        return True
    
    @lru_cache(maxsize=100)
    def calculate_template_value(self, template_id: str, quality_tier: str = None) -> int:
        """Calculate the base value for an equipment template with quality adjustments."""
        template = self.get_equipment_template(template_id)
        if not template:
            return 0
        
        # Use template's quality tier or override
        tier_name = quality_tier or template.quality_tier
        quality = self.get_quality_tier(tier_name)
        
        if quality:
            return int(template.base_value * quality.value_multiplier)
        return template.base_value
    
    def reload_templates(self) -> bool:
        """Reload all templates from disk."""
        logger.info("Reloading equipment templates from disk")
        self._equipment_templates.clear()
        self._enchantment_templates.clear()
        self._quality_tiers.clear()
        self._loaded = False
        self.calculate_template_value.cache_clear()
        
        return self.load_all_templates()


# Global template service instance
template_service = EquipmentTemplateService() 