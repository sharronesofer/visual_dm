"""
Equipment Template Repository - JSON Template Management (Infrastructure Layer)

Provides JSON-based template management according to Development Bible standards.
This is INFRASTRUCTURE code - handles file I/O and template loading.

Key Features:
- Load equipment base templates from JSON files
- Template validation and caching
- Quality tier and equipment set management
- Integration with business logic through interfaces
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import asdict
import logging

from backend.systems.equipment.services.business_logic_service import (
    EquipmentBaseTemplate, QualityTierData, RarityTierData, EquipmentSetData, EquipmentSlot
)
from backend.systems.equipment.repositories import IEquipmentTemplateRepository


logger = logging.getLogger(__name__)


class EquipmentTemplateRepository(IEquipmentTemplateRepository):
    """JSON-based equipment template repository implementation"""
    
    def __init__(self, templates_path: str = "data/systems/equipment"):
        self.templates_path = Path(templates_path)
        self._templates_cache: Dict[str, EquipmentBaseTemplate] = {}
        self._quality_tiers_cache: Dict[str, QualityTierData] = {}
        self._rarity_tiers_cache: Dict[str, RarityTierData] = {}
        self._equipment_sets_cache: Dict[str, EquipmentSetData] = {}
        self._loaded = False
    
    def _ensure_loaded(self) -> None:
        """Load templates if not already loaded"""
        if not self._loaded:
            self._load_all_templates()
            self._loaded = True
    
    def _load_all_templates(self) -> None:
        """Load all equipment templates from JSON files"""
        try:
            # Load quality and rarity tiers
            self._load_quality_and_rarity_tiers()
            
            # Load equipment sets
            self._load_equipment_sets()
            
            # Load base templates
            self._load_base_templates()
            
            logger.info(f"Loaded {len(self._templates_cache)} equipment templates")
            
        except Exception as e:
            logger.error(f"Failed to load equipment templates: {e}")
            raise
    
    def _load_quality_and_rarity_tiers(self) -> None:
        """Load quality tier and rarity tier configurations"""
        quality_file = self.templates_path / "quality_tiers.json"
        if quality_file.exists():
            with open(quality_file, 'r') as f:
                data = json.load(f)
                
                # Load quality tiers
                quality_tiers = data.get("quality_tiers", {})
                for tier_id, tier_data in quality_tiers.items():
                    self._quality_tiers_cache[tier_id] = QualityTierData(
                        tier_id=tier_id,
                        name=tier_data["name"],
                        durability_multiplier=tier_data["durability_multiplier"],
                        repair_cost_multiplier=tier_data["repair_cost_multiplier"],
                        crafting_difficulty=tier_data["crafting_difficulty"],
                        description=tier_data["description"],
                        degradation_rate=tier_data["degradation_rate"],
                        max_durability_base=tier_data["max_durability_base"]
                    )
                
                # Load rarity tiers
                rarity_tiers = data.get("rarity_tiers", {})
                for tier_id, tier_data in rarity_tiers.items():
                    self._rarity_tiers_cache[tier_id] = RarityTierData(
                        tier_id=tier_id,
                        name=tier_data["name"],
                        stat_multiplier=tier_data["stat_multiplier"],
                        enchantment_slots=tier_data["enchantment_slots"],
                        rarity_weight=tier_data["rarity_weight"],
                        value_multiplier=tier_data["value_multiplier"],
                        description=tier_data["description"]
                    )
        else:
            # Create default tiers
            self._create_default_quality_tiers()
            self._create_default_rarity_tiers()
    
    def _create_default_quality_tiers(self) -> None:
        """Create default quality tiers if none exist"""
        default_tiers = {
            "basic": QualityTierData("basic", "Basic", 1.0, 1.0, 1, 
                                   "Basic quality equipment made with standard materials.", 1.0, 100),
            "military": QualityTierData("military", "Military", 1.5, 1.3, 3,
                                      "Military grade equipment built for durability.", 0.7, 150),
            "mastercraft": QualityTierData("mastercraft", "Mastercraft", 2.5, 2.0, 5,
                                         "Mastercraft equipment created by legendary artisans.", 0.4, 250)
        }
        self._quality_tiers_cache.update(default_tiers)
    
    def _create_default_rarity_tiers(self) -> None:
        """Create default rarity tiers if none exist"""
        default_tiers = {
            "common": RarityTierData("common", "Common", 1.0, 1, 1.0, 1.0,
                                   "Standard equipment with baseline stats"),
            "rare": RarityTierData("rare", "Rare", 1.3, 2, 0.3, 3.0,
                                 "Enhanced equipment with improved stats"),
            "epic": RarityTierData("epic", "Epic", 1.6, 3, 0.1, 8.0,
                                 "Exceptional equipment with powerful enhancements"),
            "legendary": RarityTierData("legendary", "Legendary", 2.0, 4, 0.02, 20.0,
                                      "Legendary equipment of unparalleled power")
        }
        self._rarity_tiers_cache.update(default_tiers)
    
    def _load_equipment_sets(self) -> None:
        """Load equipment set configurations"""
        sets_file = self.templates_path / "equipment_sets.json"
        if sets_file.exists():
            with open(sets_file, 'r') as f:
                data = json.load(f)
                for set_id, set_data in data.items():
                    self._equipment_sets_cache[set_id] = EquipmentSetData(
                        set_id=set_id,
                        name=set_data["name"],
                        required_slots=set([EquipmentSlot(slot) for slot in set_data["required_slots"]]),
                        set_bonuses=set_data["set_bonuses"],
                        lore_description=set_data.get("lore_description", "")
                    )
        else:
            # Create default equipment sets
            self._create_default_equipment_sets()
    
    def _create_default_equipment_sets(self) -> None:
        """Create default equipment sets if none exist"""
        # Create all 12 equipment sets as required
        default_sets = {
            "warrior": EquipmentSetData(
                "warrior", "Warrior's Might", 
                {EquipmentSlot.WEAPON, EquipmentSlot.CHEST, EquipmentSlot.GLOVES},
                {"2_piece": "+10% Physical Damage", "3_piece": "+15% Physical Damage, +5% Critical Hit"},
                "Ancient armor worn by legendary warriors."
            ),
            "mage": EquipmentSetData(
                "mage", "Arcane Mastery",
                {EquipmentSlot.HAT, EquipmentSlot.CHEST, EquipmentSlot.WEAPON},
                {"2_piece": "+10% Magical Damage", "3_piece": "+15% Magical Damage, +20 Mana"},
                "Robes imbued with arcane energies."
            ),
            "ranger": EquipmentSetData(
                "ranger", "Forest Guardian",
                {EquipmentSlot.WEAPON, EquipmentSlot.BOOTS, EquipmentSlot.GLOVES},
                {"2_piece": "+10% Ranged Damage", "3_piece": "+15% Movement Speed, +10% Critical Hit"},
                "Gear favored by forest dwellers."
            ),
            "paladin": EquipmentSetData(
                "paladin", "Divine Protection",
                {EquipmentSlot.CHEST, EquipmentSlot.OFF_HAND, EquipmentSlot.GLOVES},
                {"2_piece": "+15% Holy Damage", "3_piece": "+10% Damage Reduction, +25% Healing"},
                "Sacred armor blessed by divine light."
            ),
            "assassin": EquipmentSetData(
                "assassin", "Shadow's Edge",
                {EquipmentSlot.WEAPON, EquipmentSlot.BOOTS, EquipmentSlot.PANTS},
                {"2_piece": "+20% Critical Hit", "3_piece": "+15% Movement Speed, +25% Stealth"},
                "Gear designed for silent strikes."
            ),
            "berserker": EquipmentSetData(
                "berserker", "Primal Fury",
                {EquipmentSlot.WEAPON, EquipmentSlot.CHEST, EquipmentSlot.HAT},
                {"2_piece": "+15% Attack Speed", "3_piece": "+20% Damage when below 50% health"},
                "Barbaric equipment that feeds on rage."
            ),
            "scholar": EquipmentSetData(
                "scholar", "Ancient Knowledge",
                {EquipmentSlot.HAT, EquipmentSlot.AMULET, EquipmentSlot.RING_1},
                {"2_piece": "+25% Experience Gain", "3_piece": "+10% to all skills"},
                "Artifacts of forgotten scholars."
            ),
            "demon_hunter": EquipmentSetData(
                "demon_hunter", "Infernal Bane",
                {EquipmentSlot.WEAPON, EquipmentSlot.AMULET, EquipmentSlot.EARRING_1},
                {"2_piece": "+20% Damage vs Demons", "3_piece": "+15% Fire Resistance"},
                "Blessed weapons for hunting dark creatures."
            ),
            "necromancer": EquipmentSetData(
                "necromancer", "Death's Embrace",
                {EquipmentSlot.WEAPON, EquipmentSlot.CHEST, EquipmentSlot.RING_2},
                {"2_piece": "+15% Dark Damage", "3_piece": "+20% Minion Damage"},
                "Dark artifacts that channel death magic."
            ),
            "monk": EquipmentSetData(
                "monk", "Enlightened Path",
                {EquipmentSlot.GLOVES, EquipmentSlot.BOOTS, EquipmentSlot.PANTS},
                {"2_piece": "+10% Movement Speed", "3_piece": "+15% Chi regeneration"},
                "Simple yet powerful monastic gear."
            ),
            "druid": EquipmentSetData(
                "druid", "Nature's Harmony",
                {EquipmentSlot.CHEST, EquipmentSlot.BOOTS, EquipmentSlot.EARRING_2},
                {"2_piece": "+15% Nature Damage", "3_piece": "+20% Transformation Speed"},
                "Living armor that adapts to nature."
            ),
            "elementalist": EquipmentSetData(
                "elementalist", "Primal Elements",
                {EquipmentSlot.WEAPON, EquipmentSlot.HAT, EquipmentSlot.AMULET},
                {"2_piece": "+10% Elemental Damage", "3_piece": "Immune to elemental effects"},
                "Gear attuned to elemental forces."
            )
        }
        self._equipment_sets_cache.update(default_sets)
    
    def _load_base_templates(self) -> None:
        """Load base equipment templates"""
        template_files = [
            'templates/weapons.json',
            'templates/armor.json',
            'templates/accessories.json'
        ]
        
        for template_file in template_files:
            file_path = self.templates_path / template_file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    for template_id, template_data in data.items():
                        self._templates_cache[template_id] = EquipmentBaseTemplate(
                            template_id=template_id,
                            name=template_data["name"],
                            slot=EquipmentSlot(template_data["slot"]),
                            base_stats=template_data["base_stats"],
                            requirements=template_data.get("requirements", {}),
                            max_durability=template_data.get("max_durability", 100),
                            description=template_data.get("description", ""),
                            equipment_set=template_data.get("equipment_set"),
                            allowed_quality_tiers=template_data.get("allowed_quality_tiers", ["basic", "military"]),
                            allowed_rarity_tiers=template_data.get("allowed_rarity_tiers", ["common", "rare"])
                        )
                        
                except Exception as e:
                    logger.error(f"Failed to load template file {template_file}: {e}")
        
        # If no templates were loaded, create defaults
        if not self._templates_cache:
            self._create_default_templates()
    
    def _create_default_templates(self) -> None:
        """Create default equipment templates if none exist"""
        # Create basic templates for each slot
        default_templates = {
            "iron_sword": EquipmentBaseTemplate(
                "iron_sword", "Iron Sword", EquipmentSlot.WEAPON,
                {"physical_damage": 25, "weight": 3}, {"strength": 10}, 120,
                "A well-balanced iron sword.", "warrior", ["basic", "military"]
            ),
            "leather_chest": EquipmentBaseTemplate(
                "leather_chest", "Leather Chestpiece", EquipmentSlot.CHEST,
                {"armor": 15, "weight": 2}, {"constitution": 8}, 100,
                "Sturdy leather armor.", "ranger", ["basic", "military"]
            ),
            "cloth_hat": EquipmentBaseTemplate(
                "cloth_hat", "Cloth Hat", EquipmentSlot.HAT,
                {"magical_defense": 8, "weight": 1}, {"intelligence": 5}, 80,
                "A simple cloth hat for magic users.", "mage", ["basic", "military"]
            ),
            "iron_boots": EquipmentBaseTemplate(
                "iron_boots", "Iron Boots", EquipmentSlot.BOOTS,
                {"armor": 10, "movement_speed": -2, "weight": 4}, {"constitution": 6}, 110,
                "Heavy iron boots providing protection.", "warrior", ["basic", "military"]
            ),
            "leather_gloves": EquipmentBaseTemplate(
                "leather_gloves", "Leather Gloves", EquipmentSlot.GLOVES,
                {"dexterity": 3, "weight": 1}, {"dexterity": 4}, 90,
                "Flexible leather gloves.", "ranger", ["basic", "military"]
            )
        }
        self._templates_cache.update(default_templates)
    
    # Interface implementation
    def get_template(self, template_id: str) -> Optional[EquipmentBaseTemplate]:
        """Get equipment template by ID"""
        self._ensure_loaded()
        return self._templates_cache.get(template_id)
    
    def get_all_templates(self) -> List[EquipmentBaseTemplate]:
        """Get all available templates"""
        self._ensure_loaded()
        return list(self._templates_cache.values())
    
    def get_templates_by_slot(self, slot: EquipmentSlot) -> List[EquipmentBaseTemplate]:
        """Get templates for specific equipment slot"""
        self._ensure_loaded()
        return [template for template in self._templates_cache.values() if template.slot == slot]
    
    def get_templates_by_set(self, equipment_set: str) -> List[EquipmentBaseTemplate]:
        """Get templates for specific equipment set"""
        self._ensure_loaded()
        return [template for template in self._templates_cache.values() if template.equipment_set == equipment_set]
    
    def get_quality_tier(self, tier_id: str) -> Optional[QualityTierData]:
        """Get quality tier data"""
        self._ensure_loaded()
        return self._quality_tiers_cache.get(tier_id)
    
    def get_all_quality_tiers(self) -> List[QualityTierData]:
        """Get all quality tiers"""
        self._ensure_loaded()
        return list(self._quality_tiers_cache.values())
    
    def get_rarity_tier(self, tier_id: str) -> Optional[RarityTierData]:
        """Get rarity tier data"""
        self._ensure_loaded()
        return self._rarity_tiers_cache.get(tier_id)
    
    def get_all_rarity_tiers(self) -> List[RarityTierData]:
        """Get all rarity tiers"""
        self._ensure_loaded()
        return list(self._rarity_tiers_cache.values())
    
    def get_equipment_set(self, set_id: str) -> Optional[EquipmentSetData]:
        """Get equipment set data"""
        self._ensure_loaded()
        return self._equipment_sets_cache.get(set_id)
    
    def get_all_equipment_sets(self) -> List[EquipmentSetData]:
        """Get all equipment sets"""
        self._ensure_loaded()
        return list(self._equipment_sets_cache.values()) 