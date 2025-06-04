"""
Equipment Template Repository - Infrastructure Layer

Implements loading and caching of equipment templates from JSON files.
Provides the infrastructure implementation for the EquipmentTemplateRepository protocol.
"""

import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

from backend.systems.equipment.services.business_logic_service import (
    EquipmentBaseTemplate, QualityTierData
)
from backend.systems.equipment.services.character_equipment_service import (
    EquipmentTemplateRepository as EquipmentTemplateRepositoryProtocol
)


@dataclass
class LoadedTemplate:
    """Loaded equipment template with all data"""
    id: str
    name: str
    description: str
    item_type: str
    quality_tier: str
    rarity: str
    base_value: int
    equipment_slots: List[str]
    stat_modifiers: Dict[str, int]
    abilities: List[Dict[str, Any]]
    material: str
    weight: float
    durability_multiplier: float
    compatible_enchantments: List[str]
    thematic_tags: List[str]
    restrictions: Dict[str, Any]
    visual_description: str
    lore_text: str
    crafting_requirements: Optional[Dict[str, Any]] = None


class EquipmentTemplateRepository:
    """Infrastructure implementation for equipment template loading"""
    
    def __init__(self, templates_path: str = None):
        if templates_path is None:
            # Default path relative to project root
            self.templates_path = os.path.join(
                os.path.dirname(__file__), 
                '../../data/systems/equipment/equipment_templates.json'
            )
        else:
            self.templates_path = templates_path
        
        self.quality_tiers_path = os.path.join(
            os.path.dirname(__file__),
            '../../data/systems/equipment/quality_tiers.json'
        )
        self.effects_path = os.path.join(
            os.path.dirname(__file__),
            '../../data/systems/equipment/effects.json'
        )
        
        # Cache loaded data
        self._templates_cache: Dict[str, LoadedTemplate] = {}
        self._quality_tiers_cache: Dict[str, QualityTierData] = {}
        self._effects_cache: List[Dict[str, Any]] = []
        self._loaded = False
    
    def _load_templates(self):
        """Load all templates from JSON files"""
        if self._loaded:
            return
        
        # Load equipment templates
        try:
            with open(self.templates_path, 'r') as f:
                data = json.load(f)
                
            for template_id, template_data in data.get('equipment', {}).items():
                loaded_template = LoadedTemplate(
                    id=template_id,
                    name=template_data.get('name', template_id),
                    description=template_data.get('description', ''),
                    item_type=template_data.get('item_type', 'unknown'),
                    quality_tier=template_data.get('quality_tier', 'basic'),
                    rarity=template_data.get('rarity', 'common'),
                    base_value=template_data.get('base_value', 100),
                    equipment_slots=template_data.get('equipment_slots', []),
                    stat_modifiers=template_data.get('stat_modifiers', {}),
                    abilities=template_data.get('abilities', []),
                    material=template_data.get('material', 'unknown'),
                    weight=template_data.get('weight', 1.0),
                    durability_multiplier=template_data.get('durability_multiplier', 1.0),
                    compatible_enchantments=template_data.get('compatible_enchantments', []),
                    thematic_tags=template_data.get('thematic_tags', []),
                    restrictions=template_data.get('restrictions', {}),
                    visual_description=template_data.get('visual_description', ''),
                    lore_text=template_data.get('lore_text', ''),
                    crafting_requirements=template_data.get('crafting_requirements')
                )
                self._templates_cache[template_id] = loaded_template
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load equipment templates: {e}")
        
        # Load quality tiers
        try:
            with open(self.quality_tiers_path, 'r') as f:
                quality_data = json.load(f)
                
            for tier_name, tier_data in quality_data.get('quality_tiers', {}).items():
                quality_tier = QualityTierData(
                    tier=tier_name,
                    durability_weeks=tier_data.get('durability_weeks', 1),
                    value_multiplier=tier_data.get('value_multiplier', 1.0),
                    degradation_rate=tier_data.get('degradation_rate', 1.0),
                    enchantment_capacity=tier_data.get('enchantment_capacity', 1),
                    max_enchantment_power=tier_data.get('max_enchantment_power', 75)
                )
                self._quality_tiers_cache[tier_name] = quality_tier
                
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load quality tiers: {e}")
        
        # Load magical effects
        try:
            with open(self.effects_path, 'r') as f:
                effects_data = json.load(f)
                
            # Convert effect types to list of available effects
            for effect_type, effect_info in effects_data.get('effect_types', {}).items():
                for example in effect_info.get('examples', []):
                    effect = {
                        'effect_type': effect_type,
                        'description': effect_info.get('description', ''),
                        'example': example,
                        'parameters': effect_info.get('parameters', [])
                    }
                    self._effects_cache.append(effect)
                    
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load effects: {e}")
        
        self._loaded = True
    
    def get_template(self, template_id: str) -> Optional[EquipmentBaseTemplate]:
        """Get equipment base template by ID"""
        self._load_templates()
        
        loaded = self._templates_cache.get(template_id)
        if not loaded:
            return None
        
        # Convert to business domain model
        return EquipmentBaseTemplate(
            id=loaded.id,
            name=loaded.name,
            item_type=loaded.item_type,
            base_stats=loaded.stat_modifiers,
            equipment_slots=loaded.equipment_slots,
            base_value=loaded.base_value
        )
    
    def get_quality_tier(self, tier: str) -> Optional[QualityTierData]:
        """Get quality tier configuration"""
        self._load_templates()
        return self._quality_tiers_cache.get(tier)
    
    def get_available_magical_effects(self) -> List[Dict[str, Any]]:
        """Get available magical effects for equipment"""
        self._load_templates()
        return self._effects_cache.copy()
    
    def list_templates(self, item_type: Optional[str] = None, 
                      quality_tier: Optional[str] = None) -> List[EquipmentBaseTemplate]:
        """List all templates, optionally filtered by type and quality"""
        self._load_templates()
        
        templates = []
        for loaded in self._templates_cache.values():
            # Apply filters
            if item_type and loaded.item_type != item_type:
                continue
            if quality_tier and loaded.quality_tier != quality_tier:
                continue
            
            # Convert to business domain model
            template = EquipmentBaseTemplate(
                id=loaded.id,
                name=loaded.name,
                item_type=loaded.item_type,
                base_stats=loaded.stat_modifiers,
                equipment_slots=loaded.equipment_slots,
                base_value=loaded.base_value
            )
            templates.append(template)
        
        return templates
    
    def get_template_details(self, template_id: str) -> Optional[LoadedTemplate]:
        """Get full template details for display purposes"""
        self._load_templates()
        return self._templates_cache.get(template_id)
    
    def reload_templates(self):
        """Force reload templates from files"""
        self._loaded = False
        self._templates_cache.clear()
        self._quality_tiers_cache.clear()
        self._effects_cache.clear()
        self._load_templates()


# Factory function for dependency injection
def create_equipment_template_repository(templates_path: str = None) -> EquipmentTemplateRepository:
    """Create an equipment template repository instance"""
    return EquipmentTemplateRepository(templates_path) 