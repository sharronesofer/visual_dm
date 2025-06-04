"""
Equipment Template Database Repository

Database implementation for equipment template loading.
Combines database storage with JSON file loading for templates.
"""

import json
import os
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from backend.systems.equipment.services.business_logic_service import (
    EquipmentBaseTemplate, QualityTierData
)
from backend.systems.equipment.services.character_equipment_service import (
    EquipmentTemplateRepository as EquipmentTemplateRepositoryProtocol
)
from backend.infrastructure.database.models.equipment_models import (
    EquipmentTemplate, QualityTier, MagicalEffect
)


class EquipmentTemplateDatabaseRepository:
    """Database-backed equipment template repository"""
    
    def __init__(self, db_session: Session, templates_path: str = None):
        self.db = db_session
        
        # Fallback to JSON files if database is empty
        if templates_path is None:
            self.templates_path = os.path.join(
                os.path.dirname(__file__), 
                '../../../data/systems/equipment/equipment_templates.json'
            )
        else:
            self.templates_path = templates_path
        
        self.quality_tiers_path = os.path.join(
            os.path.dirname(__file__),
            '../../../data/systems/equipment/quality_tiers.json'
        )
        self.effects_path = os.path.join(
            os.path.dirname(__file__),
            '../../../data/systems/equipment/effects.json'
        )
        
        # Cache for performance
        self._quality_tiers_cache: Dict[str, QualityTierData] = {}
        self._effects_cache: List[Dict[str, Any]] = []
        self._cache_loaded = False
    
    def get_template(self, template_id: str) -> Optional[EquipmentBaseTemplate]:
        """Get equipment base template by ID"""
        # Try database first
        db_template = (
            self.db.query(EquipmentTemplate)
            .filter(EquipmentTemplate.template_id == template_id)
            .first()
        )
        
        if db_template:
            return self._convert_db_template_to_business_model(db_template)
        
        # Fallback to JSON if not in database
        return self._get_template_from_json(template_id)
    
    def get_quality_tier(self, tier: str) -> Optional[QualityTierData]:
        """Get quality tier configuration"""
        # Try database first
        db_tier = (
            self.db.query(QualityTier)
            .filter(QualityTier.tier_name == tier)
            .first()
        )
        
        if db_tier:
            return QualityTierData(
                tier=db_tier.tier_name,
                durability_weeks=db_tier.durability_weeks,
                value_multiplier=db_tier.value_multiplier,
                degradation_rate=db_tier.degradation_rate,
                enchantment_capacity=db_tier.enchantment_capacity,
                max_enchantment_power=db_tier.max_enchantment_power
            )
        
        # Fallback to JSON cache
        self._load_json_cache()
        return self._quality_tiers_cache.get(tier)
    
    def get_available_magical_effects(self) -> List[Dict[str, Any]]:
        """Get available magical effects for equipment"""
        # Try database first
        db_effects = self.db.query(MagicalEffect).all()
        
        if db_effects:
            effects = []
            for effect in db_effects:
                effect_data = {
                    'effect_type': effect.effect_type,
                    'description': effect.description,
                    'parameters': effect.parameters or {},
                    'base_power': effect.base_power,
                    'rarity': effect.rarity,
                    'compatible_item_types': effect.compatible_item_types or []
                }
                effects.append(effect_data)
            return effects
        
        # Fallback to JSON cache
        self._load_json_cache()
        return self._effects_cache.copy()
    
    def list_templates(self, item_type: Optional[str] = None, 
                      quality_tier: Optional[str] = None) -> List[EquipmentBaseTemplate]:
        """List all templates, optionally filtered by type and quality"""
        # Query database
        query = self.db.query(EquipmentTemplate)
        
        if item_type:
            query = query.filter(EquipmentTemplate.item_type == item_type)
        if quality_tier:
            query = query.filter(EquipmentTemplate.quality_tier == quality_tier)
        
        db_templates = query.all()
        
        if db_templates:
            return [self._convert_db_template_to_business_model(t) for t in db_templates]
        
        # Fallback to JSON if database is empty
        return self._list_templates_from_json(item_type, quality_tier)
    
    def create_template(self, template_data: Dict[str, Any]) -> EquipmentTemplate:
        """Create a new equipment template in the database"""
        db_template = EquipmentTemplate(
            template_id=template_data['template_id'],
            name=template_data.get('name', template_data['template_id']),
            description=template_data.get('description', ''),
            item_type=template_data.get('item_type', 'unknown'),
            quality_tier=template_data.get('quality_tier', 'basic'),
            rarity=template_data.get('rarity', 'common'),
            base_value=template_data.get('base_value', 100),
            weight=template_data.get('weight', 1.0),
            durability_multiplier=template_data.get('durability_multiplier', 1.0),
            base_stats=template_data.get('base_stats', {}),
            equipment_slots=template_data.get('equipment_slots', []),
            abilities=template_data.get('abilities', []),
            compatible_enchantments=template_data.get('compatible_enchantments', []),
            thematic_tags=template_data.get('thematic_tags', []),
            restrictions=template_data.get('restrictions', {}),
            material=template_data.get('material'),
            visual_description=template_data.get('visual_description', ''),
            lore_text=template_data.get('lore_text', ''),
            crafting_requirements=template_data.get('crafting_requirements')
        )
        
        self.db.add(db_template)
        self.db.commit()
        self.db.refresh(db_template)
        
        return db_template
    
    def update_template(self, template_id: str, template_data: Dict[str, Any]) -> bool:
        """Update an existing template"""
        db_template = (
            self.db.query(EquipmentTemplate)
            .filter(EquipmentTemplate.template_id == template_id)
            .first()
        )
        
        if not db_template:
            return False
        
        # Update fields
        for field, value in template_data.items():
            if hasattr(db_template, field):
                setattr(db_template, field, value)
        
        self.db.commit()
        return True
    
    def load_templates_from_json(self) -> int:
        """Load templates from JSON file into database"""
        loaded_count = 0
        
        try:
            with open(self.templates_path, 'r') as f:
                data = json.load(f)
            
            for template_id, template_data in data.get('equipment', {}).items():
                # Check if template already exists
                existing = (
                    self.db.query(EquipmentTemplate)
                    .filter(EquipmentTemplate.template_id == template_id)
                    .first()
                )
                
                if existing:
                    continue  # Skip existing templates
                
                # Create new template
                template_data['template_id'] = template_id
                self.create_template(template_data)
                loaded_count += 1
            
            # Load quality tiers
            self._load_quality_tiers_from_json()
            
            # Load magical effects
            self._load_magical_effects_from_json()
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load templates from JSON: {e}")
        
        return loaded_count
    
    def get_database_stats(self) -> Dict[str, int]:
        """Get statistics about templates in the database"""
        template_count = self.db.query(EquipmentTemplate).count()
        quality_tier_count = self.db.query(QualityTier).count()
        effect_count = self.db.query(MagicalEffect).count()
        
        return {
            'templates': template_count,
            'quality_tiers': quality_tier_count,
            'magical_effects': effect_count
        }
    
    # Helper methods
    def _convert_db_template_to_business_model(self, db_template: EquipmentTemplate) -> EquipmentBaseTemplate:
        """Convert database template to business domain model"""
        return EquipmentBaseTemplate(
            id=db_template.template_id,
            name=db_template.name,
            item_type=db_template.item_type,
            base_stats=db_template.base_stats or {},
            equipment_slots=db_template.equipment_slots or [],
            base_value=db_template.base_value
        )
    
    def _get_template_from_json(self, template_id: str) -> Optional[EquipmentBaseTemplate]:
        """Get template from JSON file as fallback"""
        try:
            with open(self.templates_path, 'r') as f:
                data = json.load(f)
            
            template_data = data.get('equipment', {}).get(template_id)
            if not template_data:
                return None
            
            return EquipmentBaseTemplate(
                id=template_id,
                name=template_data.get('name', template_id),
                item_type=template_data.get('item_type', 'unknown'),
                base_stats=template_data.get('stat_modifiers', {}),
                equipment_slots=template_data.get('equipment_slots', []),
                base_value=template_data.get('base_value', 100)
            )
            
        except (FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _list_templates_from_json(self, item_type: Optional[str] = None, 
                                 quality_tier: Optional[str] = None) -> List[EquipmentBaseTemplate]:
        """List templates from JSON as fallback"""
        try:
            with open(self.templates_path, 'r') as f:
                data = json.load(f)
            
            templates = []
            for template_id, template_data in data.get('equipment', {}).items():
                # Apply filters
                if item_type and template_data.get('item_type') != item_type:
                    continue
                if quality_tier and template_data.get('quality_tier') != quality_tier:
                    continue
                
                template = EquipmentBaseTemplate(
                    id=template_id,
                    name=template_data.get('name', template_id),
                    item_type=template_data.get('item_type', 'unknown'),
                    base_stats=template_data.get('stat_modifiers', {}),
                    equipment_slots=template_data.get('equipment_slots', []),
                    base_value=template_data.get('base_value', 100)
                )
                templates.append(template)
            
            return templates
            
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def _load_json_cache(self):
        """Load JSON data into cache for fallback"""
        if self._cache_loaded:
            return
        
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
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        # Load magical effects
        try:
            with open(self.effects_path, 'r') as f:
                effects_data = json.load(f)
            
            for effect_type, effect_info in effects_data.get('effect_types', {}).items():
                for example in effect_info.get('examples', []):
                    effect = {
                        'effect_type': effect_type,
                        'description': effect_info.get('description', ''),
                        'example': example,
                        'parameters': effect_info.get('parameters', [])
                    }
                    self._effects_cache.append(effect)
        except (FileNotFoundError, json.JSONDecodeError):
            pass
        
        self._cache_loaded = True
    
    def _load_quality_tiers_from_json(self):
        """Load quality tiers from JSON into database"""
        try:
            with open(self.quality_tiers_path, 'r') as f:
                quality_data = json.load(f)
            
            for tier_name, tier_data in quality_data.get('quality_tiers', {}).items():
                # Check if tier already exists
                existing = (
                    self.db.query(QualityTier)
                    .filter(QualityTier.tier_name == tier_name)
                    .first()
                )
                
                if existing:
                    continue
                
                # Create new quality tier
                quality_tier = QualityTier(
                    tier_name=tier_name,
                    display_name=tier_data.get('display_name', tier_name.title()),
                    description=tier_data.get('description', ''),
                    durability_weeks=tier_data.get('durability_weeks', 1),
                    degradation_rate=tier_data.get('degradation_rate', 1.0),
                    value_multiplier=tier_data.get('value_multiplier', 1.0),
                    enchantment_capacity=tier_data.get('enchantment_capacity', 5),
                    max_enchantment_power=tier_data.get('max_enchantment_power', 75),
                    color_code=tier_data.get('color_code', '#FFFFFF'),
                    rarity_weight=tier_data.get('rarity_weight', 1.0)
                )
                
                self.db.add(quality_tier)
            
            self.db.commit()
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load quality tiers from JSON: {e}")
    
    def _load_magical_effects_from_json(self):
        """Load magical effects from JSON into database"""
        try:
            with open(self.effects_path, 'r') as f:
                effects_data = json.load(f)
            
            for effect_type, effect_info in effects_data.get('effect_types', {}).items():
                # Check if effect already exists
                existing = (
                    self.db.query(MagicalEffect)
                    .filter(MagicalEffect.effect_type == effect_type)
                    .first()
                )
                
                if existing:
                    continue
                
                # Create new magical effect
                effect = MagicalEffect(
                    effect_id=effect_type,
                    name=effect_info.get('name', effect_type.replace('_', ' ').title()),
                    description=effect_info.get('description', ''),
                    effect_type=effect_type,
                    school=effect_info.get('school', 'general'),
                    rarity=effect_info.get('rarity', 'common'),
                    base_power=effect_info.get('base_power', 50),
                    scaling_type=effect_info.get('scaling_type', 'linear'),
                    parameters=effect_info.get('parameters', {}),
                    min_quality_tier=effect_info.get('min_quality_tier', 'basic'),
                    compatible_item_types=effect_info.get('compatible_item_types', [])
                )
                
                self.db.add(effect)
            
            self.db.commit()
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load magical effects from JSON: {e}")


# Factory function for dependency injection
def create_equipment_template_database_repository(db_session: Session, templates_path: str = None) -> EquipmentTemplateDatabaseRepository:
    """Create an equipment template database repository instance"""
    return EquipmentTemplateDatabaseRepository(db_session, templates_path) 