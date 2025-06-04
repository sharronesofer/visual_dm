"""
Character-Equipment Integration Service

This service bridges the equipment system with Visual DM's character system,
providing seamless equipment management for characters including starting
equipment, level-based recommendations, and character stat integration.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .hybrid_equipment_service import HybridEquipmentService
from .template_service import EquipmentTemplateService
from backend.systems.equipment.models.equipment_models import EquipmentInstance
from backend.systems.character.models.character import Character
from backend.systems.character.services.character_service import CharacterService

logger = logging.getLogger(__name__)

class CharacterEquipmentIntegration:
    """
    Service for integrating equipment system with character management.
    
    Handles:
    - Starting equipment for new characters
    - Equipment recommendations based on character attributes
    - Character stat modifications from equipment
    - Equipment management through character lifecycle
    """
    
    def __init__(self, session: Session):
        """Initialize the integration service."""
        self.session = session
        self.equipment_service = HybridEquipmentService(session)
        self.template_service = EquipmentTemplateService()
        self.character_service = CharacterService(session)
        
        # Ensure templates are loaded
        if not self.template_service._loaded:
            self.template_service.load_all_templates()
        
        logger.info("Initialized CharacterEquipmentIntegration service")
    
    def setup_starting_equipment(self, character_id: str, character_data: Dict[str, Any]) -> List[EquipmentInstance]:
        """
        Set up starting equipment for a new character based on their race/background.
        
        Args:
            character_id: Character's unique identifier
            character_data: Character creation data (race, background, level, etc.)
            
        Returns:
            List of created equipment instances
        """
        try:
            race = character_data.get('race', 'human').lower()
            background = character_data.get('background', 'folk_hero').lower()
            level = character_data.get('level', 1)
            
            logger.info(f"Setting up starting equipment for character {character_id} ({race} {background})")
            
            starting_equipment = []
            
            # Basic starting equipment for all characters
            basic_equipment = [
                ("iron_sword", "Starting Weapon"),
                ("leather_armor", "Starting Armor"),
                ("iron_shield", "Starting Shield")
            ]
            
            # Race-specific starting equipment
            race_equipment = {
                'elf': [("elven_longbow", "Elven Heritage Bow")],
                'dwarf': [("dwarven_axe", "Ancestral Axe")],
                'human': [("quality_cloak", "Traveler's Cloak")],
                'halfling': [("halfling_sling", "Lucky Sling")],
                'dragonborn': [("dragonscale_armor", "Draconic Heritage")],
            }
            
            # Background-specific equipment  
            background_equipment = {
                'soldier': [("military_pack", "Military Issue Gear")],
                'noble': [("signet_ring", "Family Signet"), ("quality_clothes", "Noble Attire")],
                'criminal': [("thieves_tools", "Tools of the Trade")],
                'folk_hero': [("artisan_tools", "Crafting Tools")],
                'acolyte': [("holy_symbol", "Religious Focus")],
            }
            
            # Create basic equipment
            for template_id, custom_name in basic_equipment:
                if self._template_exists(template_id):
                    equipment = self.equipment_service.create_equipment_instance(
                        template_id=template_id,
                        owner_id=character_id,
                        custom_name=custom_name
                    )
                    starting_equipment.append(equipment)
                    logger.debug(f"Created basic equipment: {custom_name}")
            
            # Add race-specific equipment
            if race in race_equipment:
                for template_id, custom_name in race_equipment[race]:
                    if self._template_exists(template_id):
                        equipment = self.equipment_service.create_equipment_instance(
                            template_id=template_id,
                            owner_id=character_id,
                            custom_name=custom_name
                        )
                        starting_equipment.append(equipment)
                        logger.debug(f"Created race equipment: {custom_name}")
            
            # Add background-specific equipment
            if background in background_equipment:
                for template_id, custom_name in background_equipment[background]:
                    if self._template_exists(template_id):
                        equipment = self.equipment_service.create_equipment_instance(
                            template_id=template_id,
                            owner_id=character_id,
                            custom_name=custom_name
                        )
                        starting_equipment.append(equipment)
                        logger.debug(f"Created background equipment: {custom_name}")
            
            # Auto-equip appropriate starting equipment
            self._auto_equip_starting_gear(starting_equipment)
            
            logger.info(f"Created {len(starting_equipment)} starting equipment items for character {character_id}")
            return starting_equipment
            
        except Exception as e:
            logger.error(f"Failed to setup starting equipment for character {character_id}: {e}")
            raise
    
    def get_character_equipment_summary(self, character_id: str) -> Dict[str, Any]:
        """
        Get comprehensive equipment summary for a character including stats.
        
        Args:
            character_id: Character's unique identifier
            
        Returns:
            Dictionary with equipment summary and computed stats
        """
        try:
            equipment_list = self.equipment_service.get_character_equipment(character_id)
            equipped_items = [eq for eq in equipment_list if eq.is_equipped]
            
            # Calculate total stat bonuses from equipped items
            stat_bonuses = {
                'strength': 0, 'dexterity': 0, 'constitution': 0,
                'intelligence': 0, 'wisdom': 0, 'charisma': 0,
                'armor_class': 10, 'attack_bonus': 0, 'damage_bonus': 0
            }
            
            equipped_details = []
            for equipment in equipped_items:
                details = self.equipment_service.get_equipment_details(equipment.id)
                equipped_details.append(details)
                
                # Add stat bonuses from equipment
                current_stats = details.get('current_stats', {})
                for stat, bonus in current_stats.items():
                    if stat in stat_bonuses:
                        stat_bonuses[stat] += bonus
            
            return {
                'character_id': character_id,
                'total_equipment': len(equipment_list),
                'equipped_count': len(equipped_items),
                'unequipped_count': len(equipment_list) - len(equipped_items),
                'equipped_items': equipped_details,
                'stat_bonuses': stat_bonuses,
                'equipment_value': sum(eq.current_value or 0 for eq in equipment_list),
                'average_durability': sum(eq.durability for eq in equipment_list) / len(equipment_list) if equipment_list else 100.0
            }
            
        except Exception as e:
            logger.error(f"Failed to get equipment summary for character {character_id}: {e}")
            raise
    
    def recommend_equipment_upgrades(self, character_id: str, character_level: int = None) -> List[Dict[str, Any]]:
        """
        Recommend equipment upgrades based on character level and current gear.
        
        Args:
            character_id: Character's unique identifier
            character_level: Character's current level (if known)
            
        Returns:
            List of recommended equipment upgrades
        """
        try:
            current_equipment = self.equipment_service.get_character_equipment(character_id)
            recommendations = []
            
            # Get character level if not provided
            if character_level is None:
                try:
                    character = self.character_service.get_character_by_id(character_id)
                    character_level = getattr(character, 'level', 1)
                except:
                    character_level = 1
            
            # Quality tier recommendations based on level
            if character_level >= 10:
                target_quality = 'noble'
            elif character_level >= 5:
                target_quality = 'military'
            else:
                target_quality = 'basic'
            
            # Check each equipped item for upgrade potential
            for equipment in current_equipment:
                if equipment.is_equipped:
                    details = self.equipment_service.get_equipment_details(equipment.id)
                    template = details.get('template')
                    
                    if template and template.quality_tier != target_quality:
                        # Find upgraded version of same equipment type
                        available_templates = self.template_service.find_equipment_by_type(template.item_type)
                        upgrades = [t for t in available_templates if t.quality_tier == target_quality]
                        
                        if upgrades:
                            best_upgrade = max(upgrades, key=lambda x: x.base_value)
                            recommendations.append({
                                'current_item': {
                                    'name': equipment.custom_name or template.name,
                                    'quality': template.quality_tier,
                                    'durability': equipment.durability
                                },
                                'recommended_upgrade': {
                                    'template_id': best_upgrade.id,
                                    'name': best_upgrade.name,
                                    'quality': best_upgrade.quality_tier,
                                    'estimated_value': best_upgrade.base_value,
                                    'reason': f"Level {character_level} character deserves {target_quality} quality gear"
                                }
                            })
            
            # Recommend missing equipment slots
            equipped_slots = {eq.equipment_slot for eq in current_equipment if eq.is_equipped and eq.equipment_slot}
            essential_slots = ['main_hand', 'chest', 'legs', 'feet']
            
            for slot in essential_slots:
                if slot not in equipped_slots:
                    # Find appropriate equipment for this slot
                    slot_templates = [t for t in self.template_service.list_equipment_templates() 
                                    if slot in t.equipment_slots and t.quality_tier == target_quality]
                    
                    if slot_templates:
                        best_option = max(slot_templates, key=lambda x: x.base_value)
                        recommendations.append({
                            'current_item': None,
                            'recommended_upgrade': {
                                'template_id': best_option.id,
                                'name': best_option.name,
                                'quality': best_option.quality_tier,
                                'estimated_value': best_option.base_value,
                                'reason': f"Missing equipment for {slot} slot"
                            }
                        })
            
            logger.info(f"Generated {len(recommendations)} equipment recommendations for character {character_id}")
            return recommendations
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations for character {character_id}: {e}")
            raise
    
    def apply_equipment_to_character_stats(self, character_id: str) -> Dict[str, int]:
        """
        Calculate character stat modifications from equipped items.
        
        Args:
            character_id: Character's unique identifier
            
        Returns:
            Dictionary of stat bonuses from equipment
        """
        try:
            equipped_items = self.equipment_service.get_character_equipment(character_id, equipped_only=True)
            
            total_bonuses = {
                'strength': 0, 'dexterity': 0, 'constitution': 0,
                'intelligence': 0, 'wisdom': 0, 'charisma': 0,
                'armor_class': 0, 'attack_bonus': 0, 'damage_bonus': 0,
                'max_hit_points': 0, 'initiative': 0, 'speed': 0
            }
            
            for equipment in equipped_items:
                details = self.equipment_service.get_equipment_details(equipment.id)
                current_stats = details.get('current_stats', {})
                
                # Apply equipment bonuses
                for stat, bonus in current_stats.items():
                    if stat in total_bonuses:
                        total_bonuses[stat] += bonus
                
                # Apply durability penalties for damaged equipment
                durability_ratio = equipment.durability / 100.0
                if durability_ratio < 0.75:  # Equipment is damaged
                    penalty_multiplier = 1.0 - (0.75 - durability_ratio)
                    for stat, bonus in current_stats.items():
                        if stat in total_bonuses and bonus > 0:
                            penalty = int(bonus * (1.0 - penalty_multiplier))
                            total_bonuses[stat] -= penalty
            
            return total_bonuses
            
        except Exception as e:
            logger.error(f"Failed to calculate equipment bonuses for character {character_id}: {e}")
            return {}
    
    def _template_exists(self, template_id: str) -> bool:
        """Check if an equipment template exists."""
        try:
            template = self.template_service.get_equipment_template(template_id)
            return template is not None
        except:
            return False
    
    def _auto_equip_starting_gear(self, equipment_list: List[EquipmentInstance]) -> None:
        """Automatically equip appropriate starting equipment."""
        try:
            # Auto-equip by priority
            equipment_priority = {
                'weapon': ['main_hand'],
                'armor': ['chest', 'legs', 'feet'],
                'shield': ['off_hand'],
                'accessory': ['finger', 'neck', 'back']
            }
            
            for equipment in equipment_list:
                details = self.equipment_service.get_equipment_details(equipment.id)
                template = details.get('template')
                
                if template and template.equipment_slots:
                    # Try to equip to the first available slot
                    for slot in template.equipment_slots:
                        try:
                            self.equipment_service.equip_item(equipment.id, slot)
                            logger.debug(f"Auto-equipped {equipment.custom_name} to {slot}")
                            break
                        except Exception:
                            continue  # Try next slot if this one fails
                            
        except Exception as e:
            logger.warning(f"Failed to auto-equip some starting gear: {e}")
    
    def on_character_level_up(self, character_id: str, new_level: int) -> Dict[str, Any]:
        """
        Handle equipment-related changes when a character levels up.
        
        Args:
            character_id: Character's unique identifier
            new_level: Character's new level
            
        Returns:
            Dictionary with level-up equipment information
        """
        try:
            logger.info(f"Processing level-up equipment changes for character {character_id} (level {new_level})")
            
            # Get recommendations for new level
            recommendations = self.recommend_equipment_upgrades(character_id, new_level)
            
            # Check if character has reached quality tier thresholds
            quality_milestone = None
            if new_level == 5:
                quality_milestone = "military"
            elif new_level == 10:
                quality_milestone = "noble"
            
            return {
                'character_id': character_id,
                'level': new_level,
                'quality_milestone': quality_milestone,
                'upgrade_recommendations': recommendations,
                'message': f"Character reached level {new_level}! Consider upgrading equipment."
            }
            
        except Exception as e:
            logger.error(f"Failed to process level-up for character {character_id}: {e}")
            return {'error': str(e)}
    
    def on_character_created(self, character_id: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle equipment setup when a new character is created.
        
        Args:
            character_id: Character's unique identifier
            character_data: Character creation data
            
        Returns:
            Dictionary with character creation equipment information
        """
        try:
            logger.info(f"Setting up equipment for newly created character {character_id}")
            
            # Set up starting equipment
            starting_equipment = self.setup_starting_equipment(character_id, character_data)
            
            # Get equipment summary
            summary = self.get_character_equipment_summary(character_id)
            
            return {
                'character_id': character_id,
                'starting_equipment_count': len(starting_equipment),
                'equipment_summary': summary,
                'message': f"Character {character_id} equipped with {len(starting_equipment)} starting items"
            }
            
        except Exception as e:
            logger.error(f"Failed to setup equipment for new character {character_id}: {e}")
            return {'error': str(e)} 